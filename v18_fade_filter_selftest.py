#!/usr/bin/env python3

import os
from pathlib import Path


ROOT = Path("/root/skynet")
ENV = ROOT / ".env"


def load_env() -> None:
    if not ENV.exists():
        return

    for raw in ENV.read_text(errors="ignore").splitlines():
        line = raw.strip()

        if (
            not line
            or line.startswith("#")
            or "=" not in line
        ):
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_env()

import v18_fade_db_shadow as fade  # noqa: E402


def row(
    pc: float,
    vol: float | None = None,
    spread: float | None = None,
    rank: int | None = None,
) -> dict:
    return {
        "clean_symbol": "FILTERTEST",
        "symbol": "FILTERTEST_USDT",
        "entry_price": 1.0,
        "price_change": pc,
        "vol_ratio": (
            max(fade.VOL_MIN, 1.0)
            if vol is None
            else vol
        ),
        "spread_bps": (
            min(fade.SPREAD_MAX, 0.1)
            if spread is None
            else spread
        ),
        "rank": (
            min(fade.RANK_MAX, 1)
            if rank is None
            else rank
        ),
    }


state = {
    "symbol_sl": {},
}

middle = (
    fade.PC_MIN
    + (fade.PC_MAX - fade.PC_MIN) / 2.0
)

epsilon = max(
    0.000001,
    abs(fade.PC_MAX) * 0.000001,
)

assert fade.PC_MIN <= fade.PC_MAX, (
    f"invalid profile: PC_MIN={fade.PC_MIN} "
    f"> PC_MAX={fade.PC_MAX}"
)

assert fade.passes(row(middle), state), (
    "valid midpoint row was rejected"
)

assert not fade.passes(
    row(fade.PC_MIN - epsilon),
    state,
), "row below PC_MIN was accepted"

assert not fade.passes(
    row(fade.PC_MAX + epsilon),
    state,
), (
    f"CRITICAL: row above PC_MAX was accepted: "
    f"pc={fade.PC_MAX + epsilon} "
    f"PC_MAX={fade.PC_MAX}"
)

assert not fade.passes(
    row(
        middle,
        vol=max(0.0, fade.VOL_MIN - 0.01),
    ),
    state,
), "row below VOL_MIN was accepted"

assert not fade.passes(
    row(
        middle,
        spread=fade.SPREAD_MAX + 0.01,
    ),
    state,
), "row above SPREAD_MAX was accepted"

assert not fade.passes(
    row(
        middle,
        rank=fade.RANK_MAX + 1,
    ),
    state,
), "row above RANK_MAX was accepted"

print(
    "FILTER_SELFTEST_OK "
    f"pc={fade.PC_MIN}..{fade.PC_MAX} "
    f"vol>={fade.VOL_MIN} "
    f"spread<={fade.SPREAD_MAX} "
    f"rank<={fade.RANK_MAX}"
)
