#!/usr/bin/env python3

import re
from pathlib import Path
from datetime import datetime, timezone

SRC = Path("/root/skynet/v18_stage2_walkforward_latest.txt")
OUT = Path("/root/skynet/v18_walkforward_cost_reprice_latest.txt")

BASE_COST = 0.03
COSTS = [0.03, 0.06, 0.10, 0.17, 0.29]

HEADER_RE = re.compile(
    r"^#(?P<num>\d+)\s+HOLDOUT_PASS\s+"
    r"score=(?P<score>[+-]?[0-9.]+)\s+"
    r"(?P<cfg>.+)$"
)

STAT_RE = re.compile(
    r"^\s*(?P<section>TRAIN75|TEST25|ALL|STRESS)\s+"
    r"n=\s*(?P<n>\d+)\s+"
    r"net=\s*(?P<net>[+-]?[0-9.]+)%"
)


def adjusted_net(base_net: float, n: int, new_cost: float) -> float:
    return base_net - n * (new_cost - BASE_COST)


def main():
    if not SRC.exists():
        raise SystemExit(f"missing source: {SRC}")

    candidates = []
    current = None

    for raw in SRC.read_text(errors="ignore").splitlines():
        mh = HEADER_RE.match(raw)

        if mh:
            current = {
                "num": int(mh.group("num")),
                "score": float(mh.group("score")),
                "cfg": mh.group("cfg"),
                "stats": {},
            }
            candidates.append(current)
            continue

        if current is None:
            continue

        ms = STAT_RE.match(raw)

        if ms:
            current["stats"][ms.group("section")] = {
                "n": int(ms.group("n")),
                "net": float(ms.group("net")),
            }

    lines = []
    lines.append("=" * 140)
    lines.append(
        "V18 WALK-FORWARD SURVIVOR COST REPRICE "
        f"UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}"
    )
    lines.append("=" * 140)
    lines.append(f"source={SRC}")
    lines.append(
        "Formula: adjusted_net = reported_net - n * (new_cost - 0.03%)."
    )
    lines.append(
        "This reprices the existing path model; it does not model real bid/ask fills."
    )

    for cost in COSTS:
        ranked = []

        for candidate in candidates:
            all_stats = candidate["stats"].get("ALL")
            test_stats = candidate["stats"].get("TEST25")

            if not all_stats or not test_stats:
                continue

            all_net = adjusted_net(
                all_stats["net"],
                all_stats["n"],
                cost,
            )
            test_net = adjusted_net(
                test_stats["net"],
                test_stats["n"],
                cost,
            )

            ranked.append({
                "cfg": candidate["cfg"],
                "score": candidate["score"],
                "all_n": all_stats["n"],
                "test_n": test_stats["n"],
                "all_net": all_net,
                "test_net": test_net,
            })

        ranked.sort(
            key=lambda row: (
                row["test_net"] > 0,
                row["all_net"] > 0,
                row["test_net"],
                row["all_net"],
            ),
            reverse=True,
        )

        survivors = [
            row
            for row in ranked
            if row["all_net"] > 0 and row["test_net"] > 0
        ]

        lines.append("")
        lines.append("=" * 140)
        lines.append(
            f"COST={cost:.2f}% "
            f"ALL_AND_TEST_POSITIVE={len(survivors)}"
        )
        lines.append("=" * 140)

        for index, row in enumerate(ranked[:20], 1):
            flag = (
                "SURVIVES"
                if row["all_net"] > 0 and row["test_net"] > 0
                else "FAIL"
            )

            lines.append(
                f"#{index:02d} {flag:<8} "
                f"ALL n={row['all_n']:3d} net={row['all_net']:+8.3f}% | "
                f"TEST n={row['test_n']:3d} net={row['test_net']:+8.3f}% | "
                f"{row['cfg']}"
            )

    lines.append("")
    lines.append("=" * 140)
    lines.append("DECISION")
    lines.append("=" * 140)
    lines.append(
        "Only configurations positive on BOTH ALL and untouched TEST "
        "at the selected cost deserve exact-execution shadow validation."
    )
    lines.append(
        "No configuration from this report is permission to enable real trading."
    )
    lines.append("REAL_TRADING=OFF.")

    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
