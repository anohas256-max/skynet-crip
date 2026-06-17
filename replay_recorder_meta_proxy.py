import asyncio
import aiohttp
import sqlite3
import csv
import math
from pathlib import Path
from collections import defaultdict

DB = Path("/root/skynet/data/skynet_recorder.sqlite3")
OUT_DIR = Path("/root/skynet/data/replay_meta_proxy")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://contract.mexc.com"

MARGIN = 3.0
LEVERAGE = 4
COMMISSION_RATE = 0.0005
PAPER_SPREAD_BPS = 2.0
PAPER_SLIPPAGE_BPS = 3.0

CONFIRM_WAIT_SEC = 60
CONFIRM_NO_RUG_PCT = -0.15
CONFIRM_MAX_AGE_SEC = 95

SL_PCT = -0.40
PARTIAL_PCT = 0.55
RUNNER_TP_PCT = 2.00
RUNNER_STOP_PCT = 0.10
TIME_STOP_MIN = 45

NOFOLLOW_AFTER_MIN = 2.0
NOFOLLOW_MFE_MAX = 0.15

MAX_ROWS = 5000
CONCURRENCY = 4


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


def calc_net(price_diff_pct, margin=MARGIN, lev=LEVERAGE):
    notional = margin * lev
    gross = notional * (price_diff_pct / 100.0)
    commission = notional * COMMISSION_RATE * 2
    spread = notional * (PAPER_SPREAD_BPS / 10000.0)
    slip = notional * (PAPER_SLIPPAGE_BPS / 10000.0) * 2
    costs = commission + spread + slip
    return gross, gross - costs, costs


def load_candidates():
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


def meta_proxy(c):
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


def meta_proxy_tight(c):
    return (
        meta_proxy(c)
        and sf(c.get("spread_bps"), 999) <= 2.0
        and si(c.get("structure_risk"), 999) <= 1
        and sf(c.get("trend_15m")) >= 0.40
    )


def micro_lite(c):
    return (
        si(c.get("score")) >= 3
        and 0.20 <= sf(c.get("price_change")) <= 0.55
        and sf(c.get("vol_ratio")) <= 30
        and sf(c.get("trend_15m")) >= 0.20
        and sf(c.get("btc_5m_change")) >= -0.08
        and sf(c.get("oi_change")) >= -0.50
        and si(c.get("depth_ok")) == 1
        and sf(c.get("spread_bps"), 999) <= 2.0
        and sf(c.get("top5_bid_usdt")) >= 3000
        and sf(c.get("top5_ask_usdt")) >= 3000
        and si(c.get("structure_risk"), 999) <= 1
        and si(c.get("initiative_proxy")) == 1
        and si(c.get("absorption_proxy")) == 0
        and si(c.get("weak_long_result")) == 0
        and si(c.get("high_effort_low_result")) == 0
    )


async def fetch_klines(session, symbol, ts):
    # MEXC futures kline usually accepts unix seconds start/end.
    start = int(ts) - 60
    end = int(ts) + 60 * 60
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

    times = d.get("time") or d.get("timestamp") or []
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


def simulate_one(c, klines, use_nofollow=False):
    signal = sf(c.get("price"))
    ts = int(sf(c.get("ts")))
    if signal <= 0:
        return {"status": "BAD_SIGNAL"}

    after_signal = [k for k in klines if k["t"] >= ts]
    if not after_signal:
        return {"status": "NO_KLINES"}

    confirm_window = [k for k in klines if ts <= k["t"] <= ts + CONFIRM_WAIT_SEC + 10]
    if not confirm_window:
        return {"status": "NO_CONFIRM_WINDOW"}

    low_pct = min(((k["low"] - signal) / signal) * 100.0 for k in confirm_window if k["low"] > 0)
    confirm_bar = None
    for k in klines:
        if k["t"] >= ts + CONFIRM_WAIT_SEC:
            confirm_bar = k
            break

    if not confirm_bar:
        return {"status": "NO_CONFIRM_BAR"}

    move_pct = ((confirm_bar["close"] - signal) / signal) * 100.0

    if low_pct <= CONFIRM_NO_RUG_PCT:
        return {"status": "CONFIRM_DROP_RUG", "confirm_move": move_pct, "confirm_low": low_pct}

    if confirm_bar["close"] <= signal:
        return {"status": "CONFIRM_DROP_NO_FOLLOW", "confirm_move": move_pct, "confirm_low": low_pct}

    entry = confirm_bar["close"]
    entry_t = confirm_bar["t"]

    path = [k for k in klines if k["t"] >= entry_t]
    if not path:
        return {"status": "NO_PATH"}

    mfe = 0.0
    mae = 0.0
    partial_taken = False
    realized_pct = 0.0
    reason = None
    exit_pct = 0.0
    exit_t = entry_t

    for k in path:
        high_pct = ((k["high"] - entry) / entry) * 100.0
        low_pct2 = ((k["low"] - entry) / entry) * 100.0
        close_pct = ((k["close"] - entry) / entry) * 100.0
        held_min = (k["t"] - entry_t) / 60.0

        mfe = max(mfe, high_pct, close_pct)
        mae = min(mae, low_pct2, close_pct)

        if use_nofollow and held_min >= NOFOLLOW_AFTER_MIN and mfe < NOFOLLOW_MFE_MAX:
            reason = "NOFOLLOW_EXIT"
            exit_pct = close_pct
            exit_t = k["t"]
            break

        if not partial_taken:
            if low_pct2 <= SL_PCT:
                reason = "SL"
                exit_pct = SL_PCT
                exit_t = k["t"]
                break
            if high_pct >= PARTIAL_PCT:
                partial_taken = True
                realized_pct += 0.5 * PARTIAL_PCT
        else:
            if high_pct >= RUNNER_TP_PCT:
                reason = "RUNNER_TP"
                exit_pct = realized_pct + 0.5 * RUNNER_TP_PCT
                exit_t = k["t"]
                break
            if low_pct2 <= RUNNER_STOP_PCT:
                reason = "RUNNER_STOP"
                exit_pct = realized_pct + 0.5 * RUNNER_STOP_PCT
                exit_t = k["t"]
                break

        if held_min >= TIME_STOP_MIN:
            reason = "TIME_PARTIAL" if partial_taken else "TIME"
            exit_pct = realized_pct + (0.5 * close_pct if partial_taken else close_pct)
            exit_t = k["t"]
            break

    if reason is None:
        last = path[-1]
        close_pct = ((last["close"] - entry) / entry) * 100.0
        reason = "END"
        exit_pct = realized_pct + (0.5 * close_pct if partial_taken else close_pct)
        exit_t = last["t"]

    gross, net, costs = calc_net(exit_pct)
    return {
        "status": "TRADE",
        "reason": reason,
        "entry": entry,
        "entry_t": entry_t,
        "exit_t": exit_t,
        "exit_pct": exit_pct,
        "gross": gross,
        "net": net,
        "costs": costs,
        "mfe": mfe,
        "mae": mae,
        "partial": int(partial_taken),
    }


def summarize(name, results):
    trades = [r for r in results if r.get("status") == "TRADE"]
    drops = [r for r in results if str(r.get("status", "")).startswith("CONFIRM_DROP")]
    no_data = [r for r in results if r.get("status") not in ("TRADE", "CONFIRM_DROP_RUG", "CONFIRM_DROP_NO_FOLLOW")]

    net = sum(r["net"] for r in trades)
    gross = sum(r["gross"] for r in trades)
    costs = sum(r["costs"] for r in trades)
    avg = net / len(trades) if trades else 0.0
    mfe = sum(r["mfe"] for r in trades) / len(trades) if trades else 0.0
    mae = sum(r["mae"] for r in trades) / len(trades) if trades else 0.0
    reasons = defaultdict(int)
    for r in trades:
        reasons[r["reason"]] += 1

    print()
    print("===", name, "===")
    print("candidates:", len(results), "trades:", len(trades), "drops:", len(drops), "no_data:", len(no_data))
    print(f"net={net:+.2f}$ gross={gross:+.2f}$ costs={costs:.2f}$ avg={avg:+.3f}$ avgMFE={mfe:.2f}% avgMAE={mae:.2f}%")
    print("reasons:", dict(sorted(reasons.items())))


async def main():
    rows = load_candidates()
    groups = {
        "META_PROXY": [r for r in rows if meta_proxy(r)],
        "META_PROXY_TIGHT": [r for r in rows if meta_proxy_tight(r)],
        "MICRO_LITE": [r for r in rows if micro_lite(r)],
    }

    print("DB rows:", len(rows))
    for k, v in groups.items():
        print(k, "candidates:", len(v))

    needed = {}
    for arr in groups.values():
        for r in arr:
            needed[(r["symbol"], int(sf(r["ts"])))] = r

    sem = asyncio.Semaphore(CONCURRENCY)
    cache = {}

    async with aiohttp.ClientSession() as session:
        async def get_for(r):
            key = (r["symbol"], int(sf(r["ts"])))
            if key in cache:
                return cache[key]
            async with sem:
                kl = await fetch_klines(session, r["symbol"], sf(r["ts"]))
                cache[key] = kl
                await asyncio.sleep(0.12)
                return kl

        all_outputs = {}
        for gname, arr in groups.items():
            base = []
            nf = []
            detail_rows = []
            for i, r in enumerate(arr, 1):
                kl = await get_for(r)
                rb = simulate_one(r, kl, use_nofollow=False)
                rn = simulate_one(r, kl, use_nofollow=True)
                base.append(rb)
                nf.append(rn)

                detail_rows.append({
                    "group": gname,
                    "time_iso": r.get("time_iso"),
                    "symbol": r.get("clean_symbol"),
                    "score": r.get("score"),
                    "pc": r.get("price_change"),
                    "vol_ratio": r.get("vol_ratio"),
                    "trend": r.get("trend_15m"),
                    "btc": r.get("btc_5m_change"),
                    "oi": r.get("oi_change"),
                    "spread": r.get("spread_bps"),
                    "bid5": r.get("top5_bid_usdt"),
                    "ask5": r.get("top5_ask_usdt"),
                    "base_status": rb.get("status"),
                    "base_reason": rb.get("reason", ""),
                    "base_net": rb.get("net", ""),
                    "base_mfe": rb.get("mfe", ""),
                    "base_mae": rb.get("mae", ""),
                    "nf_status": rn.get("status"),
                    "nf_reason": rn.get("reason", ""),
                    "nf_net": rn.get("net", ""),
                    "nf_mfe": rn.get("mfe", ""),
                    "nf_mae": rn.get("mae", ""),
                })

            summarize(gname + " BASE", base)
            summarize(gname + " NOFOLLOW", nf)

            out = OUT_DIR / f"{gname.lower()}_details.csv"
            with out.open("w", encoding="utf-8", newline="") as f:
                if detail_rows:
                    w = csv.DictWriter(f, fieldnames=list(detail_rows[0].keys()))
                    w.writeheader()
                    w.writerows(detail_rows)
            print("details:", out)

asyncio.run(main())
