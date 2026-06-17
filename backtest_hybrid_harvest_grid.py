import os
import csv
import json
import zipfile
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv("/root/skynet/.env")

ROOT = Path("/root/skynet")
OUT_DIR = ROOT / "data" / "backtest" / "hybrid_harvest_grid"

COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.0004"))

FAMILIES = ["FILTERED_055", "HYBRID_CORE", "HYBRID_SCALP", "HYBRID_SAFE"]
GUARDS = ["RAW", "NO_FALSE", "COMBO_BALANCED", "COMBO_RELAX", "CLEAN_EXEC", "OI0_CLEAN", "BTC0_CLEAN"]
CONFIRMS = ["NONE", "WAIT1_CLOSE"]


def parse_target(value):
    value = str(value).strip()
    if value.startswith("-") and value[1:].isdigit():
        return int(value)
    if value.isdigit():
        return int(value)
    return value


def parse_list_int(s):
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]


def parse_list_str(s, default):
    if not s:
        return default
    return [x.strip().upper() for x in str(s).split(",") if x.strip()]


def utc_iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def pct(a, b):
    b = float(b or 0.0)
    if b <= 0:
        return 0.0
    return (float(a) - b) / b * 100.0


def row_volume(row):
    for key in ("v", "volume", "vol", "base_volume"):
        if key in row:
            return safe_float(row[key], 0.0)
    return 0.0


def ema(values, period):
    if not values:
        return []
    k = 2.0 / (period + 1.0)
    out = [float(values[0])]
    for v in values[1:]:
        out.append(float(v) * k + out[-1] * (1.0 - k))
    return out


def candle_stats(row):
    o = safe_float(row.get("o", row.get("open", 0.0)))
    h = safe_float(row.get("h", row.get("high", 0.0)))
    l = safe_float(row.get("l", row.get("low", 0.0)))
    c = safe_float(row.get("c", row.get("close", 0.0)))
    full = h - l
    if min(o, h, l, c) <= 0 or full <= 0:
        return {
            "is_red": 0, "body_ratio": 0.0, "upper_wick_ratio": 0.0,
            "lower_wick_ratio": 0.0, "close_position": 0.5,
            "range_pct": 0.0, "turnover": 0.0,
        }
    upper = h - max(o, c)
    lower = min(o, c) - l
    body = abs(c - o)
    return {
        "is_red": 1 if c < o else 0,
        "body_ratio": body / full,
        "upper_wick_ratio": max(0.0, upper / full),
        "lower_wick_ratio": max(0.0, lower / full),
        "close_position": (c - l) / full,
        "range_pct": (full / c) * 100.0,
        "turnover": c * row_volume(row),
    }


def compute_breakout_metrics(rows, signal_i):
    if signal_i < 2:
        return {}

    lb10 = rows[max(0, signal_i - 9):signal_i + 1]
    lb15 = rows[max(0, signal_i - 14):signal_i + 1]
    lb30 = rows[max(0, signal_i - 29):signal_i + 1]
    stats10 = [candle_stats(r) for r in lb10]

    total_turnover = sum(s["turnover"] for s in stats10)
    red_turnover = sum(s["turnover"] for s in stats10 if s["is_red"])
    red_volume_share_10m = red_turnover / total_turnover if total_turnover > 0 else 0.0

    rejection_count_10m = sum(1 for s in stats10 if s["upper_wick_ratio"] >= 0.45 and s["close_position"] <= 0.65)
    weak_close_count_10m = sum(1 for s in stats10 if s["close_position"] <= 0.45)
    upper_wick_pressure_10m = sum(s["upper_wick_ratio"] for s in stats10) / max(1, len(stats10))

    false_breakouts_15m = 0
    for idx in range(max(5, signal_i - 14), signal_i + 1):
        prev = rows[max(0, idx - 5):idx]
        if not prev:
            continue
        local_high = max(r["h"] for r in prev)
        s = candle_stats(rows[idx])
        if rows[idx]["h"] > local_high and s["close_position"] < 0.60:
            false_breakouts_15m += 1

    recent_flush_15m = 0
    for r in lb15:
        o = safe_float(r.get("o", 0.0))
        l = safe_float(r.get("l", 0.0))
        if o > 0 and ((l - o) / o) * 100.0 <= -0.60:
            recent_flush_15m = 1
            break

    closes30 = [safe_float(r["c"]) for r in lb30 if safe_float(r.get("c", 0.0)) > 0]
    ema9_vals = ema(closes30, 9)
    if len(ema9_vals) >= 4:
        close_vs_ema9_pct = pct(closes30[-1], ema9_vals[-1])
        ema9_slope_3m_pct = pct(ema9_vals[-1], ema9_vals[-4])
    else:
        close_vs_ema9_pct = 0.0
        ema9_slope_3m_pct = 0.0

    risk_score = 0
    if red_volume_share_10m >= 0.60:
        risk_score += 2
    if rejection_count_10m >= 2:
        risk_score += 2
    if false_breakouts_15m >= 2:
        risk_score += 2
    if recent_flush_15m:
        risk_score += 1
    if upper_wick_pressure_10m >= 0.30:
        risk_score += 1
    if weak_close_count_10m >= 4:
        risk_score += 1
    if ema9_slope_3m_pct < 0:
        risk_score += 1
    if close_vs_ema9_pct < -0.05:
        risk_score += 1

    return {
        "red_volume_share_10m": red_volume_share_10m,
        "rejection_count_10m": rejection_count_10m,
        "weak_close_count_10m": weak_close_count_10m,
        "upper_wick_pressure_10m": upper_wick_pressure_10m,
        "false_breakouts_15m": false_breakouts_15m,
        "recent_flush_15m": recent_flush_15m,
        "close_vs_ema9_pct": close_vs_ema9_pct,
        "ema9_slope_3m_pct": ema9_slope_3m_pct,
        "breakout_risk_score": risk_score,
    }


def is_exhaustion(vol_ratio, price_change):
    return vol_ratio > 25 and price_change > 0.50


def enrich_raw(rows, raw):
    i = int(raw.get("i", -1))
    if i < 0 or i >= len(rows):
        return None

    s = dict(raw)
    m = compute_breakout_metrics(rows, i)
    s.update(m)

    # Normalize field names from backtest_1m.
    s["score"] = int(safe_float(s.get("score"), -999))
    s["price_change"] = safe_float(s.get("price_change"), 999.0)
    s["vol_ratio"] = safe_float(s.get("vol_ratio"), 999.0)
    s["trend15"] = safe_float(s.get("trend15", s.get("trend_15m")), -999.0)
    s["btc5"] = safe_float(s.get("btc5", s.get("btc_5m_change")), -999.0)
    s["oi"] = safe_float(s.get("oi", s.get("oi_change")), 0.0)
    s["structure"] = int(safe_float(s.get("structure", s.get("structure_risk")), 0))
    s["initiative"] = int(bool(s.get("initiative", s.get("initiative_buying_proxy", 0))))
    return s


def family_rule(family, s):
    score = s["score"]
    pc = s["price_change"]
    trend = s["trend15"]
    btc = s["btc5"]
    oi = s["oi"]
    vol = s["vol_ratio"]

    if family == "FILTERED_055":
        return score >= 4 and 0.25 <= pc <= 0.55 and trend > 0

    if family == "HYBRID_CORE":
        classic = score >= 4 and 0.25 <= pc <= 0.55 and 0 < trend <= 2.5 and not is_exhaustion(vol, pc)
        controlled_fomo = score >= 5 and 0.55 < pc <= 0.85 and 0 < trend <= 3.0 and btc >= 0.10 and oi > -1.0 and vol <= 25
        yellow_quality = score == 3 and 0.25 <= pc <= 0.45 and trend >= 0.30 and btc >= 0.10 and oi > 0
        return classic or controlled_fomo or yellow_quality

    if family == "HYBRID_SCALP":
        filtered = score >= 4 and 0.25 <= pc <= 0.45 and 0 < trend <= 2.5 and not is_exhaustion(vol, pc)
        strong_main = score >= 6 and 0.25 <= pc <= 0.55 and 0 < trend <= 2.5 and btc >= 0 and oi > -1.0 and not is_exhaustion(vol, pc)
        very_clean_fomo = score >= 6 and 0.55 < pc <= 0.75 and 0.30 <= trend <= 2.5 and btc >= 0.10 and oi > 1.0 and vol <= 25
        return filtered or strong_main or very_clean_fomo

    if family == "HYBRID_SAFE":
        classic = score >= 4 and 0.25 <= pc <= 0.55 and 0 < trend <= 2.5 and not is_exhaustion(vol, pc)
        controlled_fomo = score >= 6 and 0.55 < pc <= 0.75 and 0 < trend <= 2.5 and btc >= 0.15 and oi > 1.0 and vol <= 25
        yellow_quality = score == 3 and 0.25 <= pc <= 0.45 and trend >= 0.30 and btc >= 0.10 and oi > 0
        yellow_2_tight = score == 2 and 0.25 <= pc <= 0.38 and trend >= 0.30 and btc > 0.05 and oi > 0
        return classic or controlled_fomo or yellow_quality or yellow_2_tight

    return False


def combo_balanced(s):
    return (
        s.get("breakout_risk_score", 999) <= 3
        and s.get("red_volume_share_10m", 1.0) < 0.68
        and s.get("rejection_count_10m", 99) <= 2
        and s.get("false_breakouts_15m", 99) <= 1
        and s.get("recent_flush_15m", 1) == 0
        and s.get("upper_wick_pressure_10m", 999.0) < 0.38
        and s.get("ema9_slope_3m_pct", -999.0) >= -0.02
        and s.get("close_vs_ema9_pct", -999.0) >= -0.10
    )


def guard_rule(guard, s):
    if guard == "RAW":
        return True

    if guard == "NO_FALSE":
        return s.get("false_breakouts_15m", 99) <= 1

    if guard == "COMBO_BALANCED":
        return combo_balanced(s)

    if guard == "COMBO_RELAX":
        return (
            s.get("breakout_risk_score", 999) <= 4
            and s.get("false_breakouts_15m", 99) <= 3
            and s.get("recent_flush_15m", 1) == 0
            and s.get("upper_wick_pressure_10m", 999.0) < 0.45
        )

    if guard == "CLEAN_EXEC":
        return (
            s.get("breakout_risk_score", 999) <= 4
            and s.get("false_breakouts_15m", 99) <= 3
            and s["structure"] <= 2
            and s["initiative"] == 1
            and s["oi"] >= -0.50
            and s["btc5"] >= -0.10
            and s["trend15"] >= 0.30
        )

    if guard == "OI0_CLEAN":
        return (
            s.get("breakout_risk_score", 999) <= 4
            and s.get("false_breakouts_15m", 99) <= 3
            and s["structure"] <= 2
            and s["initiative"] == 1
            and s["oi"] >= 0.0
            and s["btc5"] >= -0.10
            and s["trend15"] >= 0.30
        )

    if guard == "BTC0_CLEAN":
        return (
            s.get("breakout_risk_score", 999) <= 4
            and s.get("false_breakouts_15m", 99) <= 3
            and s["structure"] <= 2
            and s["initiative"] == 1
            and s["oi"] >= -0.50
            and s["btc5"] >= 0.0
            and s["trend15"] >= 0.30
        )

    return False


def apply_confirm(bt, rows, s, confirm):
    i = s["i"]
    if confirm == "NONE":
        out = dict(s)
        out["entry_i"] = i
        out["entry_t"] = rows[i]["t"]
        out["entry"] = rows[i]["c"]
        out["confirm_move_pct"] = 0.0
        out["confirm_low_pct"] = 0.0
        return out

    if i + 1 >= len(rows):
        return None

    sig = rows[i]
    nxt = rows[i + 1]
    sig_close = sig["c"]
    if sig_close <= 0:
        return None

    low_pct = bt.pct(nxt["l"], sig_close)
    move_pct = bt.pct(nxt["c"], sig_close)

    if low_pct <= -0.15:
        return None
    if nxt["c"] <= sig_close:
        return None
    if move_pct > 0.75:
        return None

    out = dict(s)
    out["entry_i"] = i + 1
    out["entry_t"] = rows[i + 1]["t"]
    out["entry"] = rows[i + 1]["c"]
    out["confirm_move_pct"] = move_pct
    out["confirm_low_pct"] = low_pct
    return out


def pre_range_pct(rows, entry_i, lookback):
    start = max(0, entry_i - lookback)
    sub = rows[start:entry_i]
    if not sub:
        return 0.75
    hi = max(r["h"] for r in sub)
    lo = min(r["l"] for r in sub)
    close = rows[entry_i]["c"]
    return (hi - lo) / close * 100.0 if close > 0 else 0.75


def atr5b_params(rows, entry_i):
    rng5 = pre_range_pct(rows, entry_i, 5)
    if rng5 <= 0:
        rng5 = 0.75
    sl = clamp(rng5 * 0.85, 0.40, 0.85)
    partial = clamp(sl * 1.50, 0.70, 1.10)
    runner_tp = clamp(sl * 4.50, 2.00, 3.20)
    runner_stop = clamp(sl * 0.25, 0.08, 0.20)
    return {
        "sl": sl,
        "partial_at": partial,
        "partial_size": 0.50,
        "runner_tp": runner_tp,
        "runner_stop": runner_stop,
        "time_stop": 45,
        "pre_range5": rng5,
    }


def simulate_atr5b(bt, rows, entry_i):
    p = atr5b_params(rows, entry_i)
    entry = rows[entry_i]["c"]
    max_profit = 0.0
    max_loss = 0.0
    partial_done = False

    for j in range(entry_i + 1, min(entry_i + int(p["time_stop"]) + 1, len(rows))):
        held = j - entry_i
        r = rows[j]
        high_pct = bt.pct(r["h"], entry)
        low_pct = bt.pct(r["l"], entry)
        max_profit = max(max_profit, high_pct)
        max_loss = min(max_loss, low_pct)

        # Conservative ordering.
        if not partial_done and low_pct <= -p["sl"]:
            return {"reason": "SL", "exit_pct": -p["sl"], "mfe": max_profit, "mae": max_loss, "held": held, **p}

        if partial_done:
            if low_pct <= p["runner_stop"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_stop"]
                return {"reason": "RUNNER_STOP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held, **p}
            if high_pct >= p["runner_tp"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_tp"]
                return {"reason": "RUNNER_TP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held, **p}

        if not partial_done and high_pct >= p["partial_at"]:
            partial_done = True

    last_i = min(entry_i + int(p["time_stop"]), len(rows) - 1)
    close_pct = bt.pct(rows[last_i]["c"], entry)
    if partial_done:
        weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * close_pct
        reason = "TIME_PARTIAL"
    else:
        weighted = close_pct
        reason = "TIME"

    return {"reason": reason, "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": last_i - entry_i, **p}


def calc_net(margin, leverage, exit_pct, spread_bps, slippage_bps):
    notional = margin * leverage
    gross = notional * (exit_pct / 100.0)
    commission = notional * COMMISSION_RATE * 2
    spread = notional * (spread_bps / 10000.0)
    slippage = notional * (slippage_bps / 10000.0) * 2
    costs = commission + spread + slippage
    return gross, gross - costs, costs


def apply_max_open(records, max_open):
    open_until = []
    accepted = []
    skipped = 0
    for r in sorted(records, key=lambda x: (x["entry_t"], x["symbol"], x["family"], x["guard"], x["confirm"])):
        t = r["entry_t"]
        open_until = [x for x in open_until if x > t]
        if len(open_until) >= max_open:
            skipped += 1
            continue
        accepted.append(r)
        open_until.append(r["exit_t"])
    return accepted, skipped


def summarize(records, skipped_by_maxopen):
    out = {
        "trades": 0, "wins": 0, "losses": 0,
        "gross": 0.0, "net": 0.0, "costs": 0.0,
        "avg_net": 0.0, "winrate": 0.0,
        "avg_mfe": 0.0, "avg_mae": 0.0,
        "skipped_by_maxopen": skipped_by_maxopen,
    }
    for k in ["SL", "TIME", "TIME_PARTIAL", "RUNNER_STOP", "RUNNER_TP"]:
        out[k] = 0

    for r in records:
        out["trades"] += 1
        out["gross"] += r["gross"]
        out["net"] += r["net"]
        out["costs"] += r["costs"]
        out["avg_mfe"] += r["mfe"]
        out["avg_mae"] += r["mae"]
        out[r["reason"]] = out.get(r["reason"], 0) + 1
        if r["net"] > 0:
            out["wins"] += 1
        elif r["net"] < 0:
            out["losses"] += 1
    if out["trades"]:
        n = out["trades"]
        out["avg_net"] = out["net"] / n
        out["winrate"] = out["wins"] / n * 100.0
        out["avg_mfe"] /= n
        out["avg_mae"] /= n
    return out


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


async def send_to_tg(zip_path, caption, target):
    from telethon import TelegramClient
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    if not api_id or not api_hash:
        print("⚠️ Telegram skipped: API_ID/API_HASH missing.")
        return False

    session_name = os.getenv("BACKTEST_TG_SESSION", "backtest_sender_session")
    async with TelegramClient(session_name, int(api_id), api_hash) as client:
        await client.send_file(parse_target(target), str(zip_path), caption=caption)
    return True


async def run(args):
    import backtest_1m as bt
    import aiohttp

    spread_bps = float(args.spread_bps)
    slippage_bps = float(args.slippage_bps)
    max_open_values = parse_list_int(args.max_open)
    families = parse_list_str(args.families, FAMILIES)
    guards = parse_list_str(args.guards, GUARDS)
    confirms = parse_list_str(args.confirms, CONFIRMS)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.end:
        end_ts = int(datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc).timestamp())
    else:
        end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = end_ts - args.days * 24 * 3600

    print(f"🚀 SKYNET HYBRID HARVEST GRID | days={args.days} top={args.top}")
    print(f"Margin=${args.margin} lev={args.leverage}x notional=${args.margin * args.leverage:.2f}")
    print(f"Costs: spread={spread_bps}bps slippage={slippage_bps}bps commission={COMMISSION_RATE}")
    print(f"Families={families}")
    print(f"Guards={guards}")
    print(f"Confirms={confirms}")

    async with aiohttp.ClientSession() as session:
        if args.symbols:
            symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
            symbols = [s if s.endswith("_USDT") else f"{s}_USDT" for s in symbols]
        else:
            symbols = await bt.get_top_symbols(session, args.top)
        symbols = [s for s in symbols if s != "BTC_USDT"]

        print(f"Symbols: {len(symbols)}")
        print("Downloading BTC context...")
        btc_rows = await bt.download_klines(session, "BTC_USDT", start_ts, end_ts, use_cache=not args.no_cache)
        btc_close_by_t, btc_times = bt.prepare_btc_context(btc_rows)

        rows_by_symbol = {}
        signals_by_symbol = {}

        for idx, symbol in enumerate(symbols, 1):
            print(f"[{idx}/{len(symbols)}] {symbol} downloading/generating...")
            rows = await bt.download_klines(session, symbol, start_ts, end_ts, use_cache=not args.no_cache)
            if len(rows) < 200:
                print(f"  skip candles={len(rows)}")
                continue
            raw = bt.generate_signals(symbol, rows, btc_close_by_t, btc_times)
            rows_by_symbol[symbol] = rows
            signals_by_symbol[symbol] = raw
            print(f"  candles={len(rows)} raw_signals={len(raw)}")
            await asyncio.sleep(0.03)

    records_by_key = {}
    total_raw = sum(len(v) for v in signals_by_symbol.values())
    enriched = 0
    family_hits = 0
    guard_hits = 0
    confirm_hits = 0

    for symbol, raw_signals in signals_by_symbol.items():
        rows = rows_by_symbol[symbol]
        for raw in raw_signals:
            s = enrich_raw(rows, raw)
            if not s:
                continue
            enriched += 1

            for family in families:
                if not family_rule(family, s):
                    continue
                family_hits += 1

                for guard in guards:
                    if not guard_rule(guard, s):
                        continue
                    guard_hits += 1

                    for confirm in confirms:
                        entry = apply_confirm(bt, rows, s, confirm)
                        if not entry:
                            continue
                        confirm_hits += 1
                        entry_i = entry["entry_i"]
                        result = simulate_atr5b(bt, rows, entry_i)
                        exit_i = min(entry_i + int(result["held"]), len(rows) - 1)
                        gross, net, costs = calc_net(args.margin, args.leverage, result["exit_pct"], spread_bps, slippage_bps)

                        rec = {
                            "family": family,
                            "guard": guard,
                            "confirm": confirm,
                            "combo": f"{family}|{guard}|{confirm}",
                            "symbol": symbol,
                            "time": utc_iso(entry["entry_t"]),
                            "entry_t": entry["entry_t"],
                            "exit_t": rows[exit_i]["t"],
                            "score": entry["score"],
                            "price_change": entry["price_change"],
                            "vol_ratio": entry["vol_ratio"],
                            "trend15": entry["trend15"],
                            "btc5": entry["btc5"],
                            "oi": entry["oi"],
                            "structure": entry["structure"],
                            "initiative": entry["initiative"],
                            "confirm_move_pct": entry.get("confirm_move_pct", 0.0),
                            "breakout_risk_score": entry.get("breakout_risk_score", 0),
                            "false_breakouts_15m": entry.get("false_breakouts_15m", 0),
                            "red_volume_share_10m": entry.get("red_volume_share_10m", 0.0),
                            "ema9_slope_3m_pct": entry.get("ema9_slope_3m_pct", 0.0),
                            "reason": result["reason"],
                            "exit_pct": result["exit_pct"],
                            "mfe": result["mfe"],
                            "mae": result["mae"],
                            "held": result["held"],
                            "sl": result["sl"],
                            "partial_at": result["partial_at"],
                            "runner_tp": result["runner_tp"],
                            "runner_stop": result["runner_stop"],
                            "time_stop": result["time_stop"],
                            "pre_range5": result.get("pre_range5", 0.0),
                            "gross": gross,
                            "net": net,
                            "costs": costs,
                        }
                        records_by_key.setdefault(rec["combo"], []).append(rec)

    print(f"Raw signals={total_raw} enriched={enriched} family_hits={family_hits} guard_hits={guard_hits} confirm_hits={confirm_hits}")

    summaries = []
    all_trades = []

    for combo, records in records_by_key.items():
        family, guard, confirm = combo.split("|")
        for mo in max_open_values:
            accepted, skipped = apply_max_open(records, mo)
            sm = summarize(accepted, skipped)
            sm.update({
                "family": family,
                "guard": guard,
                "confirm": confirm,
                "combo": combo,
                "max_open": mo,
                "days": args.days,
                "top": args.top,
                "margin": args.margin,
                "leverage": args.leverage,
                "notional": args.margin * args.leverage,
                "spread_bps": spread_bps,
                "slippage_bps": slippage_bps,
                "monthly_pct_on_40": sm["net"] / 40.0 * 100.0,
            })
            summaries.append(sm)
            for r in accepted:
                rr = dict(r)
                rr["max_open"] = mo
                all_trades.append(rr)

    summaries.sort(key=lambda x: (x["net"], x["trades"]), reverse=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_DIR / f"hybrid_harvest_grid_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / f"hybrid_harvest_summary_{stamp}.csv"
    trades_path = run_dir / f"hybrid_harvest_trades_{stamp}.csv"
    manifest_path = run_dir / "manifest.json"
    zip_path = run_dir / f"HYBRID_HARVEST_GRID_RESULTS_{stamp}.zip"

    summary_fields = [
        "combo", "family", "guard", "confirm", "max_open", "days", "top",
        "margin", "leverage", "notional", "spread_bps", "slippage_bps",
        "trades", "skipped_by_maxopen", "wins", "losses", "winrate",
        "gross", "net", "costs", "avg_net", "monthly_pct_on_40",
        "avg_mfe", "avg_mae", "SL", "TIME", "TIME_PARTIAL", "RUNNER_STOP", "RUNNER_TP",
    ]
    trade_fields = [
        "combo", "family", "guard", "confirm", "max_open", "time", "symbol",
        "score", "price_change", "vol_ratio", "trend15", "btc5", "oi", "structure", "initiative",
        "confirm_move_pct", "breakout_risk_score", "false_breakouts_15m",
        "red_volume_share_10m", "ema9_slope_3m_pct",
        "reason", "exit_pct", "mfe", "mae", "held",
        "sl", "partial_at", "runner_tp", "runner_stop", "time_stop", "pre_range5",
        "gross", "net", "costs", "entry_t", "exit_t",
    ]

    write_csv(summary_path, summaries, summary_fields)
    write_csv(trades_path, all_trades, trade_fields)

    manifest = {
        "created_utc": stamp,
        "suite": "HYBRID_HARVEST_GRID",
        "days": args.days,
        "top": args.top,
        "margin": args.margin,
        "leverage": args.leverage,
        "notional": args.margin * args.leverage,
        "spread_bps": spread_bps,
        "slippage_bps": slippage_bps,
        "families": families,
        "guards": guards,
        "confirms": confirms,
        "max_open": max_open_values,
        "raw_signals": total_raw,
        "enriched": enriched,
        "family_hits": family_hits,
        "guard_hits": guard_hits,
        "confirm_hits": confirm_hits,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(summary_path, summary_path.name)
        z.write(trades_path, trades_path.name)
        z.write(manifest_path, manifest_path.name)

    print("\n=== TOP HYBRID HARVEST RESULTS ===")
    for r in summaries[:50]:
        print(
            f"{r['combo']:<55} MO:{r['max_open']} "
            f"Net:{r['net']:+.2f}$ On40:{r['monthly_pct_on_40']:+.1f}% "
            f"Tr:{r['trades']} WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$ "
            f"SL:{r['SL']} PTP:{r['TIME_PARTIAL'] + r['RUNNER_STOP'] + r['RUNNER_TP']}"
        )

    print("\nZIP:", zip_path)

    if args.send_tg:
        caption = (
            f"📦 SKYNET HYBRID HARVEST GRID\n"
            f"days={args.days} top={args.top} margin={args.margin} lev={args.leverage}x\n"
            f"spread={spread_bps} slip={slippage_bps}"
        )
        try:
            await send_to_tg(zip_path, caption, args.tg_target)
            print("📤 Sent to Telegram")
        except Exception as e:
            print(f"⚠️ Telegram send failed: {type(e).__name__}: {e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--top", type=int, default=50)
    p.add_argument("--symbols", default="")
    p.add_argument("--max-open", default="1,2")
    p.add_argument("--margin", type=float, default=3.0)
    p.add_argument("--leverage", type=int, default=10)
    p.add_argument("--spread-bps", type=float, default=2.0)
    p.add_argument("--slippage-bps", type=float, default=3.0)
    p.add_argument("--families", default="")
    p.add_argument("--guards", default="")
    p.add_argument("--confirms", default="")
    p.add_argument("--end", default=None)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--send-tg", action="store_true")
    p.add_argument("--tg-target", default=os.getenv("TG_TARGET", "-1002953234396"))
    args = p.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
