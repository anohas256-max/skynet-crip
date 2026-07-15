#!/usr/bin/env python3
from __future__ import annotations

import bz2
import csv
import fcntl
import gzip
import hashlib
import json
import lzma
import math
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import time
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/root/skynet")
LIVE = ROOT / "data/v18_micro_paths.sqlite3"

BASE = ROOT / "safe_exports/archive_walkforward"
LATEST = ROOT / "safe_exports/archive_walkforward_latest"
ROOT_REPORT = ROOT / "v18_archive_walkforward_latest.txt"

LOCK = Path("/run/skynet-v18-archive-walkforward.lock")

# WALL_POS candidate selection was completed at this point.
# Only later rows are untouched for the current fixed rules.
CUTOFF_TEXT = "2026-07-14 18:34:04 UTC"

CUTOFF = datetime.strptime(
    CUTOFF_TEXT,
    "%Y-%m-%d %H:%M:%S UTC",
).replace(
    tzinfo=timezone.utc,
).timestamp()

NOTIONAL = 12.0
MAX_MEMBER = 2 * 1024**3

REQUIRED = {
    "ts",
    "time_iso",
    "symbol",
    "entry_price",
    "price_change",
    "vol_ratio",
    "rank",
    "spread_bps",
    "bid1",
    "ask1",
    "wall_skew",
    "max_up",
    "max_down",
    "close_pct",
    "path_json",
    "closed",
}

COLS = [
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
    "max_up",
    "max_down",
    "close_pct",
    "path_json",
    "closed",
    "close_ts",
    "close_time_iso",
]


def tag() -> str:
    return datetime.now(
        timezone.utc,
    ).strftime(
        "%Y%m%d_%H%M%S_UTC",
    )


def utc(
    timestamp: float | None,
) -> str:
    if timestamp is None:
        return "-"

    return datetime.fromtimestamp(
        timestamp,
        timezone.utc,
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC",
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


def safe_name(value: str) -> str:
    return re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value,
    )[-120:]


def is_v18_db(name: str) -> bool:
    lower = Path(name).name.lower()

    return (
        "v18_micro_paths" in lower
        and lower.endswith(
            (
                ".sqlite3",
                ".sqlite",
                ".db",
            )
        )
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(4 * 1024**2),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def snapshot_live(destination: Path) -> None:
    if not LIVE.exists():
        raise FileNotFoundError(
            f"Live V18 DB missing: {LIVE}"
        )

    source = sqlite3.connect(
        str(LIVE),
        timeout=60,
    )

    target = sqlite3.connect(
        str(destination),
    )

    try:
        # Correctly includes the current WAL state.
        source.backup(
            target,
            pages=4096,
            sleep=0.05,
        )
    finally:
        target.close()
        source.close()


def discover(
    root: Path,
    run_dir: Path,
) -> tuple[list[Path], list[Path]]:
    direct: list[Path] = []
    archives: list[Path] = []

    for base, dirs, files in os.walk(root):
        base_path = Path(base)

        dirs[:] = [
            directory
            for directory in dirs
            if directory not in {
                ".git",
                ".venv",
                "__pycache__",
            }
        ]

        if (
            base_path.is_relative_to(run_dir)
            or base_path.is_relative_to(BASE)
        ):
            dirs[:] = []
            continue

        for filename in files:
            path = base_path / filename
            lower = filename.lower()

            if lower.endswith(
                (
                    "-wal",
                    "-shm",
                )
            ):
                continue

            if (
                is_v18_db(filename)
                and path.resolve() != LIVE.resolve()
            ):
                direct.append(path)

            elif lower.endswith(
                (
                    ".tar.gz",
                    ".tgz",
                    ".tar",
                    ".zip",
                    ".sqlite3.gz",
                    ".sqlite3.xz",
                    ".sqlite3.bz2",
                )
            ):
                archives.append(path)

    # Also check top-level /root exports, without
    # recursively walking unrelated projects.
    for path in Path("/root").iterdir():
        if not path.is_file():
            continue

        lower = path.name.lower()

        if (
            is_v18_db(path.name)
            and path.resolve() != LIVE.resolve()
        ):
            direct.append(path)

        elif lower.endswith(
            (
                ".tar.gz",
                ".tgz",
                ".tar",
                ".zip",
                ".sqlite3.gz",
                ".sqlite3.xz",
                ".sqlite3.bz2",
            )
        ):
            archives.append(path)

    return (
        sorted(set(direct)),
        sorted(set(archives)),
    )


def extract_members(
    archive: Path,
    output_directory: Path,
) -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []

    archive_id = hashlib.sha1(
        str(archive).encode(),
    ).hexdigest()[:10]

    try:
        if tarfile.is_tarfile(archive):
            with tarfile.open(
                archive,
                "r:*",
            ) as handle:
                for member in handle.getmembers():
                    if (
                        not member.isfile()
                        or not is_v18_db(member.name)
                        or member.size > MAX_MEMBER
                    ):
                        continue

                    stream = handle.extractfile(member)

                    if stream is None:
                        continue

                    destination = output_directory / (
                        f"{archive_id}__"
                        f"{safe_name(member.name)}"
                    )

                    with destination.open("wb") as output:
                        shutil.copyfileobj(
                            stream,
                            output,
                            4 * 1024**2,
                        )

                    found.append(
                        (
                            destination,
                            member.name,
                        )
                    )

            return found

        if zipfile.is_zipfile(archive):
            with zipfile.ZipFile(archive) as handle:
                for info in handle.infolist():
                    if (
                        info.is_dir()
                        or not is_v18_db(info.filename)
                        or info.file_size > MAX_MEMBER
                    ):
                        continue

                    destination = output_directory / (
                        f"{archive_id}__"
                        f"{safe_name(info.filename)}"
                    )

                    with (
                        handle.open(info) as source,
                        destination.open("wb") as output,
                    ):
                        shutil.copyfileobj(
                            source,
                            output,
                            4 * 1024**2,
                        )

                    found.append(
                        (
                            destination,
                            info.filename,
                        )
                    )

            return found

        decompressors = (
            (".gz", gzip.open),
            (".xz", lzma.open),
            (".bz2", bz2.open),
        )

        for suffix, opener in decompressors:
            if not archive.name.lower().endswith(
                suffix
            ):
                continue

            inner_name = archive.name[
                : -len(suffix)
            ]

            if not is_v18_db(inner_name):
                return found

            destination = output_directory / (
                f"{archive_id}__"
                f"{safe_name(inner_name)}"
            )

            with (
                opener(archive, "rb") as source,
                destination.open("wb") as output,
            ):
                shutil.copyfileobj(
                    source,
                    output,
                    4 * 1024**2,
                )

            found.append(
                (
                    destination,
                    inner_name,
                )
            )

            return found

    except Exception as exc:
        print(
            f"ARCHIVE_ERROR {archive}: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

    return found


def inspect_database(
    path: Path,
    label: str,
    origin: str,
    container: str = "",
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "label": label,
        "path": str(path),
        "origin": origin,
        "container": container,
        "size": path.stat().st_size,
        "sha": sha256_file(path),
        "status": "UNKNOWN",
        "rows": 0,
        "min_ts": None,
        "max_ts": None,
        "unique": 0,
        "overlap": 0,
    }

    try:
        connection = sqlite3.connect(
            f"file:{path}?mode=ro",
            uri=True,
            timeout=30,
        )

        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name "
                "FROM sqlite_master "
                "WHERE type='table'"
            )
        }

        if "signals" not in tables:
            item["status"] = "NO_SIGNALS"
            connection.close()
            return item

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(signals)"
            )
        }

        missing = REQUIRED - columns

        if missing:
            item["status"] = (
                "MISSING:"
                + ",".join(sorted(missing))
            )

            connection.close()
            return item

        row = connection.execute(
            """
            SELECT
                COUNT(*),
                MIN(ts),
                MAX(ts)
            FROM signals
            WHERE closed = 1
              AND path_json IS NOT NULL
              AND bid1 IS NOT NULL
              AND ask1 IS NOT NULL
              AND wall_skew IS NOT NULL
            """
        ).fetchone()

        item.update(
            status="OK",
            rows=int(row[0] or 0),
            min_ts=safe_float(row[1]),
            max_ts=safe_float(row[2]),
        )

        connection.close()

    except Exception as exc:
        item["status"] = (
            f"ERROR:{type(exc).__name__}:{exc}"
        )

    return item


def initialize_unified(
    path: Path,
) -> sqlite3.Connection:
    connection = sqlite3.connect(
        str(path),
    )

    connection.executescript(
        """
        PRAGMA journal_mode=OFF;
        PRAGMA synchronous=OFF;
        PRAGMA temp_store=MEMORY;
        """
    )

    connection.execute(
        """
        CREATE TABLE signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT UNIQUE,

            ts REAL,
            time_iso TEXT,
            symbol TEXT,
            clean_symbol TEXT,

            entry_price REAL,
            price_change REAL,
            vol_1m REAL,
            vol_ratio REAL,
            oi_change REAL,
            rank REAL,
            spread_bps REAL,

            bid1 REAL,
            ask1 REAL,
            bid5_usd REAL,
            ask5_usd REAL,
            bid20_usd REAL,
            ask20_usd REAL,

            imb_5 REAL,
            imb_20 REAL,
            wall_skew REAL,

            max_up REAL,
            max_down REAL,
            close_pct REAL,
            path_json TEXT,
            closed INTEGER,
            close_ts REAL,
            close_time_iso TEXT,

            source_label TEXT
        )
        """
    )

    return connection


def fingerprint(
    data: dict[str, Any],
) -> str:
    payload = [
        data.get(key)
        for key in (
            "time_iso",
            "symbol",
            "clean_symbol",
            "entry_price",
            "price_change",
            "vol_ratio",
            "rank",
            "spread_bps",
            "bid1",
            "ask1",
            "wall_skew",
            "close_pct",
            "path_json",
        )
    ]

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode()

    return hashlib.sha256(
        encoded,
    ).hexdigest()


def ingest(
    item: dict[str, Any],
    unified: sqlite3.Connection,
) -> None:
    path = Path(item["path"])

    source = sqlite3.connect(
        f"file:{path}?mode=ro",
        uri=True,
        timeout=60,
    )

    source.row_factory = sqlite3.Row

    available = {
        row[1]
        for row in source.execute(
            "PRAGMA table_info(signals)"
        )
    }

    selected = [
        column
        for column in COLS
        if column in available
    ]

    query = (
        "SELECT "
        + ",".join(selected)
        + """
          FROM signals
          WHERE closed = 1
            AND path_json IS NOT NULL
            AND bid1 IS NOT NULL
            AND ask1 IS NOT NULL
            AND wall_skew IS NOT NULL
          ORDER BY ts, id
        """
    )

    insert_columns = (
        ["fingerprint"]
        + COLS
        + ["source_label"]
    )

    insert_sql = (
        "INSERT OR IGNORE INTO signals ("
        + ",".join(insert_columns)
        + ") VALUES ("
        + ",".join(
            "?"
            for _ in insert_columns
        )
        + ")"
    )

    before = unified.total_changes
    attempted = 0

    cursor = source.execute(query)

    while True:
        rows = cursor.fetchmany(500)

        if not rows:
            break

        batch = []

        for row in rows:
            data = {
                column: (
                    row[column]
                    if column in available
                    else None
                )
                for column in COLS
            }

            if not data["clean_symbol"]:
                data["clean_symbol"] = str(
                    data["symbol"] or ""
                ).replace(
                    "_USDT",
                    "",
                )

            values = [fingerprint(data)]

            values.extend(
                data[column]
                for column in COLS
            )

            values.append(
                item["label"]
            )

            batch.append(values)
            attempted += 1

        unified.executemany(
            insert_sql,
            batch,
        )

    unified.commit()
    source.close()

    item["unique"] = (
        unified.total_changes - before
    )

    item["overlap"] = (
        attempted - item["unique"]
    )

    print(
        f"INGEST {item['label']} "
        f"attempted={attempted} "
        f"unique={item['unique']} "
        f"overlap={item['overlap']}",
        flush=True,
    )


def metric_line(
    metric: dict[str, Any],
) -> str:
    return (
        f"n={metric['n']:4d} "
        f"sum=${metric['sum']:+.5f} "
        f"avg=${metric['avg']:+.5f} "
        f"WR={metric['wr']:5.1f}% "
        f"PF={metric['pf']:5.2f} "
        f"leave_best=${metric['leave_best']:+.5f} "
        f"best={metric['best_symbol']} "
        f"share={metric['positive_share']:.1%}"
    )


def cost_metric(
    trades: list[dict[str, Any]],
    cost: float,
    rescue: Any,
) -> dict[str, Any]:
    deduction = (
        NOTIONAL * cost / 100
    )

    rows = [
        {
            "symbol": trade["symbol"],
            "value": (
                float(trade["gross"])
                - deduction
            ),
        }
        for trade in trades
    ]

    return rescue.metric(
        rows,
        "value",
    )


def analyze(
    name: str,
    config: dict[str, Any],
    rows: list[dict[str, Any]],
    rescue: Any,
    audit: Any,
) -> list[str]:
    evaluated = audit.evaluate(
        rows,
        config,
    )

    pre = rescue.select_v18_trades(
        [
            row
            for row in rows
            if row["_ts"] < CUTOFF
        ],
        config,
    )

    post = rescue.select_v18_trades(
        [
            row
            for row in rows
            if row["_ts"] >= CUTOFF
        ],
        config,
    )

    post_metric = rescue.metric(
        post,
        "stress",
    )

    output = [
        "=" * 140,
        f"{name} {rescue.config_name(config)}",
        "=" * 140,

        "TRAIN70 "
        + metric_line(
            evaluated["train"]
        ),

        "TEST30  "
        + metric_line(
            evaluated["test"]
        ),

        "ALL     "
        + metric_line(
            evaluated["all"]
        ),

        (
            "8_FOLDS_POSITIVE="
            f"{evaluated['positive_folds']}/8"
        ),
    ]

    for index, fold in enumerate(
        evaluated["folds"],
        1,
    ):
        output.append(
            f"  F{index} "
            + metric_line(fold)
        )

    output.extend(
        [
            "",
            "PRE_SELECTION  "
            + metric_line(
                rescue.metric(
                    pre,
                    "stress",
                )
            ),

            "POST_SELECTION "
            + metric_line(
                post_metric
            ),

            "",
            "COST_SENSITIVITY",
        ]
    )

    for cost in (
        0.16,
        0.20,
        0.26,
        0.30,
        0.36,
        0.40,
    ):
        output.append(
            f"  cost={cost:.2f}% "
            + metric_line(
                cost_metric(
                    evaluated["all_trades"],
                    cost,
                    rescue,
                )
            )
        )

    weeks: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    for trade in evaluated["all_trades"]:
        week = datetime.fromtimestamp(
            float(trade["ts"]),
            timezone.utc,
        ).strftime(
            "%G-W%V",
        )

        weeks[week].append(trade)

    output.extend(
        [
            "",
            "WEEKLY_STRESS",
        ]
    )

    for week in sorted(weeks):
        output.append(
            f"  {week} "
            + metric_line(
                rescue.metric(
                    weeks[week],
                    "stress",
                )
            )
        )

    historical_pass = (
        evaluated["train"]["n"] >= 50
        and evaluated["test"]["n"] >= 20

        and evaluated["train"]["sum"] > 0
        and evaluated["test"]["sum"] > 0

        and evaluated["train"]["pf"] >= 1.10
        and evaluated["test"]["pf"] >= 1.10

        and evaluated["train"]["leave_best"] > 0
        and evaluated["test"]["leave_best"] > 0
        and evaluated["all"]["leave_best"] > 0

        and evaluated["all"]["positive_share"] <= 0.45
        and evaluated["positive_folds"] >= 6
    )

    if post_metric["n"] >= 10:
        if (
            post_metric["sum"] > 0
            and post_metric["pf"] >= 1.0
        ):
            oos = "PASS_10_CONTINUE_TO_20"
        else:
            oos = "REJECT_AT_10"
    else:
        oos = (
            f"COLLECTING_"
            f"{post_metric['n']}_OF_10"
        )

    output.extend(
        [
            "",
            (
                "HISTORICAL_STRICT_GATE="
                f"{'PASS' if historical_pass else 'FAIL'}"
            ),
            f"UNTOUCHED_OOS={oos}",
            "REAL_DECISION=BLOCKED",
        ]
    )

    return output


def main() -> int:
    BASE.mkdir(
        parents=True,
        exist_ok=True,
    )

    run = BASE / (
        f"archive_walkforward_{tag()}"
    )

    extracted = run / "extracted"

    run.mkdir()
    extracted.mkdir()

    lock = LOCK.open("w")

    try:
        fcntl.flock(
            lock.fileno(),
            fcntl.LOCK_EX
            | fcntl.LOCK_NB,
        )
    except BlockingIOError:
        print(
            "ARCHIVE_WALKFORWARD_ALREADY_RUNNING"
        )
        return 2

    if (
        LATEST.is_symlink()
        or LATEST.is_file()
    ):
        LATEST.unlink()

    elif LATEST.is_dir():
        shutil.rmtree(LATEST)

    LATEST.symlink_to(run)

    print(
        f"RUN={run}",
        flush=True,
    )

    live_copy = (
        extracted
        / "live_v18_snapshot.sqlite3"
    )

    snapshot_live(live_copy)

    direct, archives = discover(
        ROOT,
        run,
    )

    items = [
        inspect_database(
            live_copy,
            "LIVE_SNAPSHOT",
            "LIVE",
        )
    ]

    for index, path in enumerate(
        direct,
        1,
    ):
        items.append(
            inspect_database(
                path,
                (
                    f"DIRECT_{index:03d}_"
                    f"{safe_name(path.name)}"
                ),
                "DIRECT",
                str(path),
            )
        )

    member_count = 0

    for archive_index, archive in enumerate(
        archives,
        1,
    ):
        members = extract_members(
            archive,
            extracted,
        )

        for member_index, (
            path,
            member,
        ) in enumerate(
            members,
            1,
        ):
            member_count += 1

            items.append(
                inspect_database(
                    path,
                    (
                        f"ARCH_{archive_index:03d}_"
                        f"{member_index:02d}_"
                        f"{safe_name(Path(member).name)}"
                    ),
                    "ARCHIVE",
                    f"{archive}::{member}",
                )
            )

    capable = [
        item
        for item in items
        if item["status"] == "OK"
    ]

    seen_hashes: set[str] = set()
    ordered: list[dict[str, Any]] = []

    for item in sorted(
        capable,
        key=lambda value: (
            (
                value["max_ts"]
                if value["max_ts"] is not None
                else float("inf")
            ),
            (
                1
                if value["origin"] == "LIVE"
                else 0
            ),
            value["label"],
        ),
    ):
        if item["sha"] in seen_hashes:
            item["status"] = (
                "IDENTICAL_DUPLICATE"
            )
            continue

        seen_hashes.add(
            item["sha"]
        )

        ordered.append(item)

    unified_path = (
        run / "unified.sqlite3"
    )

    unified = initialize_unified(
        unified_path,
    )

    for item in ordered:
        ingest(
            item,
            unified,
        )

    unified.execute(
        "CREATE INDEX idx_ts "
        "ON signals(ts)"
    )

    unified.commit()

    (
        unified_count,
        min_timestamp,
        max_timestamp,
    ) = unified.execute(
        """
        SELECT
            COUNT(*),
            MIN(ts),
            MAX(ts)
        FROM signals
        """
    ).fetchone()

    unified.close()

    census_path = (
        run / "source_census.csv"
    )

    with census_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        fields = [
            "label",
            "origin",
            "container",
            "status",
            "rows",
            "unique",
            "overlap",
            "min_utc",
            "max_utc",
            "size",
            "sha",
            "path",
        ]

        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()

        for item in items:
            writer.writerow(
                {
                    "label": item["label"],
                    "origin": item["origin"],
                    "container": item["container"],
                    "status": item["status"],
                    "rows": item["rows"],
                    "unique": item["unique"],
                    "overlap": item["overlap"],
                    "min_utc": utc(
                        item["min_ts"]
                    ),
                    "max_utc": utc(
                        item["max_ts"]
                    ),
                    "size": item["size"],
                    "sha": item["sha"],
                    "path": item["path"],
                }
            )

    sys.path.insert(
        0,
        str(ROOT),
    )

    import v18_research_rescue_lab as rescue
    import v18_wallpos_candidate_audit as audit

    rescue.V18_DB = unified_path

    rows = rescue.load_v18_rows()

    configs = {
        "WALLPOS_R80": {
            "pc_min": 1.20,
            "pc_max": 2.50,
            "vol_min": 8.0,
            "spread_max": 2.0,
            "rank_max": 80,
            "exit_mode": "TIME",
            "extra": "WALL_POS",
        },

        "WALLPOS_R120": {
            "pc_min": 1.20,
            "pc_max": 2.50,
            "vol_min": 8.0,
            "spread_max": 2.0,
            "rank_max": 120,
            "exit_mode": "TIME",
            "extra": "WALL_POS",
        },
    }

    live_rows = next(
        (
            item["rows"]
            for item in items
            if item["origin"] == "LIVE"
        ),
        0,
    )

    extra_rows = max(
        0,
        int(unified_count)
        - int(live_rows),
    )

    lines = [
        "=" * 140,
        (
            "SKYNET V18 ARCHIVE WALKFORWARD "
            f"UTC={tag()}"
        ),
        "=" * 140,

        (
            "Archive model: recorded entry bid/ask "
            "+ future path proxy. True future bid/ask "
            "remains exact-forward only."
        ),

        (
            "No orders. No filter/env/service changes. "
            "REAL_TRADING=OFF."
        ),

        "",
        "CENSUS",

        (
            f"direct_v18_dbs={len(direct)} "
            f"archives_scanned={len(archives)} "
            f"db_members_extracted={member_count}"
        ),

        (
            f"path_capable_sources={len(capable)} "
            f"unique_db_files={len(ordered)}"
        ),

        (
            f"live_closed_rows={live_rows} "
            f"unified_deduped_rows={unified_count} "
            f"unique_rows_beyond_live={extra_rows}"
        ),

        (
            f"unified_range="
            f"{utc(safe_float(min_timestamp))} .. "
            f"{utc(safe_float(max_timestamp))}"
        ),

        (
            f"usable_rows_after_filters="
            f"{len(rows)}"
        ),

        "",
        "SOURCE_CONTRIBUTIONS",
    ]

    for item in ordered:
        lines.append(
            f"{item['label']} "
            f"origin={item['origin']} "
            f"range={utc(item['min_ts'])}.."
            f"{utc(item['max_ts'])} "
            f"rows={item['rows']} "
            f"unique={item['unique']} "
            f"overlap={item['overlap']}"
        )

    archived_ok = [
        item
        for item in items
        if (
            item["origin"] == "ARCHIVE"
            and item["status"] == "OK"
        )
    ]

    if extra_rows > 0:
        census_verdict = (
            "ARCHIVES_ADD_UNIQUE_ROWS"
        )

    elif archived_ok:
        census_verdict = (
            "ARCHIVES_OVERLAP_LIVE_HISTORY"
        )

    else:
        census_verdict = (
            "NO_ARCHIVED_V18_PATH_DB_FOUND"
        )

    lines.extend(
        [
            "",
            (
                "ARCHIVE_CENSUS_VERDICT="
                f"{census_verdict}"
            ),
        ]
    )

    for name, config in configs.items():
        lines.append("")

        lines.extend(
            analyze(
                name,
                config,
                rows,
                rescue,
                audit,
            )
        )

    # This isolates the exact marginal addition of R120.
    delta_rows = [
        row
        for row in rows
        if 80 < float(row["_rank"]) <= 120
    ]

    delta = rescue.select_v18_trades(
        delta_rows,
        configs["WALLPOS_R120"],
    )

    delta_post = rescue.select_v18_trades(
        [
            row
            for row in delta_rows
            if row["_ts"] >= CUTOFF
        ],
        configs["WALLPOS_R120"],
    )

    lines.extend(
        [
            "",
            "=" * 140,
            "R120 MARGINAL BAND rank=81..120",
            "=" * 140,

            "ALL  "
            + metric_line(
                rescue.metric(
                    delta,
                    "stress",
                )
            ),

            "POST "
            + metric_line(
                rescue.metric(
                    delta_post,
                    "stress",
                )
            ),

            (
                "This isolates what R120 adds "
                "beyond the preregistered R80 lane."
            ),

            "",
            "DECISION RULES",

            (
                "Historical archives test stability, "
                "but overlapping snapshots are not "
                "independent untouched tests."
            ),

            (
                f"Only data after {CUTOFF_TEXT} are "
                "untouched for the fixed WALL_POS rules."
            ),

            (
                "At 10 untouched closes: stress<=0 "
                "or PF<1.00 => reject; otherwise "
                "continue to 20."
            ),

            (
                "At 20: stress>0, PF>=1.20, "
                "leave-best>0 and >=3 symbols "
                "=> continue to 40."
            ),

            "REAL_TRADING=OFF.",
        ]
    )

    text = "\n".join(lines) + "\n"

    report = (
        run
        / "v18_archive_walkforward_report.txt"
    )

    report.write_text(
        text,
        encoding="utf-8",
    )

    ROOT_REPORT.write_text(
        text,
        encoding="utf-8",
    )

    (
        run / "COMPLETED_UTC.txt"
    ).write_text(
        utc(time.time()) + "\n",
        encoding="utf-8",
    )

    pack = ROOT / (
        f"skynet_archive_walkforward_"
        f"{tag()}.tar.gz"
    )

    with tarfile.open(
        pack,
        "w:gz",
    ) as handle:
        handle.add(
            report,
            arcname=report.name,
        )

        handle.add(
            census_path,
            arcname="source_census.csv",
        )

    print(
        text,
        flush=True,
    )

    deliveries = (
        (
            report,
            "SKYNET archive walkforward",
        ),
        (
            census_path,
            "SKYNET archive DB census",
        ),
        (
            pack,
            "SKYNET archive walkforward pack",
        ),
    )

    for path, caption in deliveries:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "tg_send_any.py"),
                str(path),
                caption,
            ],
            cwd=ROOT,
            check=False,
        )

    # These are only temporary working copies.
    # Original databases and archives are untouched.
    shutil.rmtree(
        extracted,
        ignore_errors=True,
    )

    unified_path.unlink(
        missing_ok=True,
    )

    print(
        f"REPORT={report}\n"
        f"PACK={pack}\n"
        "ARCHIVE_WALKFORWARD_COMPLETE",
        flush=True,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
