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

def prefilter(rows, pc_min, vol_min, spread_max, rank_max):
    return [
        r for r in rows
        if f(r["price_change"]) >= pc_min
        and f(r["price_change"]) <= 3.0
        and f(r["vol_ratio"]) >= vol_min
        and f(r["spread_bps"], 999) <= spread_max
        and f(r["rank"], 999999) <= rank_max
    ]

def sim(selected, offset, tp, sl, cost):
    filled = []
    missed = 0

    for r in selected:
        max_up = f(r["max_up"])
        max_down = f(r["max_down"])
        close_pct = f(r["close_pct"])

        if max_up < offset:
            missed += 1
            continue

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

        filled.append((gross - cost, reason))

    n = len(selected)
    m = len(filled)
    if m == 0:
        return {
            "signals": n, "filled": 0, "missed": missed, "fill_rate": 0,
            "sum": 0, "avg": 0, "pos": 0,
            "tp": 0, "sl": 0, "both": 0, "time": 0,
        }

    nets = [x[0] for x in filled]
    return {
        "signals": n,
        "filled": m,
        "missed": missed,
        "fill_rate": m / n if n else 0,
        "sum": sum(nets),
        "avg": sum(nets) / m,
        "pos": sum(1 for x in nets if x > 0) / m,
        "tp": sum(1 for _, reason in filled if reason == "TP"),
        "sl": sum(1 for _, reason in filled if reason == "SL"),
        "both": sum(1 for _, reason in filled if reason == "BOTH_AS_SL"),
        "time": sum(1 for _, reason in filled if reason == "TIME"),
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
    train_rows = rows[:cut]
    test_rows = rows[cut:]

    # Сильно меньше сетка. Только реальные варианты, не весь космос.
    filters = [
        (0.50, 6.0, 15.0, 120),
        (0.50, 8.0, 15.0, 120),
        (0.60, 6.0, 15.0, 120),
        (0.60, 8.0, 15.0, 120),
        (0.70, 6.0, 15.0, 120),
        (0.70, 8.0, 15.0, 120),
        (0.85, 8.0, 15.0, 120),
        (1.00, 8.0, 15.0, 120),
        (0.70, 8.0, 20.0, 200),
        (0.50, 8.0, 20.0, 200),
    ]

    offsets = [0.03, 0.05, 0.08, 0.10, 0.15]
    exits = [
        (0.40, 0.40),
        (0.50, 0.40),
        (0.50, 0.50),
        (0.60, 0.50),
        (0.75, 0.50),
        (0.75, 0.60),
        (1.00, 0.60),
    ]
    costs = [0.03, 0.05]

    results = []
    total = 0

    for cost in costs:
        for pc, vol, sp, rk in filters:
            selected_all = prefilter(rows, pc, vol, sp, rk)
            selected_tr = prefilter(train_rows, pc, vol, sp, rk)
            selected_te = prefilter(test_rows, pc, vol, sp, rk)

            if len(selected_all) < 50:
                continue

            for off in offsets:
                for tp, sl in exits:
                    total += 1

                    a = sim(selected_all, off, tp, sl, cost)
                    if a["filled"] < 20:
                        continue

                    tr = sim(selected_tr, off, tp, sl, cost)
                    te = sim(selected_te, off, tp, sl, cost)

                    robust = (
                        tr["filled"] >= 10
                        and te["filled"] >= 5
                        and tr["sum"] > 0
                        and te["sum"] > 0
                        and a["avg"] > 0
                    )

                    score = a["sum"] + 0.5 * te["sum"] + 0.01 * a["filled"] - 0.005 * a["missed"]
                    results.append((robust, score, cost, pc, vol, sp, rk, off, tp, sl, a, tr, te))

    results.sort(key=lambda x: (x[0], x[1], x[10]["avg"]), reverse=True)
    robust_count = sum(1 for r in results if r[0])

    lines = []
    lines.append("=" * 120)
    lines.append(f"MAKER FAST LIMITED SWEEP UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 120)
    lines.append("Fast limited sweep, not huge brute force. Diagnostics only. Real trading OFF.")
    lines.append(f"rows={len(rows)} train={len(train_rows)} test={len(test_rows)} tried={total} kept={len(results)} robust={robust_count}")
    lines.append("")

    lines.append("=" * 120)
    lines.append("TOP CONFIGS")
    lines.append("=" * 120)

    for robust, score, cost, pc, vol, sp, rk, off, tp, sl, a, tr, te in results[:60]:
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
        lines.append("NO ROBUST CONFIG FOUND IN FAST LIMITED SWEEP.")
        lines.append("Conclusion: maker-short is weak/rare. Do not keep waiting as main path.")
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

    OUT.write_text("\n".join(lines))
    print(OUT)
    print("\n".join(lines[:260]))

if __name__ == "__main__":
    main()
