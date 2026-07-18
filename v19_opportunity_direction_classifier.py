#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import v19_dynamic_structure_audit as audit


ROOT = Path("/root/skynet")

REPORT = (
    ROOT
    / "v19_opportunity_direction_classifier_latest.txt"
)

CANDIDATE = (
    ROOT
    / "v19_opportunity_direction_candidate.json"
)

AGES = (5, 15, 30, 60, 300)

DECISION_AGE = 60
EXIT_AGE = 300

MAX_LATENESS = 5.0

NOTIONAL = 12.0
STRESS_COST = 0.26
HARD_COST = 0.36

RIDGE_ALPHA = 10.0

VALIDATION_THRESHOLDS = (
    0.45,
    0.55,
    0.65,
    0.75,
)


def utc(
    timestamp: float | None = None,
) -> str:
    if timestamp is None:
        timestamp = time.time()

    return datetime.fromtimestamp(
        timestamp,
        timezone.utc,
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


def sf(
    value: Any,
    default: float | None = None,
) -> float | None:
    try:
        result = float(value)

        if not math.isfinite(result):
            return default

        return result

    except Exception:
        return default


def midpoint(
    snapshot: dict[str, Any],
) -> float | None:
    return audit.midpoint(
        sf(snapshot.get("bid1")),
        sf(snapshot.get("ask1")),
    )


def pct(
    first: float | None,
    second: float | None,
) -> float:
    if (
        first is None
        or second is None
        or first <= 0
    ):
        return 0.0

    return (
        (second - first)
        / first
        * 100.0
    )


def latency_ok(
    record: dict[str, Any],
) -> bool:
    for age in AGES:
        snapshot = record[
            "snapshots"
        ].get(age)

        if snapshot is None:
            return False

        actual_age = sf(
            snapshot.get("actual_age")
        )

        if actual_age is None:
            return False

        lateness = actual_age - age

        if (
            lateness < -0.25
            or lateness > MAX_LATENESS
        ):
            return False

    return True


def exact_pnl(
    record: dict[str, Any],
    direction: str,
) -> tuple[float, float, float] | None:
    decision = record[
        "snapshots"
    ][DECISION_AGE]

    exit_snapshot = record[
        "snapshots"
    ][EXIT_AGE]

    decision_bid = sf(
        decision.get("bid1")
    )

    decision_ask = sf(
        decision.get("ask1")
    )

    exit_bid = sf(
        exit_snapshot.get("bid1")
    )

    exit_ask = sf(
        exit_snapshot.get("ask1")
    )

    if direction == "LONG":
        if (
            decision_ask is None
            or exit_bid is None
            or decision_ask <= 0
        ):
            return None

        gross_pct = (
            (exit_bid - decision_ask)
            / decision_ask
            * 100.0
        )

    else:
        if (
            decision_bid is None
            or exit_ask is None
            or decision_bid <= 0
        ):
            return None

        gross_pct = (
            (decision_bid - exit_ask)
            / decision_bid
            * 100.0
        )

    stress = (
        (gross_pct - STRESS_COST)
        * NOTIONAL
        / 100.0
    )

    hard = (
        (gross_pct - HARD_COST)
        * NOTIONAL
        / 100.0
    )

    return gross_pct, stress, hard


def build_sample(
    record: dict[str, Any],
) -> dict[str, Any] | None:
    if not latency_ok(record):
        return None

    entry_mid = audit.midpoint(
        sf(record.get("entry_bid1")),
        sf(record.get("entry_ask1")),
    )

    if (
        entry_mid is None
        or entry_mid <= 0
    ):
        return None

    snapshots = record["snapshots"]

    returns: dict[int, float] = {}
    spreads: dict[int, float] = {}
    imbalances: dict[int, float] = {}
    walls: dict[int, float] = {}
    depths: dict[int, float] = {}

    for age in (5, 15, 30, 60):
        snapshot = snapshots[age]

        mid = midpoint(snapshot)

        if mid is None:
            return None

        returns[age] = pct(
            entry_mid,
            mid,
        )

        spreads[age] = (
            sf(
                snapshot.get("spread_bps"),
                0.0,
            )
            or 0.0
        )

        imbalances[age] = (
            sf(
                snapshot.get("imb20"),
                0.0,
            )
            or 0.0
        )

        walls[age] = (
            sf(
                snapshot.get("wall_skew"),
                0.0,
            )
            or 0.0
        )

        total_depth = (
            sf(
                snapshot.get("bid20_usd"),
                0.0,
            )
            or 0.0
        ) + (
            sf(
                snapshot.get("ask20_usd"),
                0.0,
            )
            or 0.0
        )

        depths[age] = math.log1p(
            max(total_depth, 0.0)
        )

    first = snapshots[5]
    decision = snapshots[60]

    features = np.asarray(
        [
            returns[5],
            returns[15],
            returns[30],
            returns[60],

            returns[15] - returns[5],
            returns[30] - returns[15],
            returns[60] - returns[30],

            spreads[5],
            spreads[60],
            spreads[60] - spreads[5],

            imbalances[5],
            imbalances[60],
            imbalances[60] - imbalances[5],

            walls[5],
            walls[60],
            walls[60] - walls[5],

            depths[5],
            depths[60],
            depths[60] - depths[5],

            pct(
                sf(first.get("hold_vol")),
                sf(decision.get("hold_vol")),
            ),

            pct(
                sf(first.get("btc_price")),
                sf(decision.get("btc_price")),
            ),

            float(record["price_change"]),

            math.log1p(
                max(
                    float(record["vol_ratio"]),
                    0.0,
                )
            ),

            float(record["rank"]),
        ],
        dtype=float,
    )

    if not np.all(
        np.isfinite(features)
    ):
        return None

    long_result = exact_pnl(
        record,
        "LONG",
    )

    short_result = exact_pnl(
        record,
        "SHORT",
    )

    if (
        long_result is None
        or short_result is None
    ):
        return None

    long_gross, long_stress, long_hard = (
        long_result
    )

    short_gross, short_stress, short_hard = (
        short_result
    )

    if (
        long_hard <= 0
        and short_hard <= 0
    ):
        label = 0

    elif long_hard >= short_hard:
        label = 1

    else:
        label = 2

    return {
        "signal_id": int(
            record["signal_id"]
        ),

        "symbol": str(
            record["symbol"]
        ),

        "decision_ts": float(
            decision["ts"]
        ),

        "exit_ts": float(
            snapshots[300]["ts"]
        ),

        "x": features,
        "label": label,

        "long_gross": long_gross,
        "long_stress": long_stress,
        "long_hard": long_hard,

        "short_gross": short_gross,
        "short_stress": short_stress,
        "short_hard": short_hard,
    }


def fit_model(
    rows: list[dict[str, Any]],
) -> dict[str, np.ndarray]:
    x = np.vstack([
        row["x"]
        for row in rows
    ])

    y = np.asarray([
        row["label"]
        for row in rows
    ], dtype=int)

    lower = np.quantile(
        x,
        0.01,
        axis=0,
    )

    upper = np.quantile(
        x,
        0.99,
        axis=0,
    )

    clipped = np.clip(
        x,
        lower,
        upper,
    )

    mean = clipped.mean(axis=0)
    scale = clipped.std(axis=0)

    scale = np.where(
        scale < 1e-9,
        1.0,
        scale,
    )

    z = (
        clipped - mean
    ) / scale

    design = np.column_stack([
        np.ones(len(z)),
        z,
    ])

    targets = np.zeros(
        (len(rows), 3),
        dtype=float,
    )

    targets[
        np.arange(len(rows)),
        y,
    ] = 1.0

    counts = np.bincount(
        y,
        minlength=3,
    ).astype(float)

    class_weights = (
        len(rows)
        / (
            3.0
            * np.maximum(counts, 1.0)
        )
    )

    sample_weights = (
        class_weights[y]
    )

    weighted_design = (
        design
        * sample_weights[:, None]
    )

    penalty = np.eye(
        design.shape[1]
    )

    penalty[0, 0] = 0.0

    matrix = (
        design.T
        @ weighted_design
        + RIDGE_ALPHA * penalty
    )

    target = (
        design.T
        @ (
            targets
            * sample_weights[:, None]
        )
    )

    weights = (
        np.linalg.pinv(matrix)
        @ target
    )

    return {
        "lower": lower,
        "upper": upper,
        "mean": mean,
        "scale": scale,
        "weights": weights,
    }


def probabilities(
    model: dict[str, np.ndarray],
    rows: list[dict[str, Any]],
) -> np.ndarray:
    x = np.vstack([
        row["x"]
        for row in rows
    ])

    z = (
        np.clip(
            x,
            model["lower"],
            model["upper"],
        )
        - model["mean"]
    ) / model["scale"]

    design = np.column_stack([
        np.ones(len(z)),
        z,
    ])

    scores = (
        design
        @ model["weights"]
    )

    scores -= scores.max(
        axis=1,
        keepdims=True,
    )

    exp_scores = np.exp(scores)

    return (
        exp_scores
        / exp_scores.sum(
            axis=1,
            keepdims=True,
        )
    )


def predicted_trades(
    rows: list[dict[str, Any]],
    probs: np.ndarray,
    threshold: float,
) -> list[dict[str, Any]]:
    trades = []

    for row, row_probs in zip(
        rows,
        probs,
    ):
        predicted_class = int(
            np.argmax(row_probs)
        )

        confidence = float(
            row_probs[predicted_class]
        )

        if (
            predicted_class == 0
            or confidence < threshold
        ):
            continue

        direction = (
            "LONG"
            if predicted_class == 1
            else "SHORT"
        )

        prefix = (
            "long"
            if direction == "LONG"
            else "short"
        )

        trades.append({
            "signal_id": row["signal_id"],
            "symbol": row["symbol"],

            "decision_ts": (
                row["decision_ts"]
            ),

            "exit_ts": row["exit_ts"],
            "direction": direction,

            "confidence": confidence,

            "gross_pct": row[
                f"{prefix}_gross"
            ],

            "stress": row[
                f"{prefix}_stress"
            ],

            "hard": row[
                f"{prefix}_hard"
            ],
        })

    return audit.simulate_execution(
        trades
    )


def metrics(
    trades: list[dict[str, Any]],
) -> dict[str, Any]:
    stress = audit.metric(
        trades,
        "stress",
    )

    hard = audit.metric(
        trades,
        "hard",
    )

    halves = audit.chronological_parts(
        trades,
        2,
    )

    half_metrics = [
        audit.metric(
            part,
            "stress",
        )
        for part in halves
    ]

    folds = audit.chronological_parts(
        trades,
        4,
    )

    fold_metrics = [
        audit.metric(
            part,
            "stress",
        )
        for part in folds
    ]

    positive_halves = sum(
        row["n"] > 0
        and row["sum"] > 0
        for row in half_metrics
    )

    positive_folds = sum(
        row["n"] > 0
        and row["sum"] > 0
        for row in fold_metrics
    )

    return {
        "stress": stress,
        "hard": hard,

        "halves": half_metrics,
        "folds": fold_metrics,

        "positive_halves": (
            positive_halves
        ),

        "positive_folds": (
            positive_folds
        ),
    }


def validation_pass(
    result: dict[str, Any],
) -> bool:
    stress = result["stress"]
    hard = result["hard"]

    return (
        stress["n"] >= 20
        and stress["symbols"] >= 8

        and stress["sum"] > 0
        and stress["leave_best"] > 0

        and hard["sum"] > 0
        and hard["leave_best"] > 0
    )


def final_pass(
    result: dict[str, Any],
) -> bool:
    stress = result["stress"]
    hard = result["hard"]

    return (
        stress["n"] >= 20
        and stress["symbols"] >= 8

        and stress["sum"] > 0
        and stress["pf"] >= 1.20
        and stress["leave_best"] > 0
        and stress["positive_share"] <= 0.45

        and hard["sum"] > 0
        and hard["pf"] >= 1.05
        and hard["leave_best"] > 0

        and result[
            "positive_halves"
        ] == 2

        and result[
            "positive_folds"
        ] >= 3
    )


def main() -> None:
    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="v19_classifier_",
            dir="/tmp",
        )
    )

    db_snapshot = (
        temp_dir / "v19.sqlite3"
    )

    try:
        audit.snapshot_database(
            db_snapshot
        )

        records, _ = audit.load_records(
            db_snapshot
        )

        clustered = audit.cluster_events(
            records
        )

        samples = []

        for record in clustered:
            sample = build_sample(record)

            if sample is not None:
                samples.append(sample)

        samples.sort(
            key=lambda row: (
                row["decision_ts"],
                row["signal_id"],
            )
        )

        if len(samples) < 1000:
            raise RuntimeError(
                f"Insufficient samples: "
                f"{len(samples)}"
            )

        train_end = int(
            len(samples) * 0.50
        )

        validation_end = int(
            len(samples) * 0.75
        )

        train = samples[:train_end]

        validation = samples[
            train_end:validation_end
        ]

        final_test = samples[
            validation_end:
        ]

        model = fit_model(train)

        validation_probs = probabilities(
            model,
            validation,
        )

        validation_results = []

        for threshold in (
            VALIDATION_THRESHOLDS
        ):
            trades = predicted_trades(
                validation,
                validation_probs,
                threshold,
            )

            result = metrics(trades)

            validation_results.append({
                "threshold": threshold,
                "trades": trades,
                "result": result,
                "passed": validation_pass(
                    result
                ),
            })

        passing_validation = [
            row
            for row in validation_results
            if row["passed"]
        ]

        selected_threshold = None
        final_result = None
        final_trades = []

        if passing_validation:
            passing_validation.sort(
                key=lambda row: (
                    row["result"][
                        "hard"
                    ]["sum"],

                    row["result"][
                        "stress"
                    ]["sum"],
                ),
                reverse=True,
            )

            selected_threshold = (
                passing_validation[0][
                    "threshold"
                ]
            )

            final_probs = probabilities(
                model,
                final_test,
            )

            final_trades = predicted_trades(
                final_test,
                final_probs,
                selected_threshold,
            )

            final_result = metrics(
                final_trades
            )

        label_names = {
            0: "SKIP",
            1: "LONG",
            2: "SHORT",
        }

        lines = [
            "=" * 150,

            (
                "SKYNET V19 OPPORTUNITY/DIRECTION "
                f"CLASSIFIER UTC={utc()}"
            ),

            "=" * 150,

            (
                "One fixed three-class model: "
                "SKIP / LONG / SHORT."
            ),

            (
                "Train=first 50%, validation=next 25%, "
                "untouched final test=last 25%."
            ),

            (
                "Validation chooses one confidence "
                "threshold from a frozen list."
            ),

            (
                "The final test is evaluated once."
            ),

            (
                "Decision=60s, exact executable "
                "exit=300s."
            ),

            (
                f"stress_cost={STRESS_COST:.2f}% "
                f"hard_cost={HARD_COST:.2f}%"
            ),

            "REAL_TRADING=OFF.",
            "",

            f"quality_records={len(records)}",

            (
                f"clustered_records="
                f"{len(clustered)}"
            ),

            (
                f"usable_samples="
                f"{len(samples)}"
            ),

            (
                f"train_n={len(train)} "
                f"validation_n={len(validation)} "
                f"final_test_n={len(final_test)}"
            ),

            "",

            "CLASS DISTRIBUTION:",
        ]

        for split_name, split_rows in (
            ("TRAIN", train),
            ("VALIDATION", validation),
            ("FINAL_TEST", final_test),
        ):
            counts = {
                class_id: sum(
                    row["label"] == class_id
                    for row in split_rows
                )
                for class_id in (0, 1, 2)
            }

            lines.append(
                f"{split_name}: "
                + " ".join(
                    (
                        f"{label_names[class_id]}="
                        f"{counts[class_id]}"
                    )
                    for class_id in (0, 1, 2)
                )
            )

        lines.extend([
            "",
            "=" * 150,
            "VALIDATION THRESHOLDS",
            "=" * 150,
        ])

        for row in validation_results:
            result = row["result"]

            lines.extend([
                "",

                (
                    f"threshold="
                    f"{row['threshold']:.2f} "
                    f"PASS={int(row['passed'])}"
                ),

                (
                    "STRESS "
                    + audit.fmt_metric(
                        result["stress"]
                    )
                ),

                (
                    "HARD   "
                    + audit.fmt_metric(
                        result["hard"]
                    )
                ),
            ])

        lines.extend([
            "",
            "=" * 150,
            "FINAL UNTOUCHED TEST",
            "=" * 150,
        ])

        if selected_threshold is None:
            decision = (
                "NO_VALIDATION_EDGE"
            )

            lines.extend([
                (
                    "selected_threshold=NONE"
                ),

                (
                    "Final test was not opened because "
                    "no validation threshold passed."
                ),
            ])

            CANDIDATE.unlink(
                missing_ok=True
            )

        else:
            passed = final_pass(
                final_result
            )

            decision = (
                "FINAL_TEST_PASS"
                if passed
                else "FINAL_TEST_FAIL"
            )

            lines.extend([
                (
                    f"selected_threshold="
                    f"{selected_threshold:.2f}"
                ),

                (
                    f"executed="
                    f"{len(final_trades)}"
                ),

                (
                    "STRESS "
                    + audit.fmt_metric(
                        final_result["stress"]
                    )
                ),

                (
                    "HARD   "
                    + audit.fmt_metric(
                        final_result["hard"]
                    )
                ),

                (
                    f"POSITIVE_HALVES="
                    f"{final_result['positive_halves']}/2"
                ),

                (
                    f"POSITIVE_FOLDS="
                    f"{final_result['positive_folds']}/4"
                ),
            ])

            for index, fold in enumerate(
                final_result["folds"],
                1,
            ):
                lines.append(
                    f"  F{index} "
                    f"n={fold['n']} "
                    f"sum=${fold['sum']:+.5f} "
                    f"PF={fold['pf']:.2f}"
                )

            if passed:
                cutoff = time.time()

                candidate_payload = {
                    "version": 1,

                    "created_utc": utc(),

                    "cutoff_ts": cutoff,

                    "cutoff_utc": utc(
                        cutoff
                    ),

                    "model_family": (
                        "V19_THREE_CLASS_LINEAR_RIDGE"
                    ),

                    "classes": [
                        "SKIP",
                        "LONG",
                        "SHORT",
                    ],

                    "decision_age": (
                        DECISION_AGE
                    ),

                    "exit_age": EXIT_AGE,

                    "confidence_threshold": (
                        selected_threshold
                    ),

                    "ridge_alpha": (
                        RIDGE_ALPHA
                    ),

                    "maximum_forward_hours": 24,

                    "maximum_forward_trades": 20,

                    "real_trading": False,

                    "model": {
                        "lower": model[
                            "lower"
                        ].tolist(),

                        "upper": model[
                            "upper"
                        ].tolist(),

                        "mean": model[
                            "mean"
                        ].tolist(),

                        "scale": model[
                            "scale"
                        ].tolist(),

                        "weights": model[
                            "weights"
                        ].tolist(),
                    },
                }

                CANDIDATE.write_text(
                    json.dumps(
                        candidate_payload,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )

            else:
                CANDIDATE.unlink(
                    missing_ok=True
                )

        lines.extend([
            "",
            "=" * 150,

            (
                f"CLASSIFIER_DECISION="
                f"{decision}"
            ),

            (
                "If this test fails, retire this "
                "directional anomaly signal family."
            ),

            "REAL_DECISION=BLOCKED",
            "REAL_TRADING=OFF",
        ])

        report_text = (
            "\n".join(lines) + "\n"
        )

        REPORT.write_text(
            report_text,
            encoding="utf-8",
        )

        print(report_text)

    finally:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )


if __name__ == "__main__":
    main()
