import asyncio
import aiohttp
import sqlite3
import csv
from pathlib import Path
from collections import defaultdict

DB = Path("/root/skynet/data/skynet_recorder.sqlite3")
OUT_DIR = Path("/root/skynet/data/replay_dynamic_ban")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://contract.mexc.com"

MARGIN = 3.0
LEVERAGE = 4
TAKER_FEE = 0.0008
SPREAD_BPS = 2.0
SLIPPAGE_BPS = 3.0

MAX_ROWS = 30000
CONCURRENCY = 4

WAITS = [15, 30, 45, 60]
RUGS = [-0.10, -0.15]
ENTRY_MOVES = [0.00, 0.03, 0.06]
SLS = [0.18, 0.20, 0.25, 0.30]
TPS = [0.25, 0.30, 0.35, 0.45]
TIME_STOPS = [3, 5, 8, 12]

TOX_LIMITS = [1, 2, 3]
BAN_HOURS = [3, 6, 12, 24]
CD_AFTER_SL = [3, 6, 12]

STATIC_BAD_VARIANTS = [
    [],
    ["AAVE"],
    ["AAVE", "DOGE"],
    ["AAVE", "DOGE", "BEAT", "TAO", "VVV"],
]


def sf(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def si(x, default=0):
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default


def net_usd(pct):
    notional = MARGIN * LEVERAGE
    gross = notional * (pct / 100.0)
    fees = notional * TAKER_FEE * 2
    spread = notional * (SPREAD_BPS / 10000.0)
    slip = notional * (SLIPPAGE_BPS / 10000.0) * 2
    costs = fees + spread + slip
    return gross, gross - costs, costs


def load_rows():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("""
        SELECT *
        FROM candidate_events
        ORDER BY ts ASC
        LIMIT ?
    """, (MAX_ROWS,)).fetchall()
    con.close()
    return [dict(r) for r in rows]


def meta_filter(c):
    return (
        si(c.get("score")) >= 4
        and 0.20 <= sf(c.get("price_change")) <= 0.65
        and sf(c.get("vol_ratio")) <= 35
        and sf(c.get("trend_15m")) >= 0.30
        and sf(c.get("btc_5m_change")) >= -0.10
        and sf(c.get("oi_change")) >= -0.50
        and si(c.get("depth_ok")) == 1
        and sf(c.get("spread_bps"), 999) <= 5.0
        and sf(c.get("top5_bid_usdt")) >= 3000
        and sf(c.get("top5_ask_usdt")) >= 3000
        and si(c.get("structure_risk"), 999) <= 2
        and si(c.get("initiative_proxy")) == 1
        and si(c.get("absorption_proxy")) == 0
        and si(c.get("weak_long_result")) == 0
        and si(c.get("high_effort_low_result")) == 0
    )


def strict_filter(c):
    return (
        meta_filter(c)
        and sf(c.get("spread_bps"), 999) <= 2.0
        and si(c.get("structure_risk"), 999) <= 1
        and sf(c.get("trend_15m")) >= 0.40
    )


def liquid_filter(c):
    return (
        si(c.get("score")) >= 3
        and 0.18 <= sf(c.get("price_change")) <= 0.70
        and sf(c.get("vol_ratio")) <= 45
        and sf(c.get("trend_15m")) >= 0.20
        and sf(c.get("btc_5m_change")) >= -0.12
        and sf(c.get("oi_change")) >= -1.00
        and si(c.get("depth_ok")) == 1
        and sf(c.get("spread_bps"), 999) <= 3.0
        and sf(c.get("top5_bid_usdt")) >= 10000
        and sf(c.get("top5_ask_usdt")) >= 10000
        and si(c.get("structure_risk"), 999) <= 2
        and si(c.get("initiative_proxy")) == 1
        and si(c.get("absorption_proxy")) == 0
        and si(c.get("weak_long_result")) == 0
    )


FILTERS = {
    "META": meta_filter,
    "STRICT": strict_filter,
    "LIQUID": liquid_filter,
}


async def fetch_klines(session, symbol, ts):
    start = int(ts) - 180
    end = int(ts) + 60 * 120
    url = f"{BASE_URL}/api/v1/contract/kline/{symbol}"
    params = {"interval": "Min1", "start": start, "end": end}

    try:
        async with session.get(url, params=params, timeout=12) as r:
            if r.status != 200:
                return []
            payload = await r.json()
    except Exception:
        return []

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return []

    times = data.get("time") or []
    opens = data.get("open") or []
    highs = data.get("high") or []
    lows = data.get("low") or []
    closes = data.get("close") or []

    n = min(len(times), len(opens), len(highs), len(lows), len(closes))
    out = []

    for i in range(n):
        out.append({
            "t": int(sf(times[i])),
            "open": sf(opens[i]),
            "high": sf(highs[i]),
            "low": sf(lows[i]),
            "close": sf(closes[i]),
        })

    out.sort(key=lambda x: x["t"])
    return out


def simulate(c, klines, wait, rug, entry_move, sl, tp, time_stop):
    signal = sf(c.get("price"))
    ts = int(sf(c.get("ts")))

    if signal <= 0:
        return {"status": "BAD_SIGNAL"}

    confirm = None
    for k in klines:
        if k["t"] >= ts + wait:
            confirm = k
            break

    if not confirm:
        return {"status": "NO_CONFIRM"}

    window = [k for k in klines if ts <= k["t"] <= confirm["t"]]
    if not window:
        return {"status": "NO_WINDOW"}

    low_from_signal = min(((k["low"] - signal) / signal) * 100 for k in window if k["low"] > 0)
    move_from_signal = ((confirm["close"] - signal) / signal) * 100

    if low_from_signal <= rug:
        return {"status": "DROP_RUG"}

    if move_from_signal < entry_move:
        return {"status": "DROP_NO_FOLLOW"}

    entry = confirm["close"]
    entry_t = confirm["t"]
    path = [k for k in klines if k["t"] >= entry_t]

    if not path:
        return {"status": "NO_PATH"}

    mfe = 0.0
    mae = 0.0
    reason = "END"
    exit_pct = 0.0

    for k in path:
        held = (k["t"] - entry_t) / 60.0
        high_pct = ((k["high"] - entry) / entry) * 100
        low_pct = ((k["low"] - entry) / entry) * 100
        close_pct = ((k["close"] - entry) / entry) * 100

        mfe = max(mfe, high_pct, close_pct)
        mae = min(mae, low_pct, close_pct)

        # если в одной минуте и TP и SL — считаем SL, чтобы не самообманываться
        if low_pct <= -sl:
            reason = "SL"
            exit_pct = -sl
            break

        if high_pct >= tp:
            reason = "TP"
            exit_pct = tp
            break

        if held >= time_stop:
            reason = "TIME"
            exit_pct = close_pct
            break

    if reason == "END":
        last = path[-1]
        exit_pct = ((last["close"] - entry) / entry) * 100

    gross, net, costs = net_usd(exit_pct)

    return {
        "status": "TRADE",
        "reason": reason,
        "net": net,
        "gross": gross,
        "costs": costs,
        "mfe": mfe,
        "mae": mae,
        "symbol": c.get("clean_symbol"),
        "time_iso": c.get("time_iso"),
    }


def run_dynamic(candidates, cache, p):
    toxic = defaultdict(float)
    ban_until = defaultdict(float)

    trades = []
    drops = 0
    nodata = 0
    skip_ban = 0
    static_bad = set(p["static_bad"])

    for c in candidates:
        ts = int(sf(c.get("ts")))
        sym = c.get("clean_symbol") or c.get("symbol", "").replace("_USDT", "")

        if sym in static_bad:
            skip_ban += 1
            continue

        if ban_until[sym] > ts:
            skip_ban += 1
            continue

        kl = cache.get((c["symbol"], int(sf(c["ts"]))), [])
        r = simulate(c, kl, p["wait"], p["rug"], p["entry"], p["sl"], p["tp"], p["time_stop"])
        st = r.get("status")

        if st == "TRADE":
            trades.append(r)

            if r["reason"] == "SL":
                toxic[sym] += 2.0
                ban_until[sym] = max(ban_until[sym], ts + p["cd_sl"] * 3600)

            elif r["reason"] == "TIME":
                if r["net"] < 0 or r["mfe"] < 0.15:
                    toxic[sym] += 1.0
                else:
                    toxic[sym] = max(0.0, toxic[sym] - 0.25)

            elif r["reason"] == "TP":
                toxic[sym] = max(0.0, toxic[sym] - 1.0)

            if toxic[sym] >= p["tox_limit"]:
                ban_until[sym] = max(ban_until[sym], ts + p["ban_h"] * 3600)

        elif st == "DROP_RUG":
            drops += 1
            toxic[sym] += 0.35
            if toxic[sym] >= p["tox_limit"]:
                ban_until[sym] = max(ban_until[sym], ts + p["ban_h"] * 3600)

        elif st == "DROP_NO_FOLLOW":
            drops += 1
            toxic[sym] += 0.15

        else:
            nodata += 1

    return trades, drops, nodata, skip_ban, dict(toxic)


def summarize(fname, candidates, p, result):
    trades, drops, nodata, skip_ban, toxic = result

    if not trades:
        return None

    wins = [x for x in trades if x["net"] > 0]
    losses = [x for x in trades if x["net"] <= 0]

    net = sum(x["net"] for x in trades)
    gross = sum(x["gross"] for x in trades)
    costs = sum(x["costs"] for x in trades)
    avg = net / len(trades)

    win_sum = sum(x["net"] for x in wins)
    loss_abs = abs(sum(x["net"] for x in losses))
    pf = win_sum / loss_abs if loss_abs > 0 else 999.0
    wr = len(wins) / len(trades) * 100

    avg_mfe = sum(x["mfe"] for x in trades) / len(trades)
    avg_mae = sum(x["mae"] for x in trades) / len(trades)

    reasons = defaultdict(int)
    sym_pnl = defaultdict(float)

    for x in trades:
        reasons[x["reason"]] += 1
        sym_pnl[x["symbol"]] += x["net"]

    best = sorted(sym_pnl.items(), key=lambda x: x[1], reverse=True)[:8]
    worst = sorted(sym_pnl.items(), key=lambda x: x[1])[:8]
    toxic_top = sorted(toxic.items(), key=lambda x: x[1], reverse=True)[:8]

    return {
        "filter": fname,
        "candidates": len(candidates),
        "trades": len(trades),
        "drops": drops,
        "nodata": nodata,
        "skip_ban": skip_ban,
        "net": net,
        "gross": gross,
        "costs": costs,
        "avg": avg,
        "pf": pf,
        "winrate": wr,
        "avg_mfe": avg_mfe,
        "avg_mae": avg_mae,
        "wait": p["wait"],
        "rug": p["rug"],
        "entry": p["entry"],
        "sl": p["sl"],
        "tp": p["tp"],
        "time_stop": p["time_stop"],
        "tox_limit": p["tox_limit"],
        "ban_h": p["ban_h"],
        "cd_sl": p["cd_sl"],
        "static_bad": ",".join(p["static_bad"]),
        "reasons": str(dict(sorted(reasons.items()))),
        "best": str(best),
        "worst": str(worst),
        "toxic_top": str(toxic_top),
    }


async def main():
    rows = load_rows()
    print("DB rows:", len(rows))

    groups = {name: [r for r in rows if fn(r)] for name, fn in FILTERS.items()}

    for name, arr in groups.items():
        print(name, "candidates:", len(arr))

    unique = {}
    for arr in groups.values():
        for r in arr:
            unique[(r["symbol"], int(sf(r["ts"])))] = r

    print("unique klines:", len(unique))

    cache = {}
    sem = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        async def get_one(r):
            key = (r["symbol"], int(sf(r["ts"])))
            if key in cache:
                return
            async with sem:
                cache[key] = await fetch_klines(session, r["symbol"], sf(r["ts"]))
                await asyncio.sleep(0.08)

        for i, r in enumerate(unique.values(), 1):
            await get_one(r)
            if i % 25 == 0:
                print("fetched", i, "/", len(unique))

    summaries = []

    for fname, candidates in groups.items():
        for wait in WAITS:
            for rug in RUGS:
                for entry in ENTRY_MOVES:
                    for sl in SLS:
                        for tp in TPS:
                            for time_stop in TIME_STOPS:
                                for tox_limit in TOX_LIMITS:
                                    for ban_h in BAN_HOURS:
                                        for cd_sl in CD_AFTER_SL:
                                            for static_bad in STATIC_BAD_VARIANTS:
                                                p = {
                                                    "wait": wait,
                                                    "rug": rug,
                                                    "entry": entry,
                                                    "sl": sl,
                                                    "tp": tp,
                                                    "time_stop": time_stop,
                                                    "tox_limit": tox_limit,
                                                    "ban_h": ban_h,
                                                    "cd_sl": cd_sl,
                                                    "static_bad": static_bad,
                                                }
                                                res = run_dynamic(candidates, cache, p)
                                                s = summarize(fname, candidates, p, res)
                                                if s:
                                                    summaries.append(s)

    summaries.sort(key=lambda x: (x["net"], x["pf"], x["trades"]), reverse=True)

    out = OUT_DIR / "dynamic_ban_summary.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        w.writeheader()
        w.writerows(summaries)

    print()
    print("=== TOP 30 DYNAMIC BAN CONFIGS ===")
    for i, r in enumerate(summaries[:30], 1):
        print(
            f"{i:02d}. {r['filter']} wait={r['wait']} rug={r['rug']} entry={r['entry']} "
            f"SL={r['sl']} TP={r['tp']} T={r['time_stop']}m "
            f"tox={r['tox_limit']} ban={r['ban_h']}h cdSL={r['cd_sl']}h "
            f"static=[{r['static_bad']}] | "
            f"cand={r['candidates']} trades={r['trades']} skipBan={r['skip_ban']} drops={r['drops']} "
            f"net={r['net']:+.2f}$ avg={r['avg']:+.3f}$ pf={r['pf']:.2f} "
            f"wr={r['winrate']:.1f}% mfe={r['avg_mfe']:.2f}% mae={r['avg_mae']:.2f}% "
            f"reasons={r['reasons']}"
        )
        print("    best :", r["best"])
        print("    worst:", r["worst"])
        print("    toxic:", r["toxic_top"])

    print()
    print("saved:", out)

asyncio.run(main())
