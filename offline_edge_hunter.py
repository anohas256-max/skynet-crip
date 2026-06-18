#!/usr/bin/env python3
import argparse
import csv
import gzip
import math
import os
import sqlite3
import statistics
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/root/skynet")
DATA = ROOT / "data"
ARCHIVE = ROOT / "archive"
OUT_DIR = ROOT / "safe_exports" / "offline_edge"

def now_tag():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

def sf(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default

def si(x, default=0):
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default

def money(x):
    return f"{x:+.2f}$"

def pf(vals):
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    if neg <= 0:
        return 999.0 if pos > 0 else 0.0
    return pos / neg

def stat(vals):
    vals = list(vals)
    n = len(vals)
    if not n:
        return {"n":0, "sum":0.0, "avg":0.0, "wr":0.0, "pf":0.0, "med":0.0, "best":0.0, "worst":0.0}
    s = sum(vals)
    return {
        "n": n,
        "sum": s,
        "avg": s / n,
        "wr": sum(1 for v in vals if v > 0) / n * 100.0,
        "pf": pf(vals),
        "med": statistics.median(vals),
        "best": max(vals),
        "worst": min(vals),
    }

def open_ro(db):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=20)
    con.row_factory = sqlite3.Row
    return con

def split_rows(rows, train_ratio=0.70):
    n = len(rows)
    i = int(n * train_ratio)
    return rows[:i], rows[i:]

def row_val(r, k):
    return sf(r.get(k))

def simulate_path_net(r, side, tp, sl, fee_cost_pct):
    """
    Conservative path sim from V18:
    If both TP and SL touched during hold window, assume SL first.
    LONG uses max_up / max_down / close_pct.
    SHORT inverts path: profit when max_down magnitude is enough.
    """
    up = sf(r.get("max_up"))
    down = sf(r.get("max_down"))
    closep = sf(r.get("close_pct"))

    if side == "LONG":
        hit_tp = up >= tp
        hit_sl = down <= -sl
        if hit_sl:
            move = -sl
            reason = "SL"
        elif hit_tp:
            move = tp
            reason = "TP"
        else:
            move = closep
            reason = "TIME"
    else:
        # SHORT profit if price goes down.
        hit_tp = down <= -tp
        hit_sl = up >= sl
        if hit_sl:
            move = -sl
            reason = "SL"
        elif hit_tp:
            move = tp
            reason = "TP"
        else:
            move = -closep
            reason = "TIME"

    # notional ~= 12$ for margin 3 * 4x. PnL dollars = 12 * move%.
    gross = 12.0 * (move / 100.0)
    costs = 12.0 * (fee_cost_pct / 100.0)
    return gross - costs, reason, move

def make_conditions_v17():
    conds = [
        ("ALL", lambda r: True),

        ("SP2", lambda r: row_val(r,"spread_bps") <= 2),
        ("SP3", lambda r: row_val(r,"spread_bps") <= 3),
        ("SP5", lambda r: row_val(r,"spread_bps") <= 5),
        ("SP7", lambda r: row_val(r,"spread_bps") <= 7),
        ("SP12", lambda r: row_val(r,"spread_bps") <= 12),

        ("R40", lambda r: row_val(r,"current_turnover_rank") <= 40),
        ("R80", lambda r: row_val(r,"current_turnover_rank") <= 80),
        ("R150", lambda r: row_val(r,"current_turnover_rank") <= 150),

        ("PC_POS", lambda r: row_val(r,"price_change") > 0),
        ("PC_NEG", lambda r: row_val(r,"price_change") < 0),
        ("ABS030", lambda r: abs(row_val(r,"price_change")) >= 0.30),
        ("ABS050", lambda r: abs(row_val(r,"price_change")) >= 0.50),
        ("ABS070", lambda r: abs(row_val(r,"price_change")) >= 0.70),

        ("V5", lambda r: row_val(r,"vol_ratio") >= 5),
        ("V8", lambda r: row_val(r,"vol_ratio") >= 8),
        ("V12", lambda r: row_val(r,"vol_ratio") >= 12),

        ("OI_POS", lambda r: row_val(r,"oi_change") > 0),
        ("OI_NEG", lambda r: row_val(r,"oi_change") < 0),
        ("OI_BIG_POS", lambda r: row_val(r,"oi_change") >= 2),
        ("OI_BIG_NEG", lambda r: row_val(r,"oi_change") <= -2),

        ("IMB_ASK", lambda r: row_val(r,"imb_5") <= -0.20),
        ("IMB_ASK10", lambda r: row_val(r,"imb_5") <= -0.10),
        ("IMB_BID", lambda r: row_val(r,"imb_5") >= 0.20),

        ("WALL_NEG", lambda r: row_val(r,"wall_skew") < 0),
        ("WALL_POS", lambda r: row_val(r,"wall_skew") > 0),
    ]
    return conds

def build_rule_grid():
    """
    Not insane full cartesian. Aggressive but bounded.
    """
    parts = {
        "pc": ["PC_POS", "PC_NEG", "ABS030", "ABS050", "ABS070"],
        "sp": ["SP2", "SP3", "SP5", "SP7", "SP12"],
        "rank": ["R40", "R80", "R150"],
        "vol": ["V5", "V8", "V12"],
        "oi": ["", "OI_POS", "OI_NEG", "OI_BIG_POS", "OI_BIG_NEG"],
        "imb": ["", "IMB_ASK", "IMB_ASK10", "IMB_BID"],
        "wall": ["", "WALL_NEG", "WALL_POS"],
    }
    rules = []

    # single conditions
    for group in parts.values():
        for x in group:
            if x:
                rules.append([x])

    # practical grids
    for pc in parts["pc"]:
        for sp in parts["sp"]:
            for rank in parts["rank"]:
                for vol in parts["vol"]:
                    base = [pc, sp, rank, vol]
                    rules.append(base)
                    for oi in parts["oi"]:
                        if oi:
                            rules.append(base + [oi])
                    for imb in parts["imb"]:
                        if imb:
                            rules.append(base + [imb])
                    for wall in parts["wall"]:
                        if wall:
                            rules.append(base + [wall])
                    for oi in ["OI_POS", "OI_NEG"]:
                        for imb in ["IMB_ASK", "IMB_ASK10", "IMB_BID"]:
                            rules.append(base + [oi, imb])

    # hand hypotheses
    rules += [
        ["PC_POS", "SP3", "R40", "V8", "IMB_ASK"],
        ["PC_POS", "SP5", "R80", "V8", "IMB_ASK10"],
        ["PC_NEG", "SP3", "R150", "V8", "IMB_ASK"],
        ["ABS030", "SP3", "R150", "V5", "IMB_ASK"],
        ["ABS030", "SP5", "R150", "V5", "IMB_ASK10"],
        ["ABS030", "SP7", "R150", "V5"],
        ["ABS050", "SP7", "R150", "V8"],
        ["ABS070", "SP12", "R150", "V8"],
    ]

    seen = set()
    out = []
    for r in rules:
        key = tuple(r)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out

def filter_rows(rows, rule, cond_map):
    fns = [cond_map[x] for x in rule]
    out = []
    for r in rows:
        ok = True
        for fn in fns:
            try:
                if not fn(r):
                    ok = False
                    break
            except Exception:
                ok = False
                break
        if ok:
            out.append(r)
    return out

def symbol_breakdown(rows, vals):
    by = defaultdict(list)
    for r, v in zip(rows, vals):
        by[r.get("clean_symbol") or r.get("symbol") or "?"].append(v)
    items = []
    for sym, xs in by.items():
        s = stat(xs)
        items.append((s["sum"], sym, s["n"], s["avg"], s["pf"]))
    return sorted(items, reverse=True)[:5], sorted(items)[:5]

def robust_line(r):
    return (
        f"{r['source']:4s} {r['side']:5s} {r['rule'][:52]:52s} "
        f"ALL n={r['all']['n']:4d} sum={money(r['all']['sum']):>8s} avg={money(r['all']['avg']):>8s} "
        f"wr={r['all']['wr']:5.1f}% pf={r['all']['pf']:.2f} | "
        f"TR n={r['tr']['n']:4d} sum={money(r['tr']['sum']):>8s} pf={r['tr']['pf']:.2f} | "
        f"TE n={r['te']['n']:4d} sum={money(r['te']['sum']):>8s} pf={r['te']['pf']:.2f}"
    )

def scan_v17(min_train, min_test):
    db = DATA / "v17_microstructure.sqlite3"
    if not db.exists():
        return [], ["NO v17 db"]

    con = open_ro(db)
    rows = [dict(x) for x in con.execute("""
        SELECT *
        FROM signals
        WHERE long_net_5m IS NOT NULL
          AND short_net_5m IS NOT NULL
        ORDER BY ts ASC
    """)]
    con.close()

    train, test = split_rows(rows)
    cond_map = dict(make_conditions_v17())
    rules = build_rule_grid()

    found = []
    notes = [f"V17 rows={len(rows)} train={len(train)} test={len(test)} rules={len(rules)}"]

    for rule in rules:
        name = "|".join(rule)
        tr_rows = filter_rows(train, rule, cond_map)
        te_rows = filter_rows(test, rule, cond_map)
        if len(tr_rows) < min_train or len(te_rows) < min_test:
            continue

        for side, col in [("LONG","long_net_5m"), ("SHORT","short_net_5m")]:
            tr_vals = [sf(x.get(col)) for x in tr_rows]
            te_vals = [sf(x.get(col)) for x in te_rows]
            all_rows = tr_rows + te_rows
            all_vals = tr_vals + te_vals
            tr = stat(tr_vals)
            te = stat(te_vals)
            al = stat(all_vals)

            robust = tr["sum"] > 0 and te["sum"] > 0 and tr["pf"] >= 1.05 and te["pf"] >= 1.05 and al["avg"] > 0
            score = te["sum"] * 2 + tr["sum"] * 0.5 + al["n"] * 0.01 - abs(tr["avg"] - te["avg"]) * 5

            best, worst = symbol_breakdown(all_rows, all_vals)
            found.append({
                "source": "V17",
                "side": side,
                "rule": name,
                "tr": tr,
                "te": te,
                "all": al,
                "robust": robust,
                "score": score,
                "best": best,
                "worst": worst,
            })

    return found, notes

def scan_v18(min_train, min_test):
    db = DATA / "v18_micro_paths.sqlite3"
    if not db.exists():
        return [], ["NO v18 db"]

    con = open_ro(db)
    rows = [dict(x) for x in con.execute("""
        SELECT *
        FROM signals
        WHERE closed=1
        ORDER BY ts ASC
    """)]
    con.close()

    train, test = split_rows(rows)
    cond_map = dict(make_conditions_v17())
    rules = build_rule_grid()

    # Estimated taker cost in percent on notional: commission 0.08%*2 + spread/slippage model.
    # We use conservative ~0.27% notional cost by default.
    fee_cost_pct = 0.27

    grids = [
        (0.30, 0.30),
        (0.35, 0.45),
        (0.40, 0.50),
        (0.50, 0.50),
        (0.60, 0.50),
        (0.60, 0.80),
        (0.80, 0.50),
        (0.80, 0.80),
        (1.00, 0.70),
    ]

    found = []
    notes = [f"V18 rows={len(rows)} train={len(train)} test={len(test)} rules={len(rules)} grids={len(grids)}"]

    for rule in rules:
        name = "|".join(rule)
        tr_base = filter_rows(train, rule, cond_map)
        te_base = filter_rows(test, rule, cond_map)
        if len(tr_base) < min_train or len(te_base) < min_test:
            continue

        for tp, sl in grids:
            for side in ["LONG", "SHORT"]:
                tr_pairs = [simulate_path_net(x, side, tp, sl, fee_cost_pct) for x in tr_base]
                te_pairs = [simulate_path_net(x, side, tp, sl, fee_cost_pct) for x in te_base]
                tr_vals = [x[0] for x in tr_pairs]
                te_vals = [x[0] for x in te_pairs]
                all_rows = tr_base + te_base
                all_vals = tr_vals + te_vals

                tr = stat(tr_vals)
                te = stat(te_vals)
                al = stat(all_vals)

                robust = tr["sum"] > 0 and te["sum"] > 0 and tr["pf"] >= 1.05 and te["pf"] >= 1.05 and al["avg"] > 0
                score = te["sum"] * 2 + tr["sum"] * 0.5 + al["n"] * 0.01 - abs(tr["avg"] - te["avg"]) * 5

                best, worst = symbol_breakdown(all_rows, all_vals)
                found.append({
                    "source": "V18",
                    "side": side,
                    "rule": f"{name}|TP{tp:.2f}|SL{sl:.2f}",
                    "tr": tr,
                    "te": te,
                    "all": al,
                    "robust": robust,
                    "score": score,
                    "best": best,
                    "worst": worst,
                })

    return found, notes

def scan_backtest_csvs():
    notes = []
    found_files = []

    patterns = [
        DATA / "backtest",
        DATA / "replay_sweep",
        DATA / "replay_meta_proxy",
        DATA / "replay_dynamic_ban",
        ARCHIVE / "compressed_data_keep",
    ]

    for base in patterns:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and (p.suffix.lower() in [".csv", ".gz"]):
                found_files.append(p)

    notes.append(f"CSV/GZ files found={len(found_files)}")
    previews = []

    for p in sorted(found_files, key=lambda x: x.stat().st_size, reverse=True)[:40]:
        previews.append(f"{p.stat().st_size/1024/1024:.2f} MB {p}")

    return notes, previews

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-train", type=int, default=35)
    ap.add_argument("--min-test", type=int, default=12)
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--full-v18", action="store_true", help="run heavy V18 full grid")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("=" * 110)
    lines.append(f"SKYNET OFFLINE EDGE HUNTER UTC={now_tag()}")
    lines.append("=" * 110)
    lines.append("Goal: stop waiting blindly; mine archives/recorders for robust train/test candidates.")
    lines.append("Real trading remains OFF. Results are candidates for shadow-only / dry-live only.")
    lines.append("")

    all_found = []

    v17, notes17 = scan_v17(args.min_train, args.min_test)
    all_found.extend(v17)
    lines.append("\n".join(notes17))

    if args.full_v18:
        v18, notes18 = scan_v18(args.min_train, args.min_test)
        all_found.extend(v18)
        lines.append("\n".join(notes18))
    else:
        lines.append("V18 full grid skipped by default to keep context-pack fast. Use --full-v18 manually.")

    csv_notes, csv_previews = scan_backtest_csvs()
    lines.append("\n".join(csv_notes))

    robust = [x for x in all_found if x["robust"]]
    top_test = sorted(all_found, key=lambda x: x["te"]["sum"], reverse=True)[:args.top]
    top_score = sorted(all_found, key=lambda x: x["score"], reverse=True)[:args.top]

    lines.append("")
    lines.append("=" * 110)
    lines.append("ROBUST TRAIN/TEST CANDIDATES")
    lines.append("=" * 110)

    if not robust:
        lines.append("[EMPTY] No robust train/test candidate found. Do not promote any new strategy.")
    else:
        for r in sorted(robust, key=lambda x: x["score"], reverse=True)[:args.top]:
            lines.append(robust_line(r))
            lines.append(f"      best={[(b[1], round(b[0],3), b[2]) for b in r['best']]}")
            lines.append(f"      worst={[(w[1], round(w[0],3), w[2]) for w in r['worst']]}")

    lines.append("")
    lines.append("=" * 110)
    lines.append("TOP BY TEST SUM")
    lines.append("=" * 110)
    for r in top_test[:args.top]:
        lines.append(robust_line(r))

    lines.append("")
    lines.append("=" * 110)
    lines.append("TOP BY ROBUST SCORE")
    lines.append("=" * 110)
    for r in top_score[:args.top]:
        lines.append(robust_line(r))

    lines.append("")
    lines.append("=" * 110)
    lines.append("ARCHIVE CSV INVENTORY PREVIEW")
    lines.append("=" * 110)
    lines.extend(csv_previews)

    lines.append("")
    lines.append("=" * 110)
    lines.append("DECISION")
    lines.append("=" * 110)
    lines.append("1. If ROBUST is empty: current features do not prove edge. Stop adding live variants from this dataset.")
    lines.append("2. If V18 robust exists but V17 not: candidate depends on path/TP/SL, add shadow-only with exact TP/SL.")
    lines.append("3. If V17 robust exists: candidate can become dry-live shadow track after live sanity.")
    lines.append("4. If only TOP TEST is green but train red: regime/noise, not strategy.")
    lines.append("5. Next aggressive move: parse CSV archive winners and replay them with current cost model.")

    text = "\n".join(lines) + "\n"

    if args.stdout:
        print(text)
        return

    out = OUT_DIR / f"offline_edge_hunter_{now_tag()}.txt"
    out.write_text(text, encoding="utf-8", errors="ignore")
    print(out)

if __name__ == "__main__":
    main()
