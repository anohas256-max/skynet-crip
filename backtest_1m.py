import os
import csv
import json
import time
import math
import argparse
import asyncio
import zipfile
from pathlib import Path
from datetime import datetime, timezone

import aiohttp
from dotenv import load_dotenv
from telethon import TelegramClient

# ============================================================
# SKYNET HISTORICAL 1M CANDLE BACKTEST v1
#
# Purpose:
# - Fast historical test over MEXC futures 1m candles.
# - Does NOT trade.
# - Does NOT touch running skynet service.
# - Does NOT use depth/spread/OI history because ordinary historical klines
#   do not contain historical depth or reliable per-minute OI.
#
# What it can test:
# - price_change / volume anomaly
# - 15m trend
# - BTC 5m context
# - candle body / close position / wick
# - score thresholds
# - TP/SL/TIME
# - FAST_FAIL / MICRO_LOCK / BE_V2 approximations
#
# What it cannot honestly test:
# - real historical spread/depth
# - order book walls / spoofing / iceberg
# - exact intra-candle event order
# - exact live slippage
# ============================================================

load_dotenv("/root/skynet/.env")

# Optional Telegram sending after backtest.
# Recommended: use a separate session name so it does not fight with the running skynet service.
BACKTEST_SEND_TG = os.getenv("BACKTEST_SEND_TG", "false").lower() == "true"
TG_TARGET = os.getenv("TG_TARGET", "-1002953234396")
BACKTEST_TG_SESSION = os.getenv("BACKTEST_TG_SESSION", "backtest_sender_session")

BASE_URL = "https://contract.mexc.com"
TICKER_URL = f"{BASE_URL}/api/v1/contract/ticker"

BOT_VERSION = "SKYNET_BACKTEST_1M_V1"

DATA_DIR = Path(os.getenv("BACKTEST_DATA_DIR", "/root/skynet/data/backtest"))
CACHE_DIR = DATA_DIR / "cache"
RESULTS_DIR = DATA_DIR / "results"

EXACT_BLACKLIST = {
    "USDC", "USDE", "FDUSD", "TUSD", "BUSD", "DAI", "EUR",
    "SILVER", "GOLD", "USOIL", "UKOIL", "WTI", "BRENT",
    "COINBASE", "SPX", "NDX", "DXY", "TSLA", "AAPL",
    "NVIDIA", "ROBINHOOD", "ALUMINUM", "XPD", "B", "H", "ON",
    "US", "UB", "COPPER", "RIVER", "PENGU", "FARTCOIN",
    "PLAY", "TESLA", "NAS100", "US30", "XAUT", "XAU", "BTC", "SPX500"
}
PARTIAL_BLACKLIST = ("TRUMP", "MAGA", "STOCK")

# Cost model from bot, for margin/leverage test.
COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.0004"))  # per side
SPREAD_BPS = float(os.getenv("SPREAD_BPS", "2"))
SLIPPAGE_BPS = float(os.getenv("SLIPPAGE_BPS", "3"))

MARGIN = float(os.getenv("BACKTEST_MARGIN", "3.0"))
LEVERAGE = float(os.getenv("BACKTEST_LEVERAGE", "4.0"))
TP = float(os.getenv("BACKTEST_TP", "0.8"))
SL = float(os.getenv("BACKTEST_SL", "0.5"))
TIME_STOP_MIN = int(os.getenv("BACKTEST_TIME_STOP_MIN", "15"))

MIN_VOL_RATIO = float(os.getenv("BACKTEST_VOL_RATIO", "8"))
MIN_PRICE_CHANGE = float(os.getenv("BACKTEST_PRICE_MIN", "0.20"))
MAX_PRICE_CHANGE = float(os.getenv("BACKTEST_PRICE_MAX", "0.85"))
ROLLING_VOL_WINDOW = int(os.getenv("BACKTEST_ROLLING_VOL_WINDOW", "1440"))  # 24h of 1m candles

# Context gates to test.
BTC_GATE = float(os.getenv("BACKTEST_BTC_GATE", "-0.05"))
TREND_GATE = float(os.getenv("BACKTEST_TREND_GATE", "0.30"))
FOMO_TREND_GATE = float(os.getenv("BACKTEST_FOMO_TREND_GATE", "0.50"))

# Exit test params.
FAST_FAIL_MIN = int(os.getenv("BACKTEST_FAST_FAIL_MIN", "1"))
FAST_FAIL_MFE = float(os.getenv("BACKTEST_FAST_FAIL_MFE", "0.10"))
FAST_FAIL_PNL = float(os.getenv("BACKTEST_FAST_FAIL_PNL", "-0.20"))

MICRO_LOCK_TRIGGER = float(os.getenv("BACKTEST_MICRO_LOCK_TRIGGER", "0.30"))
MICRO_LOCK_STOP = float(os.getenv("BACKTEST_MICRO_LOCK_STOP", "0.00"))

BE_V2_TRIGGER = float(os.getenv("BACKTEST_BE_V2_TRIGGER", "0.65"))
BE_V2_STOP = float(os.getenv("BACKTEST_BE_V2_STOP", "0.20"))


def safe_float(v, default=0.0):
    try:
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def clean_symbol(symbol):
    return symbol.replace("_USDT", "")


def is_blacklisted(symbol):
    c = clean_symbol(symbol)
    return c in EXACT_BLACKLIST or any(bad in c for bad in PARTIAL_BLACKLIST)


def iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def pct(a, b):
    if b <= 0:
        return 0.0
    return ((a - b) / b) * 100.0


def calc_net_pnl(price_diff_pct, margin=MARGIN, leverage=LEVERAGE):
    notional = margin * leverage
    gross_pnl = notional * (price_diff_pct / 100.0)
    commission_cost = notional * COMMISSION_RATE * 2.0
    spread_cost = notional * (SPREAD_BPS / 10000.0)
    slippage_cost = notional * (SLIPPAGE_BPS / 10000.0) * 2.0
    costs = commission_cost + spread_cost + slippage_cost
    net_pnl = gross_pnl - costs
    return gross_pnl, net_pnl, costs


def parse_mexc_kline(data):
    """
    MEXC futures kline response usually:
    data = {
      time: [...],
      open: [...],
      close: [...],
      high: [...],
      low: [...],
      vol: [...]
    }
    Some variants may return list-like rows; handle common forms.
    """
    if not data:
        return []

    if isinstance(data, dict):
        times = data.get("time") or data.get("t") or []
        opens = data.get("open") or data.get("o") or []
        highs = data.get("high") or data.get("h") or []
        lows = data.get("low") or data.get("l") or []
        closes = data.get("close") or data.get("c") or []
        vols = data.get("vol") or data.get("v") or data.get("amount") or []

        out = []
        n = min(len(times), len(opens), len(highs), len(lows), len(closes), len(vols))
        for i in range(n):
            out.append({
                "t": int(safe_float(times[i])),
                "o": safe_float(opens[i]),
                "h": safe_float(highs[i]),
                "l": safe_float(lows[i]),
                "c": safe_float(closes[i]),
                "v": safe_float(vols[i]),
            })
        out.sort(key=lambda x: x["t"])
        return out

    if isinstance(data, list):
        out = []
        for row in data:
            if isinstance(row, dict):
                t = int(safe_float(row.get("time") or row.get("t")))
                out.append({
                    "t": t,
                    "o": safe_float(row.get("open") or row.get("o")),
                    "h": safe_float(row.get("high") or row.get("h")),
                    "l": safe_float(row.get("low") or row.get("l")),
                    "c": safe_float(row.get("close") or row.get("c")),
                    "v": safe_float(row.get("vol") or row.get("v") or row.get("amount")),
                })
            elif isinstance(row, (list, tuple)) and len(row) >= 6:
                # Guess: time, open, high, low, close, vol
                out.append({
                    "t": int(safe_float(row[0])),
                    "o": safe_float(row[1]),
                    "h": safe_float(row[2]),
                    "l": safe_float(row[3]),
                    "c": safe_float(row[4]),
                    "v": safe_float(row[5]),
                })
        out.sort(key=lambda x: x["t"])
        return out

    return []


async def fetch_json(session, url, params=None, timeout=15):
    async with session.get(url, params=params, timeout=timeout) as res:
        if res.status == 429:
            raise RuntimeError("HTTP_429")
        if res.status != 200:
            text = await res.text()
            raise RuntimeError(f"HTTP_{res.status}: {text[:120]}")
        return await res.json()


async def get_top_symbols(session, top_n):
    payload = await fetch_json(session, TICKER_URL)
    market = payload.get("data", [])
    rows = []
    for coin in market:
        symbol = coin.get("symbol", "")
        if not symbol.endswith("_USDT") or is_blacklisted(symbol):
            continue
        amount = safe_float(coin.get("amount24", 0.0))
        rows.append((amount, symbol))
    rows.sort(reverse=True)
    return [s for _, s in rows[:top_n]]


async def download_klines(session, symbol, start_ts, end_ts, use_cache=True):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{symbol}_{start_ts}_{end_ts}_Min1.json"

    if use_cache and cache_file.exists() and cache_file.stat().st_size > 100:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    all_rows = []
    cursor = start_ts
    # MEXC docs: max 2000 points per request.
    step = 2000 * 60

    while cursor < end_ts:
        chunk_end = min(cursor + step - 60, end_ts)
        url = f"{BASE_URL}/api/v1/contract/kline/{symbol}"
        params = {"interval": "Min1", "start": cursor, "end": chunk_end}

        try:
            payload = await fetch_json(session, url, params=params)
        except RuntimeError as e:
            if "HTTP_429" in str(e):
                await asyncio.sleep(3)
                continue
            print(f"⚠️ kline fetch error {symbol}: {e}")
            break

        rows = parse_mexc_kline(payload.get("data"))
        if rows:
            all_rows.extend(rows)

        cursor = chunk_end + 60
        await asyncio.sleep(0.08)

    # Deduplicate by time and keep valid OHLC.
    by_t = {}
    for r in all_rows:
        if r["t"] and r["o"] > 0 and r["h"] > 0 and r["l"] > 0 and r["c"] > 0:
            by_t[r["t"]] = r

    out = [by_t[t] for t in sorted(by_t)]
    cache_file.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    return out


def candle_metrics(row):
    o, h, l, c = row["o"], row["h"], row["l"], row["c"]
    rng = h - l
    if rng <= 0:
        return {
            "is_red": 0,
            "has_tail": 0,
            "cp": 0.5,
            "body": 0.0,
            "upper": 0.0,
            "lower": 0.0,
        }
    upper = h - max(o, c)
    lower = min(o, c) - l
    body = abs(c - o)
    return {
        "is_red": 1 if c < o else 0,
        "has_tail": 1 if upper / rng > 0.40 else 0,
        "cp": (c - l) / rng,
        "body": body / rng,
        "upper": max(0.0, upper / rng),
        "lower": max(0.0, lower / rng),
    }


def compute_score(signal):
    score = 0
    if signal["btc15_vol"] < 0.15:
        score -= 3
    if signal["btc5"] <= -0.30:
        score -= 10
    elif signal["btc5"] >= 0.10:
        score += 1

    if signal["trend15"] <= 0.0:
        score -= 10
    elif signal["trend15"] >= 0.30:
        score += 1

    if signal["is_red"] and signal["price_change"] > 0:
        pass
    else:
        score += 2

    if signal["has_tail"]:
        score -= 2
    elif not signal["is_red"]:
        score += 1

    # Historical candles don't have OI. Keep OI neutral in candle backtest.
    return int(score)


def context_flags(signal):
    structure = 0
    weak_long = signal["cp"] < 0.55
    high_effort_low_result = signal["vol_ratio"] >= 12 and signal["body"] < 0.25
    absorption = signal["vol_ratio"] >= 8 and signal["upper"] > 0.40 and signal["cp"] < 0.65
    initiative = signal["cp"] >= 0.75 and signal["body"] >= 0.45 and signal["is_red"] == 0

    if weak_long:
        structure += 2
    if high_effort_low_result:
        structure += 2
    if absorption:
        structure += 3
    if signal["btc5"] < -0.05:
        structure += 1
    if signal["trend15"] < 0.30:
        structure += 1

    return {
        "structure": structure,
        "weak_long": int(weak_long),
        "high_effort_low_result": int(high_effort_low_result),
        "absorption": int(absorption),
        "initiative": int(initiative),
    }


def strategy_allows(strategy, s):
    # Raw references similar to old profitable branches.
    if strategy == "MAIN_RAW_SCORE4":
        return s["score"] >= 4 and 0.25 <= s["price_change"] <= 0.75 and s["trend15"] > 0

    if strategy == "MAIN_RAW_SCORE5":
        return s["score"] >= 5 and 0.25 <= s["price_change"] <= 0.75 and s["trend15"] > 0

    # Candidate for v11.1 context.
    if strategy == "MAIN_CONTEXT":
        return (
            s["score"] >= 5
            and 0.25 <= s["price_change"] <= 0.75
            and s["trend15"] >= TREND_GATE
            and s["btc5"] >= BTC_GATE
            and s["structure"] <= 3
        )

    if strategy == "MAIN_CONTEXT_STRICT":
        return (
            s["score"] >= 5
            and 0.25 <= s["price_change"] <= 0.65
            and s["trend15"] >= 0.50
            and s["btc5"] >= 0.0
            and s["structure"] <= 2
        )

    if strategy == "FOMO_CONTEXT":
        return (
            s["score"] >= 6
            and 0.55 < s["price_change"] <= 0.85
            and s["trend15"] >= FOMO_TREND_GATE
            and s["btc5"] >= 0.0
            and s["structure"] <= 2
        )

    if strategy == "INITIATIVE_CONTEXT":
        return (
            s["score"] >= 5
            and 0.25 <= s["price_change"] <= 0.75
            and s["trend15"] >= TREND_GATE
            and s["btc5"] >= BTC_GATE
            and s["initiative"] == 1
            and s["absorption"] == 0
        )

    return False


def simulate_trade(rows, entry_i, mode):
    entry = rows[entry_i]["c"]
    max_profit = 0.0
    max_loss = 0.0
    be_armed = False
    micro_armed = False

    for j in range(entry_i + 1, min(entry_i + TIME_STOP_MIN + 1, len(rows))):
        held = j - entry_i
        r = rows[j]
        high_pct = pct(r["h"], entry)
        low_pct = pct(r["l"], entry)
        close_pct = pct(r["c"], entry)

        max_profit = max(max_profit, high_pct)
        max_loss = min(max_loss, low_pct)

        # Conservative event order: if SL and TP in same candle, count SL first.
        if low_pct <= -SL:
            return {
                "reason": "SL",
                "exit_pct": -SL,
                "mfe": max_profit,
                "mae": max_loss,
                "held": held,
            }

        if mode == "FAST_FAIL" and held >= FAST_FAIL_MIN:
            if max_profit < FAST_FAIL_MFE and close_pct <= FAST_FAIL_PNL:
                return {
                    "reason": "FAST_FAIL",
                    "exit_pct": close_pct,
                    "mfe": max_profit,
                    "mae": max_loss,
                    "held": held,
                }

        # Arm only after a candle proves it. Stop can trigger from next candle onward.
        if mode == "MICRO_LOCK":
            if micro_armed and low_pct <= MICRO_LOCK_STOP:
                return {
                    "reason": "MICRO_LOCK",
                    "exit_pct": MICRO_LOCK_STOP,
                    "mfe": max_profit,
                    "mae": max_loss,
                    "held": held,
                }
            if high_pct >= MICRO_LOCK_TRIGGER:
                micro_armed = True

        if mode == "BE_V2":
            if be_armed and low_pct <= BE_V2_STOP:
                return {
                    "reason": "BE_V2",
                    "exit_pct": BE_V2_STOP,
                    "mfe": max_profit,
                    "mae": max_loss,
                    "held": held,
                }
            if high_pct >= BE_V2_TRIGGER:
                be_armed = True

        if high_pct >= TP:
            return {
                "reason": "TP",
                "exit_pct": TP,
                "mfe": max_profit,
                "mae": max_loss,
                "held": held,
            }

    # Time stop at close of last available candle in window.
    last_i = min(entry_i + TIME_STOP_MIN, len(rows) - 1)
    exit_pct = pct(rows[last_i]["c"], entry)
    return {
        "reason": "TIME",
        "exit_pct": exit_pct,
        "mfe": max_profit,
        "mae": max_loss,
        "held": last_i - entry_i,
    }


def prepare_btc_context(btc_rows):
    # map timestamp -> BTC close
    close_by_t = {r["t"]: r["c"] for r in btc_rows}
    times = sorted(close_by_t)
    return close_by_t, times


def lookup_close_at_or_before(close_by_t, times, ts):
    # simple binary search without bisect import? use bisect.
    import bisect
    pos = bisect.bisect_right(times, ts) - 1
    if pos < 0:
        return None
    return close_by_t[times[pos]]


def generate_signals(symbol, rows, btc_close_by_t, btc_times):
    signals = []
    if len(rows) < max(ROLLING_VOL_WINDOW, 60):
        return signals

    vols = [max(0.0, r["v"]) for r in rows]

    # Rolling volume sum for avg. O(n) cumulative.
    cum = [0.0]
    for v in vols:
        cum.append(cum[-1] + v)

    for i in range(max(ROLLING_VOL_WINDOW, 20), len(rows) - TIME_STOP_MIN - 1):
        r = rows[i]
        prev = rows[i - 1]
        if prev["c"] <= 0:
            continue

        price_change = pct(r["c"], prev["c"])

        start = max(0, i - ROLLING_VOL_WINDOW)
        avg_vol = (cum[i] - cum[start]) / max(1, i - start)
        vol_ratio = r["v"] / avg_vol if avg_vol > 0 else 0.0

        if not (vol_ratio > MIN_VOL_RATIO and MIN_PRICE_CHANGE <= price_change <= MAX_PRICE_CHANGE):
            continue

        trend15 = pct(r["c"], rows[i - 15]["c"]) if i >= 15 else 0.0

        btc_now = lookup_close_at_or_before(btc_close_by_t, btc_times, r["t"])
        btc_5m_old = lookup_close_at_or_before(btc_close_by_t, btc_times, r["t"] - 5 * 60)
        btc_15m_old = lookup_close_at_or_before(btc_close_by_t, btc_times, r["t"] - 15 * 60)

        btc5 = pct(btc_now, btc_5m_old) if btc_now and btc_5m_old else 0.0
        btc15_vol = 100.0
        if btc_now and btc_15m_old:
            # Approx substitute; not real high-low vol, but enough for "dead BTC" penalty tests.
            btc15_vol = abs(pct(btc_now, btc_15m_old))

        cm = candle_metrics(r)
        s = {
            "symbol": symbol,
            "i": i,
            "t": r["t"],
            "entry": r["c"],
            "price_change": price_change,
            "vol_ratio": vol_ratio,
            "trend15": trend15,
            "btc5": btc5,
            "btc15_vol": btc15_vol,
            "is_red": cm["is_red"],
            "has_tail": cm["has_tail"],
            "cp": cm["cp"],
            "body": cm["body"],
            "upper": cm["upper"],
            "lower": cm["lower"],
        }
        s["score"] = compute_score(s)
        s.update(context_flags(s))
        signals.append(s)

    return signals


def summarize(trades):
    by = {}
    for t in trades:
        key = (t["strategy"], t["mode"])
        if key not in by:
            by[key] = {
                "strategy": t["strategy"],
                "mode": t["mode"],
                "trades": 0,
                "TP": 0,
                "SL": 0,
                "TIME": 0,
                "FAST_FAIL": 0,
                "MICRO_LOCK": 0,
                "BE_V2": 0,
                "gross": 0.0,
                "net": 0.0,
                "costs": 0.0,
                "wins": 0,
                "losses": 0,
                "mfe_sum": 0.0,
                "mae_sum": 0.0,
            }
        r = by[key]
        r["trades"] += 1
        r[t["reason"]] = r.get(t["reason"], 0) + 1
        r["gross"] += t["gross"]
        r["net"] += t["net"]
        r["costs"] += t["costs"]
        r["mfe_sum"] += t["mfe"]
        r["mae_sum"] += t["mae"]
        if t["net"] > 0:
            r["wins"] += 1
        elif t["net"] < 0:
            r["losses"] += 1

    rows = []
    for r in by.values():
        trades_n = max(1, r["trades"])
        r["avg_net"] = r["net"] / trades_n
        r["winrate"] = r["wins"] / trades_n * 100.0
        r["avg_mfe"] = r["mfe_sum"] / trades_n
        r["avg_mae"] = r["mae_sum"] / trades_n
        rows.append(r)

    rows.sort(key=lambda x: x["net"], reverse=True)
    return rows


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)



def make_results_zip(zip_path, files):
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            p = Path(p)
            if p.exists():
                z.write(p, p.name)
    return zip_path


def parse_tg_target(value):
    value = str(value).strip()
    if value.startswith("-") and value[1:].isdigit():
        return int(value)
    if value.isdigit():
        return int(value)
    return value


async def send_zip_to_telegram(zip_path, caption, target_value=None):
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")

    if not api_id or not api_hash:
        print("⚠️ Telegram send skipped: API_ID/API_HASH not found in .env")
        return False

    target = parse_tg_target(target_value or TG_TARGET)

    async with TelegramClient(BACKTEST_TG_SESSION, int(api_id), api_hash) as client:
        await client.send_file(
            target,
            str(zip_path),
            caption=caption,
        )

    print(f"📤 Sent to Telegram: {zip_path}")
    return True


async def run(args):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    end_ts = int(time.time()) if args.end is None else int(datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc).timestamp())
    start_ts = end_ts - args.days * 24 * 3600

    async with aiohttp.ClientSession() as session:
        if args.symbols:
            symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
            symbols = [s if s.endswith("_USDT") else f"{s}_USDT" for s in symbols]
        else:
            symbols = await get_top_symbols(session, args.top)

        if "BTC_USDT" not in symbols:
            btc_symbol = "BTC_USDT"
        else:
            btc_symbol = "BTC_USDT"

        print(f"🚀 {BOT_VERSION}")
        print(f"Period: {iso(start_ts)} -> {iso(end_ts)} UTC | days={args.days}")
        print(f"Symbols: {len(symbols)} + BTC context")
        print("Downloading BTC...")
        btc_rows = await download_klines(session, btc_symbol, start_ts, end_ts, use_cache=not args.no_cache)
        btc_close_by_t, btc_times = prepare_btc_context(btc_rows)

        all_trades = []
        signal_rows = []

        strategies = args.strategies.split(",")
        modes = args.modes.split(",")

        for idx, symbol in enumerate(symbols, 1):
            if symbol == "BTC_USDT" or is_blacklisted(symbol):
                continue

            print(f"[{idx}/{len(symbols)}] {symbol} downloading...")
            rows = await download_klines(session, symbol, start_ts, end_ts, use_cache=not args.no_cache)
            if len(rows) < 200:
                print(f"  skip, too few candles: {len(rows)}")
                continue

            signals = generate_signals(symbol, rows, btc_close_by_t, btc_times)
            print(f"  candles={len(rows)} signals={len(signals)}")

            for s in signals:
                signal_rows.append({
                    "time": iso(s["t"]),
                    "symbol": s["symbol"],
                    "score": s["score"],
                    "price_change": round(s["price_change"], 4),
                    "vol_ratio": round(s["vol_ratio"], 4),
                    "trend15": round(s["trend15"], 4),
                    "btc5": round(s["btc5"], 4),
                    "structure": s["structure"],
                    "initiative": s["initiative"],
                    "absorption": s["absorption"],
                    "cp": round(s["cp"], 4),
                    "body": round(s["body"], 4),
                    "upper": round(s["upper"], 4),
                })

                for strategy in strategies:
                    if not strategy_allows(strategy, s):
                        continue
                    for mode in modes:
                        result = simulate_trade(rows, s["i"], mode)
                        gross, net, costs = calc_net_pnl(result["exit_pct"])
                        all_trades.append({
                            "time": iso(s["t"]),
                            "symbol": symbol,
                            "strategy": strategy,
                            "mode": mode,
                            "entry": s["entry"],
                            "score": s["score"],
                            "price_change": s["price_change"],
                            "vol_ratio": s["vol_ratio"],
                            "trend15": s["trend15"],
                            "btc5": s["btc5"],
                            "structure": s["structure"],
                            "initiative": s["initiative"],
                            "absorption": s["absorption"],
                            "reason": result["reason"],
                            "exit_pct": result["exit_pct"],
                            "mfe": result["mfe"],
                            "mae": result["mae"],
                            "held": result["held"],
                            "gross": gross,
                            "net": net,
                            "costs": costs,
                        })

            await asyncio.sleep(0.1)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    summary_rows = summarize(all_trades)

    summary_path = RESULTS_DIR / f"summary_{stamp}.csv"
    trades_path = RESULTS_DIR / f"trades_{stamp}.csv"
    signals_path = RESULTS_DIR / f"signals_{stamp}.csv"

    write_csv(summary_path, summary_rows, [
        "strategy", "mode", "trades", "TP", "SL", "TIME", "FAST_FAIL", "MICRO_LOCK", "BE_V2",
        "net", "gross", "costs", "avg_net", "winrate", "avg_mfe", "avg_mae", "wins", "losses"
    ])

    write_csv(trades_path, all_trades, [
        "time", "symbol", "strategy", "mode", "entry", "score", "price_change", "vol_ratio",
        "trend15", "btc5", "structure", "initiative", "absorption",
        "reason", "exit_pct", "mfe", "mae", "held", "gross", "net", "costs"
    ])

    write_csv(signals_path, signal_rows, [
        "time", "symbol", "score", "price_change", "vol_ratio", "trend15", "btc5",
        "structure", "initiative", "absorption", "cp", "body", "upper"
    ])

    print("\n=== SUMMARY ===")
    for r in summary_rows[:20]:
        print(
            f"{r['strategy']:<24} {r['mode']:<10} "
            f"Net:{r['net']:+.2f}$ Trades:{r['trades']} TP:{r.get('TP',0)} SL:{r.get('SL',0)} "
            f"TIME:{r.get('TIME',0)} FF:{r.get('FAST_FAIL',0)} ML:{r.get('MICRO_LOCK',0)} BE:{r.get('BE_V2',0)} "
            f"Avg:{r['avg_net']:+.3f}$ WR:{r['winrate']:.1f}% MFE:{r['avg_mfe']:.2f}%"
        )

    zip_path = RESULTS_DIR / f"backtest_results_{stamp}.zip"
    make_results_zip(zip_path, [summary_path, trades_path, signals_path])

    print("\nFiles:")
    print(summary_path)
    print(trades_path)
    print(signals_path)
    print(zip_path)

    should_send = args.send_tg or BACKTEST_SEND_TG
    if should_send:
        caption = (
            f"📊 SKYNET backtest results\n"
            f"Period: {iso(start_ts)} → {iso(end_ts)} UTC\n"
            f"Days: {args.days} | Top: {args.top} | Trades: {len(all_trades)} | Signals: {len(signal_rows)}"
        )
        try:
            await send_zip_to_telegram(zip_path, caption, args.tg_target)
        except Exception as e:
            print(f"⚠️ Telegram send failed: {type(e).__name__}: {e}")
            print("ZIP is still saved locally; you can send it manually.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7, help="How many days back from now")
    p.add_argument("--top", type=int, default=30, help="Top N current futures by 24h amount")
    p.add_argument("--symbols", default="", help="Comma list, e.g. ONDO_USDT,FET_USDT,INJ_USDT")
    p.add_argument("--end", default=None, help="UTC ISO end time, e.g. 2026-05-31T00:00:00")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument(
        "--strategies",
        default="MAIN_RAW_SCORE4,MAIN_RAW_SCORE5,MAIN_CONTEXT,MAIN_CONTEXT_STRICT,FOMO_CONTEXT,INITIATIVE_CONTEXT",
    )
    p.add_argument(
        "--modes",
        default="BASE,FAST_FAIL,MICRO_LOCK,BE_V2",
        help="BASE,FAST_FAIL,MICRO_LOCK,BE_V2"
    )
    p.add_argument("--send-tg", action="store_true", help="Send result ZIP to Telegram after run")
    p.add_argument("--tg-target", default=TG_TARGET, help="Telegram target: chat id, @username or me")
    args = p.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
