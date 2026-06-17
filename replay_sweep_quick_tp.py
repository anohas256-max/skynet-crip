import asyncio
import aiohttp
import sqlite3
import csv
from pathlib import Path
from collections import defaultdict

DB = Path("/root/skynet/data/skynet_recorder.sqlite3")
OUT_DIR = Path("/root/skynet/data/replay_sweep")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://contract.mexc.com"

MARGIN = 3.0
LEVERAGE = 4

# API futures taker осторожно считаем 0.06% per side
TAKER_FEE = 0.0006

# бумажные доп. потери
SPREAD_BPS = 2.0
SLIPPAGE_BPS = 3.0

MAX_ROWS = 10000
CONCURRENCY = 4

CONFIRM_WAITS = [15, 30, 45, 60]
RUG_LIMITS = [-0.10, -0.15, -0.20]
ENTRY_MIN_MOVES = [0.00, 0.03, 0.06]
SL_LIST = [0.20, 0.25, 0.30, 0.35, 0.40]
TP_LIST = [0.20, 0.25, 0.30, 0.35, 0.45, 0.55]
TIME_STOPS = [3, 5, 8, 12, 20]


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


def base_meta_filter(c):
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
        base_meta_filter(c)
        and sf(c.get("spread_bps"), 999) <= 2.0
        and si(c.get("structure_risk"), 999) <= 1
        and sf(c.get("trend_15m")) >= 0.40
    )


def loose_liquid_filter(c):
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
    "META_PROXY": base_meta_filter,
    "STRICT": strict_filter,
    "LOOSE_LIQUID": loose_liquid_filter,
}


async def fetch_klines(session, symbol, ts):
    start = int(ts) - 120
    end = int(ts) + 60 * 90
    url = f"{BASE_URL}/api/v1/contract/kline/{symbol}"
    params = {"interval": "Min1", "start": start, "end": end}
    try:
        async with session.get(url, params=params, timeout=12) as r:
            if r.status != 200:
                return []
            payload = await r.json()
    except Exception:
        return []

    d = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(d, dict):
        return []

    times = d.get("time") or []
    opens = d.get("open") or []
    highs = d.get("high") or []
    lows = d.get("low") or []
    closes = d.get("close") or []

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


def simulate(c, klines, wait_sec, rug_limit, entry_min_move, sl, tp, time_stop):
    signal = sf(c.get("price"))
    ts = int(sf(c.get("ts")))

    if signal <= 0:
        return {"status": "BAD_SIGNAL"}

    confirm_bar = None
    for k in klines:
        if k["t"] >= ts + wait_sec:
            confirm_bar = k
            break

    if not confirm_bar:
        return {"status": "NO_CONFIRM"}

    confirm_window = [k for k in klines if ts <= k["t"] <= confirm_bar["t"]]
    if not confirm_window:
        return {"status": "NO_WINDOW"}

    low_from_signal = min(((k["low"] - signal) / signal) * 100.0 for k in confirm_window if k["low"] > 0)
    move_from_signal = ((confirm_bar["close"] - signal) / signal) * 100.0

    if low_from_signal <= rug_limit:
        return {"status": "DROP_RUG"}

    if move_from_signal < entry_min_move:
        return {"status": "DROP_NO_FOLLOW"}

    entry = confirm_bar["close"]
    entry_t = confirm_bar["t"]
    path = [k for k in klines if k["t"] >= entry_t]

    if not path:
        return {"status": "NO_PATH"}

    mfe = 0.0
    mae = 0.0
    exit_pct = 0.0
    reason = "END"
    exit_t = path[-1]["t"]

    for k in path:
        held = (k["t"] - entry_t) / 60.0
        high_pct = ((k["high"] - entry) / entry) * 100.0
        low_pct = ((k["low"] - entry) / entry) * 100.0
        close_pct = ((k["close"] - entry) / entry) * 100.0

        mfe = max(mfe, high_pct, close_pct)
        mae = min(mae, low_pct, close_pct)

        # В одной минутной свече если и SL и TP — считаем хуже для честности
        if low_pct <= -sl:
            exit_pct = -sl
            reason = "SL"
            exit_t = k["t"]
            break

        if high_pct >= tp:
            exit_pct = tp
            reason = "TP"
            exit_t = k["t"]
            break

        if held >= time_stop:
            exit_pct = close_pct
            reason = "TIME"
            exit_t = k["t"]
            break

    if reason == "END":
        last = path[-1]
        exit_pct = ((last["close"] - entry) / entry) * 100.0

    gross, net, costs = net_usd(exit_pct)

    return {
        "status": "TRADE",
        "reason": reason,
        "exit_pct": exit_pct,
        "gross": gross,
        "net": net,
        "costs": costs,
        "mfe": mfe,
        "mae": mae,
        "symbol": c.get("clean_symbol"),
        "time_iso": c.get("time_iso"),
        "score": si(c.get("score")),
        "spread": sf(c.get("spread_bps"), 999),
        "trend": sf(c.get("trend_15m")),
        "pc": sf(c.get("price_change")),
        "vol_ratio": sf(c.get("vol_ratio")),
    }


def score_summary(results):
    trades = [r for r in results if r.get("status") == "TRADE"]
    drops = [r for r in results if r.get("status", "").startswith("DROP")]
    nodata = [r for r in results if r.get("status") not in ("TRADE", "DROP_RUG", "DROP_NO_FOLLOW")]

    if not trades:
        return None

    wins = [r for r in trades if r["net"] > 0]
    losses = [r for r in trades if r["net"] <= 0]
    net = sum(r["net"] for r in trades)
    gross = sum(r["gross"] for r in trades)
    costs = sum(r["costs"] for r in trades)
    win_gross = sum(r["net"] for r in wins)
    loss_abs = abs(sum(r["net"] for r in losses))
    pf = (win_gross / loss_abs) if loss_abs > 0 else 999.0
    avg = net / len(trades)
    winrate = len(wins) / len(trades) * 100.0
    avg_mfe = sum(r["mfe"] for r in trades) / len(trades)
    avg_mae = sum(r["mae"] for r in trades) / len(trades)

    reasons = defaultdict(int)
    symbols = defaultdict(float)
    sym_count = defaultdict(int)
    for r in trades:
        reasons[r["reason"]] += 1
        symbols[r["symbol"]] += r["net"]
        sym_count[r["symbol"]] += 1

    worst_symbols = sorted(symbols.items(), key=lambda x: x[1])[:8]
    best_symbols = sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:8]

    return {
        "candidates": len(results),
        "trades": len(trades),
        "drops": len(drops),
        "nodata": len(nodata),
        "net": net,
        "gross": gross,
        "costs": costs,
        "avg": avg,
        "pf": pf,
        "winrate": winrate,
        "avg_mfe": avg_mfe,
        "avg_mae": avg_mae,
        "reasons": dict(sorted(reasons.items())),
        "worst_symbols": worst_symbols,
        "best_symbols": best_symbols,
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

    sem = asyncio.Semaphore(CONCURRENCY)
    cache = {}

    async with aiohttp.ClientSession() as session:
        async def get_kl(r):
            key = (r["symbol"], int(sf(r["ts"])))
            if key in cache:
                return cache[key]
            async with sem:
                kl = await fetch_klines(session, r["symbol"], sf(r["ts"]))
                cache[key] = kl
                await asyncio.sleep(0.08)
                return kl

        for r in unique.values():
            await get_kl(r)

    summaries = []
    best_details = []

    for fname, arr in groups.items():
        for wait in CONFIRM_WAITS:
            for rug in RUG_LIMITS:
                for entry_move in ENTRY_MIN_MOVES:
                    for sl in SL_LIST:
                        for tp in TP_LIST:
                            for tstop in TIME_STOPS:
                                results = []
                                for r in arr:
                                    kl = cache.get((r["symbol"], int(sf(r["ts"]))), [])
                                    results.append(simulate(r, kl, wait, rug, entry_move, sl, tp, tstop))

                                s = score_summary(results)
                                if not s:
                                    continue

                                row = {
                                    "filter": fname,
                                    "wait": wait,
                                    "rug": rug,
                                    "entry_move": entry_move,
                                    "sl": sl,
                                    "tp": tp,
                                    "time_stop": tstop,
                                    **{k: v for k, v in s.items() if k not in ("reasons", "worst_symbols", "best_symbols")},
                                    "reasons": str(s["reasons"]),
                                    "worst_symbols": str(s["worst_symbols"]),
                                    "best_symbols": str(s["best_symbols"]),
                                }
                                summaries.append(row)

    summaries.sort(key=lambda r: (r["net"], r["pf"], r["trades"]), reverse=True)

    out = OUT_DIR / "sweep_summary.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        w.writeheader()
        w.writerows(summaries)

    print()
    print("=== TOP 30 CONFIGS BY NET ===")
    for i, r in enumerate(summaries[:30], 1):
        print(
            f"{i:02d}. {r['filter']} wait={r['wait']} rug={r['rug']} entry={r['entry_move']} "
            f"SL={r['sl']} TP={r['tp']} T={r['time_stop']}m | "
            f"cand={r['candidates']} trades={r['trades']} drops={r['drops']} "
            f"net={r['net']:+.2f}$ avg={r['avg']:+.3f}$ pf={r['pf']:.2f} "
            f"wr={r['winrate']:.1f}% mfe={r['avg_mfe']:.2f}% mae={r['avg_mae']:.2f}% "
            f"reasons={r['reasons']}"
        )
        print("    best:", r["best_symbols"])
        print("    worst:", r["worst_symbols"])

    print()
    print("saved:", out)

asyncio.run(main())
