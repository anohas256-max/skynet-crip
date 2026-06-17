#!/usr/bin/env python3
# V3 wrapper over backtest_smart_universe_v2_grid.py.
# It DOES NOT touch live bot.
# It monkey-patches V2 modes/allow-rule to test "no override / whitelist" variants.

import argparse
import asyncio
from pathlib import Path

import backtest_smart_universe_v2_grid as v2

v2.OUT_DIR = Path("/root/skynet/data/backtest/smart_universe_v3_grid")

V3_MODES = {
    "CORE_ONLY": {"desc": "rank <= core_top only"},
    "STATIC_TOP60": {"desc": "baseline static rank <= 60"},
    "STATIC_TOP80": {"desc": "baseline static rank <= 80"},

    # Previous winner baseline.
    "V2_STRICT": {
        "desc": "previous V2 winner baseline",
        "cold_policy": "ultra",
        "min_obs": 2,
        "min_avg_net": 0.00,
        "max_sl_rate": 0.55,
        "min_avg_mfe": 0.45,
        "max_bad_streak": 1,
        "cooldown_hours": 24,
        "allow_strong_override": True,
        "allow_ultra_override": True,
    },

    # Main V3 tests.
    "V3_STRICT_NO_OVERRIDE": {
        "desc": "V2 strict, but MID cannot override quality with strong current signal",
        "cold_policy": "ultra",
        "min_obs": 2,
        "min_avg_net": 0.00,
        "max_sl_rate": 0.55,
        "min_avg_mfe": 0.45,
        "max_bad_streak": 1,
        "cooldown_hours": 24,
        "allow_strong_override": False,
        "allow_ultra_override": False,
    },
    "V3_WHITELIST_NO_OVERRIDE": {
        "desc": "MID only proven whitelist; no overrides",
        "cold_policy": "deny",
        "min_obs": 3,
        "min_avg_net": 0.02,
        "max_sl_rate": 0.50,
        "min_avg_mfe": 0.50,
        "max_bad_streak": 1,
        "cooldown_hours": 24,
        "allow_strong_override": False,
        "allow_ultra_override": False,
    },
    "V3_STRICT_ULTRA_ONLY": {
        "desc": "no strong override; ultra may override cold/cooldown/bad-streak",
        "cold_policy": "ultra",
        "min_obs": 2,
        "min_avg_net": 0.00,
        "max_sl_rate": 0.55,
        "min_avg_mfe": 0.45,
        "max_bad_streak": 1,
        "cooldown_hours": 24,
        "allow_strong_override": False,
        "allow_ultra_override": True,
    },
}


def v3_allow(e, mode_name, params, quality, core_top, mid_top):
    rank = int(e.get("rank", 999999))

    if mode_name == "CORE_ONLY":
        return (rank <= core_top), "CORE" if rank <= core_top else "OUTSIDE_CORE"

    if mode_name == "STATIC_TOP60":
        return (rank <= 60), "STATIC_TOP60" if rank <= 60 else "OUTSIDE_TOP60"

    if mode_name == "STATIC_TOP80":
        return (rank <= 80), "STATIC_TOP80" if rank <= 80 else "OUTSIDE_TOP80"

    if rank <= core_top:
        return True, "CORE"

    # Explore zone: monitor-only.
    if rank > mid_top:
        return False, "EXPLORE_MONITOR_ONLY"

    q = quality.features()
    allow_strong = bool(params.get("allow_strong_override", False))
    allow_ultra = bool(params.get("allow_ultra_override", False))

    if q["cooldown_until"] and e["entry_t"] < q["cooldown_until"]:
        if allow_ultra and v2.ultra_candidate(e):
            return True, "COOLDOWN_ULTRA_OVERRIDE"
        return False, "COOLDOWN"

    if q["bad_streak"] >= params.get("max_bad_streak", 1):
        if allow_ultra and v2.ultra_candidate(e):
            return True, "BAD_STREAK_ULTRA_OVERRIDE"
        return False, "BAD_STREAK"

    # Cold MID symbols: do not pay for weak learning.
    if q["obs"] < params.get("min_obs", 2):
        policy = params.get("cold_policy", "ultra")
        if policy == "clean" and v2.clean_candidate(e):
            return True, "MID_COLD_CLEAN"
        if policy == "strong" and v2.strong_candidate(e):
            return True, "MID_COLD_STRONG"
        if policy == "ultra" and v2.ultra_candidate(e):
            return True, "MID_COLD_ULTRA"
        return False, "MID_COLD_REJECT"

    quality_ok = (
        q["avg_net"] >= params.get("min_avg_net", 0.0)
        and q["sl_rate"] <= params.get("max_sl_rate", 0.55)
        and q["avg_mfe"] >= params.get("min_avg_mfe", 0.45)
        and v2.clean_candidate(e)
    )

    if quality_ok:
        return True, "MID_QUALITY_OK"

    # This is the key comparison:
    # V2_STRICT can use MID_STRONG_OVERRIDE.
    # V3_STRICT_NO_OVERRIDE / WHITELIST cannot.
    if allow_strong and v2.strong_candidate(e) and q["sl_rate"] <= min(0.75, params.get("max_sl_rate", 0.55) + 0.15):
        return True, "MID_STRONG_OVERRIDE"

    if allow_ultra and v2.ultra_candidate(e) and q["sl_rate"] <= 0.75:
        return True, "MID_ULTRA_OVERRIDE"

    return False, "MID_QUALITY_REJECT"


def main():
    # Monkey-patch V2 engine.
    v2.V2_MODES = V3_MODES
    v2.v2_allow = v3_allow

    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--top", type=int, default=150)
    p.add_argument("--core-top", type=int, default=30)
    p.add_argument("--mid-top", type=int, default=70)
    p.add_argument("--symbols", default="")
    p.add_argument("--max-open", default="1,2")
    p.add_argument("--margin", type=float, default=3.0)
    p.add_argument("--leverage", type=int, default=10)
    p.add_argument("--spread-bps", type=float, default=2.0)
    p.add_argument("--slippage-bps", type=float, default=3.0)
    p.add_argument("--families", default="")
    p.add_argument("--guards", default="")
    p.add_argument("--confirms", default="")
    p.add_argument("--modes", default="")
    p.add_argument("--end", default=None)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--send-tg", action="store_true")
    p.add_argument("--tg-target", default=None)

    args = p.parse_args()
    if not args.modes:
        args.modes = "CORE_ONLY,STATIC_TOP60,STATIC_TOP80,V2_STRICT,V3_STRICT_NO_OVERRIDE,V3_WHITELIST_NO_OVERRIDE,V3_STRICT_ULTRA_ONLY"
    if args.tg_target is None:
        import os
        args.tg_target = os.getenv("TG_TARGET", "-1002953234396")

    print("🚀 V3 wrapper active: testing no-override / whitelist modes over V2 engine")
    asyncio.run(v2.run(args))


if __name__ == "__main__":
    main()
