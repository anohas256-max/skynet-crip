#!/usr/bin/env python3

import v18_exact_multi_shadow as exact


R80 = "RESEARCH_PC120_250_WALLPOS_TIME"
R120 = "RESEARCH_PC120_250_WALLPOS_R120_TIME"


def row(
    pc=1.50,
    vol=12.0,
    spread=1.0,
    rank=40,
    wall=0.25,
):
    return {
        "price_change": pc,
        "vol_ratio": vol,
        "spread_bps": spread,
        "rank": rank,
        "wall_skew": wall,
        "bid1": 1.0,
        "ask1": 1.0001,
    }


r80 = exact.LANES[R80]
r120 = exact.LANES[R120]

assert exact.lane_passes(row(rank=40), r80)
assert exact.lane_passes(row(rank=40), r120)

assert not exact.lane_passes(
    row(rank=81),
    r80,
), "R80 accepted rank=81"

assert exact.lane_passes(
    row(rank=100),
    r120,
), "R120 rejected rank=100"

assert not exact.lane_passes(
    row(rank=121),
    r120,
), "R120 accepted rank=121"

for config in (r80, r120):
    assert not exact.lane_passes(
        row(wall=0.0),
        config,
    )

    assert not exact.lane_passes(
        row(wall=-0.1),
        config,
    )

    assert not exact.lane_passes(
        row(pc=1.19),
        config,
    )

    assert not exact.lane_passes(
        row(pc=2.51),
        config,
    )

    assert not exact.lane_passes(
        row(vol=7.99),
        config,
    )

    assert not exact.lane_passes(
        row(spread=2.01),
        config,
    )

    assert config["time_only"] is True
    assert config["open_enabled"] is True

for lane in (
    "WF_PC120_SL03_BAN1",
    "WF_PC120_SL05_BAN1",
    "CONTROL_STAGE2",
):
    assert (
        exact.LANES[lane]["open_enabled"] is False
    ), f"{lane} unexpectedly enabled"

print(
    "EXACT_WALLPOS_SELFTEST_OK "
    "R80+R120 wall>0 TIME_ONLY; "
    "old negative lanes disabled"
)
