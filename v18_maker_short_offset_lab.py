#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "v18_maker_short_offset_lab_latest.txt"


def q(x, d=0.0):
    try:
        if x is None:
            return d
        return float(x)
    except Exception:
        return d


def load_rows():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    rows = con.execute("""
        SELECT
            id,
            clean_symbol,
            price_change,
            vol_ratio,
            oi_change,
            rank,
            spread_bps,
            bid5_usd,
            ask5_usd,
            imb_5,
            imb_20,
            wall_skew,
            max_up,
            max_down,
            close_pct
        FROM signals
        WHERE closed = 1
          AND max_up IS NOT NULL
          AND max_down IS NOT NULL
          AND close_pct IS NOT NULL
        ORDER BY id
    """).fetchall()

    con.close()
    return [dict(r) for r in rows]


def split_train_test(rows):
    cut = int(len(rows) * 0.70)
    return rows[:cut], rows[cut:]


def base_filter(r):
    # Не пытаемся “умничать” слишком рано.
    # Берём основу самой прибыльной cost-гипотезы:
    # SHORT после сильного движения, дальше maker-limit выше текущей цены.
    return True


def signal_filter(r):
    # Более реалистичный short fade trigger:
    # цена уже сделала >= +1% импульс, есть хоть какая-то ликвидность,
    # не берём совсем дикий spread.
    return (
        q(r["price_change"]) >= 1.0
        and q(r["vol_ratio"]) >= 5.0
        and q(r["spread_bps"], 999) <= 15.0
        and q(r["rank"], 999) <= 150
    )


def signal_filter_strict(r):
    return (
        q(r["price_change"]) >= 1.0
        and q(r["vol_ratio"]) >= 8.0
        and q(r["spread_bps"], 999) <= 8.0
        and q(r["rank"], 999) <= 80
    )


def signal_filter_wall_neg(r):
    return (
        q(r["price_change"]) >= 1.0
        and q(r["vol_ratio"]) >= 5.0
        and q(r["spread_bps"], 999) <= 15.0
        and q(r["rank"], 999) <= 150
        and q(r["wall_skew"]) < -0.10
    )


FILTERS = [
    ("ALL_ROWS_COST_PROOF", base_filter),
    ("FADE_POS_PC1_VOL5_SP15_R150", signal_filter),
    ("FADE_POS_PC1_VOL8_SP8_R80", signal_filter_strict),
    ("FADE_POS_PC1_VOL5_SP15_R150_WALL_NEG", signal_filter_wall_neg),
]


def sim(rows, pred, offset, tp=3.0, sl=0.3, cost=0.03):
    selected = [r for r in rows if pred(r)]
    n_signal = len(selected)

    filled = []
    missed = 0

    for r in selected:
        max_up = q(r["max_up"])
        max_down = q(r["max_down"])
        close_pct = q(r["close_pct"])

        # SHORT maker-limit выше текущей цены.
        # Fill считается, если цена после сигнала поднималась хотя бы на offset.
        if max_up < offset:
            missed += 1
            continue

        # После fill entry лучше на +offset%.
        # Для short:
        # TP 3% от limit-entry примерно требует max_down <= -(tp - offset)
        # SL 0.3% от limit-entry примерно требует max_up >= offset + sl
        hit_tp = max_down <= -(tp - offset)
        hit_sl = max_up >= (offset + sl)

        # Conservative: если TP и SL достижимы, считаем SL.
        if hit_tp and hit_sl:
            gross = -sl
            reason = "BOTH_AS_SL"
        elif hit_sl:
            gross = -sl
            reason = "SL"
        elif hit_tp:
            gross = tp
            reason = "TP"
        else:
            # close_pct относительно market-entry.
            # Для short от limit-entry добавляем улучшение offset.
            gross = -close_pct + offset
            reason = "TIME"

        net = gross - cost

        filled.append({
            "net": net,
            "gross": gross,
            "reason": reason,
            "symbol": r["clean_symbol"],
            "pc": q(r["price_change"]),
            "vol": q(r["vol_ratio"]),
            "spread": q(r["spread_bps"], 999),
            "rank": q(r["rank"], 999),
            "max_up": max_up,
            "max_down": max_down,
            "close_pct": close_pct,
        })

    if not filled:
        return {
            "signals": n_signal,
            "filled": 0,
            "missed": missed,
            "fill_rate": 0.0,
            "sum": 0.0,
            "avg": 0.0,
            "pos": 0.0,
            "tp": 0,
            "sl": 0,
            "both": 0,
            "time": 0,
            "best": [],
            "worst": [],
        }

    nets = [x["net"] for x in filled]

    return {
        "signals": n_signal,
        "filled": len(filled),
        "missed": missed,
        "fill_rate": len(filled) / n_signal if n_signal else 0.0,
        "sum": sum(nets),
        "avg": sum(nets) / len(nets),
        "pos": sum(1 for x in nets if x > 0) / len(nets),
        "tp": sum(1 for x in filled if x["reason"] == "TP"),
        "sl": sum(1 for x in filled if x["reason"] == "SL"),
        "both": sum(1 for x in filled if x["reason"] == "BOTH_AS_SL"),
        "time": sum(1 for x in filled if x["reason"] == "TIME"),
        "best": sorted(filled, key=lambda x: x["net"], reverse=True)[:5],
        "worst": sorted(filled, key=lambda x: x["net"])[:5],
    }


def fmt(r):
    return (
        f"signals={r['signals']} filled={r['filled']} missed={r['missed']} "
        f"fill%={r['fill_rate']*100:.1f} sum={r['sum']:+.2f}% "
        f"avg={r['avg']:+.4f}% pos={r['pos']*100:.1f}% "
        f"tp={r['tp']} sl={r['sl']} both={r['both']} time={r['time']}"
    )


def mini_rows(xs):
    out = []
    for x in xs:
        out.append(
            f"{x['symbol']} net={x['net']:+.3f}% reason={x['reason']} "
            f"pc={x['pc']:+.2f}% vol={x['vol']:.1f} sp={x['spread']:.2f} "
            f"rank={x['rank']:.0f} up={x['max_up']:+.2f}% down={x['max_down']:+.2f}% close={x['close_pct']:+.2f}%"
        )
    return out


def main():
    rows = load_rows()
    train, test = split_train_test(rows)

    offsets = [0.03, 0.05, 0.08, 0.10, 0.15, 0.20]
    costs = [0.03, 0.01, 0.00]

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

    lines = []
    lines.append("=" * 120)
    lines.append(f"V18 MAKER SHORT OFFSET LAB UTC={ts}")
    lines.append("=" * 120)
    lines.append("Goal: test most profitable hypothesis: maker-only SHORT TP=3.0 SL=0.3.")
    lines.append("Diagnostics only. Real trading OFF.")
    lines.append("Conservative model: if TP and SL both reachable after fill, SL wins.")
    lines.append("Fill model: SHORT limit is placed above signal price by offset%; fill if max_up >= offset.")
    lines.append(f"rows={len(rows)} train={len(train)} test={len(test)}")
    lines.append("")

    all_results = []

    for cost in costs:
        lines.append("")
        lines.append("=" * 120)
        lines.append(f"EXEC_COST={cost:.2f}%")
        lines.append("=" * 120)

        for fname, pred in FILTERS:
            lines.append("")
            lines.append(f"--- FILTER: {fname} ---")

            for off in offsets:
                a = sim(rows, pred, off, cost=cost)
                tr = sim(train, pred, off, cost=cost)
                te = sim(test, pred, off, cost=cost)

                robust = (
                    tr["filled"] >= 30
                    and te["filled"] >= 10
                    and tr["sum"] > 0
                    and te["sum"] > 0
                    and a["avg"] > 0
                )

                all_results.append((robust, a["avg"], a["sum"], cost, fname, off, a, tr, te))

                lines.append(f"{'[ROBUST]' if robust else '[weak]'} offset={off:.2f}%")
                lines.append(f"  ALL   {fmt(a)}")
                lines.append(f"  TRAIN {fmt(tr)}")
                lines.append(f"  TEST  {fmt(te)}")

    all_results.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)

    lines.append("")
    lines.append("=" * 120)
    lines.append("BEST MAKER SHORT CONFIGS")
    lines.append("=" * 120)

    for robust, avg, total, cost, fname, off, a, tr, te in all_results[:40]:
        lines.append("")
        lines.append(f"{'[ROBUST]' if robust else '[weak]'} cost={cost:.2f}% filter={fname} offset={off:.2f}%")
        lines.append(f"  ALL   {fmt(a)}")
        lines.append(f"  TRAIN {fmt(tr)}")
        lines.append(f"  TEST  {fmt(te)}")
        lines.append("  BEST:")
        lines.extend("    " + s for s in mini_rows(a["best"]))
        lines.append("  WORST:")
        lines.extend("    " + s for s in mini_rows(a["worst"]))

    text = "\n".join(lines)
    OUT.write_text(text)
    print(OUT)
    print(text[:30000])


if __name__ == "__main__":
    main()
