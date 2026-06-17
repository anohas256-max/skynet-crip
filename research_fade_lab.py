#!/usr/bin/env python3
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DATA = ROOT / "data"
OUT_DIR = ROOT / "safe_exports" / "research_reports"

DB = DATA / "v17_microstructure.sqlite3"

def ts():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

def f(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
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
    n = len(vals)
    if not n:
        return {
            "n": 0,
            "sum": 0.0,
            "avg": 0.0,
            "wr": 0.0,
            "pf": 0.0,
            "best": 0.0,
            "worst": 0.0,
        }
    return {
        "n": n,
        "sum": sum(vals),
        "avg": sum(vals) / n,
        "wr": sum(1 for v in vals if v > 0) / n * 100,
        "pf": pf(vals),
        "best": max(vals),
        "worst": min(vals),
    }

def connect():
    if not DB.exists():
        raise SystemExit(f"NO DB: {DB}")
    uri = f"file:{DB}?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con

def load_rows():
    con = connect()
    rows = con.execute("""
        SELECT *
        FROM signals
        WHERE long_net_5m IS NOT NULL
          AND short_net_5m IS NOT NULL
        ORDER BY ts ASC
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]

def val(row, k):
    return f(row.get(k))

def make_rules():
    spread_rules = [
        ("SP2", lambda r: val(r, "spread_bps") <= 2),
        ("SP3", lambda r: val(r, "spread_bps") <= 3),
        ("SP5", lambda r: val(r, "spread_bps") <= 5),
        ("SP7", lambda r: val(r, "spread_bps") <= 7),
        ("SP12", lambda r: val(r, "spread_bps") <= 12),
    ]

    rank_rules = [
        ("R40", lambda r: val(r, "current_turnover_rank") <= 40),
        ("R80", lambda r: val(r, "current_turnover_rank") <= 80),
        ("R150", lambda r: val(r, "current_turnover_rank") <= 150),
    ]

    pc_rules = [
        ("PC_POS", lambda r: val(r, "price_change") > 0),
        ("PC_NEG", lambda r: val(r, "price_change") < 0),
        ("ABS030", lambda r: abs(val(r, "price_change")) >= 0.30),
        ("ABS050", lambda r: abs(val(r, "price_change")) >= 0.50),
        ("ABS070", lambda r: abs(val(r, "price_change")) >= 0.70),
        ("SMALL030", lambda r: abs(val(r, "price_change")) < 0.30),
    ]

    vol_rules = [
        ("V3", lambda r: val(r, "vol_ratio") >= 3),
        ("V5", lambda r: val(r, "vol_ratio") >= 5),
        ("V8", lambda r: val(r, "vol_ratio") >= 8),
        ("V12", lambda r: val(r, "vol_ratio") >= 12),
    ]

    oi_rules = [
        ("OI_ANY", lambda r: True),
        ("OI_POS", lambda r: val(r, "oi_change") > 0),
        ("OI_NEG", lambda r: val(r, "oi_change") < 0),
        ("OI_BIG_POS", lambda r: val(r, "oi_change") >= 2),
        ("OI_BIG_NEG", lambda r: val(r, "oi_change") <= -2),
    ]

    imb_rules = [
        ("IMB_ANY", lambda r: True),
        ("IMB_BID", lambda r: val(r, "imb_5") > 0.2),
        ("IMB_ASK", lambda r: val(r, "imb_5") < -0.2),
    ]

    wall_rules = [
        ("WALL_ANY", lambda r: True),
        ("WALL_POS", lambda r: val(r, "wall_skew") > 0),
        ("WALL_NEG", lambda r: val(r, "wall_skew") < 0),
    ]

    rules = []

    for spn, spf in spread_rules:
        for rn, rf in rank_rules:
            for pcn, pcf in pc_rules:
                for vn, vf in vol_rules:
                    for oin, oif in oi_rules:
                        for imbn, imbf in imb_rules:
                            for wn, wf in wall_rules:
                                name = "|".join([pcn, spn, rn, vn, oin, imbn, wn])
                                funcs = [spf, rf, pcf, vf, oif, imbf, wf]
                                rules.append((name, funcs))

    return rules

def apply_rule(rows, funcs):
    out = []
    for r in rows:
        ok = True
        for fn in funcs:
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

def row_net(row, side):
    if side == "LONG":
        return f(row.get("long_net_5m"))
    return f(row.get("short_net_5m"))

def symbol_stats(rows, side):
    by = {}
    for r in rows:
        sym = r.get("clean_symbol") or r.get("symbol") or "?"
        by.setdefault(sym, []).append(row_net(r, side))

    items = []
    for sym, vals in by.items():
        s = stat(vals)
        items.append((s["sum"], sym, s))

    best = sorted(items, reverse=True)[:8]
    worst = sorted(items)[:8]
    return best, worst

def render_side_summary(rows, side):
    vals = [row_net(r, side) for r in rows]
    s = stat(vals)
    return (
        f"{side:5s} n={s['n']:4d} sum={money(s['sum']):>8s} avg={money(s['avg']):>8s} "
        f"wr={s['wr']:5.1f}% pf={s['pf']:.2f} best={money(s['best'])} worst={money(s['worst'])}"
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-train", type=int, default=40)
    ap.add_argument("--min-test", type=int, default=15)
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    rows = load_rows()
    if not rows:
        raise SystemExit("NO CLOSED V17 ROWS")

    split_i = int(len(rows) * 0.70)
    train = rows[:split_i]
    test = rows[split_i:]

    lines = []
    lines.append("=" * 100)
    lines.append(f"SKYNET RESEARCH FADE LAB UTC={ts()}")
    lines.append("=" * 100)
    lines.append("")
    lines.append(f"DB={DB}")
    lines.append(f"rows_total={len(rows)} train={len(train)} test={len(test)} split=70/30 chronological")
    lines.append("")
    lines.append("GLOBAL:")
    lines.append("  " + render_side_summary(rows, "LONG"))
    lines.append("  " + render_side_summary(rows, "SHORT"))
    lines.append("")
    lines.append("TRAIN:")
    lines.append("  " + render_side_summary(train, "LONG"))
    lines.append("  " + render_side_summary(train, "SHORT"))
    lines.append("")
    lines.append("TEST:")
    lines.append("  " + render_side_summary(test, "LONG"))
    lines.append("  " + render_side_summary(test, "SHORT"))
    lines.append("")

    results = []
    rules = make_rules()

    for name, funcs in rules:
        train_rows = apply_rule(train, funcs)
        test_rows = apply_rule(test, funcs)

        if len(train_rows) < args.min_train or len(test_rows) < args.min_test:
            continue

        for side in ["LONG", "SHORT"]:
            tr_vals = [row_net(r, side) for r in train_rows]
            te_vals = [row_net(r, side) for r in test_rows]
            all_vals = [row_net(r, side) for r in train_rows + test_rows]

            tr = stat(tr_vals)
            te = stat(te_vals)
            al = stat(all_vals)

            robust = (
                tr["sum"] > 0
                and te["sum"] > 0
                and tr["pf"] >= 1.05
                and te["pf"] >= 1.05
                and al["avg"] > 0
            )

            # score punishes tiny test and unstable splits
            score = (
                te["sum"] * 2.0
                + tr["sum"] * 0.5
                + min(te["n"], 80) * 0.01
                - abs(tr["avg"] - te["avg"]) * 5.0
            )

            results.append({
                "robust": robust,
                "score": score,
                "side": side,
                "name": name,
                "train_rows": train_rows,
                "test_rows": test_rows,
                "train": tr,
                "test": te,
                "all": al,
            })

    robust = [r for r in results if r["robust"]]
    lines.append("=" * 100)
    lines.append("ROBUST RULES: train positive + test positive + PF>=1.05")
    lines.append("=" * 100)

    if not robust:
        lines.append("[EMPTY] Нет устойчивых правил по строгому train/test. Это важный вывод: edge пока не доказан.")
    else:
        for r in sorted(robust, key=lambda x: x["score"], reverse=True)[:args.top]:
            tr, te, al = r["train"], r["test"], r["all"]
            lines.append(
                f"{r['side']:5s} {r['name']:55s} "
                f"ALL n={al['n']:4d} sum={money(al['sum']):>8s} avg={money(al['avg']):>8s} wr={al['wr']:5.1f}% pf={al['pf']:.2f} | "
                f"TR n={tr['n']:4d} sum={money(tr['sum']):>8s} avg={money(tr['avg']):>8s} pf={tr['pf']:.2f} | "
                f"TE n={te['n']:4d} sum={money(te['sum']):>8s} avg={money(te['avg']):>8s} pf={te['pf']:.2f}"
            )
            best, worst = symbol_stats(r["test_rows"], r["side"])
            lines.append(f"      test_best_symbols ={[(s, round(st['sum'], 3), st['n']) for _, s, st in best]}")
            lines.append(f"      test_worst_symbols={[(s, round(st['sum'], 3), st['n']) for _, s, st in worst]}")

    lines.append("")
    lines.append("=" * 100)
    lines.append("TOP TEST RULES, EVEN IF TRAIN NOT ROBUST")
    lines.append("=" * 100)

    for r in sorted(results, key=lambda x: x["test"]["sum"], reverse=True)[:args.top]:
        tr, te, al = r["train"], r["test"], r["all"]
        lines.append(
            f"{r['side']:5s} {r['name']:55s} "
            f"TE n={te['n']:4d} sum={money(te['sum']):>8s} avg={money(te['avg']):>8s} wr={te['wr']:5.1f}% pf={te['pf']:.2f} | "
            f"TR n={tr['n']:4d} sum={money(tr['sum']):>8s} avg={money(tr['avg']):>8s} pf={tr['pf']:.2f} | "
            f"ALL sum={money(al['sum']):>8s} avg={money(al['avg']):>8s}"
        )

    lines.append("")
    lines.append("=" * 100)
    lines.append("INTERPRETATION")
    lines.append("=" * 100)
    lines.append("1. Если ROBUST RULES пустой — real нельзя даже обсуждать.")
    lines.append("2. Если robust есть только SHORT — это research-only fade, не live.")
    lines.append("3. Если train плюс, test минус — это переобучение.")
    lines.append("4. Следующий шаг после этого отчета: добавить лучший robust-rule как shadow-only track, а не real.")

    text = "\n".join(lines) + "\n"

    if args.stdout:
        print(text)
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"research_fade_lab_{ts()}.txt"
    out.write_text(text, encoding="utf-8", errors="ignore")
    print(out)

if __name__ == "__main__":
    main()
