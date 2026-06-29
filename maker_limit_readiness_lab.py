#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "maker_limit_readiness_latest.txt"

# stricter than previous broad maker lab:
# we want configs that survive train/test AND still have enough trades
PC_MIN_LIST = [0.7, 1.0, 1.3]
VOL_MIN_LIST = [8, 12, 20]
SPREAD_MAX_LIST = [3, 5, 8]
RANK_MAX_LIST = [20, 40, 80]
OFFSET_LIST = [0.05, 0.08, 0.10, 0.15, 0.20]
TP_LIST = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
SL_LIST = [0.3, 0.4, 0.5, 0.7, 1.0]

# cost percent per roundtrip.
# 0.03 is optimistic maker-like; 0.05 adds bad fill / cancel / occasional taker pain.
COSTS = [0.03, 0.05, 0.08]

MIN_ALL = 80
MIN_TRAIN = 50
MIN_TEST = 25

def f(x, d=0.0):
    try:
        return float(x)
    except Exception:
        return d

def get_col(row, names, default=0.0):
    for n in names:
        if n in row.keys():
            return f(row[n], default)
    return default

def split_rows(rows):
    n = len(rows)
    cut = int(n * 0.70)
    return rows[:cut], rows[cut:]

def eval_config(rows, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, cost):
    vals = []
    examples_best = []
    examples_worst = []

    for r in rows:
        pc = abs(get_col(r, ["price_change_pct", "pc", "ret1", "abs_pc"]))
        vol = get_col(r, ["volume_ratio", "vol_ratio", "vol"])
        spread = get_col(r, ["spread_bps", "spread"])
        rank = get_col(r, ["rank", "turnover_rank", "rank_abs_ret1"], 999)

        if pc < pc_min:
            continue
        if vol < vol_min:
            continue
        if spread > spread_max:
            continue
        if rank > rank_max:
            continue

        # For maker SHORT:
        # fill if price first/ever goes up enough to touch limit above signal.
        max_up = get_col(r, ["max_up_pct", "max_up", "mfe_up_pct"])
        max_down = get_col(r, ["max_down_pct", "max_down", "mae_down_pct"])

        # Some DBs store down as negative, some as positive magnitude.
        if max_down > 0:
            down_mag = max_down
        else:
            down_mag = abs(max_down)

        if max_up < offset:
            continue

        # After fill, conservative:
        # if both TP/down and SL/up reachable, SL wins.
        # Short entry is offset above signal, so effective TP needs down from signal enough:
        # rough conservative approximation: down_mag >= tp - offset.
        tp_hit = down_mag >= max(0.0, tp - offset)
        sl_hit = max_up >= offset + sl

        if sl_hit:
            net = -sl - cost
            reason = "SL"
        elif tp_hit:
            net = tp - cost
            reason = "TP"
        else:
            # close approximation: prefer actual close move if present
            close_pct = get_col(r, ["close_pct", "close_move_pct", "future_close_pct"], 0.0)
            # for short, positive close_pct is bad, negative is good.
            gross = -close_pct + offset
            net = gross - cost
            reason = "TIME"

        vals.append(net)
        sym = str(r["symbol"]) if "symbol" in r.keys() else "?"
        ex = (net, sym, reason, pc, vol, spread, rank, max_up, max_down)
        examples_best.append(ex)
        examples_worst.append(ex)

    if not vals:
        return None

    s = sum(vals)
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    pf = pos / neg if neg > 0 else 999 if pos > 0 else 0
    wr = sum(v > 0 for v in vals) / len(vals) * 100
    avg = s / len(vals)

    examples_best = sorted(examples_best, reverse=True)[:5]
    examples_worst = sorted(examples_worst)[:5]

    return {
        "n": len(vals),
        "sum": s,
        "avg": avg,
        "wr": wr,
        "pf": pf,
        "best": examples_best,
        "worst": examples_worst,
    }

def fmt(st):
    if not st:
        return "n=0"
    return f"n={st['n']:4d} sum={st['sum']:+8.2f}% avg={st['avg']:+7.4f}% wr={st['wr']:5.1f}% pf={st['pf']:6.2f}"

def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    rows = con.execute("SELECT * FROM signals ORDER BY id").fetchall()
    con.close()

    train, test = split_rows(rows)

    results = []

    for pc_min in PC_MIN_LIST:
        for vol_min in VOL_MIN_LIST:
            for spread_max in SPREAD_MAX_LIST:
                for rank_max in RANK_MAX_LIST:
                    for offset in OFFSET_LIST:
                        for tp in TP_LIST:
                            for sl in SL_LIST:
                                if tp <= sl:
                                    continue
                                for cost in COSTS:
                                    all_st = eval_config(rows, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, cost)
                                    tr_st = eval_config(train, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, cost)
                                    te_st = eval_config(test, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, cost)

                                    if not all_st or not tr_st or not te_st:
                                        continue
                                    if all_st["n"] < MIN_ALL or tr_st["n"] < MIN_TRAIN or te_st["n"] < MIN_TEST:
                                        continue

                                    robust = (
                                        all_st["sum"] > 0 and tr_st["sum"] > 0 and te_st["sum"] > 0
                                        and all_st["avg"] > 0.02
                                        and tr_st["avg"] > 0.01
                                        and te_st["avg"] > 0.005
                                        and all_st["pf"] > 1.05
                                        and te_st["pf"] > 1.01
                                    )

                                    score = all_st["sum"] + tr_st["sum"] * 0.5 + te_st["sum"] * 2.0 + all_st["pf"] * 5
                                    results.append((robust, score, cost, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, all_st, tr_st, te_st))

    results.sort(key=lambda x: (x[0], x[1]), reverse=True)

    lines = []
    lines.append("=" * 120)
    lines.append(f"MAKER LIMIT READINESS LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 120)
    lines.append(f"db={DB}")
    lines.append(f"rows={len(rows)} train={len(train)} test={len(test)}")
    lines.append("Goal: validate maker/limit SHORT readiness with stricter train/test and extra-cost assumptions.")
    lines.append("Real remains OFF.")
    lines.append("")
    lines.append("ROBUST CONFIGS")
    robust_count = 0

    for item in results:
        robust, score, cost, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, all_st, tr_st, te_st = item
        if not robust:
            continue
        robust_count += 1
        lines.append("")
        lines.append(
            f"[ROBUST] score={score:.2f} cost={cost:.2f}% "
            f"pc>={pc_min} vol>={vol_min} spread<={spread_max} rank<={rank_max} "
            f"offset={offset}% TP={tp}% SL={sl}%"
        )
        lines.append("  ALL   " + fmt(all_st))
        lines.append("  TRAIN " + fmt(tr_st))
        lines.append("  TEST  " + fmt(te_st))
        lines.append("  BEST examples:")
        for ex in all_st["best"]:
            net, sym, reason, pc, vol, spread, rank, up, down = ex
            lines.append(f"    {sym:<12} net={net:+.3f}% {reason:<4} pc={pc:.2f} vol={vol:.1f} sp={spread:.2f} rank={rank:.0f} up={up:+.2f} down={down:+.2f}")
        lines.append("  WORST examples:")
        for ex in all_st["worst"]:
            net, sym, reason, pc, vol, spread, rank, up, down = ex
            lines.append(f"    {sym:<12} net={net:+.3f}% {reason:<4} pc={pc:.2f} vol={vol:.1f} sp={spread:.2f} rank={rank:.0f} up={up:+.2f} down={down:+.2f}")

        if robust_count >= 30:
            break

    if robust_count == 0:
        lines.append("NO ROBUST CONFIGS UNDER STRICT READINESS GATE.")

    lines.append("")
    lines.append("TOP WEAK CONFIGS")
    for item in results[:30]:
        robust, score, cost, pc_min, vol_min, spread_max, rank_max, offset, tp, sl, all_st, tr_st, te_st = item
        tag = "ROBUST" if robust else "weak"
        lines.append("")
        lines.append(
            f"[{tag}] score={score:.2f} cost={cost:.2f}% "
            f"pc>={pc_min} vol>={vol_min} spread<={spread_max} rank<={rank_max} "
            f"offset={offset}% TP={tp}% SL={sl}%"
        )
        lines.append("  ALL   " + fmt(all_st))
        lines.append("  TRAIN " + fmt(tr_st))
        lines.append("  TEST  " + fmt(te_st))

    lines.append("")
    lines.append("=" * 120)
    lines.append("DECISION")
    lines.append("=" * 120)
    if robust_count:
        lines.append("Maker/limit SHORT has strict robust candidates. Next step: build live shadow lane with post-only simulation, fill wait, cancel/requote, and per-symbol cooldown.")
        lines.append("Still not real yet: first verify live shadow fill/miss/close behavior.")
    else:
        lines.append("No strict maker/limit candidate. Do not build real. Keep recorder and pivot to better external/catalyst/orderbook source.")

    OUT.write_text("\n".join(lines))
    print("\n".join(lines))

if __name__ == "__main__":
    main()
