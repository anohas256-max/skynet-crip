#!/usr/bin/env python3

import math
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "v18_stage2_walkforward_latest.txt"

NOTIONAL = 12.0
TTL_SECONDS = 300

BASE_BLACKLIST = {"ALLO", "XPL"}
CURRENT_BLACKLIST = {
    "ALLO", "BREV", "KORU", "LIT", "M", "PENDLE",
    "RIF", "SKYAI", "SOXL", "TAC", "XPL",
}

# Текущий профиль и ближайшие альтернативы.
BASES = [
    ("STAGE2",                    0.30, 0.80, 15.0, 2.0, 30),
    ("STAGE2_SP15",               0.30, 0.80, 15.0, 1.5, 30),
    ("STAGE2_R20",                0.30, 0.80, 15.0, 2.0, 20),

    ("PC030_050_VOL15_R30",       0.30, 0.50, 15.0, 2.0, 30),
    ("PC050_080_VOL15_R30",       0.50, 0.80, 15.0, 2.0, 30),

    ("PC030_080_VOL20_R30",       0.30, 0.80, 20.0, 2.0, 30),
    ("PC030_050_VOL20_R50",       0.30, 0.50, 20.0, 2.0, 50),
    ("PC030_050_VOL12_SP15_R50",  0.30, 0.50, 12.0, 1.5, 50),

    ("PC030_120_VOL12_R30",       0.30, 1.20, 12.0, 2.0, 30),
    ("PC030_INF_VOL12_R30",       0.30, 999.0, 12.0, 2.0, 30),
    ("PC050_080_VOL20_R50",       0.50, 0.80, 20.0, 2.0, 50),
]

TPS = [0.5, 0.8, 1.0, 3.0]
SLS = [0.3, 0.4, 0.5]

BLACKLISTS = [
    ("BASE", BASE_BLACKLIST),
    ("CURRENT", CURRENT_BLACKLIST),
]

AUTO_BANS = [0, 1]

COST_BASE = 0.03
COST_STRESS = 0.06


def fnum(value, default=None):
    try:
        if value is None:
            return default
        result = float(value)
        if not math.isfinite(result):
            return default
        return result
    except Exception:
        return default


def parse_ts(value):
    if value is None:
        return None

    text = str(value).strip()
    text = text.replace(" UTC", "").replace("Z", "+00:00")

    try:
        result = datetime.fromisoformat(text)
        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)
        return result.astimezone(timezone.utc)
    except Exception:
        return None


def profit_factor(values):
    positive = sum(x for x in values if x > 0)
    negative = -sum(x for x in values if x < 0)

    if negative == 0:
        return 999.0 if positive > 0 else 0.0

    return positive / negative


def summarize(values, reasons, symbol_net, skipped_busy, skipped_ban):
    if not values:
        return {
            "n": 0,
            "net": 0.0,
            "avg": 0.0,
            "wr": 0.0,
            "pf": 0.0,
            "sl": 0,
            "tp": 0,
            "time": 0,
            "conc": 0.0,
            "skipped_busy": skipped_busy,
            "skipped_ban": skipped_ban,
        }

    positive_by_symbol = [
        max(value, 0.0)
        for value in symbol_net.values()
    ]
    total_positive = sum(positive_by_symbol)

    concentration = (
        max(positive_by_symbol) / total_positive
        if positive_by_symbol and total_positive > 0
        else 0.0
    )

    return {
        "n": len(values),
        "net": sum(values),
        "avg": sum(values) / len(values),
        "wr": 100.0 * sum(1 for x in values if x > 0) / len(values),
        "pf": profit_factor(values),
        "sl": reasons["SL"],
        "tp": reasons["TP"],
        "time": reasons["TIME"],
        "conc": concentration,
        "skipped_busy": skipped_busy,
        "skipped_ban": skipped_ban,
    }


def path_outcome(row, tp, sl, cost):
    max_up = fnum(row["max_up"])
    max_down = fnum(row["max_down"])
    close_pct = fnum(row["close_pct"])

    if max_up is None or max_down is None or close_pct is None:
        return None

    # Для SHORT рост цены — плохо.
    # Если внутри пути были задеты обе границы, считаем SL первым:
    # это консервативный сценарий без красивого подглядывания.
    if max_up >= sl:
        return -sl - cost, "SL"

    if abs(max_down) >= tp:
        return tp - cost, "TP"

    return -close_pct - cost, "TIME"


def passes(row, cfg):
    pc = fnum(row["price_change"], -999.0)
    vol = fnum(row["vol_ratio"], -999.0)
    spread = fnum(row["spread_bps"], 999999.0)
    rank = fnum(row["rank"], 999999.0)

    return (
        cfg["pc_min"] <= pc <= cfg["pc_max"]
        and vol >= cfg["vol_min"]
        and spread <= cfg["spread_max"]
        and rank <= cfg["rank_max"]
    )


def simulate(rows, cfg, cost):
    banned_symbols = set()
    symbol_sl = defaultdict(int)

    # При max_open=1 следующую принятую сделку не открываем
    # раньше окончания 300-секундного окна предыдущей.
    busy_until = None

    values = []
    reasons = defaultdict(int)
    symbol_net = defaultdict(float)

    skipped_busy = 0
    skipped_ban = 0

    for row in rows:
        symbol = str(row["clean_symbol"] or "")
        symbol = symbol.replace("_USDT", "").upper()

        if not symbol:
            continue

        if symbol in cfg["blacklist"]:
            continue

        if cfg["auto_ban"] > 0 and symbol in banned_symbols:
            skipped_ban += 1
            continue

        if not passes(row, cfg):
            continue

        ts = row["_ts"]

        if busy_until is not None and ts is not None and ts < busy_until:
            skipped_busy += 1
            continue

        result = path_outcome(
            row,
            tp=cfg["tp"],
            sl=cfg["sl"],
            cost=cost,
        )

        if result is None:
            continue

        net, reason = result

        values.append(net)
        reasons[reason] += 1
        symbol_net[symbol] += net

        if reason == "SL" and cfg["auto_ban"] > 0:
            symbol_sl[symbol] += 1

            if symbol_sl[symbol] >= cfg["auto_ban"]:
                banned_symbols.add(symbol)

        if ts is not None:
            busy_until = ts + timedelta(seconds=TTL_SECONDS)

    return summarize(
        values,
        reasons,
        symbol_net,
        skipped_busy,
        skipped_ban,
    )


def fmt_stats(stats):
    dollars = stats["net"] * NOTIONAL / 100.0

    return (
        f"n={stats['n']:4d} "
        f"net={stats['net']:+8.3f}% (${dollars:+.3f}) "
        f"avg={stats['avg']:+7.4f}% "
        f"WR={stats['wr']:5.1f}% "
        f"PF={stats['pf']:6.2f} "
        f"SL={stats['sl']:3d} "
        f"TP={stats['tp']:3d} "
        f"TIME={stats['time']:3d} "
        f"conc={stats['conc']:5.1%} "
        f"busy_skip={stats['skipped_busy']:3d} "
        f"ban_skip={stats['skipped_ban']:3d}"
    )


def cfg_name(cfg):
    return (
        f"{cfg['base_name']}"
        f"|BL={cfg['bl_name']}"
        f"|BAN={cfg['auto_ban']}"
        f"|TP={cfg['tp']:.1f}"
        f"|SL={cfg['sl']:.1f}"
    )


def build_configs():
    configs = []

    for (
        base_name,
        pc_min,
        pc_max,
        vol_min,
        spread_max,
        rank_max,
    ) in BASES:

        for bl_name, blacklist in BLACKLISTS:
            for auto_ban in AUTO_BANS:
                for tp in TPS:
                    for sl in SLS:
                        configs.append({
                            "base_name": base_name,
                            "pc_min": pc_min,
                            "pc_max": pc_max,
                            "vol_min": vol_min,
                            "spread_max": spread_max,
                            "rank_max": rank_max,
                            "bl_name": bl_name,
                            "blacklist": blacklist,
                            "auto_ban": auto_ban,
                            "tp": tp,
                            "sl": sl,
                        })

    return configs


def main():
    if not DB.exists():
        raise SystemExit(f"missing DB: {DB}")

    con = sqlite3.connect(
        f"file:{DB}?mode=ro",
        uri=True,
        timeout=30,
    )
    con.row_factory = sqlite3.Row

    columns = {
        row[1]
        for row in con.execute(
            "PRAGMA table_info(signals)"
        ).fetchall()
    }

    required = {
        "id",
        "time_iso",
        "clean_symbol",
        "price_change",
        "vol_ratio",
        "spread_bps",
        "rank",
        "max_up",
        "max_down",
        "close_pct",
    }

    missing = sorted(required - columns)

    if missing:
        raise SystemExit(
            f"missing signals columns: {missing}"
        )

    raw_rows = con.execute("""
        SELECT
            id,
            time_iso,
            clean_symbol,
            price_change,
            vol_ratio,
            spread_bps,
            rank,
            max_up,
            max_down,
            close_pct
        FROM signals
        WHERE max_up IS NOT NULL
          AND max_down IS NOT NULL
          AND close_pct IS NOT NULL
        ORDER BY id ASC
    """).fetchall()

    con.close()

    rows = []

    for raw in raw_rows:
        row = dict(raw)
        row["_ts"] = parse_ts(row.get("time_iso"))
        rows.append(row)

    total_rows = len(rows)

    if total_rows < 40:
        raise SystemExit(
            f"not enough path rows: {total_rows}"
        )

    cuts = [
        0,
        total_rows // 4,
        total_rows // 2,
        (3 * total_rows) // 4,
        total_rows,
    ]

    folds = [
        rows[cuts[i]:cuts[i + 1]]
        for i in range(4)
    ]

    train_rows = rows[:cuts[3]]
    test_rows = rows[cuts[3]:]

    configs = build_configs()

    evaluated = []
    current_exact = None

    for cfg in configs:
        train = simulate(
            train_rows,
            cfg,
            COST_BASE,
        )

        train_folds = [
            simulate(fold, cfg, COST_BASE)
            for fold in folds[:3]
        ]

        positive_train_folds = sum(
            1
            for stats in train_folds
            if stats["n"] > 0 and stats["net"] > 0
        )

        worst_train_net = min(
            (
                stats["net"]
                for stats in train_folds
                if stats["n"] > 0
            ),
            default=-999.0,
        )

        score = (
            train["avg"] * 100.0
            + min(train["pf"], 5.0) * 2.0
            + positive_train_folds * 2.0
            - train["conc"] * 5.0
            + max(worst_train_net, -3.0) * 0.2
        )

        item = {
            "cfg": cfg,
            "train": train,
            "train_folds": train_folds,
            "positive_train_folds": positive_train_folds,
            "score": score,
        }

        evaluated.append(item)

        if (
            cfg["base_name"] == "STAGE2"
            and cfg["bl_name"] == "CURRENT"
            and cfg["auto_ban"] == 1
            and abs(cfg["tp"] - 3.0) < 1e-9
            and abs(cfg["sl"] - 0.3) < 1e-9
        ):
            current_exact = item

    # Отбор кандидатов выполняется ТОЛЬКО на первых 75%.
    train_eligible = [
        item
        for item in evaluated
        if item["train"]["n"] >= 30
        and item["train"]["net"] > 0
        and item["train"]["pf"] >= 1.15
        and item["positive_train_folds"] >= 2
        and item["train"]["conc"] <= 0.60
    ]

    shortlist = sorted(
        train_eligible,
        key=lambda item: item["score"],
        reverse=True,
    )[:25]

    # Только после фиксации shortlist открываем последние 25%.
    for item in shortlist:
        cfg = item["cfg"]

        item["test"] = simulate(
            test_rows,
            cfg,
            COST_BASE,
        )

        item["all"] = simulate(
            rows,
            cfg,
            COST_BASE,
        )

        item["stress"] = simulate(
            rows,
            cfg,
            COST_STRESS,
        )

        item["all_folds"] = [
            simulate(fold, cfg, COST_BASE)
            for fold in folds
        ]

        item["positive_folds"] = sum(
            1
            for stats in item["all_folds"]
            if stats["n"] > 0 and stats["net"] > 0
        )

        test = item["test"]

        item["holdout_pass"] = (
            test["n"] >= 8
            and test["net"] > 0
            and test["avg"] > 0
            and test["pf"] >= 1.15
            and item["stress"]["net"] > 0
            and item["positive_folds"] >= 3
        )

    lines = []

    lines.append("=" * 140)
    lines.append(
        "V18 STAGE2 CHRONOLOGICAL WALK-FORWARD LAB "
        f"UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}"
    )
    lines.append("=" * 140)

    lines.append(f"DB={DB}")
    lines.append(
        f"rows_with_path={total_rows} "
        f"train_75={len(train_rows)} "
        f"untouched_test_25={len(test_rows)} "
        f"configs={len(configs)}"
    )
    lines.append(
        f"row_time_first={rows[0].get('time_iso')} "
        f"row_time_last={rows[-1].get('time_iso')}"
    )
    lines.append(
        "Model: SHORT path simulation, conservative SL-first, "
        "300s max-open occupancy, optional first-SL symbol ban."
    )
    lines.append(
        f"Base cost={COST_BASE:.2f}% per roundtrip; "
        f"stress cost={COST_STRESS:.2f}%; "
        f"notional=${NOTIONAL:.2f}."
    )
    lines.append(
        "Selection uses only first 75%; "
        "last 25% remains untouched until shortlist is fixed."
    )
    lines.append(
        "This is path replay, not exact tick/order execution."
    )

    lines.append("")
    lines.append("=" * 140)
    lines.append("CURRENT ACTIVE STAGE2 — HISTORICAL CHECK")
    lines.append("=" * 140)

    if current_exact is None:
        lines.append("CURRENT CONFIG NOT FOUND")
    else:
        cfg = current_exact["cfg"]

        current_train = current_exact["train"]
        current_test = simulate(
            test_rows,
            cfg,
            COST_BASE,
        )
        current_all = simulate(
            rows,
            cfg,
            COST_BASE,
        )
        current_stress = simulate(
            rows,
            cfg,
            COST_STRESS,
        )
        current_folds = [
            simulate(fold, cfg, COST_BASE)
            for fold in folds
        ]

        lines.append(cfg_name(cfg))
        lines.append("TRAIN75 " + fmt_stats(current_train))
        lines.append("TEST25  " + fmt_stats(current_test))
        lines.append("ALL     " + fmt_stats(current_all))
        lines.append("STRESS  " + fmt_stats(current_stress))

        for index, stats in enumerate(current_folds, 1):
            lines.append(
                f"FOLD{index}   " + fmt_stats(stats)
            )

    lines.append("")
    lines.append("=" * 140)
    lines.append("TRAIN SHORTLIST → UNTOUCHED HOLDOUT")
    lines.append("=" * 140)

    if not shortlist:
        lines.append(
            "NO TRAIN-ROBUST CANDIDATE: "
            "no config met train n>=30, net>0, PF>=1.15, "
            "at least 2/3 positive train folds and concentration<=60%."
        )
    else:
        for index, item in enumerate(shortlist, 1):
            flag = (
                "HOLDOUT_PASS"
                if item["holdout_pass"]
                else "FAIL"
            )

            lines.append(
                f"#{index:02d} {flag} "
                f"score={item['score']:+.3f} "
                f"{cfg_name(item['cfg'])}"
            )

            lines.append(
                "  TRAIN75 " + fmt_stats(item["train"])
            )
            lines.append(
                "  TEST25  " + fmt_stats(item["test"])
            )
            lines.append(
                "  ALL     " + fmt_stats(item["all"])
            )
            lines.append(
                "  STRESS  " + fmt_stats(item["stress"])
            )

            fold_text = []

            for fold_index, stats in enumerate(
                item["all_folds"],
                1,
            ):
                fold_text.append(
                    f"F{fold_index}:"
                    f"n={stats['n']} "
                    f"net={stats['net']:+.2f}% "
                    f"PF={stats['pf']:.2f}"
                )

            lines.append(
                "  FOLDS   " + " | ".join(fold_text)
            )

    holdout_passes = [
        item
        for item in shortlist
        if item["holdout_pass"]
    ]

    lines.append("")
    lines.append("=" * 140)
    lines.append("DECISION")
    lines.append("=" * 140)

    if not holdout_passes:
        lines.append(
            "NO_HOLDOUT_PASS: "
            "do not waste days waiting for this static fade grid. "
            "Keep real OFF and pivot to another execution/feature lane."
        )
    else:
        lines.append(
            f"HOLDOUT_PASSES={len(holdout_passes)}. "
            "Do not auto-enable real and do not auto-apply from this lab."
        )
        lines.append(
            "Run the top survivors as parallel shadow lanes "
            "with exact execution-cost validation."
        )

        for item in holdout_passes[:5]:
            lines.append(
                "SURVIVOR "
                + cfg_name(item["cfg"])
                + " | TEST "
                + fmt_stats(item["test"])
                + " | STRESS "
                + fmt_stats(item["stress"])
            )

    lines.append("REAL_TRADING=OFF.")

    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
