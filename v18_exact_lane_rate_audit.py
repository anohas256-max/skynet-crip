#!/usr/bin/env python3

import json
import math
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
STATE = ROOT / "v18_exact_multi_shadow_state.json"
OUT = ROOT / "v18_exact_lane_rate_audit_latest.txt"

TTL_SECONDS = 300
COOLDOWN_SECONDS = 180

BLACKLIST = {
    "ALLO", "BREV", "KORU", "LIT", "M", "PENDLE",
    "RIF", "SKYAI", "SOXL", "TAC", "XPL",
}

LANES = {
    "WF_PC050_SP15_NOBAN": {
        "pc_min": 0.30,
        "pc_max": 0.50,
        "vol_min": 12.0,
        "spread_max": 1.50,
        "rank_max": 50,
    },
    "WF_PC120_SL03_BAN1": {
        "pc_min": 0.30,
        "pc_max": 1.20,
        "vol_min": 12.0,
        "spread_max": 2.00,
        "rank_max": 30,
    },
    "WF_PC120_SL05_BAN1": {
        "pc_min": 0.30,
        "pc_max": 1.20,
        "vol_min": 12.0,
        "spread_max": 2.00,
        "rank_max": 30,
    },
    "CONTROL_STAGE2": {
        "pc_min": 0.30,
        "pc_max": 0.80,
        "vol_min": 15.0,
        "spread_max": 2.00,
        "rank_max": 30,
    },
}


def parse_ts(value):
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


def fnum(value, default=None):
    try:
        number = float(value)

        if not math.isfinite(number):
            return default

        return number
    except Exception:
        return default


def passes(row, config):
    symbol = str(
        row.get("clean_symbol")
        or row.get("symbol")
        or ""
    ).replace("_USDT", "").upper()

    if not symbol or symbol in BLACKLIST:
        return False

    pc = fnum(row.get("price_change"))
    vol = fnum(row.get("vol_ratio"))
    spread = fnum(row.get("spread_bps"))
    rank = fnum(row.get("rank"))
    bid1 = fnum(row.get("bid1"))
    ask1 = fnum(row.get("ask1"))

    if None in (pc, vol, spread, rank, bid1, ask1):
        return False

    if bid1 <= 0 or ask1 <= bid1:
        return False

    return (
        config["pc_min"] <= pc <= config["pc_max"]
        and vol >= config["vol_min"]
        and spread <= config["spread_max"]
        and rank <= config["rank_max"]
    )


def occupancy_simulation(rows, config):
    accepted = []
    busy_until = None
    last_open = defaultdict(lambda: None)
    skipped_busy = 0
    skipped_cooldown = 0

    for row in rows:
        if not passes(row, config):
            continue

        ts = row["_ts"]

        if ts is None:
            continue

        symbol = str(
            row.get("symbol")
            or row.get("clean_symbol")
            or ""
        ).upper()

        if busy_until is not None and ts < busy_until:
            skipped_busy += 1
            continue

        previous = last_open[symbol]

        if (
            previous is not None
            and (ts - previous).total_seconds() < COOLDOWN_SECONDS
        ):
            skipped_cooldown += 1
            continue

        accepted.append(row)
        last_open[symbol] = ts
        busy_until = ts + timedelta(seconds=TTL_SECONDS)

    return accepted, skipped_busy, skipped_cooldown


def main():
    if not DB.exists():
        raise SystemExit(f"missing DB: {DB}")

    con = sqlite3.connect(
        f"file:{DB}?mode=ro",
        uri=True,
        timeout=20,
    )
    con.row_factory = sqlite3.Row

    db_max_id = int(
        con.execute(
            "SELECT COALESCE(MAX(id), 0) FROM signals"
        ).fetchone()[0]
    )

    raw = con.execute("""
        SELECT
            id,
            time_iso,
            symbol,
            clean_symbol,
            price_change,
            vol_ratio,
            spread_bps,
            rank,
            bid1,
            ask1
        FROM signals
        ORDER BY id DESC
        LIMIT 100000
    """).fetchall()

    con.close()

    rows = []

    for source in reversed(raw):
        row = dict(source)
        row["_ts"] = parse_ts(row.get("time_iso"))

        if row["_ts"] is not None:
            rows.append(row)

    now = datetime.now(timezone.utc)

    state = {}

    if STATE.exists():
        try:
            state = json.loads(
                STATE.read_text(encoding="utf-8")
            )
        except Exception:
            state = {}

    state_last_id = int(state.get("last_id") or 0)

    lines = []
    lines.append("=" * 120)
    lines.append(
        "V18 EXACT MULTI-LANE SIGNAL RATE AUDIT "
        f"UTC={now.strftime('%Y%m%d_%H%M%S_UTC')}"
    )
    lines.append("=" * 120)
    lines.append(f"db={DB}")
    lines.append(f"db_max_id={db_max_id}")
    lines.append(f"state_last_id={state_last_id}")
    lines.append(f"id_lag={db_max_id - state_last_id}")
    lines.append(
        f"state_stale_skipped={state.get('stale_skipped', 0)}"
    )
    lines.append(
        "accepted estimate models max_open=1, TTL=300s "
        "and per-symbol cooldown=180s."
    )

    for hours in (6, 24, 72):
        cutoff = now - timedelta(hours=hours)

        window = [
            row
            for row in rows
            if row["_ts"] >= cutoff
        ]

        lines.append("")
        lines.append("-" * 120)
        lines.append(
            f"WINDOW={hours}h rows={len(window)} "
            f"from={cutoff.isoformat()}"
        )
        lines.append("-" * 120)

        for lane_name, config in LANES.items():
            raw_matches = [
                row
                for row in window
                if passes(row, config)
            ]

            accepted, busy_skip, cooldown_skip = (
                occupancy_simulation(window, config)
            )

            symbols = sorted({
                str(
                    row.get("clean_symbol")
                    or row.get("symbol")
                    or ""
                ).replace("_USDT", "").upper()
                for row in accepted
            })

            per_day = (
                len(accepted) * 24.0 / hours
                if hours > 0
                else 0.0
            )

            lines.append(
                f"{lane_name:25s} "
                f"raw={len(raw_matches):4d} "
                f"accepted={len(accepted):3d} "
                f"est_per_day={per_day:5.1f} "
                f"symbols={len(symbols):3d} "
                f"busy_skip={busy_skip:3d} "
                f"cooldown_skip={cooldown_skip:3d}"
            )

            if accepted:
                last = accepted[-5:]

                lines.append(
                    "  last="
                    + " | ".join(
                        f"{row['_ts'].strftime('%m-%d %H:%M:%S')} "
                        f"{str(row.get('clean_symbol') or row.get('symbol'))}"
                        f" pc={float(row['price_change']):.2f}"
                        f" vol={float(row['vol_ratio']):.1f}"
                        f" sp={float(row['spread_bps']):.2f}"
                        f" r={int(float(row['rank']))}"
                        for row in last
                    )
                )

    lines.append("")
    lines.append("=" * 120)
    lines.append("INTERPRETATION")
    lines.append("=" * 120)

    lines.append(
        "id_lag near zero means the exact service is consuming DB rows."
    )
    lines.append(
        "accepted=0 in 24h means the lane is genuinely too strict "
        "or current market has no matching events."
    )
    lines.append(
        "accepted>0 but exact opened=0 means the service/filter path "
        "requires debugging."
    )
    lines.append("REAL_TRADING=OFF.")

    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
