import os
import time
import json
import math
import sqlite3
import asyncio
from datetime import datetime, timezone

import aiohttp
from dotenv import load_dotenv

# ============================================================
# SKYNET RECORDER v1
#
# Separate lightweight forward-data recorder.
# It DOES NOT trade.
# It DOES NOT read bot logs.
# It records candidate anomaly context into SQLite for later replay/backtests:
# - ticker-derived anomaly metrics
# - 1m candle shape
# - 15m trend
# - BTC context
# - depth/spread only for top candidates
#
# Runs parallel to skynet_main.py as a separate systemd service.
# ============================================================

ENV_PATH = os.getenv("SKYNET_ENV", "/root/skynet/.env")
load_dotenv(ENV_PATH)

BOT_VERSION = "SKYNET_RECORDER_V1_CANDIDATE_DEPTH_SQLITE"

DATA_DIR = os.getenv("RECORDER_DATA_DIR", "/root/skynet/data")
DB_PATH = os.getenv("RECORDER_DB_PATH", os.path.join(DATA_DIR, "skynet_recorder.sqlite3"))

TICKER_URL = "https://contract.mexc.com/api/v1/contract/ticker"

SCAN_SLEEP_SECONDS = float(os.getenv("RECORDER_SCAN_SLEEP_SECONDS", "5"))

# Base anomaly settings should stay close to main bot.
MIN_VOL_1M = float(os.getenv("MIN_VOL_1M", "30000"))
MIN_AVG_1M_VOL = float(os.getenv("MIN_AVG_1M_VOL", "4000"))
VOL_MULTIPLIER = float(os.getenv("VOL_MULTIPLIER", "8"))
PRICE_CHANGE_MIN = float(os.getenv("PRICE_CHANGE_MIN", "0.20"))
PRICE_CHANGE_MAX = float(os.getenv("PRICE_CHANGE_MAX", "0.85"))

BTC_DUMP_LIMIT = float(os.getenv("BTC_DUMP_LIMIT", "-0.30"))
TREND_15M_LIMIT = float(os.getenv("TREND_15M_LIMIT", "0.0"))

DEPTH_LIMIT = int(os.getenv("RECORDER_DEPTH_LIMIT", "5"))
DEPTH_TIMEOUT = float(os.getenv("RECORDER_DEPTH_TIMEOUT", "3"))
MAX_SPREAD_BPS_RECORD_OK = float(os.getenv("RECORDER_MAX_SPREAD_BPS_RECORD_OK", "10"))
MIN_TOP5_BID_USDT_RECORD_OK = float(os.getenv("RECORDER_MIN_TOP5_BID_USDT_RECORD_OK", "1000"))
MIN_TOP5_ASK_USDT_RECORD_OK = float(os.getenv("RECORDER_MIN_TOP5_ASK_USDT_RECORD_OK", "1000"))

MAX_DEPTH_CANDIDATES_PER_SNAPSHOT = int(os.getenv("RECORDER_MAX_DEPTH_CANDIDATES_PER_SNAPSHOT", "8"))
DEPTH_CONCURRENCY = int(os.getenv("RECORDER_DEPTH_CONCURRENCY", "2"))
KLINE_CONCURRENCY = int(os.getenv("RECORDER_KLINE_CONCURRENCY", "4"))

EXACT_BLACKLIST = {
    "USDC", "USDE", "FDUSD", "TUSD", "BUSD", "DAI", "EUR",
    "SILVER", "GOLD", "USOIL", "UKOIL", "WTI", "BRENT",
    "COINBASE", "SPX", "NDX", "DXY", "TSLA", "AAPL",
    "NVIDIA", "ROBINHOOD", "ALUMINUM", "XPD", "B", "H", "ON",
    "US", "UB", "COPPER", "RIVER", "PENGU", "FARTCOIN",
    "PLAY", "TESLA", "NAS100", "US30", "XAUT", "XAU", "BTC", "SPX500"
}
PARTIAL_BLACKLIST = ("TRUMP", "MAGA", "STOCK")

depth_cache = {}
DEPTH_CACHE_TTL = float(os.getenv("RECORDER_DEPTH_CACHE_TTL", "3"))


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def now_iso(ts=None):
    if ts is None:
        ts = time.time()
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def is_blacklisted(clean_symbol):
    return clean_symbol in EXACT_BLACKLIST or any(bad in clean_symbol for bad in PARTIAL_BLACKLIST)


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS candidate_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            time_iso TEXT NOT NULL,
            symbol TEXT NOT NULL,
            clean_symbol TEXT NOT NULL,

            price REAL,
            vol_24h REAL,
            vol_1m REAL,
            avg_1m_vol REAL,
            vol_ratio REAL,
            price_change REAL,
            current_oi REAL,
            oi_change REAL,
            funding REAL,

            btc_5m_change REAL,
            btc_15m_volatility REAL,
            trend_15m REAL,

            k_open REAL,
            k_high REAL,
            k_low REAL,
            k_close REAL,
            is_red INTEGER,
            has_tail INTEGER,
            close_position REAL,
            body_ratio REAL,
            upper_wick_ratio REAL,
            lower_wick_ratio REAL,

            score INTEGER,
            structure_risk INTEGER,
            initiative_proxy INTEGER,
            absorption_proxy INTEGER,
            weak_long_result INTEGER,
            high_effort_low_result INTEGER,
            middle_range_noise INTEGER,

            depth_checked INTEGER,
            depth_ok INTEGER,
            depth_reason TEXT,
            bid REAL,
            ask REAL,
            spread_bps REAL,
            top5_bid_usdt REAL,
            top5_ask_usdt REAL,

            raw_json TEXT
        );
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_candidate_ts ON candidate_events(ts);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_candidate_symbol_ts ON candidate_events(symbol, ts);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_candidate_score ON candidate_events(score);")
    con.execute("""
        CREATE TABLE IF NOT EXISTS recorder_heartbeat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            time_iso TEXT NOT NULL,
            loop_count INTEGER,
            market_count INTEGER,
            candidate_count INTEGER,
            depth_checked_count INTEGER,
            error_count INTEGER,
            note TEXT
        );
    """)
    con.commit()
    return con


def candle_shape_metrics(open_p, high_p, low_p, close_p):
    full = high_p - low_p
    if open_p <= 0 or high_p <= 0 or low_p <= 0 or close_p <= 0 or full <= 0:
        return {
            "is_red": 0,
            "has_tail": 0,
            "close_position": 0.5,
            "body_ratio": 0.0,
            "upper_wick_ratio": 0.0,
            "lower_wick_ratio": 0.0,
        }

    is_red = 1 if close_p < open_p else 0
    upper = high_p - max(open_p, close_p)
    lower = min(open_p, close_p) - low_p
    body = abs(close_p - open_p)

    upper_ratio = max(0.0, upper / full)
    lower_ratio = max(0.0, lower / full)
    body_ratio = max(0.0, body / full)
    close_pos = (close_p - low_p) / full
    has_tail = 1 if upper_ratio > 0.40 else 0

    return {
        "is_red": is_red,
        "has_tail": has_tail,
        "close_position": close_pos,
        "body_ratio": body_ratio,
        "upper_wick_ratio": upper_ratio,
        "lower_wick_ratio": lower_ratio,
    }


def compute_score(c):
    score = 0

    if c["btc_15m_volatility"] < 0.15:
        score -= 3

    if c["btc_5m_change"] <= BTC_DUMP_LIMIT:
        score -= 10
    elif c["btc_5m_change"] >= 0.10:
        score += 1

    if c["trend_15m"] <= TREND_15M_LIMIT:
        score -= 10
    elif c["trend_15m"] >= 0.30:
        score += 1

    if c["is_red"] and c["price_change"] > 0:
        pass
    else:
        score += 2

    if c["has_tail"]:
        score -= 2
    elif not c["is_red"]:
        score += 1

    if c["oi_change"] <= -3.0:
        score -= 4
    elif c["oi_change"] > 1.0:
        score += 1
    elif c["oi_change"] < -1.0:
        score -= 1

    if c["funding"] <= -0.01:
        score += 1

    return int(score)


def compute_context_flags(c):
    structure_risk = 0

    close_position = c.get("close_position", 0.5)
    body_ratio = c.get("body_ratio", 0.0)
    upper_wick_ratio = c.get("upper_wick_ratio", 0.0)
    vol_ratio = c.get("vol_ratio", 0.0)

    weak_long_result = int(close_position < 0.55)
    high_effort_low_result = int(vol_ratio >= 12 and body_ratio < 0.25)
    absorption_proxy = int(vol_ratio >= 8 and upper_wick_ratio > 0.40 and close_position < 0.65)
    initiative_proxy = int(close_position >= 0.75 and body_ratio >= 0.45 and not c.get("is_red", 0))

    if weak_long_result:
        structure_risk += 2
    if high_effort_low_result:
        structure_risk += 2
    if absorption_proxy:
        structure_risk += 3
    if c.get("btc_5m_change", 0.0) < -0.05:
        structure_risk += 1
    if c.get("trend_15m", 0.0) < 0.30:
        structure_risk += 1
    if c.get("oi_change", 0.0) < 0:
        structure_risk += 1

    # Candle-only recorder cannot know rolling range position yet.
    middle_range_noise = 0

    return {
        "structure_risk": int(structure_risk),
        "initiative_proxy": initiative_proxy,
        "absorption_proxy": absorption_proxy,
        "weak_long_result": weak_long_result,
        "high_effort_low_result": high_effort_low_result,
        "middle_range_noise": middle_range_noise,
    }


def candidate_priority(c):
    price_center_bonus = -abs(c["price_change"] - 0.45) * 20.0
    trend_quality = min(max(c["trend_15m"], -2.0), 2.0) * 2.0
    oi_quality = max(min(c["oi_change"], 8.0), -4.0)
    btc_quality = c["btc_5m_change"] * 3.0
    vol_quality = min(c["vol_ratio"], 30.0) / 10.0
    structure_penalty = c.get("structure_risk", 0) * 5.0

    return (
        c["score"] * 100.0
        + oi_quality * 4.0
        + trend_quality
        + btc_quality
        + price_center_bonus
        + vol_quality
        - structure_penalty
    )


async def get_kline_1m(session, symbol):
    try:
        url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval=Min1&limit=1"
        async with session.get(url, timeout=5) as res:
            if res.status != 200:
                return None
            payload = await res.json()
            d = payload.get("data")
            if not d or not d.get("open") or not d.get("close"):
                return None

            return {
                "k_open": safe_float(d["open"][0]),
                "k_close": safe_float(d["close"][0]),
                "k_high": safe_float(d["high"][0]),
                "k_low": safe_float(d["low"][0]),
            }
    except Exception:
        return None


async def get_trend_15m(session, symbol):
    try:
        url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval=Min15&limit=1"
        async with session.get(url, timeout=5) as res:
            if res.status != 200:
                return None
            payload = await res.json()
            d = payload.get("data")
            if not d or not d.get("open") or not d.get("close"):
                return None

            open_p = safe_float(d["open"][0])
            close_p = safe_float(d["close"][0])
            if open_p <= 0:
                return None
            return ((close_p - open_p) / open_p) * 100
    except Exception:
        return None


def parse_depth_level(level):
    if isinstance(level, dict):
        p = safe_float(level.get("price") or level.get("p") or level.get("0"))
        q = safe_float(level.get("vol") or level.get("quantity") or level.get("q") or level.get("1"))
        return p, q
    if isinstance(level, (list, tuple)) and len(level) >= 2:
        return safe_float(level[0]), safe_float(level[1])
    return 0.0, 0.0


async def get_depth_metrics(session, symbol):
    try:
        url = f"https://contract.mexc.com/api/v1/contract/depth/{symbol}?limit={DEPTH_LIMIT}"
        async with session.get(url, timeout=DEPTH_TIMEOUT) as res:
            if res.status != 200:
                return {"depth_checked": 1, "depth_ok": 0, "depth_reason": f"HTTP_{res.status}"}

            payload = await res.json()
            d = payload.get("data", payload)
            asks = d.get("asks") or d.get("asksList") or []
            bids = d.get("bids") or d.get("bidsList") or []

            if not asks or not bids:
                return {"depth_checked": 1, "depth_ok": 0, "depth_reason": "EMPTY_BOOK"}

            ask0, _ = parse_depth_level(asks[0])
            bid0, _ = parse_depth_level(bids[0])

            if ask0 <= 0 or bid0 <= 0 or ask0 <= bid0:
                return {
                    "depth_checked": 1, "depth_ok": 0, "depth_reason": "BAD_BID_ASK",
                    "bid": bid0, "ask": ask0
                }

            spread_bps = ((ask0 - bid0) / bid0) * 10000
            top_asks = [parse_depth_level(x) for x in asks[:DEPTH_LIMIT]]
            top_bids = [parse_depth_level(x) for x in bids[:DEPTH_LIMIT]]

            top5_ask_usdt = sum(p * q for p, q in top_asks if p > 0 and q > 0)
            top5_bid_usdt = sum(p * q for p, q in top_bids if p > 0 and q > 0)

            ok = (
                spread_bps <= MAX_SPREAD_BPS_RECORD_OK
                and top5_bid_usdt >= MIN_TOP5_BID_USDT_RECORD_OK
                and top5_ask_usdt >= MIN_TOP5_ASK_USDT_RECORD_OK
            )

            if spread_bps > MAX_SPREAD_BPS_RECORD_OK:
                reason = "SPREAD_WIDE"
            elif top5_bid_usdt < MIN_TOP5_BID_USDT_RECORD_OK or top5_ask_usdt < MIN_TOP5_ASK_USDT_RECORD_OK:
                reason = "DEPTH_THIN"
            else:
                reason = "DEPTH_OK"

            return {
                "depth_checked": 1,
                "depth_ok": int(ok),
                "depth_reason": reason,
                "bid": bid0,
                "ask": ask0,
                "spread_bps": spread_bps,
                "top5_bid_usdt": top5_bid_usdt,
                "top5_ask_usdt": top5_ask_usdt,
            }

    except Exception as e:
        return {"depth_checked": 1, "depth_ok": 0, "depth_reason": f"EXC_{type(e).__name__}", "error": str(e)}


async def enrich_candidates(session, candidates):
    if not candidates:
        return candidates

    kline_sem = asyncio.Semaphore(max(1, KLINE_CONCURRENCY))

    async def add_kline_and_trend(c):
        async with kline_sem:
            k = await get_kline_1m(session, c["symbol"])
            t = await get_trend_15m(session, c["symbol"])

        if k is None or t is None:
            c["bad_enrich"] = True
            return c

        c.update(k)
        c["trend_15m"] = t
        c.update(candle_shape_metrics(c["k_open"], c["k_high"], c["k_low"], c["k_close"]))
        c["score"] = compute_score(c)
        c.update(compute_context_flags(c))
        return c

    enriched = await asyncio.gather(*(add_kline_and_trend(c) for c in candidates))
    enriched = [c for c in enriched if not c.get("bad_enrich")]

    if not enriched:
        return []

    # Check depth only for top-N by priority to avoid API spam.
    ordered = sorted(enriched, key=candidate_priority, reverse=True)
    selected = ordered[:MAX_DEPTH_CANDIDATES_PER_SNAPSHOT]
    selected_symbols = {c["symbol"] for c in selected}

    depth_sem = asyncio.Semaphore(max(1, DEPTH_CONCURRENCY))

    async def add_depth(c):
        symbol = c["symbol"]
        cached = depth_cache.get(symbol)
        now = time.time()
        if cached and now - cached["time"] <= DEPTH_CACHE_TTL:
            c.update(cached["metrics"])
            c["depth_cache"] = 1
            return c

        async with depth_sem:
            m = await get_depth_metrics(session, symbol)

        depth_cache[symbol] = {"time": time.time(), "metrics": dict(m)}
        c.update(m)
        c["depth_cache"] = 0
        return c

    selected = await asyncio.gather(*(add_depth(c) for c in selected))
    selected_by_symbol = {c["symbol"]: c for c in selected}

    out = []
    for c in enriched:
        if c["symbol"] in selected_by_symbol:
            out.append(selected_by_symbol[c["symbol"]])
        else:
            c.update({
                "depth_checked": 0,
                "depth_ok": 0,
                "depth_reason": "NOT_CHECKED_LIMIT",
                "bid": 0.0,
                "ask": 0.0,
                "spread_bps": 999.0,
                "top5_bid_usdt": 0.0,
                "top5_ask_usdt": 0.0,
            })
            out.append(c)

    return out


def insert_candidates(con, candidates):
    if not candidates:
        return 0

    rows = []
    for c in candidates:
        rows.append((
            c["ts"], now_iso(c["ts"]), c["symbol"], c["clean_symbol"],
            c.get("price", 0.0), c.get("vol_24h", 0.0), c.get("vol_1m", 0.0), c.get("avg_1m_vol", 0.0),
            c.get("vol_ratio", 0.0), c.get("price_change", 0.0), c.get("current_oi", 0.0), c.get("oi_change", 0.0),
            c.get("funding", 0.0), c.get("btc_5m_change", 0.0), c.get("btc_15m_volatility", 0.0),
            c.get("trend_15m", 0.0), c.get("k_open", 0.0), c.get("k_high", 0.0), c.get("k_low", 0.0), c.get("k_close", 0.0),
            int(c.get("is_red", 0)), int(c.get("has_tail", 0)), c.get("close_position", 0.0), c.get("body_ratio", 0.0),
            c.get("upper_wick_ratio", 0.0), c.get("lower_wick_ratio", 0.0), int(c.get("score", 0)),
            int(c.get("structure_risk", 0)), int(c.get("initiative_proxy", 0)), int(c.get("absorption_proxy", 0)),
            int(c.get("weak_long_result", 0)), int(c.get("high_effort_low_result", 0)), int(c.get("middle_range_noise", 0)),
            int(c.get("depth_checked", 0)), int(c.get("depth_ok", 0)), c.get("depth_reason", ""),
            c.get("bid", 0.0), c.get("ask", 0.0), c.get("spread_bps", 999.0), c.get("top5_bid_usdt", 0.0), c.get("top5_ask_usdt", 0.0),
            json.dumps(c, ensure_ascii=False, separators=(",", ":")),
        ))

    con.executemany("""
        INSERT INTO candidate_events (
            ts, time_iso, symbol, clean_symbol,
            price, vol_24h, vol_1m, avg_1m_vol, vol_ratio, price_change, current_oi, oi_change, funding,
            btc_5m_change, btc_15m_volatility, trend_15m,
            k_open, k_high, k_low, k_close, is_red, has_tail, close_position, body_ratio, upper_wick_ratio, lower_wick_ratio,
            score, structure_risk, initiative_proxy, absorption_proxy, weak_long_result, high_effort_low_result, middle_range_noise,
            depth_checked, depth_ok, depth_reason, bid, ask, spread_bps, top5_bid_usdt, top5_ask_usdt,
            raw_json
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, rows)
    con.commit()
    return len(rows)


def insert_heartbeat(con, loop_count, market_count, candidate_count, depth_checked_count, error_count, note=""):
    ts = time.time()
    con.execute("""
        INSERT INTO recorder_heartbeat (
            ts, time_iso, loop_count, market_count, candidate_count, depth_checked_count, error_count, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ts, now_iso(ts), loop_count, market_count, candidate_count, depth_checked_count, error_count, note))
    con.commit()


async def main():
    print(f"🚀 {BOT_VERSION} started")
    print(f"DB: {DB_PATH}")
    print(
        "Recorder settings: "
        f"sleep={SCAN_SLEEP_SECONDS}s depth_top={MAX_DEPTH_CANDIDATES_PER_SNAPSHOT} "
        f"depth_conc={DEPTH_CONCURRENCY}"
    )

    con = init_db()

    history = {}
    btc_history = []
    loop_count = 0
    error_count = 0
    last_heartbeat = time.time()
    last_print = time.time()

    async with aiohttp.ClientSession() as session:
        while True:
            loop_count += 1
            current_time = time.time()
            candidate_count = 0
            depth_checked_count = 0
            market_count = 0

            try:
                async with session.get(TICKER_URL, timeout=10) as res:
                    if res.status == 429:
                        print("⚠️ recorder got 429, sleeping 60s")
                        insert_heartbeat(con, loop_count, 0, 0, 0, error_count, "HTTP_429")
                        await asyncio.sleep(60)
                        continue
                    if res.status != 200:
                        error_count += 1
                        await asyncio.sleep(10)
                        continue
                    payload = await res.json()

                market_data = payload.get("data", [])
                if not isinstance(market_data, list):
                    error_count += 1
                    await asyncio.sleep(10)
                    continue

                market_count = len(market_data)

                btc_price = next(
                    (safe_float(coin.get("lastPrice", 0.0)) for coin in market_data if coin.get("symbol") == "BTC_USDT"),
                    0.0
                )

                btc_5m_change = 0.0
                btc_15m_volatility = 100.0

                if btc_price > 0:
                    btc_history.append((current_time, btc_price))
                    btc_history = [x for x in btc_history if current_time - x[0] <= 900]

                if len(btc_history) >= 2:
                    history_5m = [x for x in btc_history if current_time - x[0] <= 300]
                    if len(history_5m) >= 2 and history_5m[0][1] > 0:
                        btc_5m_change = ((btc_price - history_5m[0][1]) / history_5m[0][1]) * 100

                    if len(btc_history) > 5:
                        high = max(x[1] for x in btc_history)
                        low = min(x[1] for x in btc_history)
                        if low > 0:
                            btc_15m_volatility = ((high - low) / low) * 100

                candidates = []

                for coin in market_data:
                    symbol = coin.get("symbol", "")
                    if not symbol.endswith("_USDT"):
                        continue

                    clean_symbol = symbol.replace("_USDT", "")
                    if is_blacklisted(clean_symbol):
                        continue

                    price = safe_float(coin.get("lastPrice", 0.0))
                    vol_24h = safe_float(coin.get("amount24", 0.0))
                    current_oi = safe_float(coin.get("holdVol", 0.0))
                    funding = safe_float(coin.get("fundingRate", 0.0)) * 100

                    if price <= 0:
                        continue

                    if symbol not in history:
                        history[symbol] = {"vol": vol_24h, "price": price, "time": current_time, "oi": current_oi}
                        continue

                    time_since_last = current_time - history[symbol]["time"]

                    if time_since_last < 60:
                        continue

                    old = history[symbol]
                    history[symbol] = {"vol": vol_24h, "price": price, "time": current_time, "oi": current_oi}

                    if time_since_last > 120:
                        continue

                    old_vol = old["vol"]
                    old_price = old["price"]
                    old_oi = old["oi"]

                    vol_1m = vol_24h - old_vol
                    price_change = ((price - old_price) / old_price) * 100 if old_price > 0 else 0.0
                    avg_1m_vol = vol_24h / (24 * 60) if vol_24h > 0 else 1.0
                    oi_change = ((current_oi - old_oi) / old_oi) * 100 if old_oi > 0 else 0.0
                    vol_ratio = vol_1m / avg_1m_vol if avg_1m_vol > 0 else 0.0

                    if (
                        vol_ratio > VOL_MULTIPLIER
                        and vol_1m > MIN_VOL_1M
                        and avg_1m_vol > MIN_AVG_1M_VOL
                        and PRICE_CHANGE_MIN <= price_change <= PRICE_CHANGE_MAX
                        and vol_ratio <= 100
                        and abs(oi_change) <= 20
                    ):
                        candidates.append({
                            "ts": current_time,
                            "symbol": symbol,
                            "clean_symbol": clean_symbol,
                            "price": price,
                            "vol_24h": vol_24h,
                            "vol_1m": vol_1m,
                            "avg_1m_vol": avg_1m_vol,
                            "vol_ratio": vol_ratio,
                            "price_change": price_change,
                            "current_oi": current_oi,
                            "oi_change": oi_change,
                            "funding": funding,
                            "btc_5m_change": btc_5m_change,
                            "btc_15m_volatility": btc_15m_volatility,
                        })

                if candidates:
                    candidates = await enrich_candidates(session, candidates)
                    inserted = insert_candidates(con, candidates)
                    candidate_count = inserted
                    depth_checked_count = sum(1 for c in candidates if c.get("depth_checked"))

                    if inserted:
                        top = sorted(candidates, key=candidate_priority, reverse=True)[:5]
                        print(f"📼 [{time.strftime('%H:%M:%S')}] recorded {inserted} candidates")
                        for c in top:
                            print(
                                f"  {c['clean_symbol']} score={c.get('score')} price={c['price_change']:.2f}% "
                                f"vol=x{c['vol_ratio']:.0f} oi={c['oi_change']:.1f}% "
                                f"trend={c.get('trend_15m', 0.0):.2f}% btc={c['btc_5m_change']:.2f}% "
                                f"spread={c.get('spread_bps', 999):.2f}bps depth={c.get('depth_reason')}"
                            )

                if current_time - last_heartbeat >= 300:
                    insert_heartbeat(con, loop_count, market_count, candidate_count, depth_checked_count, error_count, "OK")
                    last_heartbeat = current_time

                if current_time - last_print >= 60:
                    print(
                        f"✅ [{time.strftime('%H:%M:%S')}] recorder alive | "
                        f"market={market_count} candidates={candidate_count} errors={error_count}"
                    )
                    last_print = current_time

                await asyncio.sleep(SCAN_SLEEP_SECONDS)

            except Exception as e:
                error_count += 1
                print(f"⚠️ recorder exception: {type(e).__name__}: {e}")
                insert_heartbeat(con, loop_count, market_count, candidate_count, depth_checked_count, error_count, f"EXC {type(e).__name__}: {e}")
                await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
