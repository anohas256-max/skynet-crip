#!/usr/bin/env python3
import os
import sqlite3
import math
import statistics
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DBS = [
    ROOT / "data/v18_micro_paths.sqlite3",
    ROOT / "data/v17_microstructure.sqlite3",
    ROOT / "data/skynet_recorder.sqlite3",
]

OUT_DIR = ROOT / "safe_exports" / "feature_lab"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def qnum(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def fmt(x, nd=3):
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def table_cols(con, table):
    cur = con.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def find_tables(con):
    rows = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r[0] for r in rows]


def pick_col(cols, names):
    low = {c.lower(): c for c in cols}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    for c in cols:
        cl = c.lower()
        for n in names:
            if n.lower() in cl:
                return c
    return None


def load_rows_from_db(path):
    if not path.exists():
        return []

    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    all_rows = []

    for table in find_tables(con):
        cols = table_cols(con, table)
        if not cols:
            continue

        # Need enough event-like fields.
        pc_col = pick_col(cols, ["price_change", "pc", "price_change_pct", "change_pct"])
        vol_col = pick_col(cols, ["vol_ratio", "volume_ratio", "vol"])
        sym_col = pick_col(cols, ["symbol", "sym"])
        if not pc_col or not vol_col:
            continue

        # Forward outcome columns may have different names.
        mfe_cols = [c for c in cols if "mfe" in c.lower() or "max_up" in c.lower() or "future_up" in c.lower()]
        mae_cols = [c for c in cols if "mae" in c.lower() or "drawdown" in c.lower() or "future_down" in c.lower()]
        ret_cols = [c for c in cols if "return" in c.lower() or "ret_" in c.lower() or "pnl" in c.lower()]

        if not mfe_cols and not mae_cols and not ret_cols:
            continue

        wanted = []
        for c in [
            sym_col,
            pc_col,
            vol_col,
            pick_col(cols, ["oi_change", "oi", "open_interest_change"]),
            pick_col(cols, ["trend_15m", "trend", "trend15m"]),
            pick_col(cols, ["btc_5m_change", "btc_5m", "btc_change"]),
            pick_col(cols, ["score"]),
            pick_col(cols, ["structure_risk", "struct", "struct_risk"]),
            pick_col(cols, ["breakout_risk_score", "brisk", "breakout_risk"]),
            pick_col(cols, ["false_breakouts_15m", "fb", "false_breakouts"]),
            pick_col(cols, ["spread_bps", "spread"]),
            pick_col(cols, ["rank", "current_turnover_rank", "turnover_rank"]),
            pick_col(cols, ["imbalance", "imb", "orderbook_imbalance"]),
            pick_col(cols, ["wall_imbalance", "wall"]),
        ]:
            if c and c not in wanted:
                wanted.append(c)

        for c in mfe_cols[:8] + mae_cols[:8] + ret_cols[:8]:
            if c and c not in wanted:
                wanted.append(c)

        sql = f"SELECT {', '.join([repr(c).strip(chr(39)) for c in wanted])} FROM {table} LIMIT 200000"
        try:
            rows = con.execute(sql).fetchall()
        except Exception:
            continue

        for r in rows:
            d = dict(r)
            d["_db"] = path.name
            d["_table"] = table
            d["_sym_col"] = sym_col
            d["_pc_col"] = pc_col
            d["_vol_col"] = vol_col
            d["_mfe_cols"] = ",".join(mfe_cols[:8])
            d["_mae_cols"] = ",".join(mae_cols[:8])
            d["_ret_cols"] = ",".join(ret_cols[:8])
            all_rows.append(d)

    con.close()
    return all_rows


def choose_outcome(row):
    # Prefer explicit MFE/MAE if available.
    keys = list(row.keys())
    mfe_keys = [k for k in keys if "mfe" in k.lower() or "max_up" in k.lower() or "future_up" in k.lower()]
    mae_keys = [k for k in keys if "mae" in k.lower() or "drawdown" in k.lower() or "future_down" in k.lower()]
    ret_keys = [k for k in keys if "return" in k.lower() or "ret_" in k.lower() or "pnl" in k.lower()]

    mfe = None
    mae = None

    for k in mfe_keys:
        v = qnum(row.get(k), None)
        if v is not None:
            mfe = max(mfe, v) if mfe is not None else v

    for k in mae_keys:
        v = qnum(row.get(k), None)
        if v is not None:
            mae = min(mae, v) if mae is not None else v

    # If only returns exist, use best absolute ret proxy.
    if mfe is None and ret_keys:
        vals = [qnum(row.get(k), None) for k in ret_keys]
        vals = [v for v in vals if v is not None]
        if vals:
            mfe = max(vals)
            mae = min(vals)

    return mfe, mae


def feature(row, names):
    keys = list(row.keys())
    c = pick_col(keys, names)
    return qnum(row.get(c), None) if c else None


def bucket(v, cuts):
    if v is None:
        return "NA"
    for c in cuts:
        if v < c:
            return f"<{c}"
    return f">={cuts[-1]}"


def summarize_group(rows, title):
    if not rows:
        return [f"{title}: no rows"]

    mfes = [r["mfe"] for r in rows if r["mfe"] is not None]
    maes = [r["mae"] for r in rows if r["mae"] is not None]
    good = [r for r in rows if (r["mfe"] is not None and r["mfe"] >= 0.8)]
    bad = [r for r in rows if (r["mae"] is not None and r["mae"] <= -0.5)]

    out = []
    out.append(f"{title}: n={len(rows)} good_mfe>=0.8={len(good)} bad_mae<=-0.5={len(bad)}")
    if mfes:
        out.append(f"  MFE avg={fmt(sum(mfes)/len(mfes))}% med={fmt(statistics.median(mfes))}% p90={fmt(sorted(mfes)[int(0.9*(len(mfes)-1))])}%")
    if maes:
        out.append(f"  MAE avg={fmt(sum(maes)/len(maes))}% med={fmt(statistics.median(maes))}% p10={fmt(sorted(maes)[int(0.1*(len(maes)-1))])}%")
    return out


def score_rule(rows, pred):
    sub = [r for r in rows if pred(r)]
    if len(sub) < 20:
        return None
    tp = [r for r in sub if r["mfe"] is not None and r["mfe"] >= 0.8]
    sl = [r for r in sub if r["mae"] is not None and r["mae"] <= -0.5]
    neutral = len(sub) - len(tp) - len(sl)
    # crude utility
    utility = len(tp)*0.8 - len(sl)*0.5 - neutral*0.03
    return {
        "n": len(sub),
        "tp": len(tp),
        "sl": len(sl),
        "neutral": neutral,
        "tp_rate": len(tp)/len(sub),
        "sl_rate": len(sl)/len(sub),
        "utility": utility,
        "avg_mfe": sum([r["mfe"] for r in sub if r["mfe"] is not None]) / max(1, len([r for r in sub if r["mfe"] is not None])),
        "avg_mae": sum([r["mae"] for r in sub if r["mae"] is not None]) / max(1, len([r for r in sub if r["mae"] is not None])),
    }


def main():
    rows = []
    for db in DBS:
        loaded = load_rows_from_db(db)
        rows.extend(loaded)

    norm = []
    for r in rows:
        mfe, mae = choose_outcome(r)
        if mfe is None and mae is None:
            continue

        nr = {
            "db": r.get("_db"),
            "table": r.get("_table"),
            "symbol": str(r.get(r.get("_sym_col"), "")),
            "pc": feature(r, ["price_change", "pc", "price_change_pct", "change_pct"]),
            "vol": feature(r, ["vol_ratio", "volume_ratio", "vol"]),
            "oi": feature(r, ["oi_change", "oi", "open_interest_change"]),
            "trend": feature(r, ["trend_15m", "trend", "trend15m"]),
            "btc": feature(r, ["btc_5m_change", "btc_5m", "btc_change"]),
            "score": feature(r, ["score"]),
            "struct": feature(r, ["structure_risk", "struct", "struct_risk"]),
            "brisk": feature(r, ["breakout_risk_score", "brisk", "breakout_risk"]),
            "fb": feature(r, ["false_breakouts_15m", "fb", "false_breakouts"]),
            "spread": feature(r, ["spread_bps", "spread"]),
            "rank": feature(r, ["rank", "current_turnover_rank", "turnover_rank"]),
            "imb": feature(r, ["imbalance", "imb", "orderbook_imbalance"]),
            "wall": feature(r, ["wall_imbalance", "wall"]),
            "mfe": mfe,
            "mae": mae,
        }
        norm.append(nr)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    out_path = OUT_DIR / f"v18_feature_mining_lab_{ts}.txt"

    lines = []
    lines.append("=" * 120)
    lines.append(f"V18 FEATURE MINING LAB UTC={ts}")
    lines.append("=" * 120)
    lines.append("Goal: find features that separate future TP-like moves from SL-like moves. Diagnostics only. Real trading OFF.")
    lines.append("")
    lines.append(f"loaded_rows_with_outcome={len(norm)}")
    by_src = {}
    for r in norm:
        by_src[(r["db"], r["table"])] = by_src.get((r["db"], r["table"]), 0) + 1
    lines.append("sources:")
    for k, v in sorted(by_src.items(), key=lambda x: -x[1])[:20]:
        lines.append(f"  {k[0]}::{k[1]} n={v}")

    lines.append("")
    lines.extend(summarize_group(norm, "ALL"))

    # Buckets.
    specs = [
        ("pc", [0.2, 0.3, 0.5, 0.7, 1.0]),
        ("vol", [5, 8, 12, 20, 40]),
        ("oi", [-3, -1, 0, 1, 3]),
        ("trend", [-1, 0, 0.5, 1.5, 3]),
        ("btc", [-0.1, 0, 0.1, 0.3]),
        ("score", [0, 2, 4, 6]),
        ("struct", [1, 3, 5, 7]),
        ("brisk", [1, 3, 5, 7]),
        ("fb", [1, 2, 3, 5]),
        ("rank", [20, 40, 80, 150]),
    ]

    lines.append("")
    lines.append("=" * 120)
    lines.append("BUCKET QUALITY")
    lines.append("=" * 120)
    for feat, cuts in specs:
        groups = {}
        for r in norm:
            b = bucket(r.get(feat), cuts)
            groups.setdefault(b, []).append(r)
        lines.append("")
        lines.append(f"--- {feat} ---")
        for b, rs in sorted(groups.items(), key=lambda x: x[0]):
            if len(rs) < 20:
                continue
            tp = sum(1 for r in rs if r["mfe"] is not None and r["mfe"] >= 0.8)
            sl = sum(1 for r in rs if r["mae"] is not None and r["mae"] <= -0.5)
            avg_mfe = sum([r["mfe"] for r in rs if r["mfe"] is not None]) / max(1, len([r for r in rs if r["mfe"] is not None]))
            avg_mae = sum([r["mae"] for r in rs if r["mae"] is not None]) / max(1, len([r for r in rs if r["mae"] is not None]))
            lines.append(f"{b:>10} n={len(rs):5d} tp={tp:4d} sl={sl:4d} tp%={tp/len(rs)*100:5.1f} sl%={sl/len(rs)*100:5.1f} avg_mfe={avg_mfe:+.3f}% avg_mae={avg_mae:+.3f}%")

    # Rule search. LONG TP style.
    candidates = []
    pcs = [0.2, 0.3, 0.5, 0.7]
    vols = [5, 8, 12, 20]
    scores = [2, 3, 4, 5]
    trends = [-0.5, 0, 0.5, 1.5]
    ois = [-3, -1, 0, 1]
    structs = [2, 4, 6]
    brisks = [2, 4, 6]
    fbs = [1, 2, 3]

    for pc in pcs:
        for vol in vols:
            for score in scores:
                for trend in trends:
                    for oi in ois:
                        for struct in structs:
                            for brisk in brisks:
                                for fb in fbs:
                                    desc = f"LONG pc>={pc} vol>={vol} score>={score} trend>={trend} oi>={oi} struct<={struct} brisk<={brisk} fb<={fb}"
                                    res = score_rule(norm, lambda r, pc=pc, vol=vol, score=score, trend=trend, oi=oi, struct=struct, brisk=brisk, fb=fb:
                                                     (r["pc"] is not None and r["pc"] >= pc) and
                                                     (r["vol"] is not None and r["vol"] >= vol) and
                                                     (r["score"] is not None and r["score"] >= score) and
                                                     (r["trend"] is None or r["trend"] >= trend) and
                                                     (r["oi"] is None or r["oi"] >= oi) and
                                                     (r["struct"] is None or r["struct"] <= struct) and
                                                     (r["brisk"] is None or r["brisk"] <= brisk) and
                                                     (r["fb"] is None or r["fb"] <= fb))
                                    if res:
                                        candidates.append((res["utility"], desc, res))

    candidates.sort(reverse=True, key=lambda x: x[0])

    lines.append("")
    lines.append("=" * 120)
    lines.append("TOP LONG FEATURE RULES BY CRUDE UTILITY")
    lines.append("=" * 120)
    for util, desc, res in candidates[:80]:
        lines.append(f"{desc} | n={res['n']} tp={res['tp']} sl={res['sl']} neutral={res['neutral']} tp%={res['tp_rate']*100:.1f} sl%={res['sl_rate']*100:.1f} util={res['utility']:+.2f} avg_mfe={res['avg_mfe']:+.3f}% avg_mae={res['avg_mae']:+.3f}%")

    out_path.write_text("\n".join(lines))
    print(out_path)
    print("\n".join(lines[:260]))


if __name__ == "__main__":
    main()
