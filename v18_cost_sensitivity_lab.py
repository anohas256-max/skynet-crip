#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "v18_cost_sensitivity_lab_latest.txt"


def q(x, d=0.0):
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
            oi_change,
            rank,
            spread_bps,
            bid5_usd,
            ask5_usd,
            imb_5,
            imb_20,
            wall_skew,
            max_up,
            max_down,
            close_pct
        FROM signals
        WHERE closed = 1
          AND max_up IS NOT NULL
          AND max_down IS NOT NULL
          AND close_pct IS NOT NULL
        ORDER BY id
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]


def split_train_test(rows):
    cut = int(len(rows) * 0.70)
    return rows[:cut], rows[cut:]


def sim(rows, side, tp, sl, cost):
    n = len(rows)
    if n == 0:
        return None

    net_sum = 0.0
    pos = 0
    tp_count = 0
    sl_count = 0
    both_count = 0
    time_count = 0

    for r in rows:
        up = q(r["max_up"])
        down = q(r["max_down"])
        close_pct = q(r["close_pct"])

        if side == "LONG":
            hit_tp = up >= tp
            hit_sl = down <= -sl

            # conservative: if both touched, count SL
            if hit_tp and hit_sl:
                both_count += 1
                sl_count += 1
                gross = -sl
            elif hit_sl:
                sl_count += 1
                gross = -sl
            elif hit_tp:
                tp_count += 1
                gross = tp
            else:
                time_count += 1
                gross = close_pct

        else:
            hit_tp = down <= -tp
            hit_sl = up >= sl

            # conservative: if both touched, count SL
            if hit_tp and hit_sl:
                both_count += 1
                sl_count += 1
                gross = -sl
            elif hit_sl:
                sl_count += 1
                gross = -sl
            elif hit_tp:
                tp_count += 1
                gross = tp
            else:
                time_count += 1
                gross = -close_pct

        net = gross - cost
        net_sum += net
        if net > 0:
            pos += 1

    return {
        "n": n,
        "sum": net_sum,
        "avg": net_sum / n,
        "pos": pos / n,
        "tp": tp_count,
        "sl": sl_count,
        "both": both_count,
        "time": time_count,
    }


def fmt(r):
    return (
        f"n={r['n']} sum={r['sum']:+.2f}% avg={r['avg']:+.4f}% "
        f"pos={r['pos']*100:.1f}% tp={r['tp']} sl={r['sl']} "
        f"both={r['both']} time={r['time']}"
    )


def main():
    rows = load_rows()
    train, test = split_train_test(rows)

    costs = [0.29, 0.20, 0.17, 0.15, 0.10, 0.05, 0.03, 0.00]
    tps = [0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0]
    sls = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

    lines = []
    lines.append("=" * 120)
    lines.append(f"V18 COST SENSITIVITY LAB UTC={ts}")
    lines.append("=" * 120)
    lines.append("Question: does edge appear if execution cost is lower than active taker 0.29%?")
    lines.append("Uses sqlite directly. No pandas/numpy. Diagnostics only. Real trading OFF.")
    lines.append(f"db={DB}")
    lines.append(f"rows={len(rows)} train={len(train)} test={len(test)}")
    lines.append("Conservative order: if TP and SL both touched inside path, SL wins.")
    lines.append("")

    for cost in costs:
        lines.append("")
        lines.append("=" * 120)
        lines.append(f"COST={cost:.2f}%")
        lines.append("=" * 120)

        variants = []

        for side in ["LONG", "SHORT"]:
            for tp in tps:
                for sl in sls:
                    all_res = sim(rows, side, tp, sl, cost)
                    train_res = sim(train, side, tp, sl, cost)
                    test_res = sim(test, side, tp, sl, cost)

                    robust = train_res["sum"] > 0 and test_res["sum"] > 0
                    variants.append((
                        robust,
                        all_res["avg"],
                        min(train_res["sum"], test_res["sum"]),
                        side,
                        tp,
                        sl,
                        all_res,
                        train_res,
                        test_res,
                    ))

        variants.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
        robust_rows = [v for v in variants if v[0]]

        if robust_rows:
            lines.append("ROBUST TRAIN+TEST FOUND:")
            for robust, avg, min_part, side, tp, sl, all_res, train_res, test_res in robust_rows[:30]:
                lines.append(f"{side} TP={tp} SL={sl}")
                lines.append(f"  ALL   {fmt(all_res)}")
                lines.append(f"  TRAIN {fmt(train_res)}")
                lines.append(f"  TEST  {fmt(test_res)}")
        else:
            lines.append("NO ROBUST TRAIN+TEST")

        lines.append("")
        lines.append("TOP BY ALL AVG:")
        for robust, avg, min_part, side, tp, sl, all_res, train_res, test_res in variants[:20]:
            lines.append(f"{'[ROBUST]' if robust else '[weak]'} {side} TP={tp} SL={sl}")
            lines.append(f"  ALL   {fmt(all_res)}")
            lines.append(f"  TRAIN {fmt(train_res)}")
            lines.append(f"  TEST  {fmt(test_res)}")

    text = "\n".join(lines)
    OUT.write_text(text)

    print(OUT)
    print(text[:25000])


if __name__ == "__main__":
    main()
