#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/root/skynet")

EXACT_STATE = ROOT / "v18_exact_multi_shadow_state.json"
OVERRIDES = ROOT / "v18_exact_lane_gate_overrides.json"
GATE_STATE = ROOT / "v18_exact_forward_gate_state.json"
REPORT = ROOT / "v18_exact_forward_gate_latest.txt"

TARGETS = {
    "WF_PC050_SP15_NOBAN": {
        "label": "PC050_CONTROL",
    },
    "RESEARCH_PC120_250_WALLPOS_TIME": {
        "label": "WALLPOS_R80",
    },
    "RESEARCH_PC120_250_WALLPOS_R120_TIME": {
        "label": "WALLPOS_R120",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime(
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
            path.read_text(encoding="utf-8")
        )
    except Exception:
        return default


def save_json_atomic(
    path: Path,
    data: Any,
) -> None:
    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary.replace(path)


def profit_factor(
    positive: float,
    negative: float,
) -> float:
    if negative <= 0:
        return 999.0 if positive > 0 else 0.0

    return positive / negative


def concentration(
    recent: list[dict],
) -> dict[str, Any]:
    by_symbol: dict[str, float] = defaultdict(float)

    for event in recent:
        symbol = str(
            event.get("symbol") or "?"
        ).upper()

        try:
            value = float(event.get("net_stress", 0.0))
        except Exception:
            value = 0.0

        by_symbol[symbol] += value

    if not by_symbol:
        return {
            "symbols": 0,
            "best_symbol": "-",
            "best_sum": 0.0,
            "positive_share": 0.0,
            "leave_best": 0.0,
        }

    best_symbol, best_sum = max(
        by_symbol.items(),
        key=lambda item: item[1],
    )

    total = sum(by_symbol.values())

    positive_total = sum(
        max(value, 0.0)
        for value in by_symbol.values()
    )

    positive_share = (
        max(best_sum, 0.0) / positive_total
        if positive_total > 0
        else 0.0
    )

    return {
        "symbols": len(by_symbol),
        "best_symbol": best_symbol,
        "best_sum": best_sum,
        "positive_share": positive_share,
        "leave_best": total - best_sum,
    }


def disable_lane(
    overrides: dict,
    lane_name: str,
) -> None:
    overrides[lane_name] = False


def main() -> None:
    exact = load_json(EXACT_STATE, {})
    overrides = load_json(OVERRIDES, {})
    gate = load_json(
        GATE_STATE,
        {
            "lanes": {},
            "events": [],
        },
    )

    if not isinstance(overrides, dict):
        overrides = {}

    if not isinstance(gate, dict):
        gate = {
            "lanes": {},
            "events": [],
        }

    gate.setdefault("lanes", {})
    gate.setdefault("events", [])

    exact_lanes = exact.get("lanes", {})

    lines = [
        "=" * 120,
        f"SKYNET EXACT FORWARD GATE UTC={utc_now()}",
        "=" * 120,
        "Rules are preregistered. No threshold optimization.",
        "REAL_TRADING=OFF",
        "",
    ]

    new_events: list[str] = []
    override_changed = False

    for lane_name, target in TARGETS.items():
        lane = exact_lanes.get(lane_name)

        if not isinstance(lane, dict):
            lines.append(
                f"{target['label']} | "
                f"{lane_name} | STATE_MISSING"
            )
            continue

        stats = lane.get("stats", {})

        closed = int(stats.get("closed", 0) or 0)
        opened = int(stats.get("opened", 0) or 0)

        stress_sum = float(
            stats.get("stress_sum", 0.0) or 0.0
        )

        stress_pos = float(
            stats.get("stress_pos", 0.0) or 0.0
        )

        stress_neg = float(
            stats.get("stress_neg", 0.0) or 0.0
        )

        pf = profit_factor(
            stress_pos,
            stress_neg,
        )

        recent = list(
            stats.get("recent", [])
            if isinstance(stats.get("recent"), list)
            else []
        )

        symbol_stats = concentration(recent)

        lane_gate = gate["lanes"].setdefault(
            lane_name,
            {
                "next_gate": 10,
                "status": "COLLECTING_TO_10",
            },
        )

        next_gate = int(
            lane_gate.get("next_gate", 10)
        )

        effective_enabled = bool(
            overrides.get(lane_name, True)
        )

        while effective_enabled and closed >= next_gate:
            if next_gate == 10:
                passed = (
                    stress_sum > 0
                    and pf >= 1.00
                )

                if passed:
                    lane_gate["next_gate"] = 20
                    lane_gate["status"] = (
                        "PASSED_10_COLLECTING_TO_20"
                    )

                    event = (
                        f"PASS_10 {lane_name}: "
                        f"closed={closed} "
                        f"stress=${stress_sum:+.5f} "
                        f"PF={pf:.2f}; continue to 20"
                    )

                    new_events.append(event)
                    next_gate = 20
                else:
                    disable_lane(overrides, lane_name)
                    override_changed = True
                    effective_enabled = False

                    lane_gate["next_gate"] = 999999
                    lane_gate["status"] = "REJECTED_AT_10"

                    event = (
                        f"REJECT_10 {lane_name}: "
                        f"closed={closed} "
                        f"stress=${stress_sum:+.5f} "
                        f"PF={pf:.2f}"
                    )

                    new_events.append(event)

            elif next_gate == 20:
                passed = (
                    stress_sum > 0
                    and pf >= 1.20
                    and symbol_stats["symbols"] >= 3
                    and symbol_stats["leave_best"] > 0
                    and symbol_stats["positive_share"] <= 0.50
                )

                if passed:
                    lane_gate["next_gate"] = 40
                    lane_gate["status"] = (
                        "PASSED_20_COLLECTING_TO_40"
                    )

                    event = (
                        f"PASS_20 {lane_name}: "
                        f"stress=${stress_sum:+.5f} "
                        f"PF={pf:.2f} "
                        f"symbols={symbol_stats['symbols']} "
                        f"leave_best="
                        f"${symbol_stats['leave_best']:+.5f} "
                        f"share="
                        f"{symbol_stats['positive_share']:.1%}; "
                        f"continue to 40"
                    )

                    new_events.append(event)
                    next_gate = 40
                else:
                    disable_lane(overrides, lane_name)
                    override_changed = True
                    effective_enabled = False

                    lane_gate["next_gate"] = 999999
                    lane_gate["status"] = "REJECTED_AT_20"

                    event = (
                        f"REJECT_20 {lane_name}: "
                        f"stress=${stress_sum:+.5f} "
                        f"PF={pf:.2f} "
                        f"symbols={symbol_stats['symbols']} "
                        f"leave_best="
                        f"${symbol_stats['leave_best']:+.5f} "
                        f"share="
                        f"{symbol_stats['positive_share']:.1%}"
                    )

                    new_events.append(event)

            elif next_gate == 40:
                passed = (
                    stress_sum > 0
                    and pf >= 1.20
                    and symbol_stats["symbols"] >= 5
                    and symbol_stats["leave_best"] > 0
                    and symbol_stats["positive_share"] <= 0.40
                )

                disable_lane(overrides, lane_name)
                override_changed = True
                effective_enabled = False

                lane_gate["next_gate"] = 999999

                if passed:
                    lane_gate["status"] = (
                        "PASSED_40_FROZEN_FOR_DRY_REVIEW"
                    )

                    event = (
                        f"PASS_40_FREEZE {lane_name}: "
                        f"stress=${stress_sum:+.5f} "
                        f"PF={pf:.2f}; "
                        f"candidate frozen for dry review. "
                        f"REAL remains OFF"
                    )
                else:
                    lane_gate["status"] = "REJECTED_AT_40"

                    event = (
                        f"REJECT_40 {lane_name}: "
                        f"stress=${stress_sum:+.5f} "
                        f"PF={pf:.2f} "
                        f"symbols={symbol_stats['symbols']} "
                        f"leave_best="
                        f"${symbol_stats['leave_best']:+.5f} "
                        f"share="
                        f"{symbol_stats['positive_share']:.1%}"
                    )

                new_events.append(event)

            else:
                break

        lane_gate["last_closed"] = closed
        lane_gate["last_stress_sum"] = stress_sum
        lane_gate["last_pf"] = pf
        lane_gate["updated_utc"] = utc_now()

        lines.append(
            f"{target['label']} | {lane_name}"
        )

        lines.append(
            f"  opened={opened} closed={closed} "
            f"stress=${stress_sum:+.5f} "
            f"PF={pf:.2f}"
        )

        lines.append(
            f"  symbols={symbol_stats['symbols']} "
            f"best={symbol_stats['best_symbol']} "
            f"share={symbol_stats['positive_share']:.1%} "
            f"leave_best="
            f"${symbol_stats['leave_best']:+.5f}"
        )

        lines.append(
            f"  effective_open="
            f"{int(bool(overrides.get(lane_name, True)))} "
            f"status={lane_gate['status']} "
            f"next_gate={lane_gate['next_gate']}"
        )

        lines.append("")

    for event in new_events:
        gate["events"].append({
            "utc": utc_now(),
            "event": event,
        })

    gate["events"] = gate["events"][-100:]
    gate["updated_utc"] = utc_now()

    if override_changed or not OVERRIDES.exists():
        save_json_atomic(OVERRIDES, overrides)

    save_json_atomic(GATE_STATE, gate)

    if new_events:
        lines.append("NEW GATE EVENTS:")

        for event in new_events:
            lines.append(f"  {event}")

        lines.append("")

    lines.append(
        "Gate 10: stress>0 and PF>=1.00."
    )

    lines.append(
        "Gate 20: stress>0, PF>=1.20, >=3 symbols, "
        "leave-best>0, best positive share<=50%."
    )

    lines.append(
        "Gate 40: same with >=5 symbols and share<=40%; "
        "lane is frozen for review."
    )

    lines.append("REAL_TRADING=OFF.")

    REPORT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(REPORT.read_text(encoding="utf-8"))

    if new_events:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tg_send_any.py"),
                str(REPORT),
                "SKYNET exact forward gate event",
            ],
            cwd=ROOT,
            check=False,
        )


if __name__ == "__main__":
    main()
