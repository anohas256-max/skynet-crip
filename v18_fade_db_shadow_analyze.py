#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
LOG = ROOT / "v18_fade_db_shadow.log"
OUT = ROOT / "v18_fade_db_shadow_analysis_latest.txt"

open_re = re.compile(
    r"V18_FADE_DB_OPEN \| .*? \| SHORT \| (?P<sym>[^|]+) \| "
    r"entry=(?P<entry>[0-9.]+) signal_id=(?P<sid>\d+) "
    r"pc=(?P<pc>[+-]?[0-9.]+)% vol=x(?P<vol>[0-9.]+) "
    r"spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>\d+)"
)

close_re = re.compile(
    r"V18_FADE_DB_CLOSE \| .*? \| SHORT \| (?P<sym>[^|]+) \| (?P<reason>TP|SL|TIME) \| "
    r"entry=(?P<entry>[0-9.]+) exit=(?P<exit>[0-9.]+) "
    r"move=(?P<move>[+-]?[0-9.]+)% gross=\$(?P<gross>[+-]?[0-9.\-]+) "
    r"net=\$(?P<net>[+-]?[0-9.\-]+) cost=\$(?P<cost>[0-9.]+) "
    r"age=(?P<age>\d+)s signal_id=(?P<sid>\d+)"
)

def stat(rows):
    n = len(rows)
    if not n:
        return None
    net = sum(r["net"] for r in rows)
    pos = sum(r["net"] for r in rows if r["net"] > 0)
    neg = -sum(r["net"] for r in rows if r["net"] < 0)
    pf = pos / neg if neg > 0 else 999 if pos > 0 else 0
    wr = sum(r["net"] > 0 for r in rows) / n * 100
    tp = sum(r["reason"] == "TP" for r in rows)
    sl = sum(r["reason"] == "SL" for r in rows)
    tm = sum(r["reason"] == "TIME" for r in rows)
    avg = net / n
    return {
        "n": n,
        "net": net,
        "avg": avg,
        "pf": pf,
        "wr": wr,
        "tp": tp,
        "sl": sl,
        "time": tm,
    }

def fmt(s):
    if not s:
        return "n=0"
    return (
        f"n={s['n']:4d} net=${s['net']:+8.4f} avg=${s['avg']:+8.5f} "
        f"WR={s['wr']:5.1f}% PF={s['pf']:5.2f} "
        f"TP={s['tp']:3d} SL={s['sl']:3d} TIME={s['time']:3d}"
    )

def main():
    text = LOG.read_text(errors="ignore") if LOG.exists() else ""

    opens = {}
    for m in open_re.finditer(text):
        d = m.groupdict()
        opens[d["sid"]] = {
            "sym": d["sym"].strip(),
            "entry": float(d["entry"]),
            "sid": d["sid"],
            "pc": float(d["pc"]),
            "vol": float(d["vol"]),
            "spread": float(d["spread"]),
            "rank": int(d["rank"]),
        }

    rows = []
    missing_open = 0
    for m in close_re.finditer(text):
        d = m.groupdict()
        o = opens.get(d["sid"])
        if not o:
            missing_open += 1
            o = {
                "sym": d["sym"].strip(),
                "sid": d["sid"],
                "pc": -1.0,
                "vol": -1.0,
                "spread": 999.0,
                "rank": 999999,
            }

        rows.append({
            **o,
            "reason": d["reason"],
            "move": float(d["move"]),
            "gross": float(d["gross"]),
            "net": float(d["net"]),
            "cost": float(d["cost"]),
            "age": int(d["age"]),
        })

    lines = []
    lines.append("=" * 110)
    lines.append(f"V18 FADE DB SHADOW ANALYSIS UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 110)
    lines.append(f"log={LOG}")
    lines.append(f"opens_parsed={len(opens)} closes_parsed={len(rows)} missing_open_for_close={missing_open}")
    lines.append("real_trading=OFF")
    lines.append("")

    lines.append("=== TOTAL ===")
    lines.append(fmt(stat(rows)))
    lines.append("")

    lines.append("=== BY REASON ===")
    for reason in ["TP", "SL", "TIME"]:
        lines.append(f"{reason:<5} " + fmt(stat([r for r in rows if r["reason"] == reason])))
    lines.append("")

    buckets = [
        ("pc_030_050", lambda r: 0.30 <= r["pc"] < 0.50),
        ("pc_050_080", lambda r: 0.50 <= r["pc"] < 0.80),
        ("pc_080_120", lambda r: 0.80 <= r["pc"] < 1.20),
        ("pc_120_plus", lambda r: r["pc"] >= 1.20),
        ("spread_0_1", lambda r: r["spread"] <= 1.0),
        ("spread_1_2", lambda r: 1.0 < r["spread"] <= 2.0),
        ("spread_2_3", lambda r: 2.0 < r["spread"] <= 3.0),
        ("rank_1_30", lambda r: r["rank"] <= 30),
        ("rank_31_80", lambda r: 30 < r["rank"] <= 80),
        ("rank_81_150", lambda r: 80 < r["rank"] <= 150),
        ("vol_5_8", lambda r: 5 <= r["vol"] < 8),
        ("vol_8_15", lambda r: 8 <= r["vol"] < 15),
        ("vol_15_plus", lambda r: r["vol"] >= 15),
        ("fast_sl_age20", lambda r: r["age"] <= 20),
    ]

    lines.append("=== BUCKETS ===")
    for name, fn in buckets:
        lines.append(f"{name:<16} " + fmt(stat([r for r in rows if fn(r)])))
    lines.append("")

    by_sym = defaultdict(list)
    for r in rows:
        by_sym[r["sym"]].append(r)

    sym_stats = []
    for sym, rr in by_sym.items():
        s = stat(rr)
        sym_stats.append((sym, s))

    lines.append("=== WORST SYMBOLS n>=2 ===")
    for sym, s in sorted([x for x in sym_stats if x[1]["n"] >= 2], key=lambda x: x[1]["net"])[:25]:
        lines.append(f"{sym:<14} " + fmt(s))
    lines.append("")

    lines.append("=== BEST SYMBOLS n>=2 ===")
    for sym, s in sorted([x for x in sym_stats if x[1]["n"] >= 2], key=lambda x: -x[1]["net"])[:25]:
        lines.append(f"{sym:<14} " + fmt(s))
    lines.append("")

    pc_mins = [0.30, 0.50, 0.70, 1.00, 1.20]
    vol_mins = [5, 8, 10, 15, 20]
    spread_maxs = [1.0, 1.5, 2.0, 2.5, 3.0]
    rank_maxs = [30, 50, 80, 120, 150]

    sweeps = []
    for pc in pc_mins:
        for vol in vol_mins:
            for sp in spread_maxs:
                for rk in rank_maxs:
                    rr = [
                        r for r in rows
                        if r["pc"] >= pc
                        and r["vol"] >= vol
                        and r["spread"] <= sp
                        and r["rank"] <= rk
                    ]
                    s = stat(rr)
                    if not s or s["n"] < 10:
                        continue
                    score = s["net"] + s["avg"] * 50 + max(0, s["pf"] - 1) * 0.25
                    sweeps.append((score, pc, vol, sp, rk, s))

    lines.append("=== TOP FILTER SWEEP n>=10 ===")
    for score, pc, vol, sp, rk, s in sorted(sweeps, key=lambda x: x[0], reverse=True)[:40]:
        lines.append(
            f"pc>={pc:<4} vol>={vol:<4} spread<={sp:<4} rank<={rk:<4} "
            + fmt(s)
        )
    lines.append("")

    lines.append("=== DECISION ===")
    total = stat(rows)
    if total and total["n"] >= 50 and total["net"] > 0 and total["avg"] < 0.003:
        lines.append("Exact profile is only barely positive. Too thin for real. Tighten filter and continue shadow.")
    elif total and total["net"] <= 0:
        lines.append("Exact profile is negative. Stop real discussion; only stricter research.")
    else:
        lines.append("Need more closes or stricter filter validation before any real discussion.")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
