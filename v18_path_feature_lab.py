#!/usr/bin/env python3
import sqlite3
import statistics
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "v18_path_feature_lab_latest.txt"


def q(x, d=0.0):
    try:
        if x is None:
            return d
        return float(x)
    except Exception:
        return d


def bucket(v, cuts):
    for c in cuts:
        if v < c:
            return f"<{c}"
    return f">={cuts[-1]}"


def load():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    rows = con.execute("""
        SELECT
            id, time_iso, clean_symbol, entry_price,
            price_change, vol_ratio, oi_change, rank, spread_bps,
            bid5_usd, ask5_usd, bid20_usd, ask20_usd,
            imb_5, imb_20, wall_skew,
            max_up, max_down, close_pct
        FROM signals
        WHERE closed = 1
          AND max_up IS NOT NULL
          AND max_down IS NOT NULL
    """).fetchall()

    con.close()
    return [dict(r) for r in rows]


def split_train_test(rows):
    rows = sorted(rows, key=lambda r: r["id"])
    cut = int(len(rows) * 0.70)
    return rows[:cut], rows[cut:]


def eval_side(rows, side, pred):
    sub = [r for r in rows if pred(r)]
    if not sub:
        return None

    if side == "LONG":
        tp = [r for r in sub if q(r["max_up"]) >= 0.80]
        sl = [r for r in sub if q(r["max_down"]) <= -0.50]
        # примерная net-модель: TP +0.8%, SL -0.5%, TIME close_pct, комиссия/проскальз ~0.29%
        nets = []
        for r in sub:
            if q(r["max_up"]) >= 0.80:
                gross = 0.80
            elif q(r["max_down"]) <= -0.50:
                gross = -0.50
            else:
                gross = q(r["close_pct"])
            nets.append(gross - 0.29)
    else:
        tp = [r for r in sub if q(r["max_down"]) <= -0.80]
        sl = [r for r in sub if q(r["max_up"]) >= 0.50]
        nets = []
        for r in sub:
            if q(r["max_down"]) <= -0.80:
                gross = 0.80
            elif q(r["max_up"]) >= 0.50:
                gross = -0.50
            else:
                gross = -q(r["close_pct"])
            nets.append(gross - 0.29)

    wins = [x for x in nets if x > 0]
    losses = [x for x in nets if x <= 0]
    pf = sum(wins) / abs(sum(losses)) if losses and abs(sum(losses)) > 1e-9 else 999.0

    return {
        "n": len(sub),
        "tp": len(tp),
        "sl": len(sl),
        "time": len(sub) - len(tp) - len(sl),
        "sum": sum(nets),
        "avg": sum(nets) / len(nets),
        "pf": pf,
        "tp_rate": len(tp) / len(sub),
        "sl_rate": len(sl) / len(sub),
        "avg_max_up": statistics.mean([q(r["max_up"]) for r in sub]),
        "avg_max_down": statistics.mean([q(r["max_down"]) for r in sub]),
    }


def fmt_res(r):
    if not r:
        return "None"
    return (
        f"n={r['n']} tp={r['tp']} sl={r['sl']} time={r['time']} "
        f"sum={r['sum']:+.2f}% avg={r['avg']:+.3f}% pf={r['pf']:.2f} "
        f"tp%={r['tp_rate']*100:.1f} sl%={r['sl_rate']*100:.1f} "
        f"avg_up={r['avg_max_up']:+.3f}% avg_down={r['avg_max_down']:+.3f}%"
    )


def add_bucket_report(lines, rows, side):
    lines.append("")
    lines.append("=" * 120)
    lines.append(f"{side} BUCKET QUALITY")
    lines.append("=" * 120)

    specs = [
        ("abs_pc", lambda r: abs(q(r["price_change"])), [0.2, 0.3, 0.5, 0.7, 1.0]),
        ("pc", lambda r: q(r["price_change"]), [-1.0, -0.7, -0.5, -0.3, -0.2, 0.2, 0.3, 0.5, 0.7, 1.0]),
        ("vol", lambda r: q(r["vol_ratio"]), [5, 8, 12, 20, 40]),
        ("oi", lambda r: q(r["oi_change"]), [-5, -2, -1, 0, 1, 2, 5]),
        ("rank", lambda r: q(r["rank"], 999), [10, 20, 40, 80, 150]),
        ("spread", lambda r: q(r["spread_bps"], 999), [1, 3, 5, 8, 15, 999]),
        ("imb5", lambda r: q(r["imb_5"]), [-0.5, -0.2, 0, 0.2, 0.5]),
        ("imb20", lambda r: q(r["imb_20"]), [-0.5, -0.2, 0, 0.2, 0.5]),
        ("wall_skew", lambda r: q(r["wall_skew"]), [-0.5, -0.2, 0, 0.2, 0.5]),
        ("bid5", lambda r: q(r["bid5_usd"]), [100, 300, 700, 1500, 3000]),
        ("ask5", lambda r: q(r["ask5_usd"]), [100, 300, 700, 1500, 3000]),
    ]

    for name, getter, cuts in specs:
        groups = {}
        for r in rows:
            b = bucket(getter(r), cuts)
            groups.setdefault(b, []).append(r)

        lines.append("")
        lines.append(f"--- {name} ---")
        for b, rs in sorted(groups.items(), key=lambda x: x[0]):
            if len(rs) < 50:
                continue
            res = eval_side(rs, side, lambda r: True)
            lines.append(f"{b:>8} | {fmt_res(res)}")


def rule_search(rows, side):
    candidates = []

    abs_pcs = [0.2, 0.3, 0.5, 0.7, 1.0]
    vols = [3, 5, 8, 12, 20]
    spreads = [3, 5, 8, 15, 999]
    ranks = [20, 40, 80, 150, 999]
    oi_mins = [-999, -5, -2, -1, 0, 1]
    oi_maxs = [999, 5, 2, 1, 0, -1]
    imb_rules = [
        ("ANY", lambda r: True),
        ("IMB5_POS", lambda r: q(r["imb_5"]) > 0.10),
        ("IMB5_NEG", lambda r: q(r["imb_5"]) < -0.10),
        ("IMB20_POS", lambda r: q(r["imb_20"]) > 0.10),
        ("IMB20_NEG", lambda r: q(r["imb_20"]) < -0.10),
        ("WALL_POS", lambda r: q(r["wall_skew"]) > 0.10),
        ("WALL_NEG", lambda r: q(r["wall_skew"]) < -0.10),
    ]

    for abs_pc in abs_pcs:
        for vol in vols:
            for spread in spreads:
                for rank in ranks:
                    if side == "LONG":
                        # long только положительный импульс
                        pc_pred = lambda r, abs_pc=abs_pc: q(r["price_change"]) >= abs_pc
                        oi_grid = oi_mins
                    else:
                        # short/fade: тестируем и отрицательный импульс, и fade positive impulse
                        pc_modes = [
                            ("SHORT_NEG", lambda r, abs_pc=abs_pc: q(r["price_change"]) <= -abs_pc),
                            ("FADE_POS", lambda r, abs_pc=abs_pc: q(r["price_change"]) >= abs_pc),
                        ]
                        oi_grid = oi_maxs

                    if side == "LONG":
                        pc_modes = [("LONG_POS", pc_pred)]

                    for pc_name, pc_pred2 in pc_modes:
                        for oi_cut in oi_grid:
                            for imb_name, imb_pred in imb_rules:
                                if side == "LONG":
                                    desc = f"{side} {pc_name}|abs_pc>={abs_pc}|vol>={vol}|spread<={spread}|rank<={rank}|oi>={oi_cut}|{imb_name}"
                                    pred = lambda r, pc_pred2=pc_pred2, vol=vol, spread=spread, rank=rank, oi_cut=oi_cut, imb_pred=imb_pred: (
                                        pc_pred2(r)
                                        and q(r["vol_ratio"]) >= vol
                                        and q(r["spread_bps"], 999) <= spread
                                        and q(r["rank"], 999) <= rank
                                        and q(r["oi_change"]) >= oi_cut
                                        and imb_pred(r)
                                    )
                                else:
                                    desc = f"{side} {pc_name}|abs_pc>={abs_pc}|vol>={vol}|spread<={spread}|rank<={rank}|oi<={oi_cut}|{imb_name}"
                                    pred = lambda r, pc_pred2=pc_pred2, vol=vol, spread=spread, rank=rank, oi_cut=oi_cut, imb_pred=imb_pred: (
                                        pc_pred2(r)
                                        and q(r["vol_ratio"]) >= vol
                                        and q(r["spread_bps"], 999) <= spread
                                        and q(r["rank"], 999) <= rank
                                        and q(r["oi_change"]) <= oi_cut
                                        and imb_pred(r)
                                    )

                                all_res = eval_side(rows, side, pred)
                                if not all_res or all_res["n"] < 30:
                                    continue

                                train, test = split_train_test([r for r in rows if pred(r)])
                                if len(train) < 20 or len(test) < 8:
                                    continue

                                train_res = eval_side(train, side, lambda r: True)
                                test_res = eval_side(test, side, lambda r: True)

                                if not train_res or not test_res:
                                    continue

                                # Не просто top-test: нужно, чтобы оба периода были не труп.
                                robust = (
                                    train_res["sum"] > 0
                                    and test_res["sum"] > 0
                                    and train_res["pf"] >= 1.05
                                    and test_res["pf"] >= 1.05
                                    and all_res["avg"] > 0.02
                                )

                                score = (
                                    all_res["sum"]
                                    + min(train_res["sum"], test_res["sum"]) * 2
                                    + all_res["n"] * 0.002
                                )

                                candidates.append((robust, score, desc, all_res, train_res, test_res))

    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return candidates


def main():
    rows = load()
    train, test = split_train_test(rows)

    lines = []
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

    lines.append("=" * 120)
    lines.append(f"V18 PATH FEATURE LAB UTC={ts}")
    lines.append("=" * 120)
    lines.append("Uses exact V18 columns: max_up, max_down, close_pct. Diagnostics only. Real trading OFF.")
    lines.append(f"db={DB}")
    lines.append(f"rows={len(rows)} train={len(train)} test={len(test)}")
    lines.append("Net model: TP/SL/TIME percent minus 0.29% execution cost estimate.")
    lines.append("LONG: TP if max_up>=0.80, SL if max_down<=-0.50")
    lines.append("SHORT: TP if max_down<=-0.80, SL if max_up>=0.50")

    lines.append("")
    lines.append("=== BASELINE ===")
    for side in ["LONG", "SHORT"]:
        lines.append(f"{side} ALL:   {fmt_res(eval_side(rows, side, lambda r: True))}")
        lines.append(f"{side} TRAIN: {fmt_res(eval_side(train, side, lambda r: True))}")
        lines.append(f"{side} TEST:  {fmt_res(eval_side(test, side, lambda r: True))}")

    add_bucket_report(lines, rows, "LONG")
    add_bucket_report(lines, rows, "SHORT")

    for side in ["LONG", "SHORT"]:
        lines.append("")
        lines.append("=" * 120)
        lines.append(f"TOP {side} ROBUST RULES")
        lines.append("=" * 120)

        cands = rule_search(rows, side)
        robust = [c for c in cands if c[0]]

        if not robust:
            lines.append("NO ROBUST TRAIN+TEST RULES FOUND")
        else:
            for _, score, desc, all_res, train_res, test_res in robust[:80]:
                lines.append(desc)
                lines.append(f"  ALL   {fmt_res(all_res)}")
                lines.append(f"  TRAIN {fmt_res(train_res)}")
                lines.append(f"  TEST  {fmt_res(test_res)}")

        lines.append("")
        lines.append(f"TOP {side} BY SCORE, INCLUDING NON-ROBUST")
        for robust_flag, score, desc, all_res, train_res, test_res in cands[:40]:
            lines.append(f"{'[ROBUST]' if robust_flag else '[weak]'} {desc}")
            lines.append(f"  ALL   {fmt_res(all_res)}")
            lines.append(f"  TRAIN {fmt_res(train_res)}")
            lines.append(f"  TEST  {fmt_res(test_res)}")

    text = "\n".join(lines)
    OUT.write_text(text)
    print(text[:20000])
    print("")
    print(f"RESULT_FILE={OUT}")


if __name__ == "__main__":
    main()
