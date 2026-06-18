#!/usr/bin/env python3
import asyncio
import time
import aiohttp

from research_fade_shadow import ResearchFadeV1Shadow


def log(s):
    print(s, end="")


async def main():
    shadow = ResearchFadeV1Shadow(log)
    now = time.time()

    # synthetic old active SHORT, TTL already expired
    shadow.active["STRICT:XMR_USDT"] = {
        "key": "STRICT:XMR_USDT",
        "profile": "STRICT",
        "symbol": "XMR_USDT",
        "clean_symbol": "XMR",
        "entry": 339.0,
        "time": now - 999,
        "side": "SHORT",
        "max_profit_pct": 0.0,
        "max_loss_pct": 0.0,
        "price_change": 0.34,
        "vol_ratio": 9.9,
        "spread_bps": 0.29,
        "rank": 40,
        "imb_5": -0.33,
        "score": 4,
    }

    print("BEFORE active=", len(shadow.active))

    async with aiohttp.ClientSession() as session:
        await shadow.poll_active_prices(session, now, "SELFTEST")

    print("AFTER active=", len(shadow.active))
    print(shadow.format_report())


if __name__ == "__main__":
    asyncio.run(main())
