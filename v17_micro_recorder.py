import asyncio
import aiohttp
import sqlite3
import time
import os
from pathlib import Path

DB_PATH = Path("/root/skynet/data/v17_microstructure.sqlite3")

TICKER_URL = "https://contract.mexc.com/api/v1/contract/ticker"
DEPTH_URL = "https://contract.mexc.com/api/v1/contract/depth/{symbol}?limit=20"

POLL_SECONDS = float(os.getenv("V17_REC_POLL_SECONDS", "5"))
CLOSE_AFTER_SECONDS = float(os.getenv("V17_REC_CLOSE_AFTER_SECONDS", "300"))

# Ослабленные пороги: цель сейчас НЕ торговать, а собрать датасет.
MIN_VOL_RATIO = float(os.getenv("V17_REC_MIN_VOL_RATIO", "3"))
MIN_VOL_1M_USD = float(os.getenv("V17_REC_MIN_VOL_1M_USD", "5000"))
MIN_ABS_PRICE_CHANGE = float(os.getenv("V17_REC_MIN_ABS_PRICE_CHANGE", "0.08"))
MAX_ABS_PRICE_CHANGE = float(os.getenv("V17_REC_MAX_ABS_PRICE_CHANGE", "2.50"))
MAX_SIGNALS_PER_CYCLE = int(os.getenv("V17_REC_MAX_SIGNALS_PER_CYCLE", "16"))
SIGNAL_COOLDOWN_SECONDS = float(os.getenv("V17_REC_SIGNAL_COOLDOWN_SECONDS", "120"))

NOTIONAL_USD = float(os.getenv("V17_REC_NOTIONAL_USD", "30"))
TAKER_FEE = float(os.getenv("V17_REC_TAKER_FEE", "0.0008"))  # 0.08% per side
SLIPPAGE_BPS = float(os.getenv("V17_REC_SLIPPAGE_BPS", "5"))

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


def is_allowed_symbol(symbol):
    if not symbol.endswith("_USDT"):
        return False
    clean = symbol.replace("_USDT", "")
    if clean in EXACT_BLACKLIST:
        return False
    if any(bad in clean for bad in PARTIAL_BLACKLIST):
        return False
    return True


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
        current_turnover_rank INTEGER,

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

        max_up_5m REAL DEFAULT 0,
        max_down_5m REAL DEFAULT 0,
        close_5m REAL,
        long_net_5m REAL,
        short_net_5m REAL,

        closed INTEGER DEFAULT 0,
        close_ts REAL,
        close_time_iso TEXT
    )
    """)

    # Если таблица старая/неполная — мягко добавляем недостающие колонки.
    cols = {r["name"] for r in con.execute("PRAGMA table_info(signals)").fetchall()}
    required = {
        "ts": "REAL",
        "time_iso": "TEXT",
        "symbol": "TEXT",
        "clean_symbol": "TEXT",
        "entry_price": "REAL",
        "price_change": "REAL",
        "vol_1m": "REAL",
        "vol_ratio": "REAL",
        "oi_change": "REAL",
        "current_turnover_rank": "INTEGER",
        "spread_bps": "REAL",
        "bid1": "REAL",
        "ask1": "REAL",
        "bid5_usd": "REAL",
        "ask5_usd": "REAL",
        "bid20_usd": "REAL",
        "ask20_usd": "REAL",
        "imb_5": "REAL",
        "imb_20": "REAL",
        "wall_skew": "REAL",
        "max_up_5m": "REAL DEFAULT 0",
        "max_down_5m": "REAL DEFAULT 0",
        "close_5m": "REAL",
        "long_net_5m": "REAL",
        "short_net_5m": "REAL",
        "closed": "INTEGER DEFAULT 0",
        "close_ts": "REAL",
        "close_time_iso": "TEXT",
    }
    for name, typ in required.items():
        if name not in cols:
            con.execute(f"ALTER TABLE signals ADD COLUMN {name} {typ}")

    con.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol_ts ON signals(symbol, ts)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_signals_closed ON signals(closed)")
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
    for lvl in levels[:n]:
        p, q = parse_depth_level(lvl)
        v = p * q if p > 0 and q > 0 else 0.0
        total += v
        max_level = max(max_level, v)
    return total, max_level


async def fetch_depth(session, symbol):
    try:
        url = DEPTH_URL.format(symbol=symbol)
        async with session.get(url, timeout=5) as r:
            if r.status != 200:
                return {"ok": False, "reason": f"HTTP_{r.status}"}
            data = await r.json()
            d = data.get("data", data)
            bids = d.get("bids") or d.get("bidsList") or []
            asks = d.get("asks") or d.get("asksList") or []
            if not bids or not asks:
                return {"ok": False, "reason": "EMPTY_BOOK"}

            bid1, _ = parse_depth_level(bids[0])
            ask1, _ = parse_depth_level(asks[0])
            if bid1 <= 0 or ask1 <= 0 or ask1 <= bid1:
                return {"ok": False, "reason": "BAD_BID_ASK"}

            spread_bps = ((ask1 - bid1) / bid1) * 10000.0

            bid5, max_bid5 = depth_sum(bids, 5)
            ask5, max_ask5 = depth_sum(asks, 5)
            bid20, max_bid20 = depth_sum(bids, 20)
            ask20, max_ask20 = depth_sum(asks, 20)

            imb5 = (bid5 - ask5) / (bid5 + ask5) if (bid5 + ask5) > 0 else 0.0
            imb20 = (bid20 - ask20) / (bid20 + ask20) if (bid20 + ask20) > 0 else 0.0

            bid_wall = max_bid20 / bid20 if bid20 > 0 else 0.0
            ask_wall = max_ask20 / ask20 if ask20 > 0 else 0.0
            wall_skew = bid_wall - ask_wall

            return {
                "ok": True,
                "spread_bps": spread_bps,
                "bid1": bid1,
                "ask1": ask1,
                "bid5_usd": bid5,
                "ask5_usd": ask5,
                "bid20_usd": bid20,
                "ask20_usd": ask20,
                "imb_5": imb5,
                "imb_20": imb20,
                "wall_skew": wall_skew,
            }
    except Exception as e:
        return {"ok": False, "reason": f"EXC_{type(e).__name__}"}


def calc_net(close_pct, spread_bps):
    # close_pct — движение цены в процентах в сторону LONG.
    # Для SHORT используем -close_pct.
    fee_pct = TAKER_FEE * 2.0 * 100.0
    slip_pct = (SLIPPAGE_BPS * 2.0) / 100.0
    spread_pct = max(0.0, spread_bps) / 100.0
    total_cost_pct = fee_pct + slip_pct + spread_pct
    return NOTIONAL_USD * ((close_pct - total_cost_pct) / 100.0)


def load_active(con):
    active = {}
    rows = con.execute("""
        SELECT id, ts, symbol, clean_symbol, entry_price, spread_bps,
               COALESCE(max_up_5m, 0) AS max_up_5m,
               COALESCE(max_down_5m, 0) AS max_down_5m
        FROM signals
        WHERE closed = 0
    """).fetchall()
    for r in rows:
        active[int(r["id"])] = dict(r)
    return active


def insert_signal(con, c, d, ts):
    cur = con.execute("""
        INSERT INTO signals (
            ts, time_iso, symbol, clean_symbol,
            entry_price, price_change, vol_1m, vol_ratio, oi_change, current_turnover_rank,
            spread_bps, bid1, ask1, bid5_usd, ask5_usd, bid20_usd, ask20_usd,
            imb_5, imb_20, wall_skew,
            max_up_5m, max_down_5m, closed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
    """, (
        ts, now_iso(), c["symbol"], c["clean_symbol"],
        c["price"], c["price_change"], c["vol_1m"], c["vol_ratio"], c["oi_change"], c["rank"],
        d.get("spread_bps", 999.0), d.get("bid1", 0.0), d.get("ask1", 0.0),
        d.get("bid5_usd", 0.0), d.get("ask5_usd", 0.0),
        d.get("bid20_usd", 0.0), d.get("ask20_usd", 0.0),
        d.get("imb_5", 0.0), d.get("imb_20", 0.0), d.get("wall_skew", 0.0),
    ))
    con.commit()
    return cur.lastrowid


def close_or_update_active(con, active, price_by_symbol, ts):
    closed = 0
    for sid, a in list(active.items()):
        symbol = a["symbol"]
        price = price_by_symbol.get(symbol)
        if not price or price <= 0 or a["entry_price"] <= 0:
            continue

        diff = ((price - a["entry_price"]) / a["entry_price"]) * 100.0
        a["max_up_5m"] = max(float(a.get("max_up_5m", 0.0)), diff)
        a["max_down_5m"] = min(float(a.get("max_down_5m", 0.0)), diff)

        age = ts - float(a["ts"])
        if age >= CLOSE_AFTER_SECONDS:
            spread = sf(a.get("spread_bps"), 999.0)
            long_net = calc_net(diff, spread)
            short_net = calc_net(-diff, spread)

            con.execute("""
                UPDATE signals
                SET closed=1,
                    close_ts=?,
                    close_time_iso=?,
                    close_5m=?,
                    max_up_5m=?,
                    max_down_5m=?,
                    long_net_5m=?,
                    short_net_5m=?
                WHERE id=?
            """, (
                ts, now_iso(), diff, a["max_up_5m"], a["max_down_5m"],
                long_net, short_net, sid
            ))
            con.commit()
            print(
                f"[{now_iso()}] CLOSE id={sid} {a['clean_symbol']} "
                f"close={diff:+.2f}% mfe={a['max_up_5m']:+.2f}% mae={a['max_down_5m']:+.2f}% "
                f"longNet={long_net:+.3f}$ shortNet={short_net:+.3f}$",
                flush=True
            )
            active.pop(sid, None)
            closed += 1
        else:
            con.execute("""
                UPDATE signals
                SET max_up_5m=?, max_down_5m=?
                WHERE id=?
            """, (a["max_up_5m"], a["max_down_5m"], sid))
    if closed:
        con.commit()
    return closed


async def main():
    con = connect_db()
    init_db(con)
    active = load_active(con)

    history = {}
    last_signal_ts = {}

    last_heartbeat = 0.0
    cycles = 0
    total_raw = 0
    total_inserted = 0
    total_depth_fail = 0
    total_closed = 0

    print(
        f"[{now_iso()}] V17_MICRO_RECORDER_START "
        f"db={DB_PATH} poll={POLL_SECONDS}s minVolRatio={MIN_VOL_RATIO} "
        f"minVol1m=${MIN_VOL_1M_USD:.0f} minAbsPc={MIN_ABS_PRICE_CHANGE}% "
        f"closeAfter={CLOSE_AFTER_SECONDS}s",
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
                    print(f"[{now_iso()}] BAD_TICKER_DATA", flush=True)
                    await asyncio.sleep(POLL_SECONDS)
                    continue

                price_by_symbol = {}
                turnover = []

                for coin in rows:
                    symbol = coin.get("symbol", "")
                    if not is_allowed_symbol(symbol):
                        continue
                    price = sf(coin.get("lastPrice"))
                    amount24 = sf(coin.get("amount24") or coin.get("volume24"))
                    if price <= 0:
                        continue
                    price_by_symbol[symbol] = price
                    turnover.append((amount24, symbol))

                turnover.sort(reverse=True)
                rank_map = {sym: i + 1 for i, (_, sym) in enumerate(turnover)}

                total_closed += close_or_update_active(con, active, price_by_symbol, ts)

                candidates = []

                for coin in rows:
                    symbol = coin.get("symbol", "")
                    if not is_allowed_symbol(symbol):
                        continue

                    clean = symbol.replace("_USDT", "")
                    price = sf(coin.get("lastPrice"))
                    amount24 = sf(coin.get("amount24") or coin.get("volume24"))
                    oi = sf(coin.get("holdVol"))

                    if price <= 0 or amount24 <= 0:
                        continue

                    prev = history.get(symbol)

                    if not prev:
                        history[symbol] = {"ts": ts, "price": price, "amount24": amount24, "oi": oi}
                        continue

                    dt = ts - prev["ts"]
                    if dt < 45:
                        # ВАЖНО: baseline НЕ обновляем, иначе dt всегда будет ~5 сек.
                        continue
                    if dt > 180:
                        # Старый baseline протух — обновляем и ждём новый нормальный интервал.
                        history[symbol] = {"ts": ts, "price": price, "amount24": amount24, "oi": oi}
                        continue

                    vol_1m = amount24 - prev["amount24"]
                    if vol_1m <= 0:
                        continue

                    avg_1m = amount24 / 1440.0 if amount24 > 0 else 1.0
                    vol_ratio = vol_1m / avg_1m if avg_1m > 0 else 0.0
                    price_change = ((price - prev["price"]) / prev["price"]) * 100.0 if prev["price"] > 0 else 0.0
                    oi_change = ((oi - prev["oi"]) / prev["oi"]) * 100.0 if prev["oi"] > 0 else 0.0

                    # Теперь обновляем baseline только после нормального 45–180s сравнения.
                    history[symbol] = {"ts": ts, "price": price, "amount24": amount24, "oi": oi}

                    if vol_1m < MIN_VOL_1M_USD:
                        continue
                    if vol_ratio < MIN_VOL_RATIO:
                        continue
                    if abs(price_change) < MIN_ABS_PRICE_CHANGE:
                        continue
                    if abs(price_change) > MAX_ABS_PRICE_CHANGE:
                        continue

                    if ts - last_signal_ts.get(symbol, 0.0) < SIGNAL_COOLDOWN_SECONDS:
                        continue

                    candidates.append({
                        "symbol": symbol,
                        "clean_symbol": clean,
                        "price": price,
                        "vol_1m": vol_1m,
                        "vol_ratio": vol_ratio,
                        "price_change": price_change,
                        "oi_change": oi_change,
                        "rank": rank_map.get(symbol, 999999),
                    })

                raw_n = len(candidates)
                total_raw += raw_n

                candidates.sort(key=lambda x: (abs(x["price_change"]) * 100.0 + x["vol_ratio"]), reverse=True)
                candidates = candidates[:MAX_SIGNALS_PER_CYCLE]

                inserted = 0
                depth_fail = 0

                for c in candidates:
                    d = await fetch_depth(session, c["symbol"])
                    if not d.get("ok"):
                        depth_fail += 1
                        total_depth_fail += 1
                        continue

                    sid = insert_signal(con, c, d, ts)
                    last_signal_ts[c["symbol"]] = ts

                    active[sid] = {
                        "id": sid,
                        "ts": ts,
                        "symbol": c["symbol"],
                        "clean_symbol": c["clean_symbol"],
                        "entry_price": c["price"],
                        "spread_bps": d.get("spread_bps", 999.0),
                        "max_up_5m": 0.0,
                        "max_down_5m": 0.0,
                    }

                    inserted += 1
                    total_inserted += 1

                    print(
                        f"[{now_iso()}] SIGNAL id={sid} {c['clean_symbol']} "
                        f"pc={c['price_change']:+.2f}% vol=x{c['vol_ratio']:.1f} "
                        f"vol1m=${c['vol_1m']:.0f} oi={c['oi_change']:+.1f}% "
                        f"rank={c['rank']} spread={d.get('spread_bps',999):.2f}bps "
                        f"imb5={d.get('imb_5',0):+.2f} wall={d.get('wall_skew',0):+.2f}",
                        flush=True
                    )

                if ts - last_heartbeat >= 60:
                    last_heartbeat = ts
                    db_count = con.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
                    db_closed = con.execute("SELECT COUNT(*) FROM signals WHERE closed=1").fetchone()[0]
                    print(
                        f"[{now_iso()}] HEARTBEAT cycles={cycles} "
                        f"rawThis={raw_n} insThis={inserted} depthFailThis={depth_fail} "
                        f"totalRaw={total_raw} totalInserted={total_inserted} "
                        f"active={len(active)} dbSignals={db_count} dbClosed={db_closed} totalClosed={total_closed}",
                        flush=True
                    )

            except Exception as e:
                print(f"[{now_iso()}] LOOP_EXCEPTION {type(e).__name__}: {e}", flush=True)

            await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
