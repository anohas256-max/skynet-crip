#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "targeted_fade_v18_readiness_latest.txt"

# These are based on V17 robust-ish fade candidates:
# SHORT ABS030|SP3|R150|V5|IMB_ASK
# SHORT ABS030|SP2|R150|V5|IMB_ASK10
RULES = [
    {"name": "SHORT_ABS030_SP3_R150_V5", "pc": 0.30, "spread": 3.0, "rank": 150, "vol": 5.0},
    {"name": "SHORT_ABS030_SP2_R150_V5", "pc": 0.30, "spread": 2.0, "rank": 150, "vol": 5.0},
    {"name": "SHORT_ABS050_SP3_R150_V5", "pc": 0.50, "spread": 3.0, "rank": 150, "vol": 5.0},
    {"name": "SHORT_ABS070_SP3_R150_V8", "pc": 0.70, "spread": 3.0, "rank": 150, "vol": 8.0},
    {"name": "SHORT_ABS030_SP5_R80_V8",  "pc": 0.30, "spread": 5.0, "rank": 80,  "vol": 8.0},
]

TP_SL = [
    (0.5, 0.3),
    (0.75, 0.3),
    (1.0, 0.3),
    (1.5, 0.3),
    (2.0, 0.3),
    (3.0, 0.3),
    (1.0, 0.5),
    (2.0, 0.5),
    (3.0, 0.5),
]

COSTS = [0.03, 0.05, 0.10, 0.17, 0.29]

def val(row, names, default=0.0):
    for n in names:
        if n in row.keys():
            try:
                return float(row[n])
            except Exception:
                return default
    return default

def clean_symbol(s):
    s = str(s or "").upper()
    if s.endswith("_USDT"):
        s = s[:-5]
    if s.endswith("USDT"):
        s = s[:-4]
    return s

def split(rows):
    cut = int(len(rows) * 0.70)
    return rows[:cut], rows[cut:]

def eval_short(rows, rule, tp, sl, cost):
    out = []
    by_symbol = {}

    for r in rows:
        sym = clean_symbol(r["symbol"] if "symbol" in r.keys() else "")

        pc = abs(val(r, ["price_change", "price_change_pct", "pc", "ret1"]))
        vol = val(r, ["vol_ratio", "volume_ratio", "vol"])
        spread = val(r, ["spread_bps", "spread"], 999)
        rank = val(r, ["rank", "rank_abs_ret1", "turnover_rank"], 999)

        if pc < rule["pc"]:
            continue
        if vol < rule["vol"]:
            continue
        if spread > rule["spread"]:
            continue
        if rank > rule["rank"]:
            continue

        max_up = val(r, ["max_up_pct", "max_up", "mfe_up_pct"], 0)
        max_down = val(r, ["max_down_pct", "max_down", "mae_down_pct"], 0)
        if max_down < 0:
            max_down = abs(max_down)

        # Conservative SHORT path:
        # if both TP and SL touched, SL wins.
        tp_hit = max_down >= tp
        sl_hit = max_up >= sl

        if sl_hit:
            net = -sl - cost
            reason = "SL"
        elif tp_hit:
            net = tp - cost
            reason = "TP"
        else:
            close_pct = val(r, ["close_pct", "close_move_pct", "future_close_pct"], 0)
            net = -close_pct - cost
            reason = "TIME"

        out.append(net)
        by_symbol.setdefault(sym, [0, 0.0, 0, 0])
        by_symbol[sym][0] += 1
        by_symbol[sym][1] += net
        by_symbol[sym][2] += 1 if net > 0 else 0
        by_symbol[sym][3] += 1 if reason == "SL" else 0

    if not out:
        return None

    pos = sum(x for x in out if x > 0)
    neg = -sum(x for x in out if x < 0)
    pf = pos / neg if neg > 0 else 999 if pos > 0 else 0
    wr = sum(x > 0 for x in out) / len(out) * 100
    s = sum(out)
    avg = s / len(out)

    symbols = sorted(
        [(k, v[0], v[1], v[1] / v[0], v[2] / v[0] * 100, v[3] / v[0] * 100) for k, v in by_symbol.items()],
        key=lambda x: x[2],
        reverse=True
    )

    return {"n": len(out), "sum": s, "avg": avg, "wr": wr, "pf": pf, "symbols": symbols}

def fmt(x):
    if not x:
        return "n=0"
    return f"n={x['n']:5d} sum={x['sum']:+9.2f}% avg={x['avg']:+8.4f}% wr={x['wr']:5.1f}% pf={x['pf']:6.2f}"

def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM signals ORDER BY id").fetchall()
    con.close()

    train, test = split(rows)
    results = []

    for rule in RULES:
        for tp, sl in TP_SL:
            for cost in COSTS:
                all_s = eval_short(rows, rule, tp, sl, cost)
                tr_s = eval_short(train, rule, tp, sl, cost)
                te_s = eval_short(test, rule, tp, sl, cost)

                if not all_s or not tr_s or not te_s:
                    continue

                robust = (
                    all_s["n"] >= 80 and tr_s["n"] >= 50 and te_s["n"] >= 20
                    and all_s["sum"] > 0 and tr_s["sum"] > 0 and te_s["sum"] > 0
                    and all_s["pf"] > 1.05 and te_s["pf"] > 1.02
                    and all_s["avg"] > 0.005
                )

                score = all_s["sum"] + tr_s["sum"] * 0.5 + te_s["sum"] * 2 + all_s["pf"]
                results.append((robust, score, rule, tp, sl, cost, all_s, tr_s, te_s))

    results.sort(key=lambda x: (x[0], x[1]), reverse=True)

    lines = []
    lines.append("=" * 120)
    lines.append(f"TARGETED FADE V18 READINESS UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 120)
    lines.append(f"db={DB}")
    lines.append(f"rows={len(rows)} train={len(train)} test={len(test)}")
    lines.append("Goal: verify V17 robust-ish SHORT fade rules on V18 path recorder.")
    lines.append("Real remains OFF.")
    lines.append("")

    robust_count = sum(1 for r in results if r[0])
    lines.append(f"robust_count={robust_count}")
    lines.append("")

    lines.append("=== ROBUST ===")
    for robust, score, rule, tp, sl, cost, all_s, tr_s, te_s in results:
        if not robust:
            continue
        lines.append("")
        lines.append(f"[ROBUST] score={score:.2f} rule={rule['name']} TP={tp} SL={sl} cost={cost}")
        lines.append("  ALL   " + fmt(all_s))
        lines.append("  TRAIN " + fmt(tr_s))
        lines.append("  TEST  " + fmt(te_s))
        lines.append("  top symbols:")
        for sym in all_s["symbols"][:12]:
            lines.append(f"    {sym[0]:<12} n={sym[1]:4d} sum={sym[2]:+8.2f}% avg={sym[3]:+7.4f}% wr={sym[4]:5.1f}% sl={sym[5]:5.1f}%")

    lines.append("")
    lines.append("=== TOP 30 WEAK/ALL ===")
    for robust, score, rule, tp, sl, cost, all_s, tr_s, te_s in results[:30]:
        tag = "ROBUST" if robust else "weak"
        lines.append("")
        lines.append(f"[{tag}] score={score:.2f} rule={rule['name']} TP={tp} SL={sl} cost={cost}")
        lines.append("  ALL   " + fmt(all_s))
        lines.append("  TRAIN " + fmt(tr_s))
        lines.append("  TEST  " + fmt(te_s))
        lines.append("  top symbols: " + ", ".join(f"{s[0]}:{s[1]}/{s[2]:+.2f}%" for s in all_s["symbols"][:8]))

    lines.append("")
    lines.append("=" * 120)
    lines.append("DECISION")
    lines.append("=" * 120)
    if robust_count:
        lines.append("There are V18-confirmed fade candidates. Next step: build one shadow-only fade lane from the exact best rule, not real.")
    else:
        lines.append("No V18-confirmed robust fade candidate. V17 fade edge likely overfit/stale. Do not build real from it.")
        lines.append("Next practical path: external/catalyst/cross-market edge, or proper maker book simulation.")

    OUT.write_text("\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
