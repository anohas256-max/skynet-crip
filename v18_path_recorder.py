import asyncio
import aiohttp
import sqlite3
import time
import os
import json
from pathlib import Path

DB_PATH = Path("/root/skynet/data/v18_micro_paths.sqlite3")

TICKER_URL = "https://contract.mexc.com/api/v1/contract/ticker"
DEPTH_URL = "https://contract.mexc.com/api/v1/contract/depth/{symbol}?limit=20"

POLL_SECONDS = 5.0
CLOSE_AFTER_SECONDS = 300.0

MIN_VOL_RATIO = 3.0
MIN_VOL_1M_USD = 5000.0
MIN_ABS_PRICE_CHANGE = 0.08
MAX_ABS_PRICE_CHANGE = 2.50
MAX_SIGNALS_PER_CYCLE = 16
SIGNAL_COOLDOWN_SECONDS = 120.0

EXACT_BLACKLIST = {
    "USDC", "USDE", "FDUSD", "TUSD", "BUSD", "DAI", "EUR",
    "SILVER", "GOLD", "USOIL", "UKOIL", "WTI", "BRENT",
    "COINBASE", "SPX", "NDX", "DXY", "TSLA", "AAPL",
    "NVIDIA", "ROBINHOOD", "ALUMINUM", "XPD", "B", "H", "ON",
    "US", "UB", "COPPER", "RIVER", "PENGU", "FARTCOIN",
    "PLAY", "TESLA", "NAS100", "US30", "XAUT", "XAU", "BTC", "SPX500"
}
PARTIAL_BLACKLIST = ("TRUMP", "MAGA", "STOCK")


def sf(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def now_iso():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def is_allowed(symbol):
    if not symbol.endswith("_USDT"):
        return False
    clean = symbol.replace("_USDT", "")
    if clean in EXACT_BLACKLIST:
        return False
    return not any(x in clean for x in PARTIAL_BLACKLIST)


def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    return con


def init_db(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts REAL,
        time_iso TEXT,
        symbol TEXT,
        clean_symbol TEXT,
        entry_price REAL,

        price_change REAL,
        vol_1m REAL,
        vol_ratio REAL,
        oi_change REAL,
        rank INTEGER,

        spread_bps REAL,
        bid1 REAL,
        ask1 REAL,
        bid5_usd REAL,
        ask5_usd REAL,
        bid20_usd REAL,
        ask20_usd REAL,
        imb_5 REAL,
        imb_20 REAL,
        wall_skew REAL,

        max_up REAL DEFAULT 0,
        max_down REAL DEFAULT 0,
        close_pct REAL,
        path_json TEXT,

        closed INTEGER DEFAULT 0,
        close_ts REAL,
        close_time_iso TEXT
    )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_v18_closed ON signals(closed)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_v18_symbol ON signals(symbol)")
    con.commit()


def parse_depth_level(x):
    if isinstance(x, dict):
        p = sf(x.get("price") or x.get("p") or x.get("0"))
        q = sf(x.get("vol") or x.get("quantity") or x.get("q") or x.get("1"))
        return p, q
    if isinstance(x, (list, tuple)) and len(x) >= 2:
        return sf(x[0]), sf(x[1])
    return 0.0, 0.0


def depth_sum(levels, n):
    total = 0.0
    max_level = 0.0
    for x in levels[:n]:
        p, q = parse_depth_level(x)
        v = p * q if p > 0 and q > 0 else 0.0
        total += v
        max_level = max(max_level, v)
    return total, max_level


async def fetch_depth(session, symbol):
    try:
        async with session.get(DEPTH_URL.format(symbol=symbol), timeout=5) as r:
            if r.status != 200:
                return None
            payload = await r.json()
            d = payload.get("data", payload)
            bids = d.get("bids") or d.get("bidsList") or []
            asks = d.get("asks") or d.get("asksList") or []
            if not bids or not asks:
                return None

            bid1, _ = parse_depth_level(bids[0])
            ask1, _ = parse_depth_level(asks[0])
            if bid1 <= 0 or ask1 <= 0 or ask1 <= bid1:
                return None

            spread_bps = ((ask1 - bid1) / bid1) * 10000.0

            bid5, _ = depth_sum(bids, 5)
            ask5, _ = depth_sum(asks, 5)
            bid20, max_bid20 = depth_sum(bids, 20)
            ask20, max_ask20 = depth_sum(asks, 20)

            imb5 = (bid5 - ask5) / (bid5 + ask5) if bid5 + ask5 > 0 else 0.0
            imb20 = (bid20 - ask20) / (bid20 + ask20) if bid20 + ask20 > 0 else 0.0

            bid_wall = max_bid20 / bid20 if bid20 > 0 else 0.0
            ask_wall = max_ask20 / ask20 if ask20 > 0 else 0.0

            return {
                "spread_bps": spread_bps,
                "bid1": bid1,
                "ask1": ask1,
                "bid5_usd": bid5,
                "ask5_usd": ask5,
                "bid20_usd": bid20,
                "ask20_usd": ask20,
                "imb_5": imb5,
                "imb_20": imb20,
                "wall_skew": bid_wall - ask_wall,
            }
    except Exception:
        return None


def insert_signal(con, c, d, ts):
    cur = con.execute("""
    INSERT INTO signals (
        ts, time_iso, symbol, clean_symbol, entry_price,
        price_change, vol_1m, vol_ratio, oi_change, rank,
        spread_bps, bid1, ask1, bid5_usd, ask5_usd, bid20_usd, ask20_usd,
        imb_5, imb_20, wall_skew,
        max_up, max_down, path_json, closed
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, 0)
    """, (
        ts, now_iso(), c["symbol"], c["clean_symbol"], c["price"],
        c["price_change"], c["vol_1m"], c["vol_ratio"], c["oi_change"], c["rank"],
        d["spread_bps"], d["bid1"], d["ask1"], d["bid5_usd"], d["ask5_usd"],
        d["bid20_usd"], d["ask20_usd"], d["imb_5"], d["imb_20"], d["wall_skew"],
        json.dumps([[0.0, 0.0]], separators=(",", ":"))
    ))
    con.commit()
    return cur.lastrowid


def update_active(con, active, prices, ts):
    closed = 0

    for sid, a in list(active.items()):
        price = prices.get(a["symbol"])
        if not price or price <= 0:
            continue

        age = ts - a["ts"]
        diff = ((price - a["entry_price"]) / a["entry_price"]) * 100.0

        a["max_up"] = max(a["max_up"], diff)
        a["max_down"] = min(a["max_down"], diff)

        # Пишем путь примерно каждые 5 сек.
        if not a["path"] or age - a["path"][-1][0] >= 4.0:
            a["path"].append([round(age, 1), round(diff, 5)])

        if age >= CLOSE_AFTER_SECONDS:
            con.execute("""
            UPDATE signals
            SET closed=1,
                close_ts=?,
                close_time_iso=?,
                close_pct=?,
                max_up=?,
                max_down=?,
                path_json=?
            WHERE id=?
            """, (
                ts, now_iso(), diff, a["max_up"], a["max_down"],
                json.dumps(a["path"], separators=(",", ":")),
                sid
            ))
            con.commit()

            print(
                f"[{now_iso()}] CLOSE id={sid} {a['clean_symbol']} "
                f"close={diff:+.2f}% mfe={a['max_up']:+.2f}% mae={a['max_down']:+.2f}% "
                f"pathN={len(a['path'])}",
                flush=True
            )

            active.pop(sid, None)
            closed += 1
        else:
            con.execute("""
            UPDATE signals
            SET max_up=?, max_down=?, path_json=?
            WHERE id=?
            """, (
                a["max_up"], a["max_down"],
                json.dumps(a["path"], separators=(",", ":")),
                sid
            ))

    con.commit()
    return closed


async def main():
    con = connect_db()
    init_db(con)

    history = {}
    active = {}
    last_signal_ts = {}

    cycles = 0
    total_raw = 0
    total_inserted = 0
    total_closed = 0
    last_heartbeat = 0

    print(
        f"[{now_iso()}] V18_PATH_RECORDER_START db={DB_PATH} "
        f"poll={POLL_SECONDS}s minVolRatio={MIN_VOL_RATIO} minAbsPc={MIN_ABS_PRICE_CHANGE}",
        flush=True
    )

    async with aiohttp.ClientSession() as session:
        while True:
            ts = time.time()
            cycles += 1

            try:
                async with session.get(TICKER_URL, timeout=10) as r:
                    if r.status != 200:
                        print(f"[{now_iso()}] TICKER_HTTP_{r.status}", flush=True)
                        await asyncio.sleep(POLL_SECONDS)
                        continue
                    payload = await r.json()

                rows = payload.get("data", [])
                if not isinstance(rows, list):
                    await asyncio.sleep(POLL_SECONDS)
                    continue

                prices = {}
                turnover = []

                for coin in rows:
                    symbol = coin.get("symbol", "")
                    if not is_allowed(symbol):
                        continue
                    price = sf(coin.get("lastPrice"))
                    amount24 = sf(coin.get("amount24") or coin.get("volume24"))
                    if price <= 0:
                        continue
                    prices[symbol] = price
                    turnover.append((amount24, symbol))

                turnover.sort(reverse=True)
                ranks = {sym: i + 1 for i, (_, sym) in enumerate(turnover)}

                total_closed += update_active(con, active, prices, ts)

                candidates = []

                for coin in rows:
                    symbol = coin.get("symbol", "")
                    if symbol not in prices:
                        continue

                    clean = symbol.replace("_USDT", "")
                    price = prices[symbol]
                    amount24 = sf(coin.get("amount24") or coin.get("volume24"))
                    oi = sf(coin.get("holdVol"))

                    prev = history.get(symbol)
                    if not prev:
                        history[symbol] = {"ts": ts, "price": price, "amount24": amount24, "oi": oi}
                        continue

                    dt = ts - prev["ts"]
                    if dt < 45:
                        continue
                    if dt > 180:
                        history[symbol] = {"ts": ts, "price": price, "amount24": amount24, "oi": oi}
                        continue

                    vol_1m = amount24 - prev["amount24"]
                    if vol_1m <= 0:
                        history[symbol] = {"ts": ts, "price": price, "amount24": amount24, "oi": oi}
                        continue

                    avg_1m = amount24 / 1440.0 if amount24 > 0 else 1.0
                    vol_ratio = vol_1m / avg_1m if avg_1m > 0 else 0.0
                    pc = ((price - prev["price"]) / prev["price"]) * 100.0 if prev["price"] > 0 else 0.0
                    oi_change = ((oi - prev["oi"]) / prev["oi"]) * 100.0 if prev["oi"] > 0 else 0.0

                    history[symbol] = {"ts": ts, "price": price, "amount24": amount24, "oi": oi}

                    if vol_1m < MIN_VOL_1M_USD:
                        continue
                    if vol_ratio < MIN_VOL_RATIO:
                        continue
                    if abs(pc) < MIN_ABS_PRICE_CHANGE or abs(pc) > MAX_ABS_PRICE_CHANGE:
                        continue
                    if ts - last_signal_ts.get(symbol, 0.0) < SIGNAL_COOLDOWN_SECONDS:
                        continue

                    candidates.append({
                        "symbol": symbol,
                        "clean_symbol": clean,
                        "price": price,
                        "vol_1m": vol_1m,
                        "vol_ratio": vol_ratio,
                        "price_change": pc,
                        "oi_change": oi_change,
                        "rank": ranks.get(symbol, 999999),
                    })

                raw_n = len(candidates)
                total_raw += raw_n

                candidates.sort(key=lambda x: abs(x["price_change"]) * 100 + x["vol_ratio"], reverse=True)
                candidates = candidates[:MAX_SIGNALS_PER_CYCLE]

                inserted = 0

                for c in candidates:
                    d = await fetch_depth(session, c["symbol"])
                    if not d:
                        continue

                    sid = insert_signal(con, c, d, ts)
                    last_signal_ts[c["symbol"]] = ts

                    active[sid] = {
                        "id": sid,
                        "symbol": c["symbol"],
                        "clean_symbol": c["clean_symbol"],
                        "entry_price": c["price"],
                        "ts": ts,
                        "max_up": 0.0,
                        "max_down": 0.0,
                        "path": [[0.0, 0.0]],
                    }

                    inserted += 1
                    total_inserted += 1

                    print(
                        f"[{now_iso()}] SIGNAL id={sid} {c['clean_symbol']} "
                        f"pc={c['price_change']:+.2f}% vol=x{c['vol_ratio']:.1f} "
                        f"rank={c['rank']} oi={c['oi_change']:+.1f}% "
                        f"sp={d['spread_bps']:.2f} imb5={d['imb_5']:+.2f} wall={d['wall_skew']:+.2f}",
                        flush=True
                    )

                if ts - last_heartbeat >= 60:
                    last_heartbeat = ts
                    db_count = con.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
                    db_closed = con.execute("SELECT COUNT(*) FROM signals WHERE closed=1").fetchone()[0]
                    print(
                        f"[{now_iso()}] HEARTBEAT cycles={cycles} rawThis={raw_n} insThis={inserted} "
                        f"totalRaw={total_raw} totalInserted={total_inserted} "
                        f"active={len(active)} dbSignals={db_count} dbClosed={db_closed} totalClosed={total_closed}",
                        flush=True
                    )

            except Exception as e:
                print(f"[{now_iso()}] LOOP_EXCEPTION {type(e).__name__}: {e}", flush=True)

            await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
