#!/usr/bin/env python3

from __future__ import annotations

import csv
import itertools
import json
import math
import sqlite3
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path("/root/skynet")

V18_DB = ROOT / "data/v18_micro_paths.sqlite3"
META_DIR = ROOT / "data/replay_meta_proxy"

OUT_DIR = ROOT / "safe_exports/research_rescue"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LATEST = ROOT / "v18_research_rescue_latest.txt"

NOTIONAL_USD = 12.0

# Bid/ask spread is embedded in executable move.
# These are additional round-trip costs.
CFG_COST_PCT = 0.16
STRESS_COST_PCT = 0.26

COOLDOWN_SECONDS = 180.0

CURRENT_BLACKLIST = {
    "ALLO",
    "BREV",
    "KORU",
    "LIT",
    "M",
    "PENDLE",
    "RIF",
    "SKYAI",
    "SOXL",
    "TAC",
    "XPL",
}


def utc_tag() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_UTC"
    )


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


def parse_iso(value: Any) -> float | None:
    raw = str(value or "").strip()

    if not raw:
        return None

    raw = raw.replace(" UTC", "").replace("Z", "+00:00")

    try:
        result = datetime.fromisoformat(raw)

        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)

        return result.timestamp()
    except Exception:
        return None


def parse_path(
    raw: Any,
    close_pct: float | None,
) -> list[tuple[float, float]]:
    try:
        data = json.loads(raw or "[]")
    except Exception:
        data = []

    points: list[tuple[float, float]] = []

    if isinstance(data, list):
        for item in data:
            if (
                not isinstance(item, (list, tuple))
                or len(item) < 2
            ):
                continue

            age = sf(item[0])
            diff = sf(item[1])

            if age is None or diff is None:
                continue

            if age < 0 or age > 600:
                continue

            points.append((age, diff))

    points.sort(key=lambda item: item[0])

    deduped: list[tuple[float, float]] = []

    for point in points:
        if (
            deduped
            and abs(deduped[-1][0] - point[0]) < 1e-9
        ):
            deduped[-1] = point
        else:
            deduped.append(point)

    if close_pct is not None:
        if not deduped:
            deduped.append((300.0, close_pct))
        elif deduped[-1][0] < 295:
            deduped.append((300.0, close_pct))

    return deduped


def executable_short_outcome(
    row: dict[str, Any],
    stop_pct: float | None,
) -> dict[str, float | str] | None:
    reference = sf(row.get("entry_price"))
    bid = sf(row.get("bid1"))
    ask = sf(row.get("ask1"))

    if (
        reference is None
        or bid is None
        or ask is None
        or reference <= 0
        or bid <= 0
        or ask <= bid
    ):
        return None

    mid = (bid + ask) / 2.0

    reference_to_mid = mid / reference
    half_spread_ratio = (ask - bid) / (2.0 * mid)

    path = row.get("_path") or []

    if not path:
        return None

    final_move = None
    final_age = 300.0
    reason = "TIME"

    for age, diff_pct in path:
        future_reference = (
            reference
            * (1.0 + float(diff_pct) / 100.0)
        )

        future_mid = future_reference * reference_to_mid

        # Exit from SHORT at executable ask.
        future_ask = future_mid * (
            1.0 + half_spread_ratio
        )

        short_move_pct = (
            (bid - future_ask) / bid
        ) * 100.0

        final_move = short_move_pct
        final_age = float(age)

        if (
            stop_pct is not None
            and short_move_pct <= -abs(stop_pct)
        ):
            reason = "SL"
            break

    if final_move is None:
        return None

    return {
        "gross_pct": float(final_move),
        "cfg_pct": float(final_move) - CFG_COST_PCT,
        "stress_pct": (
            float(final_move) - STRESS_COST_PCT
        ),
        "age": max(float(final_age), 1.0),
        "reason": reason,
    }


def profit_factor(values: list[float]) -> float:
    positive = sum(value for value in values if value > 0)
    negative = -sum(value for value in values if value < 0)

    if negative <= 0:
        return 999.0 if positive > 0 else 0.0

    return positive / negative


def metric(
    trades: list[dict[str, Any]],
    key: str,
) -> dict[str, Any]:
    values = [float(trade[key]) for trade in trades]

    if not values:
        return {
            "n": 0,
            "sum": 0.0,
            "avg": 0.0,
            "wr": 0.0,
            "pf": 0.0,
            "median": 0.0,
            "leave_best": 0.0,
            "best_symbol": "-",
            "best_symbol_sum": 0.0,
            "positive_share": 0.0,
        }

    by_symbol: dict[str, float] = defaultdict(float)

    for trade in trades:
        by_symbol[str(trade["symbol"])] += float(
            trade[key]
        )

    best_symbol, best_symbol_sum = max(
        by_symbol.items(),
        key=lambda item: item[1],
    )

    positive_total = sum(
        max(value, 0.0)
        for value in by_symbol.values()
    )

    positive_share = (
        max(best_symbol_sum, 0.0) / positive_total
        if positive_total > 0
        else 0.0
    )

    total = sum(values)

    return {
        "n": len(values),
        "sum": total,
        "avg": total / len(values),
        "wr": (
            100.0
            * sum(1 for value in values if value > 0)
            / len(values)
        ),
        "pf": profit_factor(values),
        "median": statistics.median(values),
        "leave_best": total - best_symbol_sum,
        "best_symbol": best_symbol,
        "best_symbol_sum": best_symbol_sum,
        "positive_share": positive_share,
    }


def fmt_metric(result: dict[str, Any]) -> str:
    return (
        f"n={result['n']:4d} "
        f"sum=${result['sum']:+.4f} "
        f"avg=${result['avg']:+.5f} "
        f"WR={result['wr']:5.1f}% "
        f"PF={result['pf']:6.2f} "
        f"leave_best=${result['leave_best']:+.4f} "
        f"best={result['best_symbol']}"
        f"({result['positive_share']:.1%})"
    )


def load_v18_rows() -> list[dict[str, Any]]:
    if not V18_DB.exists():
        return []

    connection = sqlite3.connect(
        f"file:{V18_DB}?mode=ro",
        uri=True,
        timeout=30,
    )
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT
            id,
            ts,
            time_iso,
            symbol,
            clean_symbol,
            entry_price,
            price_change,
            vol_ratio,
            oi_change,
            rank,
            spread_bps,
            bid1,
            ask1,
            imb_5,
            imb_20,
            wall_skew,
            max_up,
            max_down,
            close_pct,
            path_json
        FROM signals
        WHERE closed = 1
          AND entry_price IS NOT NULL
          AND bid1 IS NOT NULL
          AND ask1 IS NOT NULL
          AND price_change IS NOT NULL
          AND vol_ratio IS NOT NULL
          AND spread_bps IS NOT NULL
          AND rank IS NOT NULL
        ORDER BY ts ASC, id ASC
    """).fetchall()

    connection.close()

    output: list[dict[str, Any]] = []

    for source in rows:
        row = dict(source)

        symbol = str(
            row.get("clean_symbol")
            or row.get("symbol")
            or ""
        ).replace("_USDT", "").upper()

        if not symbol or symbol in CURRENT_BLACKLIST:
            continue

        timestamp = sf(row.get("ts"))

        if timestamp is None:
            timestamp = parse_iso(row.get("time_iso"))

        pc = sf(row.get("price_change"))
        vol = sf(row.get("vol_ratio"))
        spread = sf(row.get("spread_bps"))
        rank = sf(row.get("rank"))

        if None in (timestamp, pc, vol, spread, rank):
            continue

        # This lab is specifically for upward anomalies
        # followed by a potential SHORT fade.
        if pc < 0.15:
            continue

        close_pct = sf(row.get("close_pct"))

        row["_path"] = parse_path(
            row.get("path_json"),
            close_pct,
        )

        if not row["_path"]:
            continue

        time_outcome = executable_short_outcome(
            row,
            stop_pct=None,
        )

        sl_outcome = executable_short_outcome(
            row,
            stop_pct=0.30,
        )

        if time_outcome is None or sl_outcome is None:
            continue

        max_up = sf(row.get("max_up"), 0.0) or 0.0
        max_down = sf(row.get("max_down"), 0.0) or 0.0

        row["_symbol"] = symbol
        row["_ts"] = float(timestamp)
        row["_pc"] = float(pc)
        row["_vol"] = float(vol)
        row["_spread"] = float(spread)
        row["_rank"] = float(rank)
        row["_oi"] = sf(row.get("oi_change"))
        row["_imb5"] = sf(row.get("imb_5"))
        row["_imb20"] = sf(row.get("imb_20"))
        row["_wall"] = sf(row.get("wall_skew"))

        # Correct directional labels for SHORT:
        # price down = favourable; price up = adverse.
        row["_short_mfe"] = max(0.0, -max_down)
        row["_short_mae"] = -max(0.0, max_up)

        row["_outcomes"] = {
            "TIME": time_outcome,
            "SL03": sl_outcome,
        }

        output.append(row)

    return output


EXTRA_FILTERS: dict[
    str,
    Callable[[dict[str, Any]], bool],
] = {
    "NONE": lambda row: True,

    "OI_NEG": lambda row: (
        row["_oi"] is not None
        and row["_oi"] <= 0
    ),

    "OI_LE_M1": lambda row: (
        row["_oi"] is not None
        and row["_oi"] <= -1
    ),

    "OI_POS": lambda row: (
        row["_oi"] is not None
        and row["_oi"] >= 0
    ),

    "OI_GE_1": lambda row: (
        row["_oi"] is not None
        and row["_oi"] >= 1
    ),

    "IMB_ASK": lambda row: (
        row["_imb5"] is not None
        and row["_imb5"] <= -0.10
    ),

    "IMB_BID": lambda row: (
        row["_imb5"] is not None
        and row["_imb5"] >= 0.10
    ),

    "IMB_NEUTRAL": lambda row: (
        row["_imb5"] is not None
        and abs(row["_imb5"]) < 0.10
    ),

    "WALL_NEG": lambda row: (
        row["_wall"] is not None
        and row["_wall"] < 0
    ),

    "WALL_POS": lambda row: (
        row["_wall"] is not None
        and row["_wall"] > 0
    ),
}


def config_name(config: dict[str, Any]) -> str:
    return (
        f"pc={config['pc_min']:.2f}.."
        f"{config['pc_max']:.2f}"
        f"|vol>={config['vol_min']:.0f}"
        f"|sp<={config['spread_max']:.1f}"
        f"|rank<={config['rank_max']}"
        f"|exit={config['exit_mode']}"
        f"|extra={config['extra']}"
    )


def select_v18_trades(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    trades: list[dict[str, Any]] = []

    busy_until: float | None = None
    last_by_symbol: dict[str, float] = {}

    extra = EXTRA_FILTERS[config["extra"]]

    for row in rows:
        if not (
            config["pc_min"]
            <= row["_pc"]
            <= config["pc_max"]
        ):
            continue

        if row["_vol"] < config["vol_min"]:
            continue

        if row["_spread"] > config["spread_max"]:
            continue

        if row["_rank"] > config["rank_max"]:
            continue

        if not extra(row):
            continue

        timestamp = row["_ts"]
        symbol = row["_symbol"]

        if (
            busy_until is not None
            and timestamp < busy_until
        ):
            continue

        previous = last_by_symbol.get(symbol)

        if (
            previous is not None
            and timestamp - previous < COOLDOWN_SECONDS
        ):
            continue

        outcome = row["_outcomes"][config["exit_mode"]]

        trades.append({
            "symbol": symbol,
            "ts": timestamp,
            "cfg": (
                float(outcome["cfg_pct"])
                * NOTIONAL_USD
                / 100.0
            ),
            "stress": (
                float(outcome["stress_pct"])
                * NOTIONAL_USD
                / 100.0
            ),
            "gross": (
                float(outcome["gross_pct"])
                * NOTIONAL_USD
                / 100.0
            ),
            "reason": outcome["reason"],
            "short_mfe": row["_short_mfe"],
            "short_mae": row["_short_mae"],
        })

        last_by_symbol[symbol] = timestamp

        busy_until = (
            timestamp + float(outcome["age"])
        )

    return trades


def evaluate_v18_config(
    train_rows: list[dict[str, Any]],
    test_rows: list[dict[str, Any]],
    all_rows: list[dict[str, Any]],
    folds: list[list[dict[str, Any]]],
    config: dict[str, Any],
) -> dict[str, Any]:
    train_trades = select_v18_trades(
        train_rows,
        config,
    )
    test_trades = select_v18_trades(
        test_rows,
        config,
    )
    all_trades = select_v18_trades(
        all_rows,
        config,
    )

    fold_trades = [
        select_v18_trades(fold, config)
        for fold in folds
    ]

    train_cfg = metric(train_trades, "cfg")
    train_stress = metric(train_trades, "stress")

    test_cfg = metric(test_trades, "cfg")
    test_stress = metric(test_trades, "stress")

    all_cfg = metric(all_trades, "cfg")
    all_stress = metric(all_trades, "stress")

    positive_cfg_folds = sum(
        1
        for trades in fold_trades
        if metric(trades, "cfg")["sum"] > 0
    )

    positive_stress_folds = sum(
        1
        for trades in fold_trades
        if metric(trades, "stress")["sum"] > 0
    )

    robust = (
        train_cfg["n"] >= 50
        and test_cfg["n"] >= 20

        and train_cfg["sum"] > 0
        and test_cfg["sum"] > 0

        and train_stress["sum"] > 0
        and test_stress["sum"] > 0

        and train_stress["pf"] >= 1.10
        and test_stress["pf"] >= 1.10

        and all_cfg["leave_best"] > 0
        and all_stress["leave_best"] > 0

        and all_stress["positive_share"] <= 0.45

        and positive_cfg_folds >= 3
        and positive_stress_folds >= 3
    )

    score = (
        test_stress["sum"] * 3.0
        + train_stress["sum"]
        + all_stress["leave_best"]
        + min(test_stress["pf"], 4.0) * 0.02
        - all_stress["positive_share"] * 0.10
    )

    return {
        "config": config,
        "train_cfg": train_cfg,
        "train_stress": train_stress,
        "test_cfg": test_cfg,
        "test_stress": test_stress,
        "all_cfg": all_cfg,
        "all_stress": all_stress,
        "positive_cfg_folds": positive_cfg_folds,
        "positive_stress_folds": positive_stress_folds,
        "robust": robust,
        "score": score,
    }


def build_base_configs() -> list[dict[str, Any]]:
    pc_ranges = [
        (0.20, 0.40),
        (0.30, 0.50),
        (0.40, 0.60),
        (0.50, 0.80),
        (0.30, 0.80),
        (0.80, 1.20),
        (1.20, 2.50),
    ]

    vol_mins = [5, 8, 12, 15, 20, 40]
    spread_maxes = [0.5, 1.0, 1.5, 2.0]
    rank_maxes = [20, 40, 80, 150]
    exit_modes = ["TIME", "SL03"]

    configs: list[dict[str, Any]] = []

    for (
        pc_range,
        vol_min,
        spread_max,
        rank_max,
        exit_mode,
    ) in itertools.product(
        pc_ranges,
        vol_mins,
        spread_maxes,
        rank_maxes,
        exit_modes,
    ):
        configs.append({
            "pc_min": pc_range[0],
            "pc_max": pc_range[1],
            "vol_min": float(vol_min),
            "spread_max": float(spread_max),
            "rank_max": int(rank_max),
            "exit_mode": exit_mode,
            "extra": "NONE",
        })

    return configs


def v18_directional_analysis(
    lines: list[str],
) -> None:
    rows = load_v18_rows()

    lines.append("")
    lines.append("=" * 150)
    lines.append("V18 DIRECTIONAL SHORT EXECUTION MINER")
    lines.append("=" * 150)

    if len(rows) < 100:
        lines.append(
            f"NOT_ENOUGH_ROWS n={len(rows)}"
        )
        return

    split = int(len(rows) * 0.70)

    train_rows = rows[:split]
    test_rows = rows[split:]

    cuts = [
        0,
        len(rows) // 4,
        len(rows) // 2,
        3 * len(rows) // 4,
        len(rows),
    ]

    folds = [
        rows[cuts[index]:cuts[index + 1]]
        for index in range(4)
    ]

    short_mfes = [row["_short_mfe"] for row in rows]
    short_maes = [row["_short_mae"] for row in rows]

    lines.append(f"db={V18_DB}")
    lines.append(
        f"usable_positive_pc_rows={len(rows)} "
        f"train70={len(train_rows)} "
        f"test30={len(test_rows)}"
    )
    lines.append(
        "Correct SHORT labels: "
        "MFE=-max_down; MAE=-max_up."
    )
    lines.append(
        "Execution: entry bid1, exit ask proxy from recorded path."
    )
    lines.append(
        f"CFG additional cost={CFG_COST_PCT:.2f}% | "
        f"STRESS={STRESS_COST_PCT:.2f}%"
    )
    lines.append(
        f"SHORT MFE avg={statistics.mean(short_mfes):.3f}% "
        f"median={statistics.median(short_mfes):.3f}%"
    )
    lines.append(
        f"SHORT MAE avg={statistics.mean(short_maes):.3f}% "
        f"median={statistics.median(short_maes):.3f}%"
    )

    base_configs = build_base_configs()

    prelim: list[tuple[float, dict[str, Any]]] = []

    for index, config in enumerate(base_configs, 1):
        trades = select_v18_trades(
            train_rows,
            config,
        )

        if len(trades) < 40:
            continue

        cfg_result = metric(trades, "cfg")
        stress_result = metric(trades, "stress")

        score = (
            stress_result["sum"]
            + cfg_result["sum"] * 0.25
            + min(stress_result["pf"], 3.0) * 0.01
            + stress_result["leave_best"] * 0.25
            - stress_result["positive_share"] * 0.05
        )

        prelim.append((score, config))

    prelim.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    # All holdout candidates are selected only from train data.
    selected_base = [
        config
        for _, config in prelim[:200]
    ]

    expanded: list[dict[str, Any]] = []

    for config in selected_base[:40]:
        for extra in EXTRA_FILTERS:
            if extra == "NONE":
                continue

            variant = dict(config)
            variant["extra"] = extra
            expanded.append(variant)

    candidates = selected_base + expanded

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()

    for config in candidates:
        name = config_name(config)

        if name in seen:
            continue

        seen.add(name)
        deduped.append(config)

    evaluated = [
        evaluate_v18_config(
            train_rows,
            test_rows,
            rows,
            folds,
            config,
        )
        for config in deduped
    ]

    robust = sorted(
        [
            item
            for item in evaluated
            if item["robust"]
        ],
        key=lambda item: item["score"],
        reverse=True,
    )

    top = sorted(
        evaluated,
        key=lambda item: item["score"],
        reverse=True,
    )[:40]

    lines.append("")
    lines.append(
        f"base_configs={len(base_configs)} "
        f"train_selected={len(selected_base)} "
        f"expanded={len(expanded)} "
        f"holdout_evaluated={len(evaluated)}"
    )

    lines.append("")
    lines.append("-" * 150)
    lines.append("ROBUST SHORT EXECUTION CANDIDATES")
    lines.append("-" * 150)

    if not robust:
        lines.append(
            "[EMPTY] No candidate survives train/test, "
            "stress cost, four folds and leave-best-symbol-out."
        )
    else:
        for index, item in enumerate(robust[:30], 1):
            lines.append(
                f"#{index:02d} "
                f"{config_name(item['config'])}"
            )
            lines.append(
                "  TRAIN CFG    "
                + fmt_metric(item["train_cfg"])
            )
            lines.append(
                "  TRAIN STRESS "
                + fmt_metric(item["train_stress"])
            )
            lines.append(
                "  TEST CFG     "
                + fmt_metric(item["test_cfg"])
            )
            lines.append(
                "  TEST STRESS  "
                + fmt_metric(item["test_stress"])
            )
            lines.append(
                "  ALL STRESS   "
                + fmt_metric(item["all_stress"])
            )
            lines.append(
                f"  FOLDS cfg="
                f"{item['positive_cfg_folds']}/4 "
                f"stress={item['positive_stress_folds']}/4"
            )

    lines.append("")
    lines.append("-" * 150)
    lines.append("TOP TRAIN-SELECTED RULES ON HOLDOUT")
    lines.append("-" * 150)

    for index, item in enumerate(top, 1):
        flag = "ROBUST" if item["robust"] else "FAIL"

        lines.append(
            f"#{index:02d} {flag:<6} "
            f"{config_name(item['config'])}"
        )
        lines.append(
            "  TRAIN STRESS "
            + fmt_metric(item["train_stress"])
        )
        lines.append(
            "  TEST STRESS  "
            + fmt_metric(item["test_stress"])
        )
        lines.append(
            "  ALL STRESS   "
            + fmt_metric(item["all_stress"])
        )
        lines.append(
            f"  FOLDS stress="
            f"{item['positive_stress_folds']}/4"
        )


def load_meta_rows(
    path: Path,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
        errors="ignore",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        for source in reader:
            row = dict(source)

            timestamp = parse_iso(row.get("time_iso"))

            if timestamp is None:
                continue

            row["_ts"] = timestamp
            row["_symbol"] = str(
                row.get("symbol") or "?"
            ).upper()

            for name in (
                "score",
                "pc",
                "vol_ratio",
                "trend",
                "btc",
                "oi",
                "spread",
                "bid5",
                "ask5",
                "base_net",
                "nf_net",
            ):
                row[f"_{name}"] = sf(row.get(name))

            rows.append(row)

    rows.sort(key=lambda row: row["_ts"])
    return rows


def meta_filter(
    row: dict[str, Any],
    config: dict[str, Any],
) -> bool:
    required = (
        row["_score"],
        row["_pc"],
        row["_vol_ratio"],
        row["_trend"],
        row["_oi"],
        row["_spread"],
    )

    if any(value is None for value in required):
        return False

    return (
        row["_score"] >= config["score_min"]
        and config["pc_min"]
        <= row["_pc"]
        <= config["pc_max"]
        and row["_vol_ratio"] <= config["vol_max"]
        and row["_trend"] >= config["trend_min"]
        and row["_oi"] >= config["oi_min"]
        and row["_spread"] <= config["spread_max"]
    )


def meta_trade_metric(
    rows: list[dict[str, Any]],
    key: str,
) -> dict[str, Any]:
    trades = [
        {
            "symbol": row["_symbol"],
            "net": float(row[key]),
        }
        for row in rows
        if row.get(key) is not None
    ]

    return metric(trades, "net")


def meta_config_name(config: dict[str, Any]) -> str:
    return (
        f"score>={config['score_min']}"
        f"|pc={config['pc_min']:.2f}.."
        f"{config['pc_max']:.2f}"
        f"|vol<={config['vol_max']:.0f}"
        f"|trend>={config['trend_min']:.2f}"
        f"|oi>={config['oi_min']:.1f}"
        f"|sp<={config['spread_max']:.1f}"
    )


def meta_holdout_analysis(
    lines: list[str],
) -> None:
    path = META_DIR / "meta_proxy_details.csv"
    rows = load_meta_rows(path)

    lines.append("")
    lines.append("=" * 150)
    lines.append("META DETAIL CHRONOLOGICAL HOLDOUT")
    lines.append("=" * 150)
    lines.append(f"source={path}")

    if not rows:
        lines.append("[EMPTY] Meta detail CSV not found.")
        return

    configs: list[dict[str, Any]] = []

    for (
        score_min,
        pc_range,
        vol_max,
        trend_min,
        oi_min,
        spread_max,
    ) in itertools.product(
        [3, 4, 5, 6],
        [
            (0.20, 0.40),
            (0.20, 0.50),
            (0.30, 0.50),
            (0.30, 0.65),
            (0.40, 0.65),
        ],
        [15, 20, 25, 30, 35],
        [0.20, 0.30, 0.40, 0.50, 0.70],
        [-0.50, 0.0, 0.50, 1.0],
        [1.0, 2.0, 3.0, 5.0],
    ):
        configs.append({
            "score_min": score_min,
            "pc_min": pc_range[0],
            "pc_max": pc_range[1],
            "vol_max": float(vol_max),
            "trend_min": float(trend_min),
            "oi_min": float(oi_min),
            "spread_max": float(spread_max),
        })

    lines.append(
        f"candidate_rows={len(rows)} "
        f"threshold_configs={len(configs)}"
    )

    for mode, status_field, net_field in (
        ("BASE", "base_status", "_base_net"),
        ("NOFOLLOW", "nf_status", "_nf_net"),
    ):
        trades = [
            row
            for row in rows
            if (
                row.get(status_field) == "TRADE"
                and row.get(net_field) is not None
            )
        ]

        split = int(len(trades) * 0.70)

        train = trades[:split]
        test = trades[split:]

        train_ranked: list[
            tuple[float, dict[str, Any], dict[str, Any]]
        ] = []

        for config in configs:
            selected = [
                row
                for row in train
                if meta_filter(row, config)
            ]

            result = meta_trade_metric(
                selected,
                net_field,
            )

            if result["n"] < 12:
                continue

            score = (
                result["sum"]
                + min(result["pf"], 3.0) * 0.02
                + result["leave_best"] * 0.25
                - result["positive_share"] * 0.05
            )

            train_ranked.append(
                (score, config, result)
            )

        train_ranked.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        evaluated: list[dict[str, Any]] = []

        for score, config, train_result in train_ranked[:150]:
            test_selected = [
                row
                for row in test
                if meta_filter(row, config)
            ]

            all_selected = [
                row
                for row in trades
                if meta_filter(row, config)
            ]

            test_result = meta_trade_metric(
                test_selected,
                net_field,
            )
            all_result = meta_trade_metric(
                all_selected,
                net_field,
            )

            robust = (
                train_result["n"] >= 12
                and test_result["n"] >= 5

                and train_result["sum"] > 0
                and test_result["sum"] > 0

                and train_result["pf"] >= 1.10
                and test_result["pf"] >= 1.10

                and all_result["leave_best"] > 0
                and all_result["positive_share"] <= 0.50
            )

            evaluated.append({
                "config": config,
                "train": train_result,
                "test": test_result,
                "all": all_result,
                "robust": robust,
                "score": (
                    test_result["sum"] * 3
                    + score
                ),
            })

        robust_rows = sorted(
            [
                item
                for item in evaluated
                if item["robust"]
            ],
            key=lambda item: item["score"],
            reverse=True,
        )

        top = sorted(
            evaluated,
            key=lambda item: item["score"],
            reverse=True,
        )[:25]

        lines.append("")
        lines.append("-" * 150)
        lines.append(
            f"META {mode}: trades={len(trades)} "
            f"train={len(train)} test={len(test)}"
        )
        lines.append("-" * 150)

        if not robust_rows:
            lines.append(
                "[EMPTY] No threshold subset survives "
                "chronological holdout and leave-best-symbol-out."
            )
        else:
            lines.append("ROBUST META SUBSETS:")

            for index, item in enumerate(
                robust_rows[:20],
                1,
            ):
                lines.append(
                    f"#{index:02d} "
                    f"{meta_config_name(item['config'])}"
                )
                lines.append(
                    "  TRAIN "
                    + fmt_metric(item["train"])
                )
                lines.append(
                    "  TEST  "
                    + fmt_metric(item["test"])
                )
                lines.append(
                    "  ALL   "
                    + fmt_metric(item["all"])
                )

        lines.append("TOP TRAIN-SELECTED SUBSETS:")

        for index, item in enumerate(top, 1):
            flag = "ROBUST" if item["robust"] else "FAIL"

            lines.append(
                f"#{index:02d} {flag:<6} "
                f"{meta_config_name(item['config'])}"
            )
            lines.append(
                "  TRAIN "
                + fmt_metric(item["train"])
            )
            lines.append(
                "  TEST  "
                + fmt_metric(item["test"])
            )
            lines.append(
                "  ALL   "
                + fmt_metric(item["all"])
            )


def main() -> None:
    lines: list[str] = []

    lines.append("=" * 150)
    lines.append(
        f"SKYNET V18 RESEARCH RESCUE LAB "
        f"UTC={utc_tag()}"
    )
    lines.append("=" * 150)

    lines.append(
        "Purpose: replace the broken LONG-only feature report "
        "with directional SHORT execution validation."
    )
    lines.append(
        "No strategy changes. No orders. "
        "Real trading remains OFF."
    )

    v18_directional_analysis(lines)
    meta_holdout_analysis(lines)

    lines.append("")
    lines.append("=" * 150)
    lines.append("DECISION RULE")
    lines.append("=" * 150)

    lines.append(
        "1. Empty ROBUST SHORT section: static V18 fade "
        "has no demonstrated execution-resistant edge."
    )
    lines.append(
        "2. Empty ROBUST META section: current META family "
        "remains rejected; NOFOLLOW is defensive only."
    )
    lines.append(
        "3. A non-empty section creates only a new "
        "exact-shadow candidate, never permission for real."
    )
    lines.append("REAL_TRADING=OFF.")

    text = "\n".join(lines) + "\n"

    output = OUT_DIR / (
        f"v18_research_rescue_{utc_tag()}.txt"
    )

    output.write_text(text, encoding="utf-8")
    LATEST.write_text(text, encoding="utf-8")

    print(text)
    print(f"REPORT={output}")


if __name__ == "__main__":
    main()
