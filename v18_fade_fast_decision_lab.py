#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

DB = Path("/root/skynet/data/v18_micro_paths.sqlite3")

BLACKLIST = {"ALLO", "XPL"}
COST_PCT = 0.03

# Проверяем не только с момента phase2D, а несколько окон.
WINDOWS = {
    "phase2D_since": "2026-07-04T20:08:54",
    "last_24h": None,
    "all_db": "1970-01-01T00:00:00",
}

FILTERS = [
    ("P2D_CURRENT", 0.30, 12, 2.0, 50),
    ("P2D_TIGHT_R30", 0.30, 12, 2.0, 30),
    ("P2D_VOL10", 0.30, 10, 2.0, 50),
    ("P2D_VOL12_SP3", 0.30, 12, 3.0, 50),
    ("P2D_PC05_VOL12", 0.50, 12, 2.0, 50),
    ("P2D_PC03_VOL15", 0.30, 15, 2.0, 50),
    ("P2D_PC05_VOL10", 0.50, 10, 2.0, 50),
]

def pf(vals):
    pos = sum(x for x in vals if x > 0)
    neg = -sum(x for x in vals if x < 0)
    if neg == 0:
        return 999.0 if pos > 0 else 0.0
    return pos / neg

def sim_short(row):
    max_up = float(row["max_up"])
    max_down = float(row["max_down"])
    close_pct = float(row["close_pct"])

    # SHORT:
    # max_up > 0 = плохо, цена пошла вверх
    # max_down < 0 = хорошо, цена пошла вниз
    if max_up >= 0.3:
        gross = -0.3
        reason = "SL"
    elif abs(max_down) >= 3.0:
        gross = 3.0
        reason = "TP"
    else:
        gross = -close_pct
        reason = "TIME"

    net = gross - COST_PCT
    return net, reason

def summarize(name, rows):
    print()
    print("=" * 120)
    print(f"WINDOW: {name} rows={len(rows)}")
    print("=" * 120)

    scored = []

    for fname, pc_min, vol_min, spread_max, rank_max in FILTERS:
        vals = []
        reasons = defaultdict(int)
        syms = defaultdict(lambda: {"n": 0, "net": 0.0, "sl": 0, "time": 0, "tp": 0})

        for r in rows:
            sym = r["clean_symbol"]
            if sym in BLACKLIST:
                continue
            if float(r["price_change"]) < pc_min:
                continue
            if float(r["vol_ratio"]) < vol_min:
                continue
            if float(r["spread_bps"]) > spread_max:
                continue
            if int(r["rank"]) > rank_max:
                continue

            net, reason = sim_short(r)
            vals.append(net)
            reasons[reason] += 1

            syms[sym]["n"] += 1
            syms[sym]["net"] += net
            syms[sym][reason.lower()] += 1

        n = len(vals)
        if n == 0:
            print(f"{fname:<18} n=0")
            continue

        net_sum = sum(vals)
        avg = net_sum / n
        wr = 100.0 * sum(1 for x in vals if x > 0) / n
        p = pf(vals)
        sl_n = reasons["SL"]
        time_n = reasons["TIME"]
        tp_n = reasons["TP"]

        top_sym = sorted(syms.items(), key=lambda kv: kv[1]["net"], reverse=True)[:3]
        worst_sym = sorted(syms.items(), key=lambda kv: kv[1]["net"])[:3]

        concentration = 0.0
        if net_sum > 0:
            best_net = max(v["net"] for v in syms.values())
            concentration = best_net / net_sum

        scored.append((fname, n, net_sum, avg, wr, p, sl_n, time_n, tp_n, concentration))

        print(
            f"{fname:<18} "
            f"n={n:4d} net_pct={net_sum:+8.3f} avg={avg:+7.4f} "
            f"WR={wr:5.1f}% PF={p:6.2f} "
            f"SL={sl_n:3d} TIME={time_n:3d} TP={tp_n:3d} "
            f"best_conc={concentration:5.1%}"
        )
        print("  best:", ", ".join(f"{s}:n={v['n']} net={v['net']:+.3f}" for s, v in top_sym))
        print("  worst:", ", ".join(f"{s}:n={v['n']} net={v['net']:+.3f}" for s, v in worst_sym))

    print()
    print("--- DECISION CANDIDATES ---")
    good = [
        x for x in scored
        if x[1] >= 20 and x[2] > 0 and x[3] > 0.03 and x[5] > 1.25 and x[9] < 0.45
    ]
    if not good:
        print("NO_STRONG_FILTER: нет фильтра n>=20 avg>0.03 PF>1.25 без сильной концентрации.")
    else:
        for x in sorted(good, key=lambda z: (z[5], z[3], z[2]), reverse=True):
            fname, n, net_sum, avg, wr, p, sl_n, time_n, tp_n, concentration = x
            print(
                f"KEEP/TEST {fname}: n={n} net_pct={net_sum:+.3f} "
                f"avg={avg:+.4f} WR={wr:.1f}% PF={p:.2f} conc={concentration:.1%}"
            )

def main():
    if not DB.exists():
        raise SystemExit(f"missing DB: {DB}")

    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row

    print("=" * 120)
    print(f"V18 FADE FAST DECISION LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    print("=" * 120)
    print("DB:", DB)
    print("BLACKLIST:", ",".join(sorted(BLACKLIST)))
    print("MODEL: SHORT TP=3.0 SL=0.3 TTL/path close_pct cost=0.03pct")
    print()

    max_time = con.execute("SELECT MAX(time_iso) AS t FROM signals").fetchone()["t"]
    print("db_max_time_iso:", max_time)

    # last_24h через sqlite datetime не трогаем, просто последние сутки относительно max ts грубо через unix ts
    rows_all = con.execute("""
        SELECT *
        FROM signals
        WHERE clean_symbol NOT IN ('ALLO','XPL')
          AND max_up IS NOT NULL
          AND max_down IS NOT NULL
          AND close_pct IS NOT NULL
        ORDER BY id ASC
    """).fetchall()

    rows_phase2d = [r for r in rows_all if str(r["time_iso"]) >= "2026-07-04 20:08:54" or str(r["time_iso"]) >= "2026-07-04T20:08:54"]

    # Берём хвост по id примерно как last window, чтобы быстро не мучиться с форматами дат.
    last_ids = rows_all[-12000:] if len(rows_all) > 12000 else rows_all

    summarize("phase2D_since_2026-07-04_20:08", rows_phase2d)
    summarize("recent_tail_rows", last_ids)
    summarize("all_available_db", rows_all)

    print()
    print("=" * 120)
    print("FINAL RULE:")
    print("1) Если P2D_CURRENT на phase2D_since имеет n<10: live-shadow ждём до 10 closes.")
    print("2) Если recent/all показывают P2D_CURRENT или близкий фильтр n>=20 PF>1.25 avg>0.03 и conc<45%, fade живой.")
    print("3) Если только all_db хороший, а recent плохой — edge нестабилен, real нельзя.")
    print("4) Если phase2D live на 10 closes уйдет net<=0/PF<1.15 — стоп.")
    print("=" * 120)

if __name__ == "__main__":
    main()
