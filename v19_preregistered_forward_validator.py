#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import v19_dynamic_structure_audit as audit


ROOT = Path("/root/skynet")

SOURCE_DB = (
    ROOT / "data/v19_dynamic_snapshots.sqlite3"
)

CONFIG_PATH = (
    ROOT / "v19_forward_preregister.json"
)

REPORT_PATH = (
    ROOT / "v19_preregistered_forward_latest.txt"
)

STATE_PATH = (
    ROOT / "v19_preregistered_forward_state.json"
)


def utc_text(
    timestamp: float | None = None,
) -> str:
    if timestamp is None:
        timestamp = datetime.now(
            timezone.utc
        ).timestamp()

    return datetime.fromtimestamp(
        timestamp,
        timezone.utc,
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


def load_json(
    path: Path,
    default: Any,
) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return default


def save_json(
    path: Path,
    value: Any,
) -> None:
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


def latency_is_valid(
    record: dict[str, Any],
    ages: tuple[int, ...],
    tolerance: float,
) -> bool:
    for age in ages:
        snapshot = record["snapshots"].get(
            age
        )

        if snapshot is None:
            return False

        actual_age = snapshot.get(
            "actual_age"
        )

        if actual_age is None:
            return False

        lateness = (
            float(actual_age)
            - float(age)
        )

        if (
            lateness < -0.25
            or lateness > tolerance
        ):
            return False

    return True


def metric_pair(
    trades: list[dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
]:
    return (
        audit.metric(
            trades,
            "stress",
        ),
        audit.metric(
            trades,
            "hard",
        ),
    )


def positive_halves(
    trades: list[dict[str, Any]],
) -> tuple[
    bool,
    list[dict[str, Any]],
]:
    halves = audit.chronological_parts(
        trades,
        2,
    )

    metrics = [
        audit.metric(
            part,
            "stress",
        )
        for part in halves
    ]

    passed = (
        len(metrics) == 2
        and metrics[0]["n"] > 0
        and metrics[1]["n"] > 0
        and metrics[0]["sum"] > 0
        and metrics[1]["sum"] > 0
    )

    return passed, metrics


def positive_folds(
    trades: list[dict[str, Any]],
) -> tuple[
    int,
    list[dict[str, Any]],
]:
    folds = audit.chronological_parts(
        trades,
        6,
    )

    metrics = [
        audit.metric(
            part,
            "stress",
        )
        for part in folds
    ]

    positive = sum(
        result["n"] > 0
        and result["sum"] > 0
        for result in metrics
    )

    return positive, metrics


def evaluate_gate(
    trades: list[dict[str, Any]],
) -> dict[str, Any]:
    total_stress, total_hard = metric_pair(
        trades
    )

    result: dict[str, Any] = {
        "gate": (
            f"COLLECTING_{len(trades)}_OF_10"
        ),
        "decision_n": len(trades),
        "total_stress": total_stress,
        "total_hard": total_hard,
    }

    if len(trades) < 10:
        return result

    first10 = trades[:10]
    stress10, hard10 = metric_pair(
        first10
    )

    result["n10"] = {
        "stress": stress10,
        "hard": hard10,
    }

    pass10 = (
        stress10["sum"] > 0
        and stress10["pf"] >= 1.00
    )

    if not pass10:
        result["gate"] = "REJECTED_AT_N10"
        result["decision_n"] = 10
        return result

    if len(trades) < 20:
        result["gate"] = (
            f"PASSED_N10_COLLECTING_"
            f"{len(trades)}_OF_20"
        )
        return result

    first20 = trades[:20]

    stress20, hard20 = metric_pair(
        first20
    )

    halves20_pass, halves20 = (
        positive_halves(first20)
    )

    result["n20"] = {
        "stress": stress20,
        "hard": hard20,
        "halves": halves20,
    }

    pass20 = (
        stress20["sum"] > 0
        and stress20["pf"] >= 1.20
        and stress20["leave_best"] > 0

        and hard20["sum"] > 0
        and hard20["pf"] >= 1.05
        and hard20["leave_best"] > 0

        and stress20["symbols"] >= 5

        and (
            stress20["positive_share"]
            <= 0.45
        )

        and halves20_pass
    )

    if not pass20:
        result["gate"] = "REJECTED_AT_N20"
        result["decision_n"] = 20
        return result

    if len(trades) < 40:
        result["gate"] = (
            f"PASSED_N20_COLLECTING_"
            f"{len(trades)}_OF_40"
        )
        return result

    first40 = trades[:40]

    stress40, hard40 = metric_pair(
        first40
    )

    halves40_pass, halves40 = (
        positive_halves(first40)
    )

    positive_fold_count, folds40 = (
        positive_folds(first40)
    )

    result["n40"] = {
        "stress": stress40,
        "hard": hard40,
        "halves": halves40,
        "folds": folds40,
        "positive_folds": (
            positive_fold_count
        ),
    }

    pass40 = (
        stress40["sum"] > 0
        and stress40["pf"] >= 1.30
        and stress40["leave_best"] > 0

        and hard40["sum"] > 0
        and hard40["pf"] >= 1.15
        and hard40["leave_best"] > 0

        and stress40["symbols"] >= 8

        and (
            stress40["positive_share"]
            <= 0.35
        )

        and halves40_pass
        and positive_fold_count >= 4
    )

    if pass40:
        result["gate"] = (
            "PASSED_N40_ELIGIBLE_FOR_"
            "MANUAL_EXACT_SHADOW_REVIEW"
        )
    else:
        result["gate"] = "REJECTED_AT_N40"

    result["decision_n"] = 40
    return result


def format_metric(
    result: dict[str, Any],
) -> str:
    return audit.fmt_metric(result)


def main(
    send_requested: bool,
) -> None:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Missing preregistration: "
            f"{CONFIG_PATH}"
        )

    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Missing V19 DB: {SOURCE_DB}"
        )

    config = load_json(
        CONFIG_PATH,
        None,
    )

    if not isinstance(config, dict):
        raise RuntimeError(
            "Invalid preregistration JSON"
        )

    cutoff = float(
        config["cutoff_ts"]
    )

    tolerance = float(
        config["execution"][
            "maximum_snapshot_lateness_seconds"
        ]
    )

    temporary_directory = Path(
        tempfile.mkdtemp(
            prefix="v19_forward_",
            dir="/tmp",
        )
    )

    database_snapshot = (
        temporary_directory
        / "v19_forward_snapshot.sqlite3"
    )

    try:
        audit.snapshot_database(
            database_snapshot
        )

        all_records, _ = audit.load_records(
            database_snapshot
        )

        future_records = [
            record
            for record in all_records
            if float(
                record["entry_ts"]
            ) >= cutoff
        ]

        future_records = audit.cluster_events(
            future_records
        )

        report_results = []
        new_state: dict[str, Any] = {
            "updated_utc": utc_text(),
            "cutoff_ts": cutoff,
            "hypotheses": {},
        }

        previous_state = load_json(
            STATE_PATH,
            {
                "hypotheses": {}
            },
        )

        notification_needed = (
            not STATE_PATH.exists()
        )

        for hypothesis in config[
            "hypotheses"
        ]:
            name = str(
                hypothesis["name"]
            )

            direction = str(
                hypothesis["direction"]
            )

            decision_age = int(
                hypothesis["decision_age"]
            )

            exit_age = int(
                hypothesis["exit_age"]
            )

            universe = str(
                hypothesis["universe"]
            )

            state = str(
                hypothesis["state"]
            )

            candidate_rows = []
            late_rejected = 0

            for record in future_records:
                if not latency_is_valid(
                    record,
                    (
                        decision_age,
                        exit_age,
                    ),
                    tolerance,
                ):
                    late_rejected += 1
                    continue

                trade = audit.build_trade(
                    record,
                    decision_age,
                    exit_age,
                    direction,
                )

                if trade is None:
                    continue

                if (
                    universe
                    not in trade["universes"]
                ):
                    continue

                if state not in trade["states"]:
                    continue

                candidate_rows.append(
                    trade
                )

            selected = audit.simulate_execution(
                candidate_rows
            )

            evaluation = evaluate_gate(
                selected
            )

            hypothesis_state = {
                "n": len(selected),
                "gate": evaluation["gate"],
                "late_rejected": late_rejected,
            }

            old = previous_state.get(
                "hypotheses",
                {},
            ).get(
                name,
                {},
            )

            old_n = int(
                old.get("n", 0)
                or 0
            )

            old_gate = str(
                old.get("gate", "")
            )

            if (
                hypothesis_state["gate"]
                != old_gate
            ):
                notification_needed = True

            for threshold in (
                10,
                20,
                40,
            ):
                if (
                    old_n < threshold
                    <= len(selected)
                ):
                    notification_needed = True

            new_state[
                "hypotheses"
            ][name] = hypothesis_state

            report_results.append({
                "hypothesis": hypothesis,
                "candidate_raw_n": (
                    len(candidate_rows)
                ),
                "selected": selected,
                "evaluation": evaluation,
                "late_rejected": (
                    late_rejected
                ),
            })

        lines = [
            "=" * 150,

            (
                "SKYNET V19 PREREGISTERED "
                "UNTOUCHED FORWARD "
                f"UTC={utc_text()}"
            ),

            "=" * 150,

            (
                f"cutoff={config['cutoff_utc']}"
            ),

            (
                "Only V19 signals with entry time "
                "at or after the cutoff are used."
            ),

            (
                "Snapshot lateness tolerance="
                f"{tolerance:.1f}s"
            ),

            (
                f"future_quality_records="
                f"{len(future_records)}"
            ),

            (
                "Execution: future bid/ask, "
                "max_open=1, symbol cooldown=180s."
            ),

            (
                "Gates are permanently evaluated on "
                "the first 10, 20 and 40 executed "
                "trades, not on later recovery."
            ),

            "No automatic strategy promotion.",
            "REAL_TRADING=OFF.",
        ]

        for item in report_results:
            hypothesis = item[
                "hypothesis"
            ]

            selected = item["selected"]
            evaluation = item[
                "evaluation"
            ]

            lines.extend([
                "",
                "-" * 150,

                (
                    f"{hypothesis['name']} "
                    f"role={hypothesis['role']}"
                ),

                "-" * 150,

                (
                    f"rule={hypothesis['direction']} "
                    f"entry={hypothesis['decision_age']}s "
                    f"exit={hypothesis['exit_age']}s "
                    f"universe={hypothesis['universe']} "
                    f"state={hypothesis['state']}"
                ),

                (
                    f"candidate_raw_n="
                    f"{item['candidate_raw_n']} "
                    f"executed_n={len(selected)} "
                    f"latency_rejected="
                    f"{item['late_rejected']}"
                ),

                (
                    "ALL STRESS "
                    + format_metric(
                        evaluation[
                            "total_stress"
                        ]
                    )
                ),

                (
                    "ALL HARD   "
                    + format_metric(
                        evaluation[
                            "total_hard"
                        ]
                    )
                ),

                (
                    f"FORWARD_GATE="
                    f"{evaluation['gate']}"
                ),
            ])

            for gate_name in (
                "n10",
                "n20",
                "n40",
            ):
                gate_result = evaluation.get(
                    gate_name
                )

                if not gate_result:
                    continue

                lines.append(
                    f"{gate_name.upper()} STRESS "
                    + format_metric(
                        gate_result["stress"]
                    )
                )

                lines.append(
                    f"{gate_name.upper()} HARD   "
                    + format_metric(
                        gate_result["hard"]
                    )
                )

                if (
                    gate_name == "n40"
                    and "positive_folds"
                    in gate_result
                ):
                    lines.append(
                        "N40_POSITIVE_FOLDS="
                        f"{gate_result['positive_folds']}/6"
                    )

            lines.append("RECENT EXECUTED:")

            if not selected:
                lines.append("  [EMPTY]")
            else:
                for trade in selected[-10:]:
                    lines.append(
                        "  "
                        f"{utc_text(trade['decision_ts'])} "
                        f"{trade['symbol']:<12} "
                        f"stress="
                        f"${trade['stress']:+.5f} "
                        f"hard="
                        f"${trade['hard']:+.5f}"
                    )

        lines.extend([
            "",
            "=" * 150,
            "DECISION POLICY",
            "=" * 150,

            (
                "A rejection at n10, n20 or n40 "
                "is permanent for that preregistered "
                "hypothesis."
            ),

            (
                "Passing n40 permits only manual "
                "review for one exact-shadow lane."
            ),

            (
                "No result authorizes real trading."
            ),

            "REAL_DECISION=BLOCKED",
            "REAL_TRADING=OFF",
        ])

        report_text = (
            "\n".join(lines) + "\n"
        )

        REPORT_PATH.write_text(
            report_text,
            encoding="utf-8",
        )

        save_json(
            STATE_PATH,
            new_state,
        )

        print(report_text)

        if (
            send_requested
            and notification_needed
        ):
            subprocess.run(
                [
                    sys.executable,
                    str(
                        ROOT
                        / "tg_send_any.py"
                    ),
                    str(REPORT_PATH),
                    (
                        "SKYNET V19 preregistered "
                        "forward gate update"
                    ),
                ],
                cwd=ROOT,
                check=False,
            )

            print(
                "TELEGRAM_NOTIFICATION_SENT"
            )

        elif send_requested:
            print(
                "NO_GATE_CHANGE_NO_TELEGRAM"
            )

    finally:
        shutil.rmtree(
            temporary_directory,
            ignore_errors=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--send",
        action="store_true",
    )

    arguments = parser.parse_args()

    main(
        send_requested=arguments.send
    )
