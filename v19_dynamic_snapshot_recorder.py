#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/root/skynet")

V18_DB = ROOT / "data/v18_micro_paths.sqlite3"
V19_DB = ROOT / "data/v19_dynamic_snapshots.sqlite3"

STATUS_REPORT = (
    ROOT / "v19_dynamic_snapshot_status_latest.txt"
)

TICKER_URL = (
    "https://contract.mexc.com/api/v1/contract/ticker"
)

DETAIL_URL = (
    "https://contract.mexc.com/api/v1/contract/detail"
)

DEPTH_URL = (
    "https://contract.mexc.com/api/v1/"
    "contract/depth/{symbol}?limit=20"
)

TARGET_AGES = (
    5,
    15,
    30,
    60,
    120,
    180,
    300,
)

MAX_LATE = {
    5: 12.0,
    15: 12.0,
    30: 12.0,
    60: 15.0,
    120: 15.0,
    180: 15.0,
    300: 20.0,
}

POLL_SECONDS = 2.0
FINALIZE_AFTER = 330.0
MAX_WORKERS = 8

NOTIONAL_USD = 12.0
CFG_COST_PCT = 0.16
STRESS_COST_PCT = 0.26


def sf(
    value: Any,
    default: float | None = None,
) -> float | None:
    try:
        if value is None or value == "":
            return default

        result = float(value)

        if not math.isfinite(result):
            return default

        return result

    except Exception:
        return default


def utc_text(
    timestamp: float | None = None,
) -> str:
    if timestamp is None:
        timestamp = time.time()

    return datetime.fromtimestamp(
        timestamp,
        timezone.utc,
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


def http_json(
    url: str,
    timeout: float = 8.0,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "SKYNET-V19-DYNAMIC/1.0"
            ),
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        payload = response.read()

    decoded = json.loads(
        payload.decode("utf-8")
    )

    if not isinstance(decoded, dict):
        raise ValueError(
            "API payload is not an object"
        )

    return decoded


def connect_v19() -> sqlite3.Connection:
    V19_DB.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(V19_DB),
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA journal_mode=WAL"
    )

    connection.execute(
        "PRAGMA synchronous=NORMAL"
    )

    connection.execute(
        "PRAGMA busy_timeout=30000"
    )

    return connection


def init_db(
    connection: sqlite3.Connection,
) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS signals (
            signal_id INTEGER PRIMARY KEY,

            entry_ts REAL NOT NULL,
            entry_time_iso TEXT,

            symbol TEXT NOT NULL,
            clean_symbol TEXT,

            entry_price REAL,
            price_change REAL,
            vol_1m REAL,
            vol_ratio REAL,
            oi_change REAL,
            rank INTEGER,

            entry_spread_bps REAL,
            entry_bid1 REAL,
            entry_ask1 REAL,

            entry_bid5_usd REAL,
            entry_ask5_usd REAL,
            entry_bid20_usd REAL,
            entry_ask20_usd REAL,

            entry_imb5 REAL,
            entry_imb20 REAL,
            entry_wall_skew REAL,

            imported_ts REAL NOT NULL,

            completed INTEGER
                NOT NULL DEFAULT 0,

            completion_ts REAL
        );

        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            signal_id INTEGER NOT NULL,
            target_age INTEGER NOT NULL,
            actual_age REAL,

            ts REAL NOT NULL,
            time_iso TEXT NOT NULL,
            status TEXT NOT NULL,

            contract_size REAL,

            last_price REAL,
            amount24 REAL,
            hold_vol REAL,
            btc_price REAL,

            bid1 REAL,
            ask1 REAL,
            spread_bps REAL,

            bid5_usd REAL,
            ask5_usd REAL,
            bid20_usd REAL,
            ask20_usd REAL,

            imb5 REAL,
            imb20 REAL,
            wall_skew REAL,

            gross_short_pct REAL,
            cfg_short_usd REAL,
            stress_short_usd REAL,

            error TEXT,

            UNIQUE(signal_id, target_age),

            FOREIGN KEY(signal_id)
                REFERENCES signals(signal_id)
        );

        CREATE INDEX IF NOT EXISTS
            idx_v19_pending
            ON signals(completed, entry_ts);

        CREATE INDEX IF NOT EXISTS
            idx_v19_snap_signal
            ON snapshots(
                signal_id,
                target_age
            );

        CREATE INDEX IF NOT EXISTS
            idx_v19_snap_target
            ON snapshots(
                target_age,
                status
            );
        """
    )

    connection.commit()


def meta_get(
    connection: sqlite3.Connection,
    key: str,
) -> str | None:
    row = connection.execute(
        """
        SELECT value
        FROM meta
        WHERE key=?
        """,
        (key,),
    ).fetchone()

    return str(row["value"]) if row else None


def meta_set(
    connection: sqlite3.Connection,
    key: str,
    value: str,
) -> None:
    connection.execute(
        """
        INSERT INTO meta(key, value)
        VALUES (?, ?)

        ON CONFLICT(key)
        DO UPDATE SET
            value=excluded.value
        """,
        (key, value),
    )

    connection.commit()


def verify_v18_schema() -> None:
    if not V18_DB.exists():
        raise FileNotFoundError(
            f"V18 DB missing: {V18_DB}"
        )

    connection = sqlite3.connect(
        f"file:{V18_DB}?mode=ro",
        uri=True,
        timeout=30,
    )

    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(signals)"
        )
    }

    connection.close()

    required = {
        "id",
        "ts",
        "time_iso",
        "symbol",
        "clean_symbol",
        "entry_price",
        "price_change",
        "vol_1m",
        "vol_ratio",
        "oi_change",
        "rank",
        "spread_bps",
        "bid1",
        "ask1",
        "bid5_usd",
        "ask5_usd",
        "bid20_usd",
        "ask20_usd",
        "imb_5",
        "imb_20",
        "wall_skew",
    }

    missing = sorted(
        required - columns
    )

    if missing:
        raise RuntimeError(
            "V18 schema missing: "
            + ",".join(missing)
        )


def ensure_cursor(
    connection: sqlite3.Connection,
) -> int:
    existing = meta_get(
        connection,
        "last_v18_id",
    )

    if existing is not None:
        return int(existing)

    source = sqlite3.connect(
        f"file:{V18_DB}?mode=ro",
        uri=True,
        timeout=30,
    )

    row = source.execute(
        """
        SELECT COALESCE(MAX(id), 0)
        FROM signals
        """
    ).fetchone()

    source.close()

    cursor = int(row[0] or 0)

    meta_set(
        connection,
        "last_v18_id",
        str(cursor),
    )

    meta_set(
        connection,
        "collector_start_ts",
        str(time.time()),
    )

    return cursor


def import_new_signals(
    connection: sqlite3.Connection,
    last_id: int,
) -> tuple[int, int]:
    source = sqlite3.connect(
        f"file:{V18_DB}?mode=ro",
        uri=True,
        timeout=30,
    )

    source.row_factory = sqlite3.Row

    rows = source.execute(
        """
        SELECT
            id,
            ts,
            time_iso,

            symbol,
            clean_symbol,

            entry_price,
            price_change,
            vol_1m,
            vol_ratio,
            oi_change,
            rank,

            spread_bps,
            bid1,
            ask1,

            bid5_usd,
            ask5_usd,
            bid20_usd,
            ask20_usd,

            imb_5,
            imb_20,
            wall_skew

        FROM signals

        WHERE id > ?

        ORDER BY id ASC
        """,
        (last_id,),
    ).fetchall()

    source.close()

    imported = 0
    max_seen = last_id
    now = time.time()

    for source_row in rows:
        row = dict(source_row)

        signal_id = int(row["id"])

        max_seen = max(
            max_seen,
            signal_id,
        )

        before = connection.total_changes

        connection.execute(
            """
            INSERT OR IGNORE INTO signals (
                signal_id,

                entry_ts,
                entry_time_iso,

                symbol,
                clean_symbol,

                entry_price,
                price_change,
                vol_1m,
                vol_ratio,
                oi_change,
                rank,

                entry_spread_bps,
                entry_bid1,
                entry_ask1,

                entry_bid5_usd,
                entry_ask5_usd,
                entry_bid20_usd,
                entry_ask20_usd,

                entry_imb5,
                entry_imb20,
                entry_wall_skew,

                imported_ts
            )
            VALUES (
                :id,

                :ts,
                :time_iso,

                :symbol,
                :clean_symbol,

                :entry_price,
                :price_change,
                :vol_1m,
                :vol_ratio,
                :oi_change,
                :rank,

                :spread_bps,
                :bid1,
                :ask1,

                :bid5_usd,
                :ask5_usd,
                :bid20_usd,
                :ask20_usd,

                :imb_5,
                :imb_20,
                :wall_skew,

                :imported_ts
            )
            """,
            {
                **row,
                "imported_ts": now,
            },
        )

        if connection.total_changes > before:
            imported += 1

    connection.commit()

    if max_seen != last_id:
        meta_set(
            connection,
            "last_v18_id",
            str(max_seen),
        )

    return imported, max_seen


def parse_level(
    level: Any,
) -> tuple[float, float]:
    if isinstance(level, dict):
        price = (
            sf(
                level.get("price")
                or level.get("p"),
                0.0,
            )
            or 0.0
        )

        quantity = (
            sf(
                level.get("vol")
                or level.get("quantity")
                or level.get("q"),
                0.0,
            )
            or 0.0
        )

        return price, quantity

    if (
        isinstance(level, (list, tuple))
        and len(level) >= 2
    ):
        return (
            sf(level[0], 0.0) or 0.0,
            sf(level[1], 0.0) or 0.0,
        )

    return 0.0, 0.0


def depth_stats(
    levels: list[Any],
    count: int,
    contract_size: float,
) -> tuple[float, float]:
    total = 0.0
    largest = 0.0

    for level in levels[:count]:
        price, quantity = parse_level(
            level
        )

        value = (
            price
            * quantity
            * contract_size
            if price > 0 and quantity > 0
            else 0.0
        )

        total += value
        largest = max(
            largest,
            value,
        )

    return total, largest


def parse_depth(
    payload: dict[str, Any],
    contract_size: float,
) -> dict[str, float]:
    data = payload.get(
        "data",
        payload,
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Depth data is not an object"
        )

    bids = (
        data.get("bids")
        or data.get("bidsList")
        or []
    )

    asks = (
        data.get("asks")
        or data.get("asksList")
        or []
    )

    if not bids or not asks:
        raise ValueError("Empty depth")

    bid1, _ = parse_level(bids[0])
    ask1, _ = parse_level(asks[0])

    if (
        bid1 <= 0
        or ask1 <= 0
        or ask1 <= bid1
    ):
        raise ValueError(
            "Invalid best bid/ask"
        )

    bid5, _ = depth_stats(
        bids,
        5,
        contract_size,
    )

    ask5, _ = depth_stats(
        asks,
        5,
        contract_size,
    )

    bid20, max_bid20 = depth_stats(
        bids,
        20,
        contract_size,
    )

    ask20, max_ask20 = depth_stats(
        asks,
        20,
        contract_size,
    )

    imb5 = (
        (bid5 - ask5)
        / (bid5 + ask5)
        if bid5 + ask5 > 0
        else 0.0
    )

    imb20 = (
        (bid20 - ask20)
        / (bid20 + ask20)
        if bid20 + ask20 > 0
        else 0.0
    )

    bid_wall = (
        max_bid20 / bid20
        if bid20 > 0
        else 0.0
    )

    ask_wall = (
        max_ask20 / ask20
        if ask20 > 0
        else 0.0
    )

    return {
        "bid1": bid1,
        "ask1": ask1,

        "spread_bps": (
            (ask1 - bid1)
            / bid1
            * 10000.0
        ),

        "bid5_usd": bid5,
        "ask5_usd": ask5,

        "bid20_usd": bid20,
        "ask20_usd": ask20,

        "imb5": imb5,
        "imb20": imb20,

        "wall_skew": (
            bid_wall - ask_wall
        ),
    }


def fetch_contract_sizes() -> dict[str, float]:
    payload = http_json(
        DETAIL_URL,
        timeout=12,
    )

    rows = payload.get("data", [])

    result: dict[str, float] = {}

    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue

            symbol = str(
                row.get("symbol") or ""
            )

            size = (
                sf(
                    row.get("contractSize"),
                    1.0,
                )
                or 1.0
            )

            if symbol:
                result[symbol] = size

    return result


def fetch_tickers() -> dict[
    str,
    dict[str, float],
]:
    payload = http_json(
        TICKER_URL,
        timeout=12,
    )

    rows = payload.get("data", [])

    result: dict[
        str,
        dict[str, float],
    ] = {}

    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue

            symbol = str(
                row.get("symbol") or ""
            )

            if not symbol:
                continue

            result[symbol] = {
                "last_price": (
                    sf(
                        row.get("lastPrice"),
                        0.0,
                    )
                    or 0.0
                ),

                "amount24": (
                    sf(
                        row.get("amount24")
                        or row.get("volume24"),
                        0.0,
                    )
                    or 0.0
                ),

                "hold_vol": (
                    sf(
                        row.get("holdVol"),
                        0.0,
                    )
                    or 0.0
                ),
            }

    return result


def fetch_depth(
    symbol: str,
    contract_size: float,
) -> tuple[
    str,
    dict[str, float] | None,
    str | None,
]:
    try:
        encoded = urllib.parse.quote(
            symbol,
            safe="_",
        )

        payload = http_json(
            DEPTH_URL.format(
                symbol=encoded
            ),
            timeout=8,
        )

        return (
            symbol,
            parse_depth(
                payload,
                contract_size,
            ),
            None,
        )

    except Exception as exc:
        return (
            symbol,
            None,
            f"{type(exc).__name__}:{exc}",
        )


def calculate_short(
    entry_bid: float | None,
    exit_ask: float | None,
) -> tuple[
    float | None,
    float | None,
    float | None,
]:
    if (
        entry_bid is None
        or exit_ask is None
        or entry_bid <= 0
        or exit_ask <= 0
    ):
        return None, None, None

    gross_pct = (
        (entry_bid - exit_ask)
        / entry_bid
        * 100.0
    )

    cfg = (
        (gross_pct - CFG_COST_PCT)
        * NOTIONAL_USD
        / 100.0
    )

    stress = (
        (gross_pct - STRESS_COST_PCT)
        * NOTIONAL_USD
        / 100.0
    )

    return gross_pct, cfg, stress


def insert_snapshot(
    connection: sqlite3.Connection,
    values: dict[str, Any],
) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO snapshots (
            signal_id,
            target_age,
            actual_age,

            ts,
            time_iso,
            status,

            contract_size,

            last_price,
            amount24,
            hold_vol,
            btc_price,

            bid1,
            ask1,
            spread_bps,

            bid5_usd,
            ask5_usd,
            bid20_usd,
            ask20_usd,

            imb5,
            imb20,
            wall_skew,

            gross_short_pct,
            cfg_short_usd,
            stress_short_usd,

            error
        )
        VALUES (
            :signal_id,
            :target_age,
            :actual_age,

            :ts,
            :time_iso,
            :status,

            :contract_size,

            :last_price,
            :amount24,
            :hold_vol,
            :btc_price,

            :bid1,
            :ask1,
            :spread_bps,

            :bid5_usd,
            :ask5_usd,
            :bid20_usd,
            :ask20_usd,

            :imb5,
            :imb20,
            :wall_skew,

            :gross_short_pct,
            :cfg_short_usd,
            :stress_short_usd,

            :error
        )
        """,
        values,
    )


def pending_due(
    connection: sqlite3.Connection,
    now: float,
) -> tuple[
    list[tuple[dict[str, Any], int]],
    int,
]:
    rows = connection.execute(
        """
        SELECT *
        FROM signals
        WHERE completed=0
        ORDER BY entry_ts
        """
    ).fetchall()

    due: list[
        tuple[dict[str, Any], int]
    ] = []

    missed = 0

    for source_row in rows:
        signal = dict(source_row)

        signal_id = int(
            signal["signal_id"]
        )

        age = (
            now
            - float(signal["entry_ts"])
        )

        existing = {
            int(row["target_age"])
            for row in connection.execute(
                """
                SELECT target_age
                FROM snapshots
                WHERE signal_id=?
                """,
                (signal_id,),
            )
        }

        for target in TARGET_AGES:
            if (
                target in existing
                or age < target
            ):
                continue

            lateness = age - target

            if lateness > MAX_LATE[target]:
                insert_snapshot(
                    connection,
                    {
                        "signal_id": signal_id,
                        "target_age": target,
                        "actual_age": age,

                        "ts": now,
                        "time_iso": utc_text(
                            now
                        ),
                        "status": "MISSED_LATE",

                        "contract_size": None,

                        "last_price": None,
                        "amount24": None,
                        "hold_vol": None,
                        "btc_price": None,

                        "bid1": None,
                        "ask1": None,
                        "spread_bps": None,

                        "bid5_usd": None,
                        "ask5_usd": None,
                        "bid20_usd": None,
                        "ask20_usd": None,

                        "imb5": None,
                        "imb20": None,
                        "wall_skew": None,

                        "gross_short_pct": None,
                        "cfg_short_usd": None,
                        "stress_short_usd": None,

                        "error": (
                            f"late_by="
                            f"{lateness:.1f}s"
                        ),
                    },
                )

                missed += 1

            else:
                due.append(
                    (
                        signal,
                        target,
                    )
                )

    connection.commit()

    return due, missed


def finalize_old(
    connection: sqlite3.Connection,
    now: float,
) -> int:
    completed = 0

    rows = connection.execute(
        """
        SELECT signal_id, entry_ts
        FROM signals
        WHERE completed=0
        """
    ).fetchall()

    for row in rows:
        if (
            now - float(row["entry_ts"])
            < FINALIZE_AFTER
        ):
            continue

        count = int(
            connection.execute(
                """
                SELECT COUNT(
                    DISTINCT target_age
                )
                FROM snapshots
                WHERE signal_id=?
                """,
                (
                    int(row["signal_id"]),
                ),
            ).fetchone()[0]
            or 0
        )

        if count < len(TARGET_AGES):
            continue

        connection.execute(
            """
            UPDATE signals
            SET completed=1,
                completion_ts=?
            WHERE signal_id=?
            """,
            (
                now,
                int(row["signal_id"]),
            ),
        )

        completed += 1

    connection.commit()

    return completed


def counts(
    connection: sqlite3.Connection,
) -> dict[str, int]:
    signals = int(
        connection.execute(
            "SELECT COUNT(*) FROM signals"
        ).fetchone()[0]
        or 0
    )

    completed = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE completed=1
            """
        ).fetchone()[0]
        or 0
    )

    pending = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE completed=0
            """
        ).fetchone()[0]
        or 0
    )

    snapshots = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM snapshots
            """
        ).fetchone()[0]
        or 0
    )

    quality = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT signal_id

                FROM snapshots

                WHERE status='OK'

                GROUP BY signal_id

                HAVING COUNT(
                    DISTINCT target_age
                )=?
            )
            """,
            (
                len(TARGET_AGES),
            ),
        ).fetchone()[0]
        or 0
    )

    return {
        "signals": signals,
        "completed": completed,
        "pending": pending,
        "snapshots": snapshots,
        "quality": quality,
    }


def profit_factor(
    values: list[float],
) -> float:
    positive = sum(
        value
        for value in values
        if value > 0
    )

    negative = -sum(
        value
        for value in values
        if value < 0
    )

    if negative <= 0:
        return (
            999.0
            if positive > 0
            else 0.0
        )

    return positive / negative


def create_status(
    send: bool = False,
) -> None:
    if not V19_DB.exists():
        text = (
            "V19 database does not exist yet.\n"
            "REAL_TRADING=OFF.\n"
        )

        STATUS_REPORT.write_text(
            text,
            encoding="utf-8",
        )

        print(text)
        return

    connection = connect_v19()
    init_db(connection)

    summary = counts(connection)

    collector_start = meta_get(
        connection,
        "collector_start_ts",
    )

    status_rows = connection.execute(
        """
        SELECT
            status,
            COUNT(*) AS n

        FROM snapshots

        GROUP BY status

        ORDER BY n DESC
        """
    ).fetchall()

    coverage_rows = connection.execute(
        """
        SELECT
            target_age,
            status,
            COUNT(*) AS n

        FROM snapshots

        GROUP BY
            target_age,
            status

        ORDER BY
            target_age,
            status
        """
    ).fetchall()

    age300 = connection.execute(
        """
        SELECT
            s.clean_symbol,
            s.symbol,
            p.stress_short_usd

        FROM snapshots p

        JOIN signals s
          ON s.signal_id=p.signal_id

        WHERE p.target_age=300
          AND p.status='OK'
          AND p.stress_short_usd
              IS NOT NULL

        ORDER BY p.ts
        """
    ).fetchall()

    connection.close()

    values = [
        float(row["stress_short_usd"])
        for row in age300
    ]

    total = sum(values)

    wr = (
        100.0
        * sum(value > 0 for value in values)
        / len(values)
        if values
        else 0.0
    )

    lines = [
        "=" * 120,

        (
            "SKYNET V19 DYNAMIC SNAPSHOT STATUS "
            f"UTC={utc_text()}"
        ),

        "=" * 120,

        (
            "collector_start="
            + (
                utc_text(
                    float(collector_start)
                )
                if collector_start
                else "-"
            )
        ),

        f"db={V19_DB}",

        (
            f"signals={summary['signals']} "
            f"completed={summary['completed']} "
            f"pending={summary['pending']} "
            f"snapshots={summary['snapshots']}"
        ),

        (
            "quality_complete_all_7_OK="
            f"{summary['quality']} "
            "target=100"
        ),

        "",
        "SNAPSHOT STATUS",
    ]

    for row in status_rows:
        lines.append(
            f"  {row['status']:<20} "
            f"n={row['n']}"
        )

    lines.extend(
        [
            "",
            "TARGET COVERAGE",
        ]
    )

    for row in coverage_rows:
        lines.append(
            f"  age="
            f"{int(row['target_age']):3d}s "
            f"status={row['status']:<20} "
            f"n={row['n']}"
        )

    lines.extend(
        [
            "",
            (
                "AGE 300 RAW EXACT SHORT "
                "(all recorded V18 signals; "
                "no lane selector)"
            ),

            (
                f"n={len(values)} "
                f"stress=${total:+.5f} "
                f"PF={profit_factor(values):.2f} "
                f"WR={wr:.1f}%"
            ),

            "",
            (
                "This is data-quality status, "
                "not a promotion decision."
            ),

            "REAL_TRADING=OFF.",
        ]
    )

    text = "\n".join(lines) + "\n"

    STATUS_REPORT.write_text(
        text,
        encoding="utf-8",
    )

    print(text)

    if send:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tg_send_any.py"),
                str(STATUS_REPORT),
                (
                    "SKYNET V19 dynamic "
                    "snapshot status"
                ),
            ],
            cwd=ROOT,
            check=False,
        )


def maybe_send_ready_alert(
    connection: sqlite3.Connection,
) -> None:
    summary = counts(connection)

    if summary["quality"] < 100:
        return

    if (
        meta_get(
            connection,
            "ready_100_sent",
        )
        == "1"
    ):
        return

    meta_set(
        connection,
        "ready_100_sent",
        "1",
    )

    subprocess.run(
        [
            sys.executable,
            str(Path(__file__)),
            "--status",
            "--send",
        ],
        cwd=ROOT,
        check=False,
    )


def collect() -> None:
    verify_v18_schema()

    connection = connect_v19()
    init_db(connection)

    last_id = ensure_cursor(connection)

    contract_sizes: dict[
        str,
        float,
    ] = {}

    contract_refresh = 0.0
    last_heartbeat = 0.0

    print(
        f"[{utc_text()}] "
        f"V19_START "
        f"last_v18_id={last_id} "
        f"targets={TARGET_AGES} "
        f"db={V19_DB}",
        flush=True,
    )

    try:
        while True:
            cycle_start = time.time()
            now = cycle_start

            imported, last_id = (
                import_new_signals(
                    connection,
                    last_id,
                )
            )

            due, missed = pending_due(
                connection,
                now,
            )

            ok = 0
            retries = 0

            if due:
                if (
                    now - contract_refresh
                    > 21600
                    or not contract_sizes
                ):
                    try:
                        contract_sizes = (
                            fetch_contract_sizes()
                        )

                        contract_refresh = now

                    except Exception as exc:
                        print(
                            f"[{utc_text()}] "
                            "CONTRACT_DETAIL_ERROR "
                            f"{type(exc).__name__}:"
                            f"{exc}",
                            flush=True,
                        )

                try:
                    tickers = fetch_tickers()

                except Exception as exc:
                    print(
                        f"[{utc_text()}] "
                        "TICKER_ERROR "
                        f"{type(exc).__name__}:"
                        f"{exc}",
                        flush=True,
                    )

                    tickers = {}

                btc_price = sf(
                    tickers.get(
                        "BTC_USDT",
                        {},
                    ).get("last_price")
                )

                symbols = sorted({
                    str(signal["symbol"])
                    for signal, _ in due
                })

                depth_map: dict[
                    str,
                    tuple[
                        dict[str, float] | None,
                        str | None,
                    ],
                ] = {}

                with ThreadPoolExecutor(
                    max_workers=MAX_WORKERS
                ) as pool:
                    futures = {
                        pool.submit(
                            fetch_depth,
                            symbol,
                            contract_sizes.get(
                                symbol,
                                1.0,
                            ),
                        ): symbol
                        for symbol in symbols
                    }

                    for future in as_completed(
                        futures
                    ):
                        (
                            symbol,
                            depth,
                            error,
                        ) = future.result()

                        depth_map[symbol] = (
                            depth,
                            error,
                        )

                snap_ts = time.time()

                for signal, target in due:
                    symbol = str(
                        signal["symbol"]
                    )

                    depth, error = depth_map.get(
                        symbol,
                        (
                            None,
                            "NO_DEPTH_RESULT",
                        ),
                    )

                    actual_age = (
                        snap_ts
                        - float(
                            signal["entry_ts"]
                        )
                    )

                    if depth is None:
                        retries += 1
                        continue

                    ticker = tickers.get(
                        symbol,
                        {},
                    )

                    (
                        gross,
                        cfg,
                        stress,
                    ) = calculate_short(
                        sf(
                            signal.get(
                                "entry_bid1"
                            )
                        ),
                        sf(
                            depth.get("ask1")
                        ),
                    )

                    insert_snapshot(
                        connection,
                        {
                            "signal_id": int(
                                signal["signal_id"]
                            ),

                            "target_age": target,
                            "actual_age": actual_age,

                            "ts": snap_ts,
                            "time_iso": utc_text(
                                snap_ts
                            ),

                            "status": "OK",

                            "contract_size": (
                                contract_sizes.get(
                                    symbol,
                                    1.0,
                                )
                            ),

                            "last_price": sf(
                                ticker.get(
                                    "last_price"
                                )
                            ),

                            "amount24": sf(
                                ticker.get(
                                    "amount24"
                                )
                            ),

                            "hold_vol": sf(
                                ticker.get(
                                    "hold_vol"
                                )
                            ),

                            "btc_price": btc_price,

                            "bid1": sf(
                                depth.get("bid1")
                            ),

                            "ask1": sf(
                                depth.get("ask1")
                            ),

                            "spread_bps": sf(
                                depth.get(
                                    "spread_bps"
                                )
                            ),

                            "bid5_usd": sf(
                                depth.get(
                                    "bid5_usd"
                                )
                            ),

                            "ask5_usd": sf(
                                depth.get(
                                    "ask5_usd"
                                )
                            ),

                            "bid20_usd": sf(
                                depth.get(
                                    "bid20_usd"
                                )
                            ),

                            "ask20_usd": sf(
                                depth.get(
                                    "ask20_usd"
                                )
                            ),

                            "imb5": sf(
                                depth.get("imb5")
                            ),

                            "imb20": sf(
                                depth.get("imb20")
                            ),

                            "wall_skew": sf(
                                depth.get(
                                    "wall_skew"
                                )
                            ),

                            "gross_short_pct": gross,
                            "cfg_short_usd": cfg,
                            "stress_short_usd": stress,

                            "error": error,
                        },
                    )

                    ok += 1

                connection.commit()

            finalized = finalize_old(
                connection,
                time.time(),
            )

            now = time.time()

            if (
                now - last_heartbeat
                >= 60
            ):
                last_heartbeat = now

                summary = counts(connection)

                print(
                    f"[{utc_text(now)}] "
                    "HEARTBEAT "
                    f"imported={imported} "
                    f"due={len(due)} "
                    f"ok={ok} "
                    f"retry={retries} "
                    f"missed={missed} "
                    f"finalized={finalized} "
                    f"signals={summary['signals']} "
                    f"completed={summary['completed']} "
                    f"quality={summary['quality']} "
                    f"pending={summary['pending']} "
                    f"snapshots={summary['snapshots']}",
                    flush=True,
                )

                maybe_send_ready_alert(
                    connection
                )

            elapsed = (
                time.time() - cycle_start
            )

            time.sleep(
                max(
                    0.25,
                    POLL_SECONDS - elapsed,
                )
            )

    finally:
        connection.close()


def selftest() -> None:
    payload = {
        "data": {
            "bids": [
                [100.0, 2.0],
                [99.9, 1.0],
            ],

            "asks": [
                [100.1, 2.0],
                [100.2, 1.0],
            ],
        }
    }

    parsed = parse_depth(
        payload,
        1.0,
    )

    assert parsed["bid1"] == 100.0
    assert parsed["ask1"] == 100.1
    assert parsed["spread_bps"] > 0

    gross, cfg, stress = (
        calculate_short(
            100.0,
            99.0,
        )
    )

    assert gross is not None
    assert cfg is not None
    assert stress is not None

    assert gross > 0
    assert cfg > stress

    assert (
        len(TARGET_AGES)
        == len(set(TARGET_AGES))
    )

    print(
        "V19_DYNAMIC_SNAPSHOT_SELFTEST_OK"
    )


def probe() -> None:
    sizes = fetch_contract_sizes()
    tickers = fetch_tickers()

    symbol = "BTC_USDT"

    _, depth, error = fetch_depth(
        symbol,
        sizes.get(symbol, 1.0),
    )

    if depth is None:
        raise RuntimeError(
            error
            or "BTC depth unavailable"
        )

    print(
        "V19_API_PROBE_OK "
        f"contracts={len(sizes)} "
        f"tickers={len(tickers)} "
        f"btc_bid={depth['bid1']} "
        f"btc_ask={depth['ask1']} "
        f"spread="
        f"{depth['spread_bps']:.3f}bps"
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--selftest",
        action="store_true",
    )

    parser.add_argument(
        "--probe",
        action="store_true",
    )

    parser.add_argument(
        "--status",
        action="store_true",
    )

    parser.add_argument(
        "--send",
        action="store_true",
    )

    arguments = parser.parse_args()

    if arguments.selftest:
        selftest()

    elif arguments.probe:
        probe()

    elif arguments.status:
        create_status(
            send=arguments.send,
        )

    else:
        collect()


if __name__ == "__main__":
    main()
