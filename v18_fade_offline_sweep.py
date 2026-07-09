#!/usr/bin/env python3
import re
import itertools
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict

LOG = Path("v18_fade_journal_all.log")
OUT = Path("v18_fade_offline_sweep_latest.txt")

BASE_BLACKLIST = {"ALLO", "XPL"}
KNOWN_BAD = {"ALLO", "XPL", "TAC", "SOXL"}

open_re = re.compile(
    r"\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC\] "
    r"V18_FADE_DB_OPEN .*? SHORT \| (?P<sym>[A-Z0-9]+) \| "
    r"entry=(?P<entry>[0-9.]+) signal_id=(?P<sid>[0-9]+) "
    r"pc=\+(?P<pc>[0-9.]+)% vol=x(?P<vol>[0-9.]+) spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>[0-9]+)"
)

close_re = re.compile(
    r"\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC\] "
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
    n = len(vals)
    if n == 0:
        return None
    wins = sum(1 for x in vals if x > 0)
    sl = sum(1 for r in rows if r["reason"] == "SL")
    timec = sum(1 for r in rows if r["reason"] == "TIME")
    tp = sum(1 for r in rows if r["reason"] == "TP")
    gross = sum(r["gross"] for r in rows)
    cost = sum(r["cost"] for r in rows)
    net = sum(vals)
    return {
        "n": n,
        "net": net,
        "gross": gross,
        "cost": cost,
        "avg": net / n,
        "wr": wins / n * 100,
        "pf": pf(vals),
        "sl": sl,
        "time": timec,
        "tp": tp,
    }

def ok(row, pc_min, pc_max, vol_min, spread_max, rank_max, blacklist):
    return (
        row["pc"] >= pc_min
        and row["pc"] <= pc_max
        and row["vol"] >= vol_min
        and row["spread"] <= spread_max
        and row["rank"] <= rank_max
        and row["sym"] not in blacklist
    )

def run_dynamic(rows, pc_min, pc_max, vol_min, spread_max, rank_max, blacklist, sl_ban_after, ban_hours, fast_sl_age, fast_ban_hours):
    ban_until = {}
    sl_count = defaultdict(int)
    out = []

    for r in sorted(rows, key=lambda x: x["ts"]):
        sym = r["sym"]

        if sym in blacklist:
            continue

        until = ban_until.get(sym)
        if until and r["ts"] < until:
            continue

        if not ok(r, pc_min, pc_max, vol_min, spread_max, rank_max, blacklist):
            continue

        out.append(r)

        if r["reason"] == "SL":
            sl_count[sym] += 1
            if r["age"] <= fast_sl_age:
                ban_until[sym] = r["ts"] + timedelta(hours=fast_ban_hours)
            elif sl_count[sym] >= sl_ban_after:
                ban_until[sym] = r["ts"] + timedelta(hours=ban_hours)

        if r["net"] > 0:
            sl_count[sym] = max(0, sl_count[sym] - 1)

    return out

def main():
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

            row = dict(op)
            row.update({
                "ts": dt(mc.group("ts")),
                "reason": mc.group("reason"),
                "exit": float(mc.group("exit")),
                "move": float(mc.group("move")),
                "gross": float(mc.group("gross")),
                "net": float(mc.group("net")),
                "cost": float(mc.group("cost")),
                "age": float(mc.group("age")),
            })
            rows.append(row)

    lines = []
    lines.append("=" * 120)
    lines.append(f"V18 FADE OFFLINE SWEEP FROM JOURNAL")
    lines.append("=" * 120)
    lines.append(f"parsed_closed_trades={len(rows)}")
    if rows:
        lines.append(f"from={min(r['ts'] for r in rows)}")
        lines.append(f"to={max(r['ts'] for r in rows)}")

    total = stats(rows)
    lines.append("")
    lines.append("=== ALL PARSED, NET ALREADY AFTER COMMISSION ===")
    if total:
        lines.append(
            f"n={total['n']} net=${total['net']:+.4f} gross=${total['gross']:+.4f} "
            f"cost=${total['cost']:.4f} avg=${total['avg']:+.5f} WR={total['wr']:.1f}% "
            f"PF={total['pf']:.2f} SL={total['sl']} TIME={total['time']} TP={total['tp']}"
        )

    lines.append("")
    lines.append("=== SYMBOL SUMMARY ===")
    bysym = defaultdict(list)
    for r in rows:
        bysym[r["sym"]].append(r)
    for sym, rs in sorted(bysym.items(), key=lambda kv: stats(kv[1])["net"]):
        s = stats(rs)
        lines.append(
            f"{sym:10s} n={s['n']:3d} net=${s['net']:+.4f} avg=${s['avg']:+.5f} "
            f"WR={s['wr']:5.1f}% PF={s['pf']:6.2f} SL={s['sl']:2d} TIME={s['time']:2d} cost=${s['cost']:.4f}"
        )

    lines.append("")
    lines.append("=== STATIC FILTER SWEEP n>=5, NET AFTER COMMISSION ===")
    results = []
    for pc_max, vol_min, spread_max, rank_max, bl_name, bl in itertools.product(
        [0.50, 0.80, 1.20, 999.0],
        [12.0, 15.0, 20.0, 25.0],
        [1.0, 1.5, 2.0],
        [30, 40, 50],
        [
            ("base_bl", BASE_BLACKLIST),
            ("known_bad_bl", KNOWN_BAD),
        ],
    ):
        filt = [r for r in rows if ok(r, 0.30, pc_max, vol_min, spread_max, rank_max, bl)]
        s = stats(filt)
        if not s or s["n"] < 5:
            continue
        results.append((s["pf"], s["net"], s["avg"], s["n"], pc_max, vol_min, spread_max, rank_max, bl_name, s))

    for pfv, net, avg, n, pc_max, vol_min, spread_max, rank_max, bl_name, s in sorted(results, reverse=True)[:40]:
        lines.append(
            f"pc<= {pc_max:<5} vol>={vol_min:<4} spread<={spread_max:<3} rank<={rank_max:<2} {bl_name:12s} "
            f"n={s['n']:3d} net=${s['net']:+.4f} avg=${s['avg']:+.5f} WR={s['wr']:5.1f}% PF={s['pf']:6.2f} "
            f"SL={s['sl']:2d} TIME={s['time']:2d} cost=${s['cost']:.4f}"
        )

    lines.append("")
    lines.append("=== DYNAMIC BAN SWEEP n>=5, NET AFTER COMMISSION ===")
    dyn_results = []
    for pc_max, vol_min, spread_max, rank_max, bl_name, bl, sl_after, ban_h, fast_h in itertools.product(
        [0.50, 0.80, 1.20, 999.0],
        [12.0, 15.0, 20.0],
        [1.0, 1.5, 2.0],
        [30, 40, 50],
        [
            ("base_bl", BASE_BLACKLIST),
            ("known_bad_bl", KNOWN_BAD),
        ],
        [1, 2],
        [6, 12, 24],
        [6, 12, 24],
    ):
        filt = run_dynamic(
            rows,
            pc_min=0.30,
            pc_max=pc_max,
            vol_min=vol_min,
            spread_max=spread_max,
            rank_max=rank_max,
            blacklist=bl,
            sl_ban_after=sl_after,
            ban_hours=ban_h,
            fast_sl_age=90,
            fast_ban_hours=fast_h,
        )
        s = stats(filt)
        if not s or s["n"] < 5:
            continue
        dyn_results.append((s["pf"], s["net"], s["avg"], s["n"], pc_max, vol_min, spread_max, rank_max, bl_name, sl_after, ban_h, fast_h, s))

    for pfv, net, avg, n, pc_max, vol_min, spread_max, rank_max, bl_name, sl_after, ban_h, fast_h, s in sorted(dyn_results, reverse=True)[:60]:
        lines.append(
            f"pc<= {pc_max:<5} vol>={vol_min:<4} spread<={spread_max:<3} rank<={rank_max:<2} {bl_name:12s} "
            f"sl_after={sl_after} ban={ban_h}h fast_ban={fast_h}h "
            f"n={s['n']:3d} net=${s['net']:+.4f} avg=${s['avg']:+.5f} WR={s['wr']:5.1f}% PF={s['pf']:6.2f} "
            f"SL={s['sl']:2d} TIME={s['time']:2d} cost=${s['cost']:.4f}"
        )

    lines.append("")
    lines.append("=== DECISION RULE ===")
    lines.append("Do NOT use real from this. Use the best candidate only for next shadow if:")
    lines.append("n>=20 here, net>0, avg>0 after commission, PF>1.25, and recent live shadow also confirms.")
    lines.append("Commission is included through log net/cost.")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
