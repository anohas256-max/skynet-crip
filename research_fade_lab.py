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
        return {"n": 0, "sum": 0.0, "avg": 0.0, "wr": 0.0, "pf": 0.0, "best": 0.0, "worst": 0.0}
    s = sum(vals)
    return {
        "n": n,
        "sum": s,
        "avg": s / n,
        "wr": sum(1 for v in vals if v > 0) / n * 100,
        "pf": pf(vals),
        "best": max(vals),
        "worst": min(vals),
    }

def connect():
    if not DB.exists():
        raise SystemExit(f"NO DB: {DB}")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con

def load_rows():
    con = connect()
    rows = con.execute("""
        SELECT
            ts,
            clean_symbol,
            spread_bps,
            current_turnover_rank,
            price_change,
            vol_ratio,
            oi_change,
            imb_5,
            wall_skew,
            max_up_5m,
            max_down_5m,
            close_5m,
            long_net_5m,
            short_net_5m
        FROM signals
        WHERE long_net_5m IS NOT NULL
          AND short_net_5m IS NOT NULL
        ORDER BY ts ASC
    """).fetchall()
    con.close()
    return [dict(r) for r in rows]

def row_net(r, side):
    return f(r["long_net_5m"] if side == "LONG" else r["short_net_5m"])

def side_line(rows, side):
    vals = [row_net(r, side) for r in rows]
    s = stat(vals)
    return (
        f"{side:5s} n={s['n']:4d} sum={money(s['sum']):>8s} avg={money(s['avg']):>8s} "
        f"wr={s['wr']:5.1f}% pf={s['pf']:.2f} best={money(s['best'])} worst={money(s['worst'])}"
    )

def sym_line(rows, side):
    by = {}
    for r in rows:
        sym = r.get("clean_symbol") or "?"
        by.setdefault(sym, []).append(row_net(r, side))
    items = []
    for sym, vals in by.items():
        s = stat(vals)
        items.append((s["sum"], sym, s["n"], s["avg"], s["pf"]))
    best = sorted(items, reverse=True)[:8]
    worst = sorted(items)[:8]
    return best, worst

def make_rule_parts():
    return {
        "spread": [
            ("SP2", lambda r: f(r["spread_bps"]) <= 2),
            ("SP3", lambda r: f(r["spread_bps"]) <= 3),
            ("SP5", lambda r: f(r["spread_bps"]) <= 5),
            ("SP7", lambda r: f(r["spread_bps"]) <= 7),
            ("SP12", lambda r: f(r["spread_bps"]) <= 12),
        ],
        "rank": [
            ("R40", lambda r: f(r["current_turnover_rank"]) <= 40),
            ("R80", lambda r: f(r["current_turnover_rank"]) <= 80),
            ("R150", lambda r: f(r["current_turnover_rank"]) <= 150),
        ],
        "pc": [
            ("PC_POS", lambda r: f(r["price_change"]) > 0),
            ("PC_NEG", lambda r: f(r["price_change"]) < 0),
            ("ABS030", lambda r: abs(f(r["price_change"])) >= 0.30),
            ("ABS050", lambda r: abs(f(r["price_change"])) >= 0.50),
            ("ABS070", lambda r: abs(f(r["price_change"])) >= 0.70),
        ],
        "vol": [
            ("V5", lambda r: f(r["vol_ratio"]) >= 5),
            ("V8", lambda r: f(r["vol_ratio"]) >= 8),
            ("V12", lambda r: f(r["vol_ratio"]) >= 12),
        ],
        "oi": [
            ("OI_ANY", lambda r: True),
            ("OI_POS", lambda r: f(r["oi_change"]) > 0),
            ("OI_NEG", lambda r: f(r["oi_change"]) < 0),
            ("OI_BIG_POS", lambda r: f(r["oi_change"]) >= 2),
            ("OI_BIG_NEG", lambda r: f(r["oi_change"]) <= -2),
        ],
        "imb": [
            ("IMB_ANY", lambda r: True),
            ("IMB_BID", lambda r: f(r["imb_5"]) > 0.2),
            ("IMB_ASK", lambda r: f(r["imb_5"]) < -0.2),
        ],
        "wall": [
            ("WALL_ANY", lambda r: True),
            ("WALL_POS", lambda r: f(r["wall_skew"]) > 0),
            ("WALL_NEG", lambda r: f(r["wall_skew"]) < 0),
        ],
    }

def apply_parts(rows, parts):
    out = []
    for r in rows:
        ok = True
        for _, fn in parts:
            if not fn(r):
                ok = False
                break
        if ok:
            out.append(r)
    return out

def evaluate_rule(name, parts, train, test, min_train, min_test):
    train_rows = apply_parts(train, parts)
    test_rows = apply_parts(test, parts)

    if len(train_rows) < min_train or len(test_rows) < min_test:
        return []

    res = []
    for side in ("LONG", "SHORT"):
        tr = stat([row_net(r, side) for r in train_rows])
        te = stat([row_net(r, side) for r in test_rows])
        al = stat([row_net(r, side) for r in train_rows + test_rows])

        robust = (
            tr["sum"] > 0
            and te["sum"] > 0
            and tr["pf"] >= 1.05
            and te["pf"] >= 1.05
            and al["avg"] > 0
        )

        score = te["sum"] * 2.0 + tr["sum"] * 0.5 + min(te["n"], 100) * 0.01 - abs(tr["avg"] - te["avg"]) * 5.0

        res.append({
            "name": name,
            "side": side,
            "train": tr,
            "test": te,
            "all": al,
            "robust": robust,
            "score": score,
            "test_rows": test_rows,
        })
    return res

def build_candidates(parts):
    rules = []

    # 1-part and 2-part broad rules
    groups = ["spread", "rank", "pc", "vol", "oi", "imb", "wall"]

    for g in groups:
        for name, fn in parts[g]:
            rules.append((name, [(name, fn)]))

    # core 4-part rules: pc + spread + rank + vol
    for pc in parts["pc"]:
        for sp in parts["spread"]:
            for rk in parts["rank"]:
                for vol in parts["vol"]:
                    names = [pc[0], sp[0], rk[0], vol[0]]
                    rules.append(("|".join(names), [pc, sp, rk, vol]))

                    # add one micro condition at a time, not all combinations
                    for oi in parts["oi"][1:]:
                        rules.append(("|".join(names + [oi[0]]), [pc, sp, rk, vol, oi]))
                    for imb in parts["imb"][1:]:
                        rules.append(("|".join(names + [imb[0]]), [pc, sp, rk, vol, imb]))
                    for wall in parts["wall"][1:]:
                        rules.append(("|".join(names + [wall[0]]), [pc, sp, rk, vol, wall]))

    # specific hypotheses from previous logs
    hypotheses = [
        ["PC_NEG", "SP3", "R150", "V8", "OI_POS", "IMB_ASK"],
        ["PC_NEG", "SP3", "R150", "V8", "OI_POS"],
        ["PC_NEG", "SP7", "R150", "V8", "OI_POS"],
        ["PC_POS", "SP3", "R80", "V8", "OI_POS"],
        ["PC_POS", "SP7", "R80", "V8", "OI_POS"],
        ["ABS070", "SP12", "R150", "V8"],
        ["ABS050", "SP7", "R80", "V8"],
    ]

    index = {}
    for g in parts.values():
        for item in g:
            index[item[0]] = item

    for names in hypotheses:
        available = [index[n] for n in names if n in index]
        if len(available) == len(names):
            rules.append(("HYP|" + "|".join(names), available))

    # dedupe
    seen = set()
    out = []
    for name, rule_parts in rules:
        if name in seen:
            continue
        seen.add(name)
        out.append((name, rule_parts))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-train", type=int, default=35)
    ap.add_argument("--min-test", type=int, default=12)
    ap.add_argument("--top", type=int, default=80)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    rows = load_rows()
    split_i = int(len(rows) * 0.70)
    train = rows[:split_i]
    test = rows[split_i:]

    parts = make_rule_parts()
    rules = build_candidates(parts)

    results = []
    for name, rule_parts in rules:
        results.extend(evaluate_rule(name, rule_parts, train, test, args.min_train, args.min_test))

    robust = [r for r in results if r["robust"]]

    lines = []
    lines.append("=" * 100)
    lines.append(f"SKYNET RESEARCH FADE LAB FAST UTC={ts()}")
    lines.append("=" * 100)
    lines.append(f"DB={DB}")
    lines.append(f"rows_total={len(rows)} train={len(train)} test={len(test)} split=70/30 chronological")
    lines.append(f"rules_checked={len(rules)} results={len(results)} min_train={args.min_train} min_test={args.min_test}")
    lines.append("")
    lines.append("GLOBAL:")
    lines.append("  " + side_line(rows, "LONG"))
    lines.append("  " + side_line(rows, "SHORT"))
    lines.append("")
    lines.append("TRAIN:")
    lines.append("  " + side_line(train, "LONG"))
    lines.append("  " + side_line(train, "SHORT"))
    lines.append("")
    lines.append("TEST:")
    lines.append("  " + side_line(test, "LONG"))
    lines.append("  " + side_line(test, "SHORT"))

    lines.append("")
    lines.append("=" * 100)
    lines.append("ROBUST RULES: train positive + test positive + PF>=1.05")
    lines.append("=" * 100)

    if not robust:
        lines.append("[EMPTY] Нет устойчивых правил по строгому train/test. Edge пока не доказан.")
    else:
        for r in sorted(robust, key=lambda x: x["score"], reverse=True)[:args.top]:
            tr, te, al = r["train"], r["test"], r["all"]
            lines.append(
                f"{r['side']:5s} {r['name']:55s} "
                f"ALL n={al['n']:4d} sum={money(al['sum']):>8s} avg={money(al['avg']):>8s} wr={al['wr']:5.1f}% pf={al['pf']:.2f} | "
                f"TR n={tr['n']:4d} sum={money(tr['sum']):>8s} avg={money(tr['avg']):>8s} pf={tr['pf']:.2f} | "
                f"TE n={te['n']:4d} sum={money(te['sum']):>8s} avg={money(te['avg']):>8s} pf={te['pf']:.2f}"
            )
            best, worst = sym_line(r["test_rows"], r["side"])
            lines.append(f"      test_best_symbols ={[(s, round(sm, 3), n) for sm, s, n, avg, pfv in best]}")
            lines.append(f"      test_worst_symbols={[(s, round(sm, 3), n) for sm, s, n, avg, pfv in worst]}")

    lines.append("")
    lines.append("=" * 100)
    lines.append("TOP TEST RULES")
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
    lines.append("DECISION")
    lines.append("=" * 100)
    lines.append("If ROBUST RULES is empty: do not add fade strategy yet.")
    lines.append("If robust SHORT exists: next step is shadow-only track, not real.")
    lines.append("If only TOP TEST is green but TRAIN is red: it is likely regime/noise.")

    text = "\n".join(lines) + "\n"

    if args.stdout:
        print(text)
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"research_fade_lab_fast_{ts()}.txt"
    out.write_text(text, encoding="utf-8", errors="ignore")
    print(out)

if __name__ == "__main__":
    main()
