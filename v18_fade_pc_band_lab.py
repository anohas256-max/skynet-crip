#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

DB = Path("/root/skynet/data/v18_micro_paths.sqlite3")
START = "2026-07-04 20:08:54"
BLACKLIST = {"ALLO", "XPL"}
COST_PCT = 0.03

BANDS = [
    ("pc_030_050", 0.30, 0.50),
    ("pc_050_080", 0.50, 0.80),
    ("pc_080_120", 0.80, 1.20),
    ("pc_120_plus", 1.20, 999.0),
    ("pc_030_050_or_120_plus", None, None),
]

def pf(vals):
    pos = sum(x for x in vals if x > 0)
    neg = -sum(x for x in vals if x < 0)
    if neg == 0:
        return 999.0 if pos > 0 else 0.0
    return pos / neg

def sim_short(r):
    max_up = float(r["max_up"])
    max_down = float(r["max_down"])
    close_pct = float(r["close_pct"])

    if max_up >= 0.3:
        return -0.3 - COST_PCT, "SL"
    if abs(max_down) >= 3.0:
        return 3.0 - COST_PCT, "TP"
    return -close_pct - COST_PCT, "TIME"

def run_window(name, where_extra, params):
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row

    rows = con.execute(f"""
        SELECT *
        FROM signals
        WHERE clean_symbol NOT IN ('ALLO','XPL')
          AND max_up IS NOT NULL
          AND max_down IS NOT NULL
          AND close_pct IS NOT NULL
          AND price_change >= 0.30
          AND vol_ratio >= 12
          AND spread_bps <= 2
          AND rank <= 50
          {where_extra}
        ORDER BY id ASC
    """, params).fetchall()

    print()
    print("=" * 110)
    print(f"WINDOW={name} rows={len(rows)}")
    print("=" * 110)

    for band_name, lo, hi in BANDS:
        vals = []
        reasons = defaultdict(int)
        syms = defaultdict(float)

        for r in rows:
            pc = float(r["price_change"])
            sym = r["clean_symbol"]

            if band_name == "pc_030_050_or_120_plus":
                ok = (0.30 <= pc < 0.50) or (pc >= 1.20)
            else:
                ok = lo <= pc < hi

            if not ok:
                continue

            net, reason = sim_short(r)
            vals.append(net)
            reasons[reason] += 1
            syms[sym] += net

        n = len(vals)
        if not n:
            print(f"{band_name:<24} n=0")
            continue

        net = sum(vals)
        avg = net / n
        wr = 100.0 * sum(1 for x in vals if x > 0) / n
        p = pf(vals)
        best = sorted(syms.items(), key=lambda x: x[1], reverse=True)[:4]
        worst = sorted(syms.items(), key=lambda x: x[1])[:4]
        conc = max(syms.values()) / net if net > 0 and syms else 0

        print(
            f"{band_name:<24} n={n:4d} net_pct={net:+8.3f} avg={avg:+7.4f} "
            f"WR={wr:5.1f}% PF={p:6.2f} SL={reasons['SL']:3d} TIME={reasons['TIME']:3d} "
            f"best_conc={conc:5.1%}"
        )
        print("  best:", ", ".join(f"{s}:{v:+.3f}" for s, v in best))
        print("  worst:", ", ".join(f"{s}:{v:+.3f}" for s, v in worst))

def main():
    print("=" * 110)
    print(f"V18 FADE PC BAND LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    print("=" * 110)
    print("MODEL: current phase2D base filter pc>=0.30 vol>=12 spread<=2 rank<=50; SHORT SL=0.3 TTL close cost=0.03pct")
    print("DB:", DB)

    run_window("phase2D_since", "AND time_iso >= ?", (START,))
    run_window("recent_tail_20000", "AND id >= (SELECT MAX(id)-20000 FROM signals)", ())
    run_window("all_db", "", ())

if __name__ == "__main__":
    main()
