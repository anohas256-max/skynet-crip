#!/usr/bin/env python3

import asyncio
import json
import math
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import aiohttp


ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"

STATE = ROOT / "v18_exact_multi_shadow_state.json"
LOG = ROOT / "v18_exact_multi_shadow.log"
REPORT = ROOT / "v18_exact_multi_shadow_latest.txt"

DEPTH_URL = (
    "https://contract.mexc.com/api/v1/contract/depth/"
    "{symbol}?limit=20"
)

POLL_SECONDS = 5.0
TTL_SECONDS = 300.0
COOLDOWN_SECONDS = 180.0

# Do not create fake forward trades from DB rows accumulated
# while this service was stopped. One-minute signals may be
# slightly delayed, therefore the guard is 90 seconds.
MAX_SIGNAL_AGE_SECONDS = 90.0

NOTIONAL_USD = 12.0

# Bid/ask prices already include the observed spread.
# These values therefore represent fees and additional slippage only.
LOW_FEE_RT_PCT = 0.04
CFG_FEE_RT_PCT = 0.16
STRESS_EXTRA_SLIPPAGE_RT_PCT = 0.10
STRESS_TOTAL_RT_PCT = (
    CFG_FEE_RT_PCT + STRESS_EXTRA_SLIPPAGE_RT_PCT
)

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
    # Strongest cost-resistant walk-forward survivor.
    "WF_PC050_SP15_NOBAN": {
        "pc_min": 0.30,
        "pc_max": 0.50,
        "vol_min": 12.0,
        "spread_max": 1.50,
        "rank_max": 50,
        "tp": 3.0,
        "sl": 0.3,
        "ban_after_sl": 0,
        "blacklist": CURRENT_BLACKLIST,
    },

    # Top walk-forward candidate; same profile that previously
    # disagreed with the small live-forward sample.
    "WF_PC120_SL03_BAN1": {
        "pc_min": 0.30,
        "pc_max": 1.20,
        "vol_min": 12.0,
        "spread_max": 2.00,
        "rank_max": 30,
        "tp": 3.0,
        "sl": 0.3,
        "ban_after_sl": 1,
        "blacklist": CURRENT_BLACKLIST,
    },

    # Same signal selection, wider stop.
    "WF_PC120_SL05_BAN1": {
        "pc_min": 0.30,
        "pc_max": 1.20,
        "vol_min": 12.0,
        "spread_max": 2.00,
        "rank_max": 30,
        "tp": 3.0,
        "sl": 0.5,
        "ban_after_sl": 1,
        "blacklist": CURRENT_BLACKLIST,
    },

    # Current running Stage2, used as a control lane.
    "CONTROL_STAGE2": {
        "pc_min": 0.30,
        "pc_max": 0.80,
        "vol_min": 15.0,
        "spread_max": 2.00,
        "rank_max": 30,
        "tp": 3.0,
        "sl": 0.3,
        "ban_after_sl": 1,
        "blacklist": CURRENT_BLACKLIST,
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


def safe_float(
    value: Any,
    default: float | None = None,
) -> float | None:
    try:
        result = float(value)

        if not math.isfinite(result):
            return default

        return result
    except Exception:
        return default


def parse_signal_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None

    raw = str(value).strip()
    raw = raw.replace(" UTC", "").replace("Z", "+00:00")

    try:
        result = datetime.fromisoformat(raw)

        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)

        return result.astimezone(timezone.utc)
    except Exception:
        return None


def log_line(message: str) -> None:
    line = f"[{utc_now()}] {message}"
    print(line, flush=True)

    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def empty_stats() -> dict:
    return {
        "opened": 0,
        "closed": 0,
        "gross_sum": 0.0,

        "low_sum": 0.0,
        "low_pos": 0.0,
        "low_neg": 0.0,

        "cfg_sum": 0.0,
        "cfg_pos": 0.0,
        "cfg_neg": 0.0,

        "stress_sum": 0.0,
        "stress_pos": 0.0,
        "stress_neg": 0.0,

        "reasons": {
            "TP": 0,
            "SL": 0,
            "TIME": 0,
        },

        "recent": [],
    }


def empty_lane_state() -> dict:
    return {
        "active": None,
        "banned": [],
        "symbol_sl": {},
        "last_open_by_symbol": {},
        "stats": empty_stats(),
    }


def normalize_state(state: dict) -> dict:
    state.setdefault("last_id", None)
    state.setdefault("stale_skipped", 0)
    state.setdefault("lanes", {})

    for lane_name in LANES:
        state["lanes"].setdefault(
            lane_name,
            empty_lane_state(),
        )

        lane = state["lanes"][lane_name]
        lane.setdefault("active", None)
        lane.setdefault("banned", [])
        lane.setdefault("symbol_sl", {})
        lane.setdefault("last_open_by_symbol", {})
        lane.setdefault("stats", empty_stats())

        stats = lane["stats"]
        defaults = empty_stats()

        for key, value in defaults.items():
            stats.setdefault(key, value)

        stats.setdefault(
            "reasons",
            {"TP": 0, "SL": 0, "TIME": 0},
        )

        for reason in ("TP", "SL", "TIME"):
            stats["reasons"].setdefault(reason, 0)

        stats.setdefault("recent", [])

    return state


def load_state() -> dict:
    if STATE.exists():
        try:
            data = json.loads(
                STATE.read_text(encoding="utf-8")
            )

            if isinstance(data, dict):
                return normalize_state(data)
        except Exception as exc:
            log_line(
                f"STATE_READ_ERROR | "
                f"{type(exc).__name__}: {exc}"
            )

    return normalize_state({
        "last_id": None,
        "lanes": {},
    })


def save_state(state: dict) -> None:
    temporary = STATE.with_suffix(".json.tmp")

    temporary.write_text(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    temporary.replace(STATE)


def db_connect() -> sqlite3.Connection:
    connection = sqlite3.connect(
        f"file:{DB}?mode=ro",
        uri=True,
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    return connection


def initialize_last_id(state: dict) -> None:
    if state.get("last_id") is not None:
        return

    connection = db_connect()

    try:
        row = connection.execute(
            "SELECT COALESCE(MAX(id), 0) FROM signals"
        ).fetchone()

        state["last_id"] = int(row[0] or 0)
    finally:
        connection.close()

    save_state(state)

    log_line(
        f"INIT | start_from_id={state['last_id']} "
        f"db={DB}"
    )


def fetch_new_signals(last_id: int) -> list[dict]:
    connection = db_connect()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                time_iso,
                symbol,
                clean_symbol,
                entry_price,
                price_change,
                vol_ratio,
                spread_bps,
                rank,
                bid1,
                ask1
            FROM signals
            WHERE id > ?
            ORDER BY id ASC
            LIMIT 2000
            """,
            (int(last_id),),
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


def parse_depth_level(level: Any) -> tuple[float, float]:
    if isinstance(level, dict):
        price = safe_float(
            level.get("price")
            or level.get("p")
            or level.get("0"),
            0.0,
        )
        quantity = safe_float(
            level.get("vol")
            or level.get("quantity")
            or level.get("q")
            or level.get("1"),
            0.0,
        )
        return float(price or 0.0), float(quantity or 0.0)

    if (
        isinstance(level, (list, tuple))
        and len(level) >= 2
    ):
        return (
            float(safe_float(level[0], 0.0) or 0.0),
            float(safe_float(level[1], 0.0) or 0.0),
        )

    return 0.0, 0.0


async def fetch_depth(
    session: aiohttp.ClientSession,
    symbol: str,
) -> dict | None:
    try:
        url = DEPTH_URL.format(symbol=symbol)

        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=6),
        ) as response:
            if response.status != 200:
                return None

            payload = await response.json()

        data = payload.get("data", payload)

        if not isinstance(data, dict):
            return None

        bids = data.get("bids") or data.get("bidsList") or []
        asks = data.get("asks") or data.get("asksList") or []

        if not bids or not asks:
            return None

        bid1, _ = parse_depth_level(bids[0])
        ask1, _ = parse_depth_level(asks[0])

        if bid1 <= 0 or ask1 <= 0 or ask1 <= bid1:
            return None

        spread_bps = (
            (ask1 - bid1) / bid1
        ) * 10000.0

        return {
            "bid1": bid1,
            "ask1": ask1,
            "spread_bps": spread_bps,
        }
    except Exception:
        return None


def lane_passes(
    row: dict,
    config: dict,
) -> bool:
    pc = safe_float(row.get("price_change"))
    vol = safe_float(row.get("vol_ratio"))
    spread = safe_float(row.get("spread_bps"))
    rank = safe_float(row.get("rank"))
    bid1 = safe_float(row.get("bid1"))
    ask1 = safe_float(row.get("ask1"))

    if None in (
        pc,
        vol,
        spread,
        rank,
        bid1,
        ask1,
    ):
        return False

    if bid1 <= 0 or ask1 <= bid1:
        return False

    return (
        config["pc_min"] <= pc <= config["pc_max"]
        and vol >= config["vol_min"]
        and spread <= config["spread_max"]
        and rank <= config["rank_max"]
    )


def add_metric(
    stats: dict,
    prefix: str,
    value: float,
) -> None:
    stats[f"{prefix}_sum"] += value

    if value > 0:
        stats[f"{prefix}_pos"] += value
    elif value < 0:
        stats[f"{prefix}_neg"] += -value


def profit_factor(
    positive: float,
    negative: float,
) -> float:
    if negative <= 0:
        return 999.0 if positive > 0 else 0.0

    return positive / negative


def close_trade(
    lane_name: str,
    lane_state: dict,
    config: dict,
    depth: dict,
    reason: str,
    age: float,
) -> None:
    active = lane_state["active"]

    entry_bid = float(active["entry_bid"])
    exit_ask = float(depth["ask1"])

    move_pct = (
        (entry_bid - exit_ask) / entry_bid
    ) * 100.0

    gross_usd = (
        NOTIONAL_USD * move_pct / 100.0
    )

    low_cost_usd = (
        NOTIONAL_USD * LOW_FEE_RT_PCT / 100.0
    )
    cfg_cost_usd = (
        NOTIONAL_USD * CFG_FEE_RT_PCT / 100.0
    )
    stress_cost_usd = (
        NOTIONAL_USD * STRESS_TOTAL_RT_PCT / 100.0
    )

    net_low = gross_usd - low_cost_usd
    net_cfg = gross_usd - cfg_cost_usd
    net_stress = gross_usd - stress_cost_usd

    stats = lane_state["stats"]

    stats["closed"] += 1
    stats["gross_sum"] += gross_usd
    stats["reasons"][reason] += 1

    add_metric(stats, "low", net_low)
    add_metric(stats, "cfg", net_cfg)
    add_metric(stats, "stress", net_stress)

    clean_symbol = active["clean"]

    if (
        reason == "SL"
        and int(config["ban_after_sl"]) > 0
    ):
        current_sl = int(
            lane_state["symbol_sl"].get(
                clean_symbol,
                0,
            )
        ) + 1

        lane_state["symbol_sl"][clean_symbol] = current_sl

        if current_sl >= int(config["ban_after_sl"]):
            banned = set(lane_state["banned"])
            banned.add(clean_symbol)
            lane_state["banned"] = sorted(banned)

    event = {
        "ts": utc_now(),
        "symbol": clean_symbol,
        "reason": reason,
        "signal_id": active["signal_id"],
        "age": round(age, 1),
        "entry_bid": entry_bid,
        "exit_ask": exit_ask,
        "entry_spread_bps": active["entry_spread_bps"],
        "exit_spread_bps": depth["spread_bps"],
        "move_pct": move_pct,
        "gross": gross_usd,
        "net_low": net_low,
        "net_cfg": net_cfg,
        "net_stress": net_stress,
    }

    stats["recent"].append(event)
    stats["recent"] = stats["recent"][-40:]

    log_line(
        f"EXACT_CLOSE | {lane_name} | SHORT | "
        f"{clean_symbol} | {reason} | "
        f"signal_id={active['signal_id']} "
        f"entry_bid={entry_bid:.10f} "
        f"exit_ask={exit_ask:.10f} "
        f"move={move_pct:+.4f}% "
        f"gross=${gross_usd:+.5f} "
        f"net_low=${net_low:+.5f} "
        f"net_cfg=${net_cfg:+.5f} "
        f"net_stress=${net_stress:+.5f} "
        f"entry_spread={active['entry_spread_bps']:.2f}bps "
        f"exit_spread={depth['spread_bps']:.2f}bps "
        f"age={age:.0f}s"
    )

    lane_state["active"] = None


def write_report(state: dict) -> None:
    lines = []

    lines.append("=" * 130)
    lines.append(
        f"V18 EXACT-EXECUTION MULTI-LANE SHADOW "
        f"UTC={utc_now()}"
    )
    lines.append("=" * 130)

    lines.append(f"db={DB}")
    lines.append(f"last_id={state.get('last_id')}")
    lines.append(
        f"stale_skipped={state.get('stale_skipped', 0)} "
        f"max_signal_age={MAX_SIGNAL_AGE_SECONDS:.0f}s"
    )
    lines.append(f"notional=${NOTIONAL_USD:.2f}")
    lines.append(
        "SHORT executable model: "
        "entry at recorded signal bid1, "
        "exit at current ask1."
    )
    lines.append(
        "Observed bid/ask spread is embedded in gross PnL."
    )
    lines.append(
        f"LOW fee RT={LOW_FEE_RT_PCT:.2f}% | "
        f"CFG fee RT={CFG_FEE_RT_PCT:.2f}% | "
        f"STRESS fee+slip RT={STRESS_TOTAL_RT_PCT:.2f}%"
    )
    lines.append(
        "Public market data only. No orders. "
        "REAL_TRADING=OFF."
    )

    for lane_name, config in LANES.items():
        lane = state["lanes"][lane_name]
        stats = lane["stats"]

        pf_low = profit_factor(
            stats["low_pos"],
            stats["low_neg"],
        )
        pf_cfg = profit_factor(
            stats["cfg_pos"],
            stats["cfg_neg"],
        )
        pf_stress = profit_factor(
            stats["stress_pos"],
            stats["stress_neg"],
        )

        lines.append("")
        lines.append("-" * 130)
        lines.append(lane_name)
        lines.append("-" * 130)

        lines.append(
            f"rule: pc={config['pc_min']:.2f}.."
            f"{config['pc_max']:.2f} "
            f"vol>={config['vol_min']:.1f} "
            f"spread<={config['spread_max']:.2f} "
            f"rank<={config['rank_max']} "
            f"TP={config['tp']:.2f}% "
            f"SL={config['sl']:.2f}% "
            f"ban_after_sl={config['ban_after_sl']}"
        )

        lines.append(
            f"opened={stats['opened']} "
            f"closed={stats['closed']} "
            f"active={1 if lane['active'] else 0} "
            f"banned={len(lane['banned'])} "
            f"TP={stats['reasons']['TP']} "
            f"SL={stats['reasons']['SL']} "
            f"TIME={stats['reasons']['TIME']}"
        )

        lines.append(
            f"GROSS=${stats['gross_sum']:+.5f}"
        )

        lines.append(
            f"LOW    net=${stats['low_sum']:+.5f} "
            f"PF={pf_low:.2f}"
        )
        lines.append(
            f"CFG    net=${stats['cfg_sum']:+.5f} "
            f"PF={pf_cfg:.2f}"
        )
        lines.append(
            f"STRESS net=${stats['stress_sum']:+.5f} "
            f"PF={pf_stress:.2f}"
        )

        if lane["active"]:
            active = lane["active"]
            age = time.time() - float(active["open_ts"])

            lines.append(
                f"ACTIVE {active['clean']} "
                f"entry_bid={active['entry_bid']:.10f} "
                f"age={age:.0f}s "
                f"signal_id={active['signal_id']}"
            )

        if lane["banned"]:
            lines.append(
                "BANNED="
                + ",".join(lane["banned"][-50:])
            )

        lines.append("RECENT:")

        for event in stats["recent"][-10:]:
            lines.append(
                f"  {event['ts']} "
                f"{event['symbol']:<12} "
                f"{event['reason']:<4} "
                f"move={event['move_pct']:+.4f}% "
                f"low={event['net_low']:+.5f}$ "
                f"cfg={event['net_cfg']:+.5f}$ "
                f"stress={event['net_stress']:+.5f}$ "
                f"age={event['age']:.0f}s"
            )

    REPORT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


async def main() -> None:
    if not DB.exists():
        raise SystemExit(f"missing DB: {DB}")

    state = load_state()
    initialize_last_id(state)

    for lane_name, config in LANES.items():
        log_line(
            f"EXACT_START | {lane_name} | "
            f"pc={config['pc_min']}..{config['pc_max']} "
            f"vol>={config['vol_min']} "
            f"spread<={config['spread_max']} "
            f"rank<={config['rank_max']} "
            f"TP={config['tp']} SL={config['sl']} "
            f"ban_after_sl={config['ban_after_sl']} "
            f"real=OFF"
        )

    last_report = 0.0

    timeout = aiohttp.ClientTimeout(total=8)

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:
        while True:
            try:
                rows = fetch_new_signals(
                    int(state["last_id"])
                )

                now = time.time()

                for row in rows:
                    row_id = int(row["id"])
                    state["last_id"] = max(
                        int(state["last_id"]),
                        row_id,
                    )

                    signal_time = parse_signal_timestamp(
                        row.get("time_iso")
                    )

                    signal_age = (
                        now - signal_time.timestamp()
                        if signal_time is not None
                        else None
                    )

                    if (
                        signal_age is None
                        or signal_age < -10.0
                        or signal_age > MAX_SIGNAL_AGE_SECONDS
                    ):
                        state["stale_skipped"] = (
                            int(state.get("stale_skipped", 0)) + 1
                        )

                        if (
                            int(state["stale_skipped"]) <= 10
                            or int(state["stale_skipped"]) % 100 == 0
                        ):
                            log_line(
                                f"SIGNAL_STALE_SKIP | id={row_id} "
                                f"time_iso={row.get('time_iso')} "
                                f"age={signal_age}"
                            )

                        continue

                    clean = str(
                        row.get("clean_symbol")
                        or row.get("symbol")
                        or ""
                    ).replace("_USDT", "").upper()

                    symbol = str(
                        row.get("symbol") or ""
                    )

                    for lane_name, config in LANES.items():
                        lane = state["lanes"][lane_name]

                        if lane["active"] is not None:
                            continue

                        if clean in config["blacklist"]:
                            continue

                        if clean in set(lane["banned"]):
                            continue

                        last_open = float(
                            lane["last_open_by_symbol"].get(
                                symbol,
                                0.0,
                            )
                        )

                        if now - last_open < COOLDOWN_SECONDS:
                            continue

                        if not lane_passes(row, config):
                            continue

                        entry_bid = float(row["bid1"])
                        entry_ask = float(row["ask1"])

                        lane["active"] = {
                            "symbol": symbol,
                            "clean": clean,
                            "signal_id": row_id,
                            "open_ts": now,
                            "entry_bid": entry_bid,
                            "entry_ask": entry_ask,
                            "entry_mid": float(
                                safe_float(
                                    row.get("entry_price"),
                                    (entry_bid + entry_ask) / 2,
                                )
                                or (entry_bid + entry_ask) / 2
                            ),
                            "entry_spread_bps": float(
                                row["spread_bps"]
                            ),
                            "pc": float(row["price_change"]),
                            "vol": float(row["vol_ratio"]),
                            "rank": int(float(row["rank"])),
                        }

                        lane["last_open_by_symbol"][symbol] = now
                        lane["stats"]["opened"] += 1

                        log_line(
                            f"EXACT_OPEN | {lane_name} | "
                            f"SHORT | {clean} | "
                            f"signal_id={row_id} "
                            f"entry_bid={entry_bid:.10f} "
                            f"entry_ask={entry_ask:.10f} "
                            f"spread={float(row['spread_bps']):.2f}bps "
                            f"pc={float(row['price_change']):+.2f}% "
                            f"vol=x{float(row['vol_ratio']):.1f} "
                            f"rank={int(float(row['rank']))}"
                        )

                active_symbols = sorted({
                    lane["active"]["symbol"]
                    for lane in state["lanes"].values()
                    if lane["active"] is not None
                })

                depth_map = {}

                if active_symbols:
                    results = await asyncio.gather(
                        *[
                            fetch_depth(session, symbol)
                            for symbol in active_symbols
                        ],
                        return_exceptions=True,
                    )

                    for symbol, result in zip(
                        active_symbols,
                        results,
                    ):
                        if isinstance(result, dict):
                            depth_map[symbol] = result

                now = time.time()

                for lane_name, config in LANES.items():
                    lane = state["lanes"][lane_name]
                    active = lane["active"]

                    if active is None:
                        continue

                    depth = depth_map.get(active["symbol"])

                    if not depth:
                        continue

                    age = now - float(active["open_ts"])

                    executable_move_pct = (
                        (
                            float(active["entry_bid"])
                            - float(depth["ask1"])
                        )
                        / float(active["entry_bid"])
                    ) * 100.0

                    reason = None

                    if executable_move_pct <= -float(config["sl"]):
                        reason = "SL"
                    elif executable_move_pct >= float(config["tp"]):
                        reason = "TP"
                    elif age >= TTL_SECONDS:
                        reason = "TIME"

                    if reason:
                        close_trade(
                            lane_name=lane_name,
                            lane_state=lane,
                            config=config,
                            depth=depth,
                            reason=reason,
                            age=age,
                        )

                if time.time() - last_report >= 60:
                    write_report(state)
                    last_report = time.time()

                save_state(state)

                await asyncio.sleep(POLL_SECONDS)

            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log_line(
                    f"LOOP_EXCEPTION | "
                    f"{type(exc).__name__}: {exc}"
                )
                save_state(state)
                write_report(state)
                await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
