#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/root/skynet")
SOURCE_DB = ROOT / "data/v19_dynamic_snapshots.sqlite3"

REPORT = ROOT / "v19_dynamic_structure_audit_latest.txt"
CSV_REPORT = ROOT / "v19_dynamic_structure_candidates_latest.csv"

NOTIONAL = 12.0
STRESS_COST_PCT = 0.26
HARD_COST_PCT = 0.36

DECISION_AGES = (5, 15, 30)
EXIT_AGES = (60, 120, 180, 300)

EVENT_CLUSTER_SECONDS = 60.0
SYMBOL_COOLDOWN_SECONDS = 180.0

TARGET_AGES = (
    5,
    15,
    30,
    60,
    120,
    180,
    300,
)


def utc_text(timestamp: float | None = None) -> str:
    if timestamp is None:
        timestamp = datetime.now(
            timezone.utc
        ).timestamp()

    return datetime.fromtimestamp(
        timestamp,
        timezone.utc,
    ).strftime("%Y-%m-%d %H:%M:%S UTC")


def sf(
    value: Any,
    default: float | None = None,
) -> float | None:
    try:
        if value is None or value == "":
            return default

        result = float(value)

        if not math.isfinite(result):
            return default

        return result
    except Exception:
        return default


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


def percentile(
    values: list[float],
    fraction: float,
) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)

    position = (
        fraction
        * (len(ordered) - 1)
    )

    lower = int(math.floor(position))
    upper = int(math.ceil(position))

    if lower == upper:
        return ordered[lower]

    weight = position - lower

    return (
        ordered[lower] * (1.0 - weight)
        + ordered[upper] * weight
    )


def snapshot_database(destination: Path) -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"V19 DB missing: {SOURCE_DB}"
        )

    source = sqlite3.connect(
        str(SOURCE_DB),
        timeout=60,
    )

    target = sqlite3.connect(
        str(destination),
    )

    try:
        source.backup(
            target,
            pages=4096,
            sleep=0.02,
        )
    finally:
        target.close()
        source.close()


def load_records(
    database: Path,
) -> tuple[
    list[dict[str, Any]],
    dict[int, list[float]],
]:
    connection = sqlite3.connect(
        f"file:{database}?mode=ro",
        uri=True,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    signal_rows = connection.execute(
        """
        SELECT s.*

        FROM signals s

        JOIN (
            SELECT signal_id

            FROM snapshots

            WHERE status='OK'

            GROUP BY signal_id

            HAVING COUNT(
                DISTINCT target_age
            )=7
        ) good
          ON good.signal_id=s.signal_id

        ORDER BY
            s.entry_ts,
            s.signal_id
        """
    ).fetchall()

    snapshot_rows = connection.execute(
        """
        SELECT *

        FROM snapshots

        WHERE status='OK'
          AND target_age IN (
              5, 15, 30,
              60, 120, 180, 300
          )

        ORDER BY
            signal_id,
            target_age
        """
    ).fetchall()

    latency_rows = connection.execute(
        """
        SELECT
            target_age,
            actual_age

        FROM snapshots

        WHERE status='OK'
          AND actual_age IS NOT NULL
        """
    ).fetchall()

    connection.close()

    snapshots: dict[
        int,
        dict[int, dict[str, Any]],
    ] = defaultdict(dict)

    for source in snapshot_rows:
        row = dict(source)

        snapshots[
            int(row["signal_id"])
        ][
            int(row["target_age"])
        ] = row

    records = []

    for source in signal_rows:
        signal = dict(source)
        signal_id = int(signal["signal_id"])

        path = snapshots.get(
            signal_id,
            {},
        )

        if any(
            age not in path
            for age in TARGET_AGES
        ):
            continue

        symbol = str(
            signal.get("clean_symbol")
            or signal.get("symbol")
            or ""
        ).replace(
            "_USDT",
            "",
        ).upper()

        if not symbol:
            continue

        records.append({
            "signal_id": signal_id,
            "entry_ts": float(
                signal["entry_ts"]
            ),
            "symbol": symbol,

            "price_change": sf(
                signal.get("price_change"),
                0.0,
            ) or 0.0,

            "vol_ratio": sf(
                signal.get("vol_ratio"),
                0.0,
            ) or 0.0,

            "rank": int(
                sf(
                    signal.get("rank"),
                    999999,
                )
                or 999999
            ),

            "entry_bid1": sf(
                signal.get("entry_bid1")
            ),

            "entry_ask1": sf(
                signal.get("entry_ask1")
            ),

            "entry_spread": sf(
                signal.get(
                    "entry_spread_bps"
                ),
                999999.0,
            ) or 999999.0,

            "entry_bid20": sf(
                signal.get(
                    "entry_bid20_usd"
                ),
                0.0,
            ) or 0.0,

            "entry_ask20": sf(
                signal.get(
                    "entry_ask20_usd"
                ),
                0.0,
            ) or 0.0,

            "entry_imb20": sf(
                signal.get(
                    "entry_imb20"
                ),
                0.0,
            ) or 0.0,

            "entry_wall": sf(
                signal.get(
                    "entry_wall_skew"
                ),
                0.0,
            ) or 0.0,

            "snapshots": path,
        })

    latency: dict[int, list[float]] = (
        defaultdict(list)
    )

    for row in latency_rows:
        age = int(row["target_age"])

        actual = sf(
            row["actual_age"]
        )

        if actual is None:
            continue

        latency[age].append(
            actual - age
        )

    return records, latency


def cluster_events(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    last_seen: dict[str, float] = {}
    selected = []

    for record in sorted(
        records,
        key=lambda row: (
            row["entry_ts"],
            row["signal_id"],
        ),
    ):
        symbol = record["symbol"]
        timestamp = record["entry_ts"]

        previous = last_seen.get(symbol)

        last_seen[symbol] = timestamp

        if (
            previous is not None
            and timestamp - previous
            <= EVENT_CLUSTER_SECONDS
        ):
            continue

        selected.append(record)

    return selected


def midpoint(
    bid: float | None,
    ask: float | None,
) -> float | None:
    if (
        bid is None
        or ask is None
        or bid <= 0
        or ask <= 0
    ):
        return None

    return (
        bid + ask
    ) / 2.0


def universes(
    record: dict[str, Any],
) -> set[str]:
    pc = record["price_change"]
    vol = record["vol_ratio"]
    rank = record["rank"]
    spread = record["entry_spread"]

    result = {"ALL"}

    if (
        0.30 <= pc <= 0.50
        and vol >= 12.0
        and spread <= 1.50
        and rank <= 50
    ):
        result.add("PC050_CONTROL")

    if (
        0.30 <= pc <= 0.80
        and vol >= 15.0
        and spread <= 2.00
        and rank <= 30
    ):
        result.add("PHASE2D_030_080")

    if (
        1.20 <= pc <= 2.50
        and vol >= 8.0
        and spread <= 2.00
        and rank <= 80
    ):
        result.add("R80_BASE")

    if (
        1.20 <= pc <= 2.50
        and vol >= 8.0
        and spread <= 2.00
        and rank <= 120
    ):
        result.add("R120_BASE")

    if (
        1.20 <= pc <= 2.50
        and vol >= 8.0
        and spread <= 2.00
        and 81 <= rank <= 120
    ):
        result.add("R120_MARGINAL")

    return result


def dynamic_states(
    record: dict[str, Any],
    decision_age: int,
) -> tuple[
    set[str],
    dict[str, float],
]:
    snapshot = record["snapshots"][
        decision_age
    ]

    first = record["snapshots"][5]

    entry_mid = midpoint(
        record["entry_bid1"],
        record["entry_ask1"],
    )

    decision_mid = midpoint(
        sf(snapshot.get("bid1")),
        sf(snapshot.get("ask1")),
    )

    early_move = 0.0

    if (
        entry_mid is not None
        and decision_mid is not None
        and entry_mid > 0
    ):
        early_move = (
            (decision_mid - entry_mid)
            / entry_mid
            * 100.0
        )

    spread = (
        sf(
            snapshot.get("spread_bps"),
            record["entry_spread"],
        )
        or record["entry_spread"]
    )

    imb20 = (
        sf(
            snapshot.get("imb20"),
            0.0,
        )
        or 0.0
    )

    wall = (
        sf(
            snapshot.get("wall_skew"),
            0.0,
        )
        or 0.0
    )

    bid20 = (
        sf(
            snapshot.get("bid20_usd"),
            0.0,
        )
        or 0.0
    )

    ask20 = (
        sf(
            snapshot.get("ask20_usd"),
            0.0,
        )
        or 0.0
    )

    entry_depth = (
        record["entry_bid20"]
        + record["entry_ask20"]
    )

    current_depth = bid20 + ask20

    depth_ratio = (
        current_depth / entry_depth
        if entry_depth > 0
        else 1.0
    )

    first_hold = sf(
        first.get("hold_vol")
    )

    current_hold = sf(
        snapshot.get("hold_vol")
    )

    oi_change = 0.0

    if (
        first_hold is not None
        and current_hold is not None
        and first_hold > 0
    ):
        oi_change = (
            (current_hold - first_hold)
            / first_hold
            * 100.0
        )

    first_btc = sf(
        first.get("btc_price")
    )

    current_btc = sf(
        snapshot.get("btc_price")
    )

    btc_change = 0.0

    if (
        first_btc is not None
        and current_btc is not None
        and first_btc > 0
    ):
        btc_change = (
            (current_btc - first_btc)
            / first_btc
            * 100.0
        )

    states = {"ANY"}

    if early_move < 0:
        states.add("EARLY_FADE")
    elif early_move > 0:
        states.add("EARLY_CONT")

    if early_move <= -0.20:
        states.add("STRONG_FADE")

    if early_move >= 0.20:
        states.add("STRONG_CONT")

    if wall > 0:
        states.add("WALL_POS")
    elif wall < 0:
        states.add("WALL_NEG")

    if imb20 > 0:
        states.add("IMB_BID")
    elif imb20 < 0:
        states.add("IMB_ASK")

    if spread < record["entry_spread"]:
        states.add("SPREAD_TIGHTENS")
    else:
        states.add("SPREAD_WIDENS")

    if (
        record["entry_wall"] > 0
        and wall > 0
    ):
        states.add("WALL_PERSISTS_POS")

    if (
        record["entry_wall"] > 0
        and wall <= 0
    ):
        states.add("WALL_FLIPS_NEG")

    if depth_ratio < 0.70:
        states.add("DEPTH_COLLAPSE")

    if depth_ratio > 1.30:
        states.add("DEPTH_EXPANDS")

    if oi_change > 0:
        states.add("OI_UP")
    elif oi_change < 0:
        states.add("OI_DOWN")

    if btc_change > 0:
        states.add("BTC_UP")
    elif btc_change < 0:
        states.add("BTC_DOWN")

    if (
        early_move < 0
        and imb20 < 0
    ):
        states.add("FADE_PLUS_ASK")

    if (
        early_move < 0
        and wall > 0
    ):
        states.add("FADE_PLUS_WALL_POS")

    if (
        early_move < 0
        and spread < record["entry_spread"]
    ):
        states.add("FADE_PLUS_TIGHT")

    if (
        early_move > 0
        and imb20 > 0
    ):
        states.add("CONT_PLUS_BID")

    return states, {
        "early_move": early_move,
        "spread": spread,
        "imb20": imb20,
        "wall": wall,
        "depth_ratio": depth_ratio,
        "oi_change": oi_change,
        "btc_change": btc_change,
    }


def build_trade(
    record: dict[str, Any],
    decision_age: int,
    exit_age: int,
    direction: str,
) -> dict[str, Any] | None:
    decision = record["snapshots"][
        decision_age
    ]

    exit_snapshot = record["snapshots"][
        exit_age
    ]

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

    if direction == "SHORT":
        if (
            decision_bid is None
            or exit_ask is None
            or decision_bid <= 0
            or exit_ask <= 0
        ):
            return None

        gross_pct = (
            (decision_bid - exit_ask)
            / decision_bid
            * 100.0
        )

    elif direction == "LONG":
        if (
            decision_ask is None
            or exit_bid is None
            or decision_ask <= 0
            or exit_bid <= 0
        ):
            return None

        gross_pct = (
            (exit_bid - decision_ask)
            / decision_ask
            * 100.0
        )

    else:
        raise ValueError(direction)

    states, features = dynamic_states(
        record,
        decision_age,
    )

    return {
        "signal_id": record["signal_id"],
        "symbol": record["symbol"],

        "decision_ts": float(
            decision["ts"]
        ),

        "exit_ts": float(
            exit_snapshot["ts"]
        ),

        "gross_pct": gross_pct,

        "stress": (
            (gross_pct - STRESS_COST_PCT)
            * NOTIONAL
            / 100.0
        ),

        "hard": (
            (gross_pct - HARD_COST_PCT)
            * NOTIONAL
            / 100.0
        ),

        "universes": universes(record),
        "states": states,

        **features,
    }


def simulate_execution(
    trades: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    selected = []

    busy_until = 0.0
    last_symbol_entry: dict[str, float] = {}

    for trade in sorted(
        trades,
        key=lambda row: (
            row["decision_ts"],
            row["signal_id"],
        ),
    ):
        timestamp = trade["decision_ts"]
        symbol = trade["symbol"]

        if timestamp < busy_until:
            continue

        previous = last_symbol_entry.get(
            symbol
        )

        if (
            previous is not None
            and timestamp - previous
            < SYMBOL_COOLDOWN_SECONDS
        ):
            continue

        selected.append(trade)

        last_symbol_entry[
            symbol
        ] = timestamp

        busy_until = trade["exit_ts"]

    return selected


def metric(
    trades: list[dict[str, Any]],
    key: str,
) -> dict[str, Any]:
    values = [
        float(trade[key])
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

    by_symbol: dict[
        str,
        float,
    ] = defaultdict(float)

    for trade in trades:
        by_symbol[
            trade["symbol"]
        ] += float(trade[key])

    best_symbol, best_value = max(
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

        "leave_best": (
            total - best_value
        ),

        "best_symbol": best_symbol,

        "positive_share": (
            max(best_value, 0.0)
            / positive_total
            if positive_total > 0
            else 0.0
        ),
    }


def chronological_parts(
    trades: list[dict[str, Any]],
    count: int,
) -> list[list[dict[str, Any]]]:
    ordered = sorted(
        trades,
        key=lambda row: row["decision_ts"],
    )

    cuts = [
        round(
            len(ordered) * index / count
        )
        for index in range(count + 1)
    ]

    return [
        ordered[
            cuts[index]:
            cuts[index + 1]
        ]
        for index in range(count)
    ]


def fmt_metric(
    result: dict[str, Any],
) -> str:
    return (
        f"n={result['n']:4d} "
        f"sum=${result['sum']:+.5f} "
        f"avg=${result['avg']:+.5f} "
        f"med=${result['median']:+.5f} "
        f"WR={result['wr']:5.1f}% "
        f"PF={result['pf']:5.2f} "
        f"symbols={result['symbols']:3d} "
        f"leave_best="
        f"${result['leave_best']:+.5f} "
        f"best={result['best_symbol']} "
        f"share={result['positive_share']:.1%}"
    )


def evaluate_candidate(
    name: str,
    trades: list[dict[str, Any]],
) -> dict[str, Any]:
    selected = simulate_execution(
        trades
    )

    stress = metric(
        selected,
        "stress",
    )

    hard = metric(
        selected,
        "hard",
    )

    halves = chronological_parts(
        selected,
        2,
    )

    folds = chronological_parts(
        selected,
        6,
    )

    half_metrics = [
        metric(part, "stress")
        for part in halves
    ]

    fold_metrics = [
        metric(part, "stress")
        for part in folds
    ]

    positive_folds = sum(
        fold["n"] > 0
        and fold["sum"] > 0
        for fold in fold_metrics
    )

    stable = (
        stress["n"] >= 20
        and stress["symbols"] >= 5

        and stress["sum"] > 0
        and stress["pf"] >= 1.20
        and stress["leave_best"] > 0
        and stress["positive_share"] <= 0.45

        and hard["sum"] > 0
        and hard["pf"] >= 1.05
        and hard["leave_best"] > 0

        and len(half_metrics) == 2
        and half_metrics[0]["sum"] > 0
        and half_metrics[1]["sum"] > 0

        and positive_folds >= 4
    )

    score = (
        hard["sum"]
        + stress["sum"]
        + stress["leave_best"]
        + hard["leave_best"]
        + min(stress["pf"], 3.0) * 0.05
        + positive_folds * 0.02
    )

    return {
        "name": name,
        "raw_n": len(trades),
        "selected": selected,
        "stress": stress,
        "hard": hard,
        "halves": half_metrics,
        "folds": fold_metrics,
        "positive_folds": positive_folds,
        "stable": stable,
        "score": score,
    }


def main() -> None:
    temporary_directory = Path(
        tempfile.mkdtemp(
            prefix="v19_structure_",
            dir="/tmp",
        )
    )

    snapshot_path = (
        temporary_directory
        / "v19_snapshot.sqlite3"
    )

    try:
        snapshot_database(
            snapshot_path
        )

        records, latency = load_records(
            snapshot_path
        )

        clustered = cluster_events(
            records
        )

        universe_names = (
            "ALL",
            "PC050_CONTROL",
            "PHASE2D_030_080",
            "R80_BASE",
            "R120_BASE",
            "R120_MARGINAL",
        )

        state_names = (
            "ANY",
            "EARLY_FADE",
            "EARLY_CONT",
            "STRONG_FADE",
            "STRONG_CONT",
            "WALL_POS",
            "WALL_NEG",
            "IMB_BID",
            "IMB_ASK",
            "SPREAD_TIGHTENS",
            "SPREAD_WIDENS",
            "WALL_PERSISTS_POS",
            "WALL_FLIPS_NEG",
            "DEPTH_COLLAPSE",
            "DEPTH_EXPANDS",
            "OI_UP",
            "OI_DOWN",
            "BTC_UP",
            "BTC_DOWN",
            "FADE_PLUS_ASK",
            "FADE_PLUS_WALL_POS",
            "FADE_PLUS_TIGHT",
            "CONT_PLUS_BID",
        )

        trade_sets: dict[
            tuple[int, int, str],
            list[dict[str, Any]],
        ] = {}

        for decision_age in DECISION_AGES:
            for exit_age in EXIT_AGES:
                if exit_age <= decision_age:
                    continue

                for direction in (
                    "SHORT",
                    "LONG",
                ):
                    rows = []

                    for record in clustered:
                        trade = build_trade(
                            record,
                            decision_age,
                            exit_age,
                            direction,
                        )

                        if trade is not None:
                            rows.append(trade)

                    trade_sets[
                        (
                            decision_age,
                            exit_age,
                            direction,
                        )
                    ] = rows

        results = []

        for (
            decision_age,
            exit_age,
            direction,
        ), rows in trade_sets.items():

            for universe in universe_names:
                for state in state_names:
                    candidate_rows = [
                        row
                        for row in rows
                        if (
                            universe
                            in row["universes"]
                            and state
                            in row["states"]
                        )
                    ]

                    if len(candidate_rows) < 15:
                        continue

                    name = (
                        f"{direction} "
                        f"entry={decision_age}s "
                        f"exit={exit_age}s "
                        f"universe={universe} "
                        f"state={state}"
                    )

                    result = evaluate_candidate(
                        name,
                        candidate_rows,
                    )

                    result.update({
                        "decision_age": decision_age,
                        "exit_age": exit_age,
                        "direction": direction,
                        "universe": universe,
                        "state": state,
                    })

                    results.append(result)

        results.sort(
            key=lambda row: row["score"],
            reverse=True,
        )

        stable = [
            result
            for result in results
            if result["stable"]
        ]

        lines = [
            "=" * 150,

            (
                "SKYNET V19 DYNAMIC "
                "MICROSTRUCTURE AUDIT "
                f"UTC={utc_text()}"
            ),

            "=" * 150,

            (
                "True delayed entry and exit use "
                "recorded future bid/ask snapshots."
            ),

            (
                "Signals are clustered by symbol "
                f"within {EVENT_CLUSTER_SECONDS:.0f}s."
            ),

            (
                "Execution simulation uses "
                "max_open=1 and symbol cooldown="
                f"{SYMBOL_COOLDOWN_SECONDS:.0f}s."
            ),

            (
                f"stress_cost={STRESS_COST_PCT:.2f}% "
                f"hard_cost={HARD_COST_PCT:.2f}%"
            ),

            "Exploratory same-day research only.",
            "No automatic shadow or real promotion.",
            "REAL_TRADING=OFF.",

            "",
            "DATA QUALITY",

            (
                f"quality_complete_records="
                f"{len(records)}"
            ),

            (
                f"clustered_independent_events="
                f"{len(clustered)}"
            ),

            (
                f"duplicate_or_clustered_away="
                f"{len(records) - len(clustered)}"
            ),

            "",
            "SNAPSHOT LATENCY",
        ]

        for age in TARGET_AGES:
            values = latency.get(
                age,
                [],
            )

            lines.append(
                f"age={age:3d}s "
                f"n={len(values):4d} "
                f"late_p50="
                f"{percentile(values, 0.50):.3f}s "
                f"late_p95="
                f"{percentile(values, 0.95):.3f}s "
                f"late_max="
                f"{max(values) if values else 0.0:.3f}s"
            )

        lines.extend([
            "",
            "UNCONDITIONAL DELAYED-ENTRY BASELINES",
        ])

        baseline_results = [
            result
            for result in results
            if (
                result["universe"] == "ALL"
                and result["state"] == "ANY"
            )
        ]

        baseline_results.sort(
            key=lambda row: (
                row["decision_age"],
                row["exit_age"],
                row["direction"],
            )
        )

        for result in baseline_results:
            lines.append(result["name"])
            lines.append(
                "  STRESS "
                + fmt_metric(
                    result["stress"]
                )
            )
            lines.append(
                "  HARD   "
                + fmt_metric(
                    result["hard"]
                )
            )

        lines.extend([
            "",
            "=" * 150,
            (
                "STRICTLY STABLE EXPLORATORY "
                f"CELLS n={len(stable)}"
            ),
            "=" * 150,
        ])

        if not stable:
            lines.append("[NONE]")
        else:
            for index, result in enumerate(
                stable[:30],
                1,
            ):
                lines.append(
                    f"#{index} {result['name']}"
                )

                lines.append(
                    "  STRESS "
                    + fmt_metric(
                        result["stress"]
                    )
                )

                lines.append(
                    "  HARD   "
                    + fmt_metric(
                        result["hard"]
                    )
                )

                lines.append(
                    "  HALVES "
                    + " | ".join(
                        (
                            f"H{half_index} "
                            f"n={half['n']} "
                            f"${half['sum']:+.5f} "
                            f"PF={half['pf']:.2f}"
                        )
                        for half_index, half
                        in enumerate(
                            result["halves"],
                            1,
                        )
                    )
                )

                lines.append(
                    f"  POSITIVE_FOLDS="
                    f"{result['positive_folds']}/6"
                )

        lines.extend([
            "",
            "=" * 150,
            "TOP EXPLORATORY CELLS",
            "=" * 150,
        ])

        for index, result in enumerate(
            results[:40],
            1,
        ):
            lines.append(
                f"#{index} "
                f"stable={int(result['stable'])} "
                f"{result['name']}"
            )

            lines.append(
                "  STRESS "
                + fmt_metric(
                    result["stress"]
                )
            )

            lines.append(
                "  HARD   "
                + fmt_metric(
                    result["hard"]
                )
            )

            lines.append(
                f"  POSITIVE_FOLDS="
                f"{result['positive_folds']}/6 "
                f"raw_n={result['raw_n']}"
            )

        lines.extend([
            "",
            "FINAL INTERPRETATION",
        ])

        if stable:
            lines.append(
                "DYNAMIC_STRUCTURE_CANDIDATES_FOUND"
            )

            lines.append(
                "These cells require replication "
                "on additional calendar days before "
                "one fixed exact-shadow candidate "
                "can be preregistered."
            )
        else:
            lines.append(
                "NO_STABLE_DYNAMIC_CELL_IN_CURRENT_SAMPLE"
            )

            lines.append(
                "Do not loosen gates. Continue V19 "
                "collection across more regimes."
            )

        lines.extend([
            (
                "A same-day result never authorizes "
                "real trading."
            ),
            "REAL_DECISION=BLOCKED",
            "REAL_TRADING=OFF",
        ])

        REPORT.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

        with CSV_REPORT.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            fields = [
                "stable",
                "score",
                "direction",
                "decision_age",
                "exit_age",
                "universe",
                "state",
                "raw_n",

                "stress_n",
                "stress_sum",
                "stress_avg",
                "stress_wr",
                "stress_pf",
                "stress_symbols",
                "stress_leave_best",
                "stress_positive_share",

                "hard_sum",
                "hard_pf",
                "hard_leave_best",

                "half1_sum",
                "half2_sum",
                "positive_folds",
            ]

            writer = csv.DictWriter(
                handle,
                fieldnames=fields,
            )

            writer.writeheader()

            for result in results:
                halves = result["halves"]

                writer.writerow({
                    "stable": int(
                        result["stable"]
                    ),

                    "score": result["score"],
                    "direction": result["direction"],
                    "decision_age": result["decision_age"],
                    "exit_age": result["exit_age"],
                    "universe": result["universe"],
                    "state": result["state"],
                    "raw_n": result["raw_n"],

                    "stress_n": (
                        result["stress"]["n"]
                    ),

                    "stress_sum": (
                        result["stress"]["sum"]
                    ),

                    "stress_avg": (
                        result["stress"]["avg"]
                    ),

                    "stress_wr": (
                        result["stress"]["wr"]
                    ),

                    "stress_pf": (
                        result["stress"]["pf"]
                    ),

                    "stress_symbols": (
                        result["stress"]["symbols"]
                    ),

                    "stress_leave_best": (
                        result["stress"][
                            "leave_best"
                        ]
                    ),

                    "stress_positive_share": (
                        result["stress"][
                            "positive_share"
                        ]
                    ),

                    "hard_sum": (
                        result["hard"]["sum"]
                    ),

                    "hard_pf": (
                        result["hard"]["pf"]
                    ),

                    "hard_leave_best": (
                        result["hard"][
                            "leave_best"
                        ]
                    ),

                    "half1_sum": (
                        halves[0]["sum"]
                        if len(halves) > 0
                        else 0.0
                    ),

                    "half2_sum": (
                        halves[1]["sum"]
                        if len(halves) > 1
                        else 0.0
                    ),

                    "positive_folds": (
                        result["positive_folds"]
                    ),
                })

        print(
            REPORT.read_text(
                encoding="utf-8"
            )
        )

    finally:
        shutil.rmtree(
            temporary_directory,
            ignore_errors=True,
        )


if __name__ == "__main__":
    main()
