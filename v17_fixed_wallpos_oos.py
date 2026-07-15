#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import sqlite3
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/root/skynet")

V17_DB = ROOT / "data/v17_microstructure.sqlite3"
V18_DB = ROOT / "data/v18_micro_paths.sqlite3"

REPORT = ROOT / "v17_fixed_wallpos_oos_latest.txt"
JSON_REPORT = ROOT / "v17_fixed_wallpos_oos_latest.json"

NOTIONAL_USD = 12.0

# Fixed stress assumptions:
# 0.16% round-trip fees + 0.10% round-trip slippage.
# Recorded entry spread is charged separately.
STRESS_FIXED_COST_PCT = 0.26

MAX_OPEN = 1
SYMBOL_COOLDOWN_SECONDS = 180.0
DEFAULT_HOLD_SECONDS = 300.0


CONFIGS = {
    "PC050_CONTROL": {
        "pc_min": 0.30,
        "pc_max": 0.50,
        "vol_min": 12.0,
        "spread_max": 1.50,
        "rank_min": 1,
        "rank_max": 50,
        "wall_positive": False,
    },

    "WALLPOS_R80": {
        "pc_min": 1.20,
        "pc_max": 2.50,
        "vol_min": 8.0,
        "spread_max": 2.00,
        "rank_min": 1,
        "rank_max": 80,
        "wall_positive": True,
    },

    "WALLPOS_R120": {
        "pc_min": 1.20,
        "pc_max": 2.50,
        "vol_min": 8.0,
        "spread_max": 2.00,
        "rank_min": 1,
        "rank_max": 120,
        "wall_positive": True,
    },

    # What R120 adds beyond R80.
    "R120_MARGINAL_81_120": {
        "pc_min": 1.20,
        "pc_max": 2.50,
        "vol_min": 8.0,
        "spread_max": 2.00,
        "rank_min": 81,
        "rank_max": 120,
        "wall_positive": True,
    },
}


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


def utc(timestamp: float | None) -> str:
    if timestamp is None:
        return "-"

    return datetime.fromtimestamp(
        timestamp,
        timezone.utc,
    ).strftime("%Y-%m-%d %H:%M:%S UTC")


def profit_factor(values: list[float]) -> float:
    positive = sum(
        value for value in values
        if value > 0
    )

    negative = -sum(
        value for value in values
        if value < 0
    )

    if negative <= 0:
        return 999.0 if positive > 0 else 0.0

    return positive / negative


def load_current_blacklist() -> set[str]:
    try:
        import v18_exact_multi_shadow as exact

        lane = exact.LANES.get(
            "RESEARCH_PC120_250_WALLPOS_R120_TIME",
            exact.LANES.get(
                "RESEARCH_PC120_250_WALLPOS_TIME",
                {},
            ),
        )

        return {
            str(symbol).upper()
            for symbol in lane.get("blacklist", set())
        }
    except Exception:
        return set()


def load_rows() -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
]:
    if not V17_DB.exists():
        raise FileNotFoundError(
            f"V17 DB missing: {V17_DB}"
        )

    connection = sqlite3.connect(
        f"file:{V17_DB}?mode=ro",
        uri=True,
        timeout=30,
    )
    connection.row_factory = sqlite3.Row

    columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(signals)"
        )
    }

    required = {
        "ts",
        "time_iso",
        "symbol",
        "clean_symbol",
        "price_change",
        "vol_ratio",
        "current_turnover_rank",
        "spread_bps",
        "wall_skew",
        "close_5m",
        "short_net_5m",
        "closed",
        "close_ts",
    }

    missing = sorted(required - columns)

    if missing:
        connection.close()

        raise RuntimeError(
            "V17 schema missing: "
            + ",".join(missing)
        )

    source_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total_rows,
            SUM(
                CASE WHEN closed = 1
                     THEN 1 ELSE 0 END
            ) AS closed_rows,
            MIN(ts) AS min_ts,
            MAX(ts) AS max_ts
        FROM signals
        """
    ).fetchone()

    source_rows = connection.execute(
        """
        SELECT
            id,
            ts,
            time_iso,
            symbol,
            clean_symbol,
            price_change,
            vol_ratio,
            current_turnover_rank,
            spread_bps,
            wall_skew,
            close_5m,
            short_net_5m,
            close_ts,
            close_time_iso
        FROM signals
        WHERE closed = 1
          AND ts IS NOT NULL
          AND price_change IS NOT NULL
          AND vol_ratio IS NOT NULL
          AND current_turnover_rank IS NOT NULL
          AND spread_bps IS NOT NULL
          AND wall_skew IS NOT NULL
          AND close_5m IS NOT NULL
        ORDER BY ts ASC, id ASC
        """
    ).fetchall()

    connection.close()

    blacklist = load_current_blacklist()

    output: list[dict[str, Any]] = []

    for source in source_rows:
        row = dict(source)

        timestamp = sf(row.get("ts"))
        close_timestamp = sf(row.get("close_ts"))

        pc = sf(row.get("price_change"))
        vol = sf(row.get("vol_ratio"))
        rank = sf(row.get("current_turnover_rank"))
        spread = sf(row.get("spread_bps"))
        wall = sf(row.get("wall_skew"))
        close_5m = sf(row.get("close_5m"))
        stored_short_net = sf(row.get("short_net_5m"))

        if None in (
            timestamp,
            pc,
            vol,
            rank,
            spread,
            wall,
            close_5m,
        ):
            continue

        symbol = str(
            row.get("clean_symbol")
            or row.get("symbol")
            or ""
        ).replace("_USDT", "").upper()

        if not symbol:
            continue

        if symbol in blacklist:
            continue

        # close_5m is LONG-oriented price movement.
        # SHORT gross is therefore -close_5m.
        #
        # V17 did not store future ask. We use:
        # fixed 0.26% stress cost + recorded spread.
        spread_cost_pct = max(
            float(spread),
            0.0,
        ) / 100.0

        net_pct = (
            -float(close_5m)
            - STRESS_FIXED_COST_PCT
            - spread_cost_pct
        )

        stress_net = (
            NOTIONAL_USD
            * net_pct
            / 100.0
        )

        output.append({
            "id": int(row["id"]),
            "ts": float(timestamp),
            "close_ts": (
                float(close_timestamp)
                if close_timestamp is not None
                else float(timestamp)
                + DEFAULT_HOLD_SECONDS
            ),
            "time_iso": str(
                row.get("time_iso") or ""
            ),
            "symbol": symbol,
            "pc": float(pc),
            "vol": float(vol),
            "rank": int(float(rank)),
            "spread": float(spread),
            "wall": float(wall),
            "close_5m": float(close_5m),
            "stress_net": float(stress_net),
            "stored_short_net": stored_short_net,
        })

    metadata = {
        "total_rows": int(
            source_stats["total_rows"] or 0
        ),
        "closed_rows": int(
            source_stats["closed_rows"] or 0
        ),
        "min_ts": sf(source_stats["min_ts"]),
        "max_ts": sf(source_stats["max_ts"]),
        "blacklist_size": len(blacklist),
    }

    return output, metadata


def v18_start_timestamp() -> float | None:
    if not V18_DB.exists():
        return None

    connection = sqlite3.connect(
        f"file:{V18_DB}?mode=ro",
        uri=True,
        timeout=30,
    )

    row = connection.execute(
        "SELECT MIN(ts) FROM signals"
    ).fetchone()

    connection.close()

    return sf(row[0]) if row else None


def passes(
    row: dict[str, Any],
    config: dict[str, Any],
) -> bool:
    if not (
        config["pc_min"]
        <= row["pc"]
        <= config["pc_max"]
    ):
        return False

    if row["vol"] < config["vol_min"]:
        return False

    if row["spread"] > config["spread_max"]:
        return False

    if not (
        config["rank_min"]
        <= row["rank"]
        <= config["rank_max"]
    ):
        return False

    if (
        config["wall_positive"]
        and row["wall"] <= 0
    ):
        return False

    return True


def select_trades(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []

    busy_until = 0.0
    last_symbol_entry: dict[str, float] = {}

    for row in rows:
        if not passes(row, config):
            continue

        timestamp = row["ts"]
        symbol = row["symbol"]

        # Same research assumption as V18 replay:
        # only one simultaneous position.
        if timestamp < busy_until:
            continue

        previous = last_symbol_entry.get(symbol)

        if (
            previous is not None
            and timestamp - previous
            < SYMBOL_COOLDOWN_SECONDS
        ):
            continue

        selected.append(dict(row))

        last_symbol_entry[symbol] = timestamp

        busy_until = max(
            row["close_ts"],
            timestamp + DEFAULT_HOLD_SECONDS,
        )

    return selected


def metric(
    trades: list[dict[str, Any]],
) -> dict[str, Any]:
    values = [
        float(trade["stress_net"])
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
            "best_symbol": "-",
            "best_sum": 0.0,
            "positive_share": 0.0,
            "leave_best": 0.0,
        }

    by_symbol: dict[str, float] = defaultdict(float)

    for trade in trades:
        by_symbol[trade["symbol"]] += float(
            trade["stress_net"]
        )

    best_symbol, best_sum = max(
        by_symbol.items(),
        key=lambda item: item[1],
    )

    positive_total = sum(
        max(value, 0.0)
        for value in by_symbol.values()
    )

    positive_share = (
        max(best_sum, 0.0) / positive_total
        if positive_total > 0
        else 0.0
    )

    total = sum(values)

    return {
        "n": len(values),
        "sum": total,
        "avg": total / len(values),
        "median": statistics.median(values),
        "wr": (
            100.0
            * sum(1 for value in values if value > 0)
            / len(values)
        ),
        "pf": profit_factor(values),
        "symbols": len(by_symbol),
        "best_symbol": best_symbol,
        "best_sum": best_sum,
        "positive_share": positive_share,
        "leave_best": total - best_sum,
    }


def format_metric(result: dict[str, Any]) -> str:
    return (
        f"n={result['n']:3d} "
        f"net=${result['sum']:+.5f} "
        f"avg=${result['avg']:+.5f} "
        f"median=${result['median']:+.5f} "
        f"WR={result['wr']:5.1f}% "
        f"PF={result['pf']:5.2f} "
        f"symbols={result['symbols']:2d} "
        f"leave_best=${result['leave_best']:+.5f} "
        f"best={result['best_symbol']} "
        f"share={result['positive_share']:.1%}"
    )


def split_folds(
    trades: list[dict[str, Any]],
    count: int,
) -> list[list[dict[str, Any]]]:
    if not trades:
        return [[] for _ in range(count)]

    cuts = [
        round(len(trades) * index / count)
        for index in range(count + 1)
    ]

    return [
        trades[cuts[index]:cuts[index + 1]]
        for index in range(count)
    ]


def classify(result: dict[str, Any]) -> str:
    if result["n"] < 5:
        return "INSUFFICIENT_SAMPLE"

    if (
        result["sum"] <= 0
        or result["pf"] < 1.00
    ):
        return "INDEPENDENT_CONTRADICTION"

    if (
        result["n"] >= 10
        and result["pf"] >= 1.20
        and result["symbols"] >= 3
        and result["leave_best"] > 0
        and result["positive_share"] <= 0.50
    ):
        return "INDEPENDENT_CORROBORATION"

    return "POSITIVE_BUT_INCONCLUSIVE"


def main() -> None:
    rows, metadata = load_rows()

    v18_start = v18_start_timestamp()

    gap = None

    if (
        metadata["max_ts"] is not None
        and v18_start is not None
    ):
        gap = v18_start - metadata["max_ts"]

    lines: list[str] = []

    lines.append("=" * 140)
    lines.append(
        "SKYNET V17 FIXED WALLPOS OUT-OF-SAMPLE "
        f"UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}"
    )
    lines.append("=" * 140)

    lines.append(
        "Purpose: test already-fixed V18 profiles "
        "on the earlier non-overlapping V17 period."
    )

    lines.append(
        "No parameter search. No path reconstruction. "
        "TIME-only result at recorded 5-minute close."
    )

    lines.append(
        "Stress formula: SHORT=-close_5m; "
        "cost=0.26% + recorded spread."
    )

    lines.append(
        "This is an endpoint proxy, not true future-ask execution."
    )

    lines.append("REAL_TRADING=OFF.")

    lines.append("")
    lines.append("SOURCE")

    lines.append(f"db={V17_DB}")

    lines.append(
        f"rows_total={metadata['total_rows']} "
        f"rows_closed={metadata['closed_rows']} "
        f"usable_rows={len(rows)}"
    )

    lines.append(
        f"v17_range={utc(metadata['min_ts'])} .. "
        f"{utc(metadata['max_ts'])}"
    )

    lines.append(
        f"v18_start={utc(v18_start)}"
    )

    lines.append(
        f"non_overlap_gap_seconds="
        f"{gap:.1f}"
        if gap is not None
        else "non_overlap_gap_seconds=UNKNOWN"
    )

    lines.append(
        f"current_blacklist_size="
        f"{metadata['blacklist_size']}"
    )

    output_json: dict[str, Any] = {
        "source": metadata,
        "v18_start": v18_start,
        "gap_seconds": gap,
        "profiles": {},
    }

    for name, config in CONFIGS.items():
        trades = select_trades(rows, config)
        result = metric(trades)

        halves = split_folds(trades, 2)
        folds = split_folds(trades, 4)

        decision = classify(result)

        lines.append("")
        lines.append("-" * 140)
        lines.append(name)
        lines.append("-" * 140)

        lines.append(
            "rule="
            f"pc={config['pc_min']:.2f}.."
            f"{config['pc_max']:.2f} "
            f"vol>={config['vol_min']:.1f} "
            f"spread<={config['spread_max']:.2f} "
            f"rank={config['rank_min']}.."
            f"{config['rank_max']} "
            f"wall_positive="
            f"{int(config['wall_positive'])}"
        )

        lines.append(
            "ALL    " + format_metric(result)
        )

        for index, half in enumerate(halves, 1):
            lines.append(
                f"HALF{index}  "
                + format_metric(metric(half))
            )

        positive_folds = 0

        for index, fold in enumerate(folds, 1):
            fold_result = metric(fold)

            if (
                fold_result["n"] > 0
                and fold_result["sum"] > 0
            ):
                positive_folds += 1

            lines.append(
                f"FOLD{index}  "
                + format_metric(fold_result)
            )

        lines.append(
            f"POSITIVE_FOLDS={positive_folds}/4"
        )

        lines.append(
            f"V17_OOS_DECISION={decision}"
        )

        lines.append("TRADES:")

        if not trades:
            lines.append("  [EMPTY]")
        else:
            for trade in trades:
                lines.append(
                    "  "
                    f"{utc(trade['ts'])} "
                    f"{trade['symbol']:<12} "
                    f"pc={trade['pc']:+.3f}% "
                    f"vol=x{trade['vol']:.1f} "
                    f"rank={trade['rank']:3d} "
                    f"sp={trade['spread']:.2f}bps "
                    f"wall={trade['wall']:+.3f} "
                    f"close5={trade['close_5m']:+.3f}% "
                    f"stress=${trade['stress_net']:+.5f}"
                )

        output_json["profiles"][name] = {
            "config": config,
            "metric": result,
            "positive_folds": positive_folds,
            "decision": decision,
            "trades": trades,
        }

    r80 = output_json["profiles"]["WALLPOS_R80"]
    r120 = output_json["profiles"]["WALLPOS_R120"]
    marginal = output_json["profiles"][
        "R120_MARGINAL_81_120"
    ]

    lines.append("")
    lines.append("=" * 140)
    lines.append("FINAL INTERPRETATION")
    lines.append("=" * 140)

    lines.append(
        f"R80={r80['decision']}"
    )
    lines.append(
        f"R120={r120['decision']}"
    )
    lines.append(
        f"R120_MARGINAL={marginal['decision']}"
    )

    lines.append(
        "This V17 period predates the V18 dataset and "
        "therefore supplies independent historical evidence."
    )

    lines.append(
        "It does not replace exact forward because V17 "
        "did not record the future exit ask."
    )

    lines.append(
        "Forward 10/20/40 gates remain unchanged."
    )

    lines.append("REAL_DECISION=BLOCKED")
    lines.append("REAL_TRADING=OFF")

    text = "\n".join(lines) + "\n"

    REPORT.write_text(
        text,
        encoding="utf-8",
    )

    JSON_REPORT.write_text(
        json.dumps(
            output_json,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(text)


if __name__ == "__main__":
    main()
