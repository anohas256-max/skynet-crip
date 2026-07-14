#!/usr/bin/env python3

import v18_exact_multi_shadow as exact


name = "RESEARCH_PC120_250_WALLPOS_TIME"
config = exact.LANES[name]


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


assert exact.lane_passes(
    row(),
    config,
), "valid WALL_POS candidate was rejected"

assert not exact.lane_passes(
    row(wall=0.0),
    config,
), "wall=0 was accepted"

assert not exact.lane_passes(
    row(wall=-0.10),
    config,
), "negative wall was accepted"

assert not exact.lane_passes(
    row(pc=1.19),
    config,
), "pc below range was accepted"

assert not exact.lane_passes(
    row(pc=2.51),
    config,
), "pc above range was accepted"

assert not exact.lane_passes(
    row(vol=7.9),
    config,
), "volume below minimum was accepted"

assert not exact.lane_passes(
    row(spread=2.01),
    config,
), "spread above maximum was accepted"

assert not exact.lane_passes(
    row(rank=81),
    config,
), "rank above maximum was accepted"

assert config["time_only"] is True
assert config["open_enabled"] is True

assert (
    exact.LANES["WF_PC120_SL03_BAN1"]["open_enabled"]
    is False
)

assert (
    exact.LANES["WF_PC120_SL05_BAN1"]["open_enabled"]
    is False
)

assert (
    exact.LANES["CONTROL_STAGE2"]["open_enabled"]
    is False
)

print(
    "EXACT_WALLPOS_SELFTEST_OK "
    "pc=1.20..2.50 vol>=8 spread<=2 "
    "rank<=80 wall>0 exit=TIME_ONLY"
)
