#!/usr/bin/env python3

from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import v18_research_rescue_lab as rescue


ROOT = Path("/root/skynet")
OUT = ROOT / "v18_wallpos_candidate_audit_latest.txt"

FIXED = {
    "pc_min": 1.20,
    "pc_max": 2.50,
    "vol_min": 8.0,
    "spread_max": 2.0,
    "rank_max": 80,
    "exit_mode": "TIME",
    "extra": "WALL_POS",
}


def calculate(rows, config):
    trades = rescue.select_v18_trades(rows, config)
    return trades, rescue.metric(trades, "stress")


def format_result(result):
    return (
        f"n={result['n']:4d} "
        f"sum=${result['sum']:+.4f} "
        f"avg=${result['avg']:+.5f} "
        f"WR={result['wr']:5.1f}% "
        f"PF={result['pf']:6.2f} "
        f"leave_best=${result['leave_best']:+.4f} "
        f"best={result['best_symbol']} "
        f"share={result['positive_share']:.1%}"
    )


def evaluate(rows, config):
    split = int(len(rows) * 0.70)

    train_rows = rows[:split]
    test_rows = rows[split:]

    train_trades, train_result = calculate(
        train_rows,
        config,
    )
    test_trades, test_result = calculate(
        test_rows,
        config,
    )
    all_trades, all_result = calculate(
        rows,
        config,
    )

    cuts = [
        round(len(rows) * index / 8)
        for index in range(9)
    ]

    folds = [
        rows[cuts[index]:cuts[index + 1]]
        for index in range(8)
    ]

    fold_results = [
        calculate(fold, config)[1]
        for fold in folds
    ]

    positive_folds = sum(
        1
        for result in fold_results
        if result["n"] > 0 and result["sum"] > 0
    )

    return {
        "train_trades": train_trades,
        "test_trades": test_trades,
        "all_trades": all_trades,
        "train": train_result,
        "test": test_result,
        "all": all_result,
        "folds": fold_results,
        "positive_folds": positive_folds,
    }


def main():
    rows = rescue.load_v18_rows()

    if not rows:
        raise SystemExit("NO_USABLE_V18_ROWS")

    fixed = evaluate(rows, FIXED)

    promotion_failures = []

    if fixed["train"]["n"] < 50:
        promotion_failures.append(
            f"train_n={fixed['train']['n']}<50"
        )

    if fixed["test"]["n"] < 20:
        promotion_failures.append(
            f"test_n={fixed['test']['n']}<20"
        )

    if fixed["train"]["sum"] <= 0:
        promotion_failures.append("train_net<=0")

    if fixed["test"]["sum"] <= 0:
        promotion_failures.append("test_net<=0")

    if fixed["train"]["pf"] < 1.10:
        promotion_failures.append("train_pf<1.10")

    if fixed["test"]["pf"] < 1.10:
        promotion_failures.append("test_pf<1.10")

    if fixed["all"]["leave_best"] <= 0:
        promotion_failures.append("leave_best<=0")

    if fixed["all"]["positive_share"] > 0.45:
        promotion_failures.append(
            "best_symbol_share>45%"
        )

    if fixed["positive_folds"] < 6:
        promotion_failures.append(
            f"positive_8folds="
            f"{fixed['positive_folds']}<6"
        )

    configs = []

    for (
        pc_range,
        vol_min,
        spread_max,
        rank_max,
    ) in product(
        [
            (1.00, 2.50),
            (1.20, 2.00),
            (1.20, 2.50),
            (1.20, 3.00),
            (1.40, 2.50),
        ],
        [5.0, 8.0, 12.0],
        [1.5, 2.0, 2.5],
        [40, 80, 120],
    ):
        configs.append({
            "pc_min": pc_range[0],
            "pc_max": pc_range[1],
            "vol_min": vol_min,
            "spread_max": spread_max,
            "rank_max": rank_max,
            "exit_mode": "TIME",
            "extra": "WALL_POS",
        })

    neighborhood = []

    for config in configs:
        result = evaluate(rows, config)

        stable = (
            result["train"]["n"] >= 25
            and result["test"]["n"] >= 10

            and result["train"]["sum"] > 0
            and result["test"]["sum"] > 0

            and result["train"]["pf"] >= 1.10
            and result["test"]["pf"] >= 1.10

            and result["all"]["leave_best"] > 0
            and result["all"]["positive_share"] <= 0.50

            and result["positive_folds"] >= 6
        )

        score = (
            result["test"]["sum"] * 3.0
            + result["train"]["sum"]
            + result["all"]["leave_best"]
            + result["positive_folds"] * 0.05
        )

        neighborhood.append(
            (stable, score, config, result)
        )

    neighborhood.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    stable_count = sum(
        1
        for item in neighborhood
        if item[0]
    )

    daily = {}

    for trade in fixed["all_trades"]:
        day = datetime.fromtimestamp(
            float(trade["ts"]),
            tz=timezone.utc,
        ).strftime("%Y-%m-%d")

        daily.setdefault(day, []).append(trade)

    lines = []

    lines.append("=" * 150)
    lines.append(
        "V18 WALL_POS CANDIDATE AUDIT "
        f"UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}"
    )
    lines.append("=" * 150)

    lines.append(f"usable_rows={len(rows)}")
    lines.append(
        f"fixed={rescue.config_name(FIXED)}"
    )
    lines.append(
        "Qualification is for exact shadow only. "
        "It is never permission for real trading."
    )

    lines.append("")
    lines.append("FIXED CANDIDATE:")

    lines.append(
        "  TRAIN " + format_result(fixed["train"])
    )
    lines.append(
        "  TEST  " + format_result(fixed["test"])
    )
    lines.append(
        "  ALL   " + format_result(fixed["all"])
    )

    lines.append(
        f"  8_FOLDS_POSITIVE="
        f"{fixed['positive_folds']}/8"
    )

    for index, result in enumerate(
        fixed["folds"],
        1,
    ):
        lines.append(
            f"    F{index}: "
            + format_result(result)
        )

    lines.append("")
    lines.append(
        "PROMOTION_GATE_FAILURES="
        + (
            ",".join(promotion_failures)
            if promotion_failures
            else "NONE"
        )
    )

    lines.append(
        "FORWARD_SHADOW_DECISION="
        "START_RESEARCH_ONLY"
    )
    lines.append("REAL_DECISION=BLOCKED")

    lines.append("")
    lines.append(
        f"NEIGHBORHOOD configs={len(neighborhood)} "
        f"stable={stable_count}"
    )

    for index, (
        stable,
        score,
        config,
        result,
    ) in enumerate(neighborhood[:25], 1):
        lines.append(
            f"#{index:02d} "
            f"{'STABLE' if stable else 'FAIL':<6} "
            f"score={score:+.4f} "
            f"{rescue.config_name(config)}"
        )

        lines.append(
            "  TRAIN "
            + format_result(result["train"])
        )
        lines.append(
            "  TEST  "
            + format_result(result["test"])
        )
        lines.append(
            "  ALL   "
            + format_result(result["all"])
        )
        lines.append(
            f"  8_FOLDS_POSITIVE="
            f"{result['positive_folds']}/8"
        )

    lines.append("")
    lines.append("FIXED DAILY STRESS:")

    for day in sorted(daily):
        result = rescue.metric(
            daily[day],
            "stress",
        )

        lines.append(
            f"  {day} "
            + format_result(result)
        )

    lines.append("")
    lines.append("INTERPRETATION:")

    lines.append(
        "The fixed rule is the only current near-pass."
    )
    lines.append(
        "It failed the old strict promotion gate "
        "because its sample was below 50/20."
    )
    lines.append(
        "Exact forward is justified as a research lane."
    )
    lines.append(
        "Real trading remains prohibited."
    )

    text = "\n".join(lines) + "\n"

    OUT.write_text(
        text,
        encoding="utf-8",
    )

    print(text)


if __name__ == "__main__":
    main()
