#!/usr/bin/env python3

import json
import math
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "v18_executable_proxy_replay_latest.txt"

NOTIONAL_USD = 12.0
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

LANES = {
    "SURVIVOR_PC050_SP15_NOBAN": {
        "pc_min": 0.30,
        "pc_max": 0.50,
        "vol_min": 12.0,
        "spread_max": 1.50,
        "rank_max": 50,
        "tp": 3.0,
        "sl": 0.3,
        "ban_after_sl": 0,
    },

    "WF_PC120_SL03_BAN1": {
        "pc_min": 0.30,
        "pc_max": 1.20,
        "vol_min": 12.0,
        "spread_max": 2.00,
        "rank_max": 30,
        "tp": 3.0,
        "sl": 0.3,
        "ban_after_sl": 1,
    },

    "WF_PC120_SL05_BAN1": {
        "pc_min": 0.30,
        "pc_max": 1.20,
        "vol_min": 12.0,
        "spread_max": 2.00,
        "rank_max": 30,
        "tp": 3.0,
        "sl": 0.5,
        "ban_after_sl": 1,
    },

    "CONTROL_STAGE2": {
        "pc_min": 0.30,
        "pc_max": 0.80,
        "vol_min": 15.0,
        "spread_max": 2.00,
        "rank_max": 30,
        "tp": 3.0,
        "sl": 0.3,
        "ban_after_sl": 1,
    },
}

SCENARIOS = {
    # Recorded entry spread is propagated through the path.
    "LOW_X1": {
        "cost_pct": 0.04,
        "spread_multiplier": 1.00,
    },

    "CFG_X1": {
        "cost_pct": 0.16,
        "spread_multiplier": 1.00,
    },

    # Exit spread is assumed 50% wider than at entry.
    "CFG_X15": {
        "cost_pct": 0.16,
        "spread_multiplier": 1.50,
    },

    # 0.16% fees + 0.10% additional execution/slippage stress.
    "STRESS_X15": {
        "cost_pct": 0.26,
        "spread_multiplier": 1.50,
    },

    # Very hostile spread regime.
    "STRESS_X2": {
        "cost_pct": 0.26,
        "spread_multiplier": 2.00,
    },
}


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


def parse_timestamp(row):
    ts = fnum(row.get("ts"))

    if ts is not None and ts > 0:
        return ts

    raw = str(row.get("time_iso") or "").strip()
    raw = raw.replace(" UTC", "").replace("Z", "+00:00")

    try:
        result = datetime.fromisoformat(raw)

        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)

        return result.timestamp()
    except Exception:
        return None


def parse_path(raw):
    try:
        data = json.loads(raw or "[]")
    except Exception:
        return []

    points = []

    if not isinstance(data, list):
        return []

    for item in data:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue

        age = fnum(item[0])
        diff_pct = fnum(item[1])

        if age is None or diff_pct is None:
            continue

        if age < 0 or age > 600:
            continue

        points.append((age, diff_pct))

    points.sort(key=lambda value: value[0])

    deduped = []
    last_age = None

    for point in points:
        if last_age is not None and point[0] == last_age:
            deduped[-1] = point
        else:
            deduped.append(point)
            last_age = point[0]

    return deduped


def clean_symbol(row):
    return str(
        row.get("clean_symbol")
        or row.get("symbol")
        or ""
    ).replace("_USDT", "").upper()


def passes(row, config):
    symbol = clean_symbol(row)

    if not symbol or symbol in CURRENT_BLACKLIST:
        return False

    pc = fnum(row.get("price_change"))
    vol = fnum(row.get("vol_ratio"))
    spread = fnum(row.get("spread_bps"))
    rank = fnum(row.get("rank"))
    entry_price = fnum(row.get("entry_price"))
    bid1 = fnum(row.get("bid1"))
    ask1 = fnum(row.get("ask1"))

    if None in (
        pc,
        vol,
        spread,
        rank,
        entry_price,
        bid1,
        ask1,
    ):
        return False

    if entry_price <= 0 or bid1 <= 0 or ask1 <= bid1:
        return False

    return (
        config["pc_min"] <= pc <= config["pc_max"]
        and vol >= config["vol_min"]
        and spread <= config["spread_max"]
        and rank <= config["rank_max"]
    )


def executable_outcome(
    row,
    config,
    spread_multiplier,
):
    entry_reference = float(row["entry_price"])
    entry_bid = float(row["bid1"])
    entry_ask = float(row["ask1"])

    if (
        entry_reference <= 0
        or entry_bid <= 0
        or entry_ask <= entry_bid
    ):
        return None

    entry_mid = (entry_bid + entry_ask) / 2.0
    half_spread_ratio = (
        (entry_ask - entry_bid)
        / (2.0 * entry_mid)
    )

    # Converts the recorded ticker path into a mid-price path.
    reference_to_mid = entry_mid / entry_reference

    path = row["_path"]

    if not path:
        return None

    last_result = None

    for age, diff_pct in path:
        future_reference = (
            entry_reference
            * (1.0 + diff_pct / 100.0)
        )

        future_mid = (
            future_reference
            * reference_to_mid
        )

        future_ask = future_mid * (
            1.0
            + spread_multiplier * half_spread_ratio
        )

        gross_pct = (
            (entry_bid - future_ask)
            / entry_bid
        ) * 100.0

        last_result = (
            gross_pct,
            "TIME",
            age,
            future_ask,
        )

        # The exact live service also exits at the observed price
        # after the boundary is crossed, not at an ideal stop price.
        if gross_pct <= -float(config["sl"]):
            return (
                gross_pct,
                "SL",
                age,
                future_ask,
            )

        if gross_pct >= float(config["tp"]):
            return (
                gross_pct,
                "TP",
                age,
                future_ask,
            )

    return last_result


def profit_factor(values):
    positive = sum(value for value in values if value > 0)
    negative = -sum(value for value in values if value < 0)

    if negative <= 0:
        return 999.0 if positive > 0 else 0.0

    return positive / negative


def summarize(trades, skipped):
    values = [trade["net_pct"] for trade in trades]

    symbol_net = defaultdict(float)

    for trade in trades:
        symbol_net[trade["symbol"]] += trade["net_pct"]

    positive_symbols = {
        symbol: max(net, 0.0)
        for symbol, net in symbol_net.items()
    }

    total_positive = sum(positive_symbols.values())

    concentration = (
        max(positive_symbols.values()) / total_positive
        if positive_symbols and total_positive > 0
        else 0.0
    )

    n = len(trades)

    return {
        "n": n,
        "net": sum(values),
        "avg": sum(values) / n if n else 0.0,
        "wr": (
            100.0
            * sum(1 for value in values if value > 0)
            / n
            if n
            else 0.0
        ),
        "pf": profit_factor(values),
        "tp": sum(
            1 for trade in trades
            if trade["reason"] == "TP"
        ),
        "sl": sum(
            1 for trade in trades
            if trade["reason"] == "SL"
        ),
        "time": sum(
            1 for trade in trades
            if trade["reason"] == "TIME"
        ),
        "conc": concentration,
        "symbols": len(symbol_net),
        "skipped": skipped,
    }


def simulate(
    rows,
    config,
    cost_pct,
    spread_multiplier,
):
    busy_until = None
    last_open_by_symbol = {}
    symbol_sl = defaultdict(int)
    banned = set()

    trades = []

    skipped = {
        "filter": 0,
        "busy": 0,
        "cooldown": 0,
        "ban": 0,
        "path": 0,
    }

    for row in rows:
        symbol = clean_symbol(row)

        if not passes(row, config):
            skipped["filter"] += 1
            continue

        if (
            int(config["ban_after_sl"]) > 0
            and symbol in banned
        ):
            skipped["ban"] += 1
            continue

        timestamp = row["_timestamp"]

        if timestamp is None:
            continue

        if (
            busy_until is not None
            and timestamp < busy_until
        ):
            skipped["busy"] += 1
            continue

        previous = last_open_by_symbol.get(symbol)

        if (
            previous is not None
            and timestamp - previous
            < COOLDOWN_SECONDS
        ):
            skipped["cooldown"] += 1
            continue

        result = executable_outcome(
            row=row,
            config=config,
            spread_multiplier=spread_multiplier,
        )

        if result is None:
            skipped["path"] += 1
            continue

        gross_pct, reason, exit_age, exit_ask = result
        net_pct = gross_pct - cost_pct

        trades.append({
            "id": int(row["id"]),
            "timestamp": timestamp,
            "symbol": symbol,
            "reason": reason,
            "gross_pct": gross_pct,
            "net_pct": net_pct,
            "exit_age": exit_age,
            "entry_bid": float(row["bid1"]),
            "exit_ask": exit_ask,
        })

        last_open_by_symbol[symbol] = timestamp

        busy_until = timestamp + max(
            float(exit_age),
            1.0,
        )

        if (
            reason == "SL"
            and int(config["ban_after_sl"]) > 0
        ):
            symbol_sl[symbol] += 1

            if (
                symbol_sl[symbol]
                >= int(config["ban_after_sl"])
            ):
                banned.add(symbol)

    return summarize(trades, skipped)


def format_stats(stats):
    dollars = stats["net"] * NOTIONAL_USD / 100.0

    return (
        f"n={stats['n']:4d} "
        f"net={stats['net']:+8.3f}% "
        f"(${dollars:+.3f}) "
        f"avg={stats['avg']:+7.4f}% "
        f"WR={stats['wr']:5.1f}% "
        f"PF={stats['pf']:6.2f} "
        f"TP={stats['tp']:3d} "
        f"SL={stats['sl']:3d} "
        f"TIME={stats['time']:3d} "
        f"symbols={stats['symbols']:3d} "
        f"conc={stats['conc']:5.1%}"
    )


def main():
    if not DB.exists():
        raise SystemExit(f"missing database: {DB}")

    connection = sqlite3.connect(
        f"file:{DB}?mode=ro",
        uri=True,
        timeout=30,
    )
    connection.row_factory = sqlite3.Row

    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(signals)"
        ).fetchall()
    }

    required = {
        "id",
        "ts",
        "time_iso",
        "symbol",
        "clean_symbol",
        "entry_price",
        "price_change",
        "vol_ratio",
        "rank",
        "spread_bps",
        "bid1",
        "ask1",
        "path_json",
        "closed",
    }

    missing = sorted(required - columns)

    if missing:
        raise SystemExit(
            f"missing database columns: {missing}"
        )

    raw_rows = connection.execute("""
        SELECT
            id,
            ts,
            time_iso,
            symbol,
            clean_symbol,
            entry_price,
            price_change,
            vol_ratio,
            rank,
            spread_bps,
            bid1,
            ask1,
            path_json,
            closed
        FROM signals
        WHERE closed = 1
          AND path_json IS NOT NULL
          AND bid1 IS NOT NULL
          AND ask1 IS NOT NULL
          AND entry_price IS NOT NULL
        ORDER BY id ASC
    """).fetchall()

    connection.close()

    rows = []

    for source in raw_rows:
        row = dict(source)
        row["_timestamp"] = parse_timestamp(row)
        row["_path"] = parse_path(row.get("path_json"))

        if (
            row["_timestamp"] is None
            or len(row["_path"]) < 2
        ):
            continue

        rows.append(row)

    if len(rows) < 40:
        raise SystemExit(
            f"not enough usable closed paths: {len(rows)}"
        )

    split = int(len(rows) * 0.75)

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

    results = {}

    lines = []

    lines.append("=" * 150)
    lines.append(
        "V18 EXECUTABLE-PRICE PROXY REPLAY "
        f"UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}"
    )
    lines.append("=" * 150)

    lines.append(f"db={DB}")
    lines.append(
        f"usable_closed_paths={len(rows)} "
        f"train75={len(train_rows)} "
        f"test25={len(test_rows)}"
    )
    lines.append(
        f"first={rows[0]['time_iso']} "
        f"last={rows[-1]['time_iso']}"
    )
    lines.append(
        "Entry: recorded bid1. "
        "Exit proxy: recorded ticker path converted to future mid, "
        "then ask spread applied."
    )
    lines.append(
        "This includes recorded entry spread but assumes the "
        "selected spread multiplier persists through the trade."
    )
    lines.append(
        "It is stricter than last-price replay, "
        "but it is still not a replacement for live exact bid/ask forward."
    )
    lines.append("REAL_TRADING=OFF.")

    for lane_name, config in LANES.items():
        results[lane_name] = {}

        lines.append("")
        lines.append("=" * 150)
        lines.append(lane_name)
        lines.append("=" * 150)

        lines.append(
            f"rule pc={config['pc_min']:.2f}.."
            f"{config['pc_max']:.2f} "
            f"vol>={config['vol_min']:.1f} "
            f"spread<={config['spread_max']:.2f} "
            f"rank<={config['rank_max']} "
            f"TP={config['tp']:.2f}% "
            f"SL={config['sl']:.2f}% "
            f"ban_after_sl={config['ban_after_sl']}"
        )

        for scenario_name, scenario in SCENARIOS.items():
            train = simulate(
                train_rows,
                config,
                scenario["cost_pct"],
                scenario["spread_multiplier"],
            )

            test = simulate(
                test_rows,
                config,
                scenario["cost_pct"],
                scenario["spread_multiplier"],
            )

            all_stats = simulate(
                rows,
                config,
                scenario["cost_pct"],
                scenario["spread_multiplier"],
            )

            fold_stats = [
                simulate(
                    fold,
                    config,
                    scenario["cost_pct"],
                    scenario["spread_multiplier"],
                )
                for fold in folds
            ]

            positive_folds = sum(
                1
                for stats in fold_stats
                if stats["n"] > 0 and stats["net"] > 0
            )

            results[lane_name][scenario_name] = {
                "train": train,
                "test": test,
                "all": all_stats,
                "folds": fold_stats,
                "positive_folds": positive_folds,
            }

            lines.append("")
            lines.append(
                f"{scenario_name} "
                f"cost={scenario['cost_pct']:.2f}% "
                f"spread_x={scenario['spread_multiplier']:.2f}"
            )
            lines.append(
                "  TRAIN75 " + format_stats(train)
            )
            lines.append(
                "  TEST25  " + format_stats(test)
            )
            lines.append(
                "  ALL     " + format_stats(all_stats)
            )

            fold_text = []

            for index, stats in enumerate(
                fold_stats,
                1,
            ):
                fold_text.append(
                    f"F{index}:"
                    f"n={stats['n']} "
                    f"net={stats['net']:+.2f}% "
                    f"PF={stats['pf']:.2f}"
                )

            lines.append(
                f"  FOLDS {positive_folds}/4 positive | "
                + " | ".join(fold_text)
            )

    lines.append("")
    lines.append("=" * 150)
    lines.append("DECISION")
    lines.append("=" * 150)

    robust_lanes = []
    fragile_lanes = []

    for lane_name in LANES:
        base = results[lane_name]["CFG_X1"]
        wide = results[lane_name]["CFG_X15"]
        stress = results[lane_name]["STRESS_X15"]

        base_pass = (
            base["test"]["n"] >= 10
            and base["all"]["net"] > 0
            and base["test"]["net"] > 0
            and base["test"]["pf"] >= 1.15
            and base["positive_folds"] >= 3
        )

        wide_pass = (
            wide["all"]["net"] > 0
            and wide["test"]["net"] > 0
            and wide["test"]["pf"] >= 1.10
            and wide["positive_folds"] >= 3
        )

        stress_pass = (
            stress["all"]["net"] > 0
            and stress["test"]["net"] > 0
        )

        if base_pass and wide_pass:
            robust_lanes.append(lane_name)

            flag = (
                "ROBUST_WITH_STRESS"
                if stress_pass
                else "ROBUST_CFG_ONLY"
            )
        elif base_pass:
            fragile_lanes.append(lane_name)
            flag = "FRAGILE_SPREAD_SENSITIVE"
        else:
            flag = "FAIL_EXECUTION_PROXY"

        lines.append(
            f"{flag:<28} {lane_name} | "
            f"CFG test={base['test']['net']:+.3f}% "
            f"PF={base['test']['pf']:.2f} "
            f"folds={base['positive_folds']}/4 | "
            f"WIDE test={wide['test']['net']:+.3f}% "
            f"PF={wide['test']['pf']:.2f} | "
            f"STRESS test={stress['test']['net']:+.3f}%"
        )

    lines.append("")

    if robust_lanes:
        lines.append(
            "PROXY_SURVIVORS="
            + ",".join(robust_lanes)
        )
        lines.append(
            "Keep these in exact bid/ask forward. "
            "Do not enable real until exact forward confirms them."
        )
    elif fragile_lanes:
        lines.append(
            "ONLY_FRAGILE_SURVIVORS="
            + ",".join(fragile_lanes)
        )
        lines.append(
            "Edge disappears under wider spread. "
            "Exact forward remains mandatory; real stays OFF."
        )
    else:
        lines.append(
            "NO_EXECUTION_PROXY_SURVIVOR: "
            "stop spending days on this static fade family."
        )
        lines.append(
            "Keep recorder/exact diagnostics, "
            "but move active research to another entry model."
        )

    lines.append("REAL_TRADING=OFF.")

    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
