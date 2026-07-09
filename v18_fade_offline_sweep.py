#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict

LOG = Path("v18_fade_journal_all.log")
OUT = Path("v18_fade_offline_sweep_latest.txt")

BASE_BLACKLIST = {"ALLO", "XPL"}
KNOWN_BAD = {"ALLO", "XPL", "TAC", "SOXL"}

open_re = re.compile(
    r"\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC\].*?"
    r"V18_FADE_DB_OPEN .*? SHORT \| (?P<sym>[A-Z0-9]+) \| "
    r"entry=(?P<entry>[0-9.]+) signal_id=(?P<sid>[0-9]+) "
    r"pc=\+(?P<pc>[0-9.]+)% vol=x(?P<vol>[0-9.]+) spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>[0-9]+)"
)

close_re = re.compile(
    r"\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC\].*?"
    r"V18_FADE_DB_CLOSE .*? SHORT \| (?P<sym>[A-Z0-9]+) \| (?P<reason>TP|SL|TIME) \| "
    r"entry=(?P<entry>[0-9.]+) exit=(?P<exit>[0-9.]+) move=(?P<move>[+-]?[0-9.]+)% "
    r"gross=\$(?P<gross>[+-]?[0-9.]+) net=\$(?P<net>[+-]?[0-9.]+) cost=\$(?P<cost>[0-9.]+) "
    r"age=(?P<age>[0-9.]+)s signal_id=(?P<sid>[0-9]+)"
)

def dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

def pf(vals):
    gp = sum(x for x in vals if x > 0)
    gl = -sum(x for x in vals if x < 0)
    if gl == 0 and gp > 0:
        return 999.0
    if gl == 0:
        return 0.0
    return gp / gl

def stats(rows):
    vals = [r["net"] for r in rows]
    if not vals:
        return None
    n = len(vals)
    wins = sum(1 for x in vals if x > 0)
    return {
        "n": n,
        "net": sum(vals),
        "gross": sum(r["gross"] for r in rows),
        "cost": sum(r["cost"] for r in rows),
        "avg": sum(vals) / n,
        "wr": wins / n * 100,
        "pf": pf(vals),
        "sl": sum(1 for r in rows if r["reason"] == "SL"),
        "time": sum(1 for r in rows if r["reason"] == "TIME"),
        "tp": sum(1 for r in rows if r["reason"] == "TP"),
    }

def ok(r, pc_min, pc_max, vol_min, spread_max, rank_max, blacklist):
    return (
        r["pc"] >= pc_min
        and r["pc"] <= pc_max
        and r["vol"] >= vol_min
        and r["spread"] <= spread_max
        and r["rank"] <= rank_max
        and r["sym"] not in blacklist
    )

def run_dynamic(rows, pc_max, vol_min, spread_max, rank_max, blacklist, sl_after, ban_hours, fast_ban_hours):
    ban_until = {}
    sl_count = defaultdict(int)
    out = []

    for r in sorted(rows, key=lambda x: x["ts"]):
        sym = r["sym"]

        if sym in blacklist:
            continue

        if sym in ban_until and r["ts"] < ban_until[sym]:
            continue

        if not ok(r, 0.30, pc_max, vol_min, spread_max, rank_max, blacklist):
            continue

        out.append(r)

        if r["reason"] == "SL":
            sl_count[sym] += 1
            if r["age"] <= 90:
                ban_until[sym] = r["ts"] + timedelta(hours=fast_ban_hours)
            elif sl_count[sym] >= sl_after:
                ban_until[sym] = r["ts"] + timedelta(hours=ban_hours)

        if r["net"] > 0:
            sl_count[sym] = max(0, sl_count[sym] - 1)

    return out

def parse_rows():
    if not LOG.exists():
        return []

    opens = {}
    rows = []

    for line in LOG.read_text(errors="ignore").splitlines():
        mo = open_re.search(line)
        if mo:
            sid = mo.group("sid")
            opens[sid] = {
                "ts_open": dt(mo.group("ts")),
                "sym": mo.group("sym"),
                "sid": sid,
                "entry": float(mo.group("entry")),
                "pc": float(mo.group("pc")),
                "vol": float(mo.group("vol")),
                "spread": float(mo.group("spread")),
                "rank": int(mo.group("rank")),
            }
            continue

        mc = close_re.search(line)
        if mc:
            sid = mc.group("sid")
            op = opens.get(sid)
            if not op:
                continue

            r = dict(op)
            r.update({
                "ts": dt(mc.group("ts")),
                "reason": mc.group("reason"),
                "exit": float(mc.group("exit")),
                "move": float(mc.group("move")),
                "gross": float(mc.group("gross")),
                "net": float(mc.group("net")),
                "cost": float(mc.group("cost")),
                "age": float(mc.group("age")),
            })
            rows.append(r)

    return sorted(rows, key=lambda x: x["ts"])

def fmt(name, rows):
    s = stats(rows)
    if not s:
        return f"{name:70s} n=0"
    return (
        f"{name:70s} "
        f"n={s['n']:3d} net=${s['net']:+.4f} gross=${s['gross']:+.4f} cost=${s['cost']:.4f} "
        f"avg=${s['avg']:+.5f} WR={s['wr']:5.1f}% PF={s['pf']:6.2f} "
        f"SL={s['sl']:2d} TIME={s['time']:2d} TP={s['tp']:2d}"
    )

def main():
    rows = parse_rows()
    lines = []

    lines.append("=" * 120)
    lines.append("V18 FADE OFFLINE SWEEP FROM JOURNAL — NET AFTER COMMISSION")
    lines.append("=" * 120)
    lines.append(f"parsed_closed_trades={len(rows)}")
    if rows:
        lines.append(f"from={rows[0]['ts']}")
        lines.append(f"to={rows[-1]['ts']}")

    lines.append("")
    lines.append("=== ALL PARSED ===")
    lines.append(fmt("ALL", rows))

    lines.append("")
    lines.append("=== SYMBOL SUMMARY ===")
    bysym = defaultdict(list)
    for r in rows:
        bysym[r["sym"]].append(r)

    for sym, rs in sorted(bysym.items(), key=lambda kv: stats(kv[1])["net"]):
        lines.append(fmt(sym, rs))

    lines.append("")
    lines.append("=== PC BUCKETS ===")
    buckets = {
        "pc_030_050": lambda r: 0.30 <= r["pc"] < 0.50,
        "pc_050_080": lambda r: 0.50 <= r["pc"] < 0.80,
        "pc_080_120": lambda r: 0.80 <= r["pc"] < 1.20,
        "pc_120_plus": lambda r: r["pc"] >= 1.20,
    }
    for name, fn in buckets.items():
        lines.append(fmt(name, [r for r in rows if fn(r)]))

    lines.append("")
    lines.append("=== STATIC FILTER SWEEP n>=5 ===")
    static_results = []

    for pc_max in [0.50, 0.80, 1.20, 999.0]:
        for vol_min in [12.0, 15.0, 20.0, 25.0]:
            for spread_max in [1.0, 1.5, 2.0]:
                for rank_max in [30, 40, 50]:
                    for bl_name, bl in [("base_bl", BASE_BLACKLIST), ("known_bad_bl", KNOWN_BAD)]:
                        filt = [r for r in rows if ok(r, 0.30, pc_max, vol_min, spread_max, rank_max, bl)]
                        s = stats(filt)
                        if s and s["n"] >= 5:
                            static_results.append((s["pf"], s["net"], s["avg"], s["n"], pc_max, vol_min, spread_max, rank_max, bl_name, filt))

    for _, _, _, _, pc_max, vol_min, spread_max, rank_max, bl_name, filt in sorted(static_results, reverse=True)[:50]:
        name = f"STATIC pc<= {pc_max:<5} vol>={vol_min:<4} spread<={spread_max:<3} rank<={rank_max:<2} {bl_name}"
        lines.append(fmt(name, filt))

    lines.append("")
    lines.append("=== DYNAMIC BAN SWEEP n>=5 ===")
    dyn_results = []

    for pc_max in [0.50, 0.80, 1.20, 999.0]:
        for vol_min in [12.0, 15.0, 20.0]:
            for spread_max in [1.0, 1.5, 2.0]:
                for rank_max in [30, 40, 50]:
                    for bl_name, bl in [("base_bl", BASE_BLACKLIST), ("known_bad_bl", KNOWN_BAD)]:
                        for sl_after in [1, 2]:
                            for ban_h in [6, 12, 24]:
                                for fast_h in [6, 12, 24]:
                                    filt = run_dynamic(
                                        rows,
                                        pc_max=pc_max,
                                        vol_min=vol_min,
                                        spread_max=spread_max,
                                        rank_max=rank_max,
                                        blacklist=bl,
                                        sl_after=sl_after,
                                        ban_hours=ban_h,
                                        fast_ban_hours=fast_h,
                                    )
                                    s = stats(filt)
                                    if s and s["n"] >= 5:
                                        dyn_results.append((s["pf"], s["net"], s["avg"], s["n"], pc_max, vol_min, spread_max, rank_max, bl_name, sl_after, ban_h, fast_h, filt))

    for _, _, _, _, pc_max, vol_min, spread_max, rank_max, bl_name, sl_after, ban_h, fast_h, filt in sorted(dyn_results, reverse=True)[:80]:
        name = (
            f"DYN pc<= {pc_max:<5} vol>={vol_min:<4} spread<={spread_max:<3} rank<={rank_max:<2} "
            f"{bl_name} sl_after={sl_after} ban={ban_h}h fast={fast_h}h"
        )
        lines.append(fmt(name, filt))

    lines.append("")
    lines.append("=== DECISION ===")
    lines.append("Commission is included: ranking uses NET from log, not gross.")
    lines.append("Do not enable real from this file alone.")
    lines.append("Use best candidate only for next shadow profile if n>=20, net>0, PF>1.25, avg positive, and recent window confirms.")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
