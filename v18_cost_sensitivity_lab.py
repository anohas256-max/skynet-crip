#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("/root/skynet")
CSV = ROOT / "safe_exports/v18_ml_dataset.csv"
OUT = ROOT / "v18_cost_sensitivity_lab_latest.txt"

df = pd.read_csv(CSV).sort_values("id").reset_index(drop=True)

split = int(len(df) * 0.7)
train = df.iloc[:split].copy()
test = df.iloc[split:].copy()

def sim(rows, side, tp, sl, cost):
    up = rows["max_up"].to_numpy()
    down = rows["max_down"].to_numpy()
    close = rows["close_pct"].to_numpy()

    if side == "LONG":
        hit_tp = up >= tp
        hit_sl = down <= -sl
        gross = np.where(hit_sl, -sl, np.where(hit_tp, tp, close))
    else:
        hit_tp = down <= -tp
        hit_sl = up >= sl
        gross = np.where(hit_sl, -sl, np.where(hit_tp, tp, -close))

    net = gross - cost
    return {
        "n": len(rows),
        "sum": float(net.sum()),
        "avg": float(net.mean()),
        "pos": float((net > 0).mean()),
        "tp": int(hit_tp.sum()),
        "sl": int(hit_sl.sum()),
        "both": int((hit_tp & hit_sl).sum()),
    }

def fmt(r):
    return f"n={r['n']} sum={r['sum']:+.2f}% avg={r['avg']:+.4f}% pos={r['pos']*100:.1f}% tp={r['tp']} sl={r['sl']} both={r['both']}"

lines = []
lines.append("=" * 120)
lines.append("V18 COST SENSITIVITY LAB")
lines.append("=" * 120)
lines.append("Question: does edge appear if execution cost is lower than taker 0.29%?")
lines.append(f"rows={len(df)} train={len(train)} test={len(test)}")
lines.append("Conservative order: if TP and SL both touched, SL wins.")
lines.append("")

costs = [0.29, 0.20, 0.15, 0.10, 0.05, 0.00]
tps = [0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0]
sls = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

for cost in costs:
    lines.append("")
    lines.append("=" * 120)
    lines.append(f"COST={cost:.2f}%")
    lines.append("=" * 120)

    rows = []
    for side in ["LONG", "SHORT"]:
        for tp in tps:
            for sl in sls:
                a = sim(df, side, tp, sl, cost)
                tr = sim(train, side, tp, sl, cost)
                te = sim(test, side, tp, sl, cost)

                robust = tr["sum"] > 0 and te["sum"] > 0
                rows.append((robust, a["avg"], side, tp, sl, a, tr, te))

    rows.sort(key=lambda x: (x[0], x[1]), reverse=True)

    robust_rows = [r for r in rows if r[0]]
    if robust_rows:
        lines.append("ROBUST TRAIN+TEST FOUND:")
        for robust, avg, side, tp, sl, a, tr, te in robust_rows[:20]:
            lines.append(f"{side} TP={tp} SL={sl}")
            lines.append(f"  ALL   {fmt(a)}")
            lines.append(f"  TRAIN {fmt(tr)}")
            lines.append(f"  TEST  {fmt(te)}")
    else:
        lines.append("NO ROBUST TRAIN+TEST")

    lines.append("")
    lines.append("TOP BY ALL AVG:")
    for robust, avg, side, tp, sl, a, tr, te in rows[:15]:
        lines.append(f"{'[ROBUST]' if robust else '[weak]'} {side} TP={tp} SL={sl}")
        lines.append(f"  ALL   {fmt(a)}")
        lines.append(f"  TRAIN {fmt(tr)}")
        lines.append(f"  TEST  {fmt(te)}")

OUT.write_text("\n".join(lines))
print(OUT)
print("\n".join(lines[:260]))
