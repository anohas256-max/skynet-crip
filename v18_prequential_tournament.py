#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import v18_research_rescue_lab as rescue


ROOT = Path("/root/skynet")

REPORT = ROOT / "v18_prequential_tournament_latest.txt"
JSON_REPORT = ROOT / "v18_prequential_tournament_latest.json"

NOTIONAL = 12.0
STRESS_COST_PCT = 0.26
HARD_COST_PCT = 0.36

MIN_TRAIN_DAYS = 10
ROLLING_DAYS = 14


def utc_day(timestamp: float) -> str:
    return datetime.fromtimestamp(
        timestamp,
        timezone.utc,
    ).strftime("%Y-%m-%d")


def profit_factor(values: list[float]) -> float:
    positive = sum(
        value
        for value in values
        if value > 0
    )

    negative = -sum(
        value
        for value in values
        if value < 0
    )

    if negative <= 0:
        return 999.0 if positive > 0 else 0.0

    return positive / negative


def metric(
    trades: list[dict[str, Any]],
    value_key: str,
) -> dict[str, Any]:
    values = [
        float(trade[value_key])
        for trade in trades
    ]

    if not values:
        return {
            "n": 0,
            "sum": 0.0,
            "avg": 0.0,
            "median": 0.0,
            "wr": 0.0,
            "pf": 0.0,
            "symbols": 0,
            "leave_best": 0.0,
            "best_symbol": "-",
            "positive_share": 0.0,
        }

    by_symbol: dict[str, float] = defaultdict(float)

    for trade in trades:
        by_symbol[str(trade["symbol"])] += float(
            trade[value_key]
        )

    best_symbol, best_sum = max(
        by_symbol.items(),
        key=lambda item: item[1],
    )

    positive_total = sum(
        max(value, 0.0)
        for value in by_symbol.values()
    )

    total = sum(values)

    return {
        "n": len(values),
        "sum": total,
        "avg": total / len(values),
        "median": statistics.median(values),
        "wr": (
            100.0
            * sum(value > 0 for value in values)
            / len(values)
        ),
        "pf": profit_factor(values),
        "symbols": len(by_symbol),
        "leave_best": total - best_sum,
        "best_symbol": best_symbol,
        "positive_share": (
            max(best_sum, 0.0) / positive_total
            if positive_total > 0
            else 0.0
        ),
    }


def format_metric(result: dict[str, Any]) -> str:
    return (
        f"n={result['n']:4d} "
        f"sum=${result['sum']:+.5f} "
        f"avg=${result['avg']:+.5f} "
        f"median=${result['median']:+.5f} "
        f"WR={result['wr']:5.1f}% "
        f"PF={result['pf']:5.2f} "
        f"symbols={result['symbols']:3d} "
        f"leave_best=${result['leave_best']:+.5f} "
        f"best={result['best_symbol']} "
        f"share={result['positive_share']:.1%}"
    )


def config_key(config: dict[str, Any]) -> str:
    return rescue.config_name(config)


def build_configs() -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = []

    pc_ranges = [
        (0.30, 0.50),
        (0.50, 0.80),
        (0.80, 1.20),
        (1.20, 2.50),
    ]

    volumes = [
        5.0,
        8.0,
        12.0,
    ]

    spreads = [
        1.5,
        2.0,
    ]

    ranks = [
        40,
        80,
        120,
    ]

    extras = [
        "NONE",
        "WALL_POS",
        "WALL_NEG",
        "IMB_ASK",
        "IMB_BID",
        "OI_POS",
    ]

    for (
        pc_range,
        volume,
        spread,
        rank,
        extra,
    ) in product(
        pc_ranges,
        volumes,
        spreads,
        ranks,
        extras,
    ):
        configs.append({
            "pc_min": pc_range[0],
            "pc_max": pc_range[1],
            "vol_min": volume,
            "spread_max": spread,
            "rank_max": rank,
            "exit_mode": "TIME",
            "extra": extra,
        })

    return configs


def add_hard_values(
    trades: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    hard_deduction = (
        NOTIONAL * HARD_COST_PCT / 100.0
    )

    output = []

    for source in trades:
        trade = dict(source)

        gross = float(trade["gross"])

        trade["hard"] = (
            gross - hard_deduction
        )

        trade["day"] = utc_day(
            float(trade["ts"])
        )

        output.append(trade)

    return output


def daily_ratio(
    trades: list[dict[str, Any]],
    value_key: str,
) -> tuple[int, int, float]:
    by_day: dict[str, float] = defaultdict(float)

    for trade in trades:
        by_day[trade["day"]] += float(
            trade[value_key]
        )

    if not by_day:
        return 0, 0, 0.0

    positive = sum(
        value > 0
        for value in by_day.values()
    )

    total = len(by_day)

    return (
        positive,
        total,
        positive / total,
    )


def training_gate(
    trades: list[dict[str, Any]],
) -> tuple[bool, float, dict[str, Any]]:
    stress = metric(trades, "stress")
    hard = metric(trades, "hard")

    (
        positive_days,
        active_days,
        positive_day_ratio,
    ) = daily_ratio(
        trades,
        "stress",
    )

    passed = (
        stress["n"] >= 15

        and stress["sum"] > 0
        and stress["pf"] >= 1.15
        and stress["leave_best"] > 0
        and stress["positive_share"] <= 0.45

        and hard["sum"] > 0
        and hard["pf"] >= 1.00
        and hard["leave_best"] > 0

        and active_days >= 5
        and positive_day_ratio >= 0.55
    )

    score = (
        hard["sum"] * 2.0
        + stress["sum"]
        + hard["leave_best"]
        + stress["leave_best"]
        + min(stress["pf"], 3.0) * 0.10
        + positive_day_ratio * 0.25
    )

    details = {
        "stress": stress,
        "hard": hard,
        "positive_days": positive_days,
        "active_days": active_days,
        "positive_day_ratio": positive_day_ratio,
    }

    return passed, score, details


def slice_trades(
    trades: list[dict[str, Any]],
    start_day: str | None,
    end_day: str,
) -> list[dict[str, Any]]:
    return [
        trade
        for trade in trades
        if (
            trade["day"] < end_day
            and (
                start_day is None
                or trade["day"] >= start_day
            )
        )
    ]


def test_day_trades(
    trades: list[dict[str, Any]],
    day: str,
) -> list[dict[str, Any]]:
    return [
        trade
        for trade in trades
        if trade["day"] == day
    ]


def run_mode(
    mode: str,
    days: list[str],
    config_trades: dict[
        str,
        list[dict[str, Any]],
    ],
    configs_by_key: dict[
        str,
        dict[str, Any],
    ],
) -> dict[str, Any]:
    decisions = []
    oos_trades: list[dict[str, Any]] = []

    start_index = MIN_TRAIN_DAYS

    for day_index in range(
        start_index,
        len(days),
    ):
        test_day = days[day_index]

        if mode == "EXPANDING":
            train_start_day = None

        elif mode == "ROLLING14":
            train_start_index = max(
                0,
                day_index - ROLLING_DAYS,
            )

            train_start_day = days[
                train_start_index
            ]

        else:
            raise ValueError(mode)

        candidates = []

        for key, trades in config_trades.items():
            train_trades = slice_trades(
                trades,
                train_start_day,
                test_day,
            )

            passed, score, details = training_gate(
                train_trades
            )

            if not passed:
                continue

            candidates.append(
                (
                    score,
                    key,
                    details,
                )
            )

        candidates.sort(
            reverse=True,
            key=lambda item: item[0],
        )

        if not candidates:
            decisions.append({
                "day": test_day,
                "config": None,
                "train_score": None,
                "test_n": 0,
                "test_stress": 0.0,
                "test_hard": 0.0,
            })

            continue

        (
            train_score,
            selected_key,
            training_details,
        ) = candidates[0]

        selected_trades = test_day_trades(
            config_trades[selected_key],
            test_day,
        )

        for trade in selected_trades:
            copied = dict(trade)
            copied["selected_config"] = selected_key
            copied["selection_mode"] = mode
            oos_trades.append(copied)

        decisions.append({
            "day": test_day,
            "config": selected_key,
            "train_score": train_score,
            "train_stress_n": (
                training_details["stress"]["n"]
            ),
            "train_stress_pf": (
                training_details["stress"]["pf"]
            ),
            "train_hard_pf": (
                training_details["hard"]["pf"]
            ),
            "train_positive_day_ratio": (
                training_details[
                    "positive_day_ratio"
                ]
            ),
            "test_n": len(selected_trades),
            "test_stress": sum(
                float(trade["stress"])
                for trade in selected_trades
            ),
            "test_hard": sum(
                float(trade["hard"])
                for trade in selected_trades
            ),
        })

    stress = metric(
        oos_trades,
        "stress",
    )

    hard = metric(
        oos_trades,
        "hard",
    )

    (
        positive_days,
        active_days,
        positive_day_ratio,
    ) = daily_ratio(
        oos_trades,
        "stress",
    )

    selected_counter = Counter(
        decision["config"]
        for decision in decisions
        if decision["config"]
    )

    extra_counter = Counter()

    for config_key_value, count in selected_counter.items():
        config = configs_by_key[
            config_key_value
        ]

        extra_counter[
            config["extra"]
        ] += count

    strict_pass = (
        stress["n"] >= 20

        and stress["sum"] > 0
        and stress["pf"] >= 1.20
        and stress["leave_best"] > 0
        and stress["positive_share"] <= 0.45

        and hard["sum"] > 0
        and hard["pf"] >= 1.05
        and hard["leave_best"] > 0

        and active_days >= 6
        and positive_day_ratio >= 0.55
    )

    return {
        "mode": mode,
        "decisions": decisions,
        "oos_trades": oos_trades,
        "stress": stress,
        "hard": hard,
        "positive_days": positive_days,
        "active_days": active_days,
        "positive_day_ratio": positive_day_ratio,
        "selected_counter": selected_counter,
        "extra_counter": extra_counter,
        "strict_pass": strict_pass,
    }


def baseline(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    oos_start_day: str,
) -> dict[str, Any]:
    trades = add_hard_values(
        rescue.select_v18_trades(
            rows,
            config,
        )
    )

    oos = [
        trade
        for trade in trades
        if trade["day"] >= oos_start_day
    ]

    return {
        "all_stress": metric(
            trades,
            "stress",
        ),
        "oos_stress": metric(
            oos,
            "stress",
        ),
        "oos_hard": metric(
            oos,
            "hard",
        ),
    }


def main() -> None:
    rows = rescue.load_v18_rows()

    if not rows:
        raise SystemExit(
            "NO_USABLE_V18_ROWS"
        )

    days = sorted({
        utc_day(float(row["_ts"]))
        for row in rows
    })

    if len(days) <= MIN_TRAIN_DAYS:
        raise SystemExit(
            "INSUFFICIENT_CALENDAR_DAYS"
        )

    configs = build_configs()

    configs_by_key = {
        config_key(config): config
        for config in configs
    }

    print(
        f"usable_rows={len(rows)} "
        f"calendar_days={len(days)} "
        f"configs={len(configs)}",
        flush=True,
    )

    config_trades: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for index, config in enumerate(
        configs,
        1,
    ):
        key = config_key(config)

        trades = rescue.select_v18_trades(
            rows,
            config,
        )

        config_trades[key] = add_hard_values(
            trades
        )

        if (
            index % 25 == 0
            or index == len(configs)
        ):
            print(
                f"PRECOMPUTE "
                f"{index}/{len(configs)}",
                flush=True,
            )

    results = [
        run_mode(
            "EXPANDING",
            days,
            config_trades,
            configs_by_key,
        ),
        run_mode(
            "ROLLING14",
            days,
            config_trades,
            configs_by_key,
        ),
    ]

    oos_start_day = days[
        MIN_TRAIN_DAYS
    ]

    fixed = {
        "R80": baseline(
            rows,
            {
                "pc_min": 1.20,
                "pc_max": 2.50,
                "vol_min": 8.0,
                "spread_max": 2.0,
                "rank_max": 80,
                "exit_mode": "TIME",
                "extra": "WALL_POS",
            },
            oos_start_day,
        ),

        "R120": baseline(
            rows,
            {
                "pc_min": 1.20,
                "pc_max": 2.50,
                "vol_min": 8.0,
                "spread_max": 2.0,
                "rank_max": 120,
                "exit_mode": "TIME",
                "extra": "WALL_POS",
            },
            oos_start_day,
        ),
    }

    expanding = results[0]
    rolling = results[1]

    if (
        expanding["strict_pass"]
        and rolling["strict_pass"]
    ):
        final_decision = (
            "PREQUENTIAL_EDGE_CONFIRMED_IN_BOTH_MODES"
        )

    elif (
        expanding["strict_pass"]
        or rolling["strict_pass"]
    ):
        other = (
            rolling
            if expanding["strict_pass"]
            else expanding
        )

        if (
            other["stress"]["sum"] >= 0
            and other["hard"]["sum"] >= 0
        ):
            final_decision = (
                "PREQUENTIAL_EDGE_NEAR_PASS"
            )
        else:
            final_decision = (
                "PREQUENTIAL_RESULT_UNSTABLE"
            )

    else:
        final_decision = (
            "NO_PREQUENTIAL_EDGE_IN_CURRENT_FEATURE_SPACE"
        )

    lines = []

    lines.append("=" * 150)
    lines.append(
        "SKYNET V18 PREQUENTIAL WALK-FORWARD "
        f"UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}"
    )
    lines.append("=" * 150)

    lines.append(
        "Each test day uses a configuration selected "
        "only from earlier calendar days."
    )

    lines.append(
        "Candidate family is fixed before this run. "
        "No result-based live changes."
    )

    lines.append(
        f"usable_rows={len(rows)} "
        f"calendar_days={len(days)} "
        f"candidate_configs={len(configs)}"
    )

    lines.append(
        f"data_range={days[0]}..{days[-1]} "
        f"first_prequential_test_day={oos_start_day}"
    )

    lines.append(
        f"stress_cost={STRESS_COST_PCT:.2f}% "
        f"hard_cost={HARD_COST_PCT:.2f}%"
    )

    lines.append("REAL_TRADING=OFF.")

    for result in results:
        lines.append("")
        lines.append("-" * 150)
        lines.append(result["mode"])
        lines.append("-" * 150)

        lines.append(
            "OOS STRESS "
            + format_metric(
                result["stress"]
            )
        )

        lines.append(
            "OOS HARD   "
            + format_metric(
                result["hard"]
            )
        )

        lines.append(
            f"POSITIVE_OOS_DAYS="
            f"{result['positive_days']}/"
            f"{result['active_days']} "
            f"({result['positive_day_ratio']:.1%})"
        )

        lines.append(
            "STRICT_PREQUENTIAL_GATE="
            + (
                "PASS"
                if result["strict_pass"]
                else "FAIL"
            )
        )

        lines.append("SELECTED EXTRAS:")

        for extra, count in (
            result["extra_counter"].most_common()
        ):
            lines.append(
                f"  {extra:<12} days={count}"
            )

        lines.append("TOP SELECTED CONFIGS:")

        for key, count in (
            result["selected_counter"].most_common(12)
        ):
            lines.append(
                f"  days={count:2d} {key}"
            )

        lines.append("DAILY DECISIONS:")

        for decision in result["decisions"]:
            lines.append(
                f"  {decision['day']} "
                f"config={decision['config'] or 'NONE'} "
                f"test_n={decision['test_n']} "
                f"stress=${decision['test_stress']:+.5f} "
                f"hard=${decision['test_hard']:+.5f}"
            )

    lines.append("")
    lines.append("=" * 150)
    lines.append("FIXED WALLPOS BASELINES OVER PREQUENTIAL WINDOW")
    lines.append("=" * 150)

    for name, result in fixed.items():
        lines.append(name)

        lines.append(
            "  FULL STRESS "
            + format_metric(
                result["all_stress"]
            )
        )

        lines.append(
            "  OOS STRESS  "
            + format_metric(
                result["oos_stress"]
            )
        )

        lines.append(
            "  OOS HARD    "
            + format_metric(
                result["oos_hard"]
            )
        )

    lines.append("")
    lines.append("=" * 150)
    lines.append("FINAL DECISION")
    lines.append("=" * 150)

    lines.append(
        f"PREQUENTIAL_DECISION={final_decision}"
    )

    lines.append(
        "A pass authorizes only a new exact-shadow "
        "candidate review, never real trading."
    )

    lines.append(
        "Current R80/R120 forward 10/20/40 gates "
        "remain unchanged."
    )

    lines.append("REAL_DECISION=BLOCKED")
    lines.append("REAL_TRADING=OFF")

    text = "\n".join(lines) + "\n"

    REPORT.write_text(
        text,
        encoding="utf-8",
    )

    serializable = {
        "days": days,
        "configs": configs,
        "results": [],
        "fixed": fixed,
        "final_decision": final_decision,
    }

    for result in results:
        serializable["results"].append({
            key: value
            for key, value in result.items()
            if key not in {
                "oos_trades",
                "selected_counter",
                "extra_counter",
            }
        })

    JSON_REPORT.write_text(
        json.dumps(
            serializable,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    print(text)


if __name__ == "__main__":
    main()
