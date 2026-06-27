#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "maker_fast_explore_sweep_latest.txt"

def f(x, d=0.0):
    try:
        if x is None:
            return d
        return float(x)
    except Exception:
        return d

def load_rows():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("""
        SELECT
            id,
            clean_symbol,
            price_change,
            vol_ratio,
            rank,
            spread_bps,
            max_up,
            max_down,
            close_pct
        FROM signals
        WHERE closed = 1
          AND price_change IS NOT NULL
          AND vol_ratio IS NOT NULL
          AND rank IS NOT NULL
          AND spread_bps IS NOT NULL
          AND max_up IS NOT NULL
          AND max_down IS NOT NULL
          AND close_pct IS NOT NULL
        ORDER BY id
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]

def sim(rows, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, cost):
    selected = []
    for r in rows:
        if f(r["price_change"]) < pc_min:
            continue
        if f(r["price_change"]) > 3.0:
            continue
        if f(r["vol_ratio"]) < vol_min:
            continue
        if f(r["spread_bps"], 999) > spread_max:
            continue
        if f(r["rank"], 999999) > rank_max:
            continue
        selected.append(r)

    filled = []
    missed = 0

    for r in selected:
        max_up = f(r["max_up"])
        max_down = f(r["max_down"])
        close_pct = f(r["close_pct"])

        # SHORT maker limit above signal by offset.
        if max_up < offset:
            missed += 1
            continue

        # Conservative after fill.
        hit_tp = max_down <= -(tp - offset)
        hit_sl = max_up >= (offset + sl)

        if hit_tp and hit_sl:
            gross = -sl
            reason = "BOTH_AS_SL"
        elif hit_sl:
            gross = -sl
            reason = "SL"
        elif hit_tp:
            gross = tp
            reason = "TP"
        else:
            gross = -close_pct + offset
            reason = "TIME"

        net = gross - cost
        filled.append((net, gross, reason, r))

    n = len(selected)
    m = len(filled)
    if m == 0:
        return {
            "signals": n, "filled": 0, "missed": missed, "fill_rate": 0.0,
            "sum": 0.0, "avg": 0.0, "pos": 0.0,
            "tp": 0, "sl": 0, "both": 0, "time": 0,
        }

    nets = [x[0] for x in filled]
    return {
        "signals": n,
        "filled": m,
        "missed": missed,
        "fill_rate": m / n if n else 0.0,
        "sum": sum(nets),
        "avg": sum(nets) / m,
        "pos": sum(1 for x in nets if x > 0) / m,
        "tp": sum(1 for x in filled if x[2] == "TP"),
        "sl": sum(1 for x in filled if x[2] == "SL"),
        "both": sum(1 for x in filled if x[2] == "BOTH_AS_SL"),
        "time": sum(1 for x in filled if x[2] == "TIME"),
    }

def fmt(r):
    return (
        f"signals={r['signals']} filled={r['filled']} miss={r['missed']} "
        f"fill%={r['fill_rate']*100:.1f} sum={r['sum']:+.2f}% "
        f"avg={r['avg']:+.4f}% pos={r['pos']*100:.1f}% "
        f"tp={r['tp']} sl={r['sl']} both={r['both']} time={r['time']}"
    )

def main():
    rows = load_rows()
    cut = int(len(rows) * 0.70)
    train = rows[:cut]
    test = rows[cut:]

    pc_mins = [0.30, 0.40, 0.50, 0.60, 0.70, 0.85, 1.00]
    vol_mins = [5.0, 6.0, 8.0, 10.0]
    spreads = [8.0, 12.0, 15.0, 20.0, 30.0]
    ranks = [30, 50, 80, 120, 200]
    offsets = [0.00, 0.03, 0.05, 0.08, 0.10, 0.15]
    tps = [0.30, 0.40, 0.50, 0.60, 0.75, 1.00]
    sls = [0.30, 0.40, 0.50, 0.60, 0.80]
    costs = [0.03, 0.05, 0.10]

    results = []

    for cost in costs:
        for pc in pc_mins:
            for vol in vol_mins:
                for sp in spreads:
                    for rk in ranks:
                        for off in offsets:
                            for tp in tps:
                                for sl in sls:
                                    a = sim(rows, pc, vol, sp, rk, off, tp, sl, cost)
                                    if a["signals"] < 100:
                                        continue
                                    if a["filled"] < 50:
                                        continue

                                    tr = sim(train, pc, vol, sp, rk, off, tp, sl, cost)
                                    te = sim(test, pc, vol, sp, rk, off, tp, sl, cost)

                                    robust = (
                                        tr["filled"] >= 30
                                        and te["filled"] >= 15
                                        and tr["sum"] > 0
                                        and te["sum"] > 0
                                        and a["avg"] > 0
                                    )

                                    # Penalize configs that are too rare or only test-lucky.
                                    score = (
                                        a["sum"]
                                        + 0.5 * te["sum"]
                                        + 0.02 * a["filled"]
                                        - 0.01 * a["missed"]
                                    )

                                    results.append((robust, score, cost, pc, vol, sp, rk, off, tp, sl, a, tr, te))

    results.sort(key=lambda x: (x[0], x[1], x[10]["filled"], x[10]["avg"]), reverse=True)

    lines = []
    lines.append("=" * 120)
    lines.append(f"MAKER FAST EXPLORE SWEEP UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 120)
    lines.append("Goal: stop waiting. Find high-frequency maker-short configs from V18 history.")
    lines.append("Diagnostics only. Real trading OFF.")
    lines.append(f"rows={len(rows)} train={len(train)} test={len(test)}")
    lines.append("")
    lines.append("Rule: SHORT fade after positive impulse. Conservative if TP and SL both hit => SL.")
    lines.append("Min kept: signals>=100 and filled>=50.")
    lines.append("")

    robust_count = sum(1 for r in results if r[0])
    lines.append(f"RESULTS={len(results)} ROBUST={robust_count}")
    lines.append("")

    lines.append("=" * 120)
    lines.append("TOP CONFIGS")
    lines.append("=" * 120)

    for robust, score, cost, pc, vol, sp, rk, off, tp, sl, a, tr, te in results[:80]:
        lines.append("")
        lines.append(
            f"{'[ROBUST]' if robust else '[weak]'} score={score:+.2f} "
            f"cost={cost:.2f}% pc>={pc:.2f} vol>={vol:.1f} spread<={sp:.0f} "
            f"rank<={rk} offset={off:.2f}% TP={tp:.2f}% SL={sl:.2f}%"
        )
        lines.append(f"  ALL   {fmt(a)}")
        lines.append(f"  TRAIN {fmt(tr)}")
        lines.append(f"  TEST  {fmt(te)}")

    lines.append("")
    lines.append("=" * 120)
    lines.append("DECISION")
    lines.append("=" * 120)

    if robust_count == 0:
        lines.append("NO ROBUST HIGH-FREQUENCY MAKER-SHORT CONFIG FOUND.")
        lines.append("Conclusion: do not keep waiting for this narrow maker-short idea.")
        lines.append("Next action: either kill maker-short or use it only as low-priority research.")
    else:
        best = next(r for r in results if r[0])
        _, score, cost, pc, vol, sp, rk, off, tp, sl, a, tr, te = best
        lines.append("BEST ROBUST CONFIG:")
        lines.append(
            f"cost={cost:.2f}% pc>={pc:.2f} vol>={vol:.1f} spread<={sp:.0f} "
            f"rank<={rk} offset={off:.2f}% TP={tp:.2f}% SL={sl:.2f}%"
        )
        lines.append(f"ALL   {fmt(a)}")
        lines.append(f"TRAIN {fmt(tr)}")
        lines.append(f"TEST  {fmt(te)}")
        lines.append("Next action: patch live shadow to this exact high-frequency profile, not wait blindly.")

    OUT.write_text("\n".join(lines))
    print(OUT)
    print("\n".join(lines[:220]))

if __name__ == "__main__":
    main()
