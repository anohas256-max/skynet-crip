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
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO


ROOT = Path("/root/skynet")
LIVE_DB = ROOT / "data/v18_micro_paths.sqlite3"

BASE = ROOT / "safe_exports/recursive_archive_census"
LATEST = ROOT / "safe_exports/recursive_archive_census_latest"

ROOT_REPORT = ROOT / "v18_recursive_archive_census_latest.txt"
LOCK_FILE = Path("/run/skynet-v18-recursive-archive-census.lock")

MAX_DEPTH = 3
MAX_OBJECT_BYTES = 2 * 1024**3
MAX_HEAD_BYTES = 128 * 1024
MAX_TEXT_CANDIDATES = 500

SQLITE_MAGIC = b"SQLite format 3\x00"

ARCHIVE_SUFFIXES = (
    ".tar.gz",
    ".tgz",
    ".tar",
    ".zip",
    ".gz",
    ".xz",
    ".bz2",
)

TEXT_SUFFIXES = (
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".ndjson",
    ".txt",
    ".log",
)

EXACT_REQUIRED = {
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

TEXT_FIELDS = (
    "bid1",
    "ask1",
    "wall_skew",
    "path_json",
    "max_up",
    "max_down",
    "close_pct",
    "price_change",
    "vol_ratio",
    "spread_bps",
    "rank",
    "signal_id",
)

EVENT_MARKERS = (
    "V18_PATH",
    "V18_MICRO",
    "signal_id=",
    "entry_bid",
    "future_ask",
    "EXACT_",
)


def utc_tag() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_UTC"
    )


def safe_name(value: str) -> str:
    cleaned = "".join(
        character
        if character.isalnum() or character in "._-"
        else "_"
        for character in value
    )

    return cleaned[-160:]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(4 * 1024**2),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def archive_name(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(ARCHIVE_SUFFIXES)


def text_name(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(TEXT_SUFFIXES)


def database_name(name: str) -> bool:
    lower = name.lower()

    return lower.endswith(
        (
            ".sqlite3",
            ".sqlite",
            ".db",
        )
    )


def parse_number(value: Any) -> float | None:
    try:
        result = float(value)

        if not math.isfinite(result):
            return None

        return result
    except Exception:
        return None


class Census:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.temp_dir = run_dir / "tmp"
        self.compatible_dir = run_dir / "compatible_dbs"
        self.samples_dir = run_dir / "candidate_samples"

        self.temp_dir.mkdir()
        self.compatible_dir.mkdir()
        self.samples_dir.mkdir()

        self.root_archives = 0
        self.nested_archives = 0
        self.archive_members = 0
        self.sqlite_objects = 0

        self.sqlite_rows: list[dict[str, Any]] = []
        self.text_rows: list[dict[str, Any]] = []
        self.errors: list[str] = []

        self.seen_archive_hashes: set[str] = set()
        self.seen_sqlite_hashes: set[str] = set()
        self.kept_compatible_hashes: set[str] = set()

        self.live_sha = (
            sha256_file(LIVE_DB)
            if LIVE_DB.exists()
            else ""
        )

    def record_error(
        self,
        source: str,
        error: Exception | str,
    ) -> None:
        message = (
            f"{source}: "
            f"{type(error).__name__}: {error}"
            if isinstance(error, Exception)
            else f"{source}: {error}"
        )

        self.errors.append(message)
        print(f"ERROR {message}", flush=True)

    def copy_stream_limited(
        self,
        stream: BinaryIO,
        destination: Path,
        initial: bytes = b"",
    ) -> bool:
        written = 0

        with destination.open("wb") as output:
            if initial:
                output.write(initial)
                written += len(initial)

            while True:
                chunk = stream.read(4 * 1024**2)

                if not chunk:
                    break

                written += len(chunk)

                if written > MAX_OBJECT_BYTES:
                    output.close()
                    destination.unlink(missing_ok=True)
                    return False

                output.write(chunk)

        return True

    def inspect_sqlite(
        self,
        path: Path,
        source_chain: str,
    ) -> None:
        self.sqlite_objects += 1

        try:
            digest = sha256_file(path)

            if digest in self.seen_sqlite_hashes:
                self.sqlite_rows.append({
                    "source": source_chain,
                    "status": "IDENTICAL_DUPLICATE",
                    "tables": "",
                    "signals_columns": "",
                    "missing": "",
                    "rows": 0,
                    "min_ts": "",
                    "max_ts": "",
                    "sha256": digest,
                    "kept_path": "",
                })
                return

            self.seen_sqlite_hashes.add(digest)

            connection = sqlite3.connect(
                f"file:{path}?mode=ro",
                uri=True,
                timeout=30,
            )

            tables = [
                row[0]
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table'
                    ORDER BY name
                    """
                )
            ]

            if "signals" not in tables:
                self.sqlite_rows.append({
                    "source": source_chain,
                    "status": "NO_SIGNALS",
                    "tables": ",".join(tables),
                    "signals_columns": "",
                    "missing": "",
                    "rows": 0,
                    "min_ts": "",
                    "max_ts": "",
                    "sha256": digest,
                    "kept_path": "",
                })

                connection.close()
                return

            columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(signals)"
                )
            }

            missing = sorted(
                EXACT_REQUIRED - columns
            )

            count = 0
            min_ts = None
            max_ts = None

            try:
                row = connection.execute(
                    """
                    SELECT
                        COUNT(*),
                        MIN(ts),
                        MAX(ts)
                    FROM signals
                    """
                ).fetchone()

                count = int(row[0] or 0)
                min_ts = parse_number(row[1])
                max_ts = parse_number(row[2])
            except Exception:
                pass

            connection.close()

            if not missing:
                status = "EXACT_PATH_CAPABLE"
            else:
                status = "PARTIAL_SIGNALS_SCHEMA"

            kept_path = ""

            if (
                status == "EXACT_PATH_CAPABLE"
                and digest != self.live_sha
                and digest not in self.kept_compatible_hashes
            ):
                self.kept_compatible_hashes.add(digest)

                destination = self.compatible_dir / (
                    f"{digest[:12]}__"
                    f"{safe_name(Path(source_chain).name)}"
                )

                if not database_name(destination.name):
                    destination = destination.with_suffix(
                        ".sqlite3"
                    )

                shutil.copy2(path, destination)
                kept_path = str(destination)

            self.sqlite_rows.append({
                "source": source_chain,
                "status": status,
                "tables": ",".join(tables),
                "signals_columns": ",".join(
                    sorted(columns)
                ),
                "missing": ",".join(missing),
                "rows": count,
                "min_ts": min_ts or "",
                "max_ts": max_ts or "",
                "sha256": digest,
                "kept_path": kept_path,
            })

            print(
                f"SQLITE {status} "
                f"rows={count} "
                f"missing={','.join(missing) or '-'} "
                f"{source_chain}",
                flush=True,
            )

        except Exception as exc:
            self.record_error(source_chain, exc)

    def score_text(
        self,
        name: str,
        head: bytes,
        source_chain: str,
    ) -> None:
        if len(self.text_rows) >= MAX_TEXT_CANDIDATES:
            return

        try:
            text = head.decode(
                "utf-8",
                errors="ignore",
            )
        except Exception:
            return

        lowered = text.lower()

        fields = [
            field
            for field in TEXT_FIELDS
            if field.lower() in lowered
        ]

        events = [
            marker
            for marker in EVENT_MARKERS
            if marker.lower() in lowered
        ]

        score = len(fields) + 2 * len(events)

        if score < 4:
            return

        digest = hashlib.sha256(
            (
                source_chain
                + "\n"
                + text[:65536]
            ).encode(
                "utf-8",
                errors="ignore",
            )
        ).hexdigest()

        sample = self.samples_dir / (
            f"{score:02d}_{digest[:12]}_"
            f"{safe_name(Path(name).name)}.txt"
        )

        sample.write_text(
            (
                f"SOURCE={source_chain}\n"
                f"SCORE={score}\n"
                f"FIELDS={','.join(fields)}\n"
                f"EVENTS={','.join(events)}\n"
                "\n"
                + text[:65536]
            ),
            encoding="utf-8",
        )

        self.text_rows.append({
            "source": source_chain,
            "score": score,
            "fields": ",".join(fields),
            "events": ",".join(events),
            "sample": str(sample),
        })

        print(
            f"TEXT_CANDIDATE score={score} "
            f"fields={','.join(fields)} "
            f"{source_chain}",
            flush=True,
        )

    def process_stream(
        self,
        stream: BinaryIO,
        name: str,
        declared_size: int,
        source_chain: str,
        depth: int,
    ) -> None:
        if declared_size <= 0:
            return

        if declared_size > MAX_OBJECT_BYTES:
            return

        head = stream.read(MAX_HEAD_BYTES)

        if head.startswith(SQLITE_MAGIC):
            destination = self.temp_dir / (
                f"sqlite_{hashlib.sha1(source_chain.encode()).hexdigest()[:14]}.db"
            )

            if self.copy_stream_limited(
                stream,
                destination,
                initial=head,
            ):
                try:
                    self.inspect_sqlite(
                        destination,
                        source_chain,
                    )
                finally:
                    destination.unlink(
                        missing_ok=True
                    )

            return

        if (
            archive_name(name)
            and depth < MAX_DEPTH
        ):
            destination = self.temp_dir / (
                f"nested_{depth}_"
                f"{hashlib.sha1(source_chain.encode()).hexdigest()[:14]}_"
                f"{safe_name(Path(name).name)}"
            )

            if self.copy_stream_limited(
                stream,
                destination,
                initial=head,
            ):
                try:
                    self.scan_archive(
                        destination,
                        source_chain,
                        depth + 1,
                        root=False,
                    )
                finally:
                    destination.unlink(
                        missing_ok=True
                    )

            return

        if (
            text_name(name)
            or any(
                token in name.lower()
                for token in (
                    "v17",
                    "v18",
                    "micro",
                    "path",
                    "signal",
                    "recorder",
                    "replay",
                    "shadow",
                )
            )
        ):
            self.score_text(
                name,
                head,
                source_chain,
            )

    def scan_tar(
        self,
        path: Path,
        chain: str,
        depth: int,
    ) -> None:
        with tarfile.open(path, "r:*") as handle:
            for member in handle.getmembers():
                if not member.isfile():
                    continue

                self.archive_members += 1

                stream = handle.extractfile(member)

                if stream is None:
                    continue

                with stream:
                    self.process_stream(
                        stream,
                        member.name,
                        int(member.size or 0),
                        f"{chain}::{member.name}",
                        depth,
                    )

    def scan_zip(
        self,
        path: Path,
        chain: str,
        depth: int,
    ) -> None:
        with zipfile.ZipFile(path) as handle:
            for info in handle.infolist():
                if info.is_dir():
                    continue

                self.archive_members += 1

                with handle.open(info) as stream:
                    self.process_stream(
                        stream,
                        info.filename,
                        int(info.file_size or 0),
                        f"{chain}::{info.filename}",
                        depth,
                    )

    def scan_single_compressed(
        self,
        path: Path,
        chain: str,
        depth: int,
    ) -> None:
        lower = path.name.lower()

        if lower.endswith(".gz"):
            opener = gzip.open
            inner_name = path.name[:-3]
        elif lower.endswith(".xz"):
            opener = lzma.open
            inner_name = path.name[:-3]
        elif lower.endswith(".bz2"):
            opener = bz2.open
            inner_name = path.name[:-4]
        else:
            return

        with opener(path, "rb") as stream:
            self.process_stream(
                stream,
                inner_name,
                MAX_OBJECT_BYTES,
                f"{chain}::{inner_name}",
                depth,
            )

    def scan_archive(
        self,
        path: Path,
        chain: str,
        depth: int,
        root: bool,
    ) -> None:
        try:
            digest = sha256_file(path)

            if digest in self.seen_archive_hashes:
                return

            self.seen_archive_hashes.add(digest)

            if root:
                self.root_archives += 1
            else:
                self.nested_archives += 1

            print(
                f"SCAN_ARCHIVE depth={depth} {chain}",
                flush=True,
            )

            if tarfile.is_tarfile(path):
                self.scan_tar(
                    path,
                    chain,
                    depth,
                )
                return

            if zipfile.is_zipfile(path):
                self.scan_zip(
                    path,
                    chain,
                    depth,
                )
                return

            self.scan_single_compressed(
                path,
                chain,
                depth,
            )

        except Exception as exc:
            self.record_error(chain, exc)


def discover_root_archives() -> list[Path]:
    found: set[Path] = set()

    excluded_names = {
        ".git",
        ".venv",
        "__pycache__",
    }

    for base, directories, files in os.walk(ROOT):
        base_path = Path(base)

        directories[:] = [
            directory
            for directory in directories
            if directory not in excluded_names
        ]

        try:
            if base_path.is_relative_to(BASE):
                directories[:] = []
                continue
        except Exception:
            pass

        for filename in files:
            path = base_path / filename

            if archive_name(filename):
                found.add(path)

    for path in Path("/root").iterdir():
        if (
            path.is_file()
            and archive_name(path.name)
        ):
            found.add(path)

    return sorted(found)


def discover_direct_databases() -> list[Path]:
    found: set[Path] = set()

    for directory in (
        ROOT / "data",
        ROOT / "archive",
        ROOT / "safe_exports",
    ):
        if not directory.exists():
            continue

        for path in directory.rglob("*"):
            if (
                path.is_file()
                and database_name(path.name)
            ):
                try:
                    if path.is_relative_to(BASE):
                        continue
                except Exception:
                    pass

                found.add(path)

    return sorted(found)


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fields: list[str],
) -> None:
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    BASE.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_dir = BASE / (
        f"recursive_archive_census_{utc_tag()}"
    )
    run_dir.mkdir()

    lock_handle = LOCK_FILE.open("w")

    try:
        fcntl.flock(
            lock_handle.fileno(),
            fcntl.LOCK_EX | fcntl.LOCK_NB,
        )
    except BlockingIOError:
        print(
            "RECURSIVE_ARCHIVE_CENSUS_ALREADY_RUNNING"
        )
        return 2

    if (
        LATEST.is_symlink()
        or LATEST.is_file()
    ):
        LATEST.unlink()
    elif LATEST.is_dir():
        shutil.rmtree(LATEST)

    LATEST.symlink_to(run_dir)

    census = Census(run_dir)

    direct_databases = discover_direct_databases()
    root_archives = discover_root_archives()

    print(
        f"DIRECT_DATABASES={len(direct_databases)}",
        flush=True,
    )
    print(
        f"ROOT_ARCHIVES={len(root_archives)}",
        flush=True,
    )

    for path in direct_databases:
        census.inspect_sqlite(
            path,
            str(path),
        )

    for path in root_archives:
        census.scan_archive(
            path,
            str(path),
            depth=0,
            root=True,
        )

    sqlite_csv = run_dir / "sqlite_object_census.csv"
    text_csv = run_dir / "raw_text_candidate_census.csv"

    write_csv(
        sqlite_csv,
        census.sqlite_rows,
        [
            "source",
            "status",
            "tables",
            "signals_columns",
            "missing",
            "rows",
            "min_ts",
            "max_ts",
            "sha256",
            "kept_path",
        ],
    )

    text_rows = sorted(
        census.text_rows,
        key=lambda row: int(row["score"]),
        reverse=True,
    )

    write_csv(
        text_csv,
        text_rows,
        [
            "source",
            "score",
            "fields",
            "events",
            "sample",
        ],
    )

    exact_nonlive = [
        row
        for row in census.sqlite_rows
        if (
            row["status"] == "EXACT_PATH_CAPABLE"
            and row["sha256"] != census.live_sha
        )
    ]

    partial = [
        row
        for row in census.sqlite_rows
        if row["status"] == "PARTIAL_SIGNALS_SCHEMA"
    ]

    lines = [
        "=" * 140,
        (
            "SKYNET RECURSIVE ARCHIVE PAYLOAD CENSUS "
            f"UTC={utc_tag()}"
        ),
        "=" * 140,
        (
            "Scans nested archives to depth 3, identifies "
            "SQLite by file magic and probes raw text data."
        ),
        "No strategy, service, state or environment changes.",
        "REAL_TRADING=OFF.",
        "",
        "SUMMARY",
        f"direct_databases={len(direct_databases)}",
        f"root_archives={census.root_archives}",
        f"nested_archives={census.nested_archives}",
        f"archive_members_seen={census.archive_members}",
        f"sqlite_objects={census.sqlite_objects}",
        f"exact_path_capable_nonlive={len(exact_nonlive)}",
        f"partial_signals_databases={len(partial)}",
        f"raw_text_candidates={len(text_rows)}",
        f"errors={len(census.errors)}",
        "",
        "SQLITE OBJECTS",
    ]

    for row in census.sqlite_rows:
        lines.append(
            f"{row['status']:<28} "
            f"rows={row['rows']:<10} "
            f"missing={row['missing'] or '-'} "
            f"source={row['source']}"
        )

    lines.extend(
        [
            "",
            "TOP RAW TEXT CANDIDATES",
        ]
    )

    if text_rows:
        for row in text_rows[:40]:
            lines.append(
                f"score={row['score']:<3} "
                f"fields={row['fields'] or '-'} "
                f"source={row['source']}"
            )
    else:
        lines.append("[EMPTY]")

    lines.extend(
        [
            "",
            "DECISION",
        ]
    )

    if exact_nonlive:
        lines.append(
            "EXACT_ARCHIVED_DATABASES_FOUND"
        )
        lines.append(
            "Compatible databases were retained and the "
            "deduplicated archive walk-forward will run automatically."
        )
    elif text_rows:
        lines.append(
            "RAW_DATA_CANDIDATES_FOUND"
        )
        lines.append(
            "No complete archived exact DB was found, but raw "
            "CSV/JSONL/log candidates exist for a schema adapter."
        )
    elif partial:
        lines.append(
            "ONLY_PARTIAL_DATABASES_FOUND"
        )
        lines.append(
            "Historical databases lack fields required for exact "
            "execution reconstruction."
        )
    else:
        lines.append(
            "NO_ADDITIONAL_HISTORICAL_EXECUTION_DATA_FOUND"
        )

    lines.extend(
        [
            "",
            (
                "R120 untouched forward remains governed by "
                "the preregistered 10/20/40 gate."
            ),
            "REAL_TRADING=OFF.",
        ]
    )

    text = "\n".join(lines) + "\n"

    report = run_dir / (
        "v18_recursive_archive_census_report.txt"
    )

    report.write_text(
        text,
        encoding="utf-8",
    )

    ROOT_REPORT.write_text(
        text,
        encoding="utf-8",
    )

    if census.errors:
        (
            run_dir / "errors.txt"
        ).write_text(
            "\n".join(census.errors) + "\n",
            encoding="utf-8",
        )

    (
        run_dir / "COMPLETED_UTC.txt"
    ).write_text(
        datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC\n"
        ),
        encoding="utf-8",
    )

    print(text, flush=True)

    pack = ROOT / (
        f"skynet_recursive_archive_census_"
        f"{utc_tag()}.tar.gz"
    )

    with tarfile.open(pack, "w:gz") as handle:
        handle.add(
            report,
            arcname=report.name,
        )
        handle.add(
            sqlite_csv,
            arcname=sqlite_csv.name,
        )
        handle.add(
            text_csv,
            arcname=text_csv.name,
        )

        if census.errors:
            handle.add(
                run_dir / "errors.txt",
                arcname="errors.txt",
            )

    for path, caption in (
        (
            report,
            "SKYNET recursive archive census",
        ),
        (
            sqlite_csv,
            "SKYNET archived SQLite census",
        ),
        (
            text_csv,
            "SKYNET raw data candidate census",
        ),
        (
            pack,
            "SKYNET recursive archive census pack",
        ),
    ):
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

    shutil.rmtree(
        census.temp_dir,
        ignore_errors=True,
    )

    print(f"REPORT={report}")
    print(f"PACK={pack}")

    if exact_nonlive:
        print(
            "EXACT_ARCHIVE_FOUND: "
            "starting deduplicated walk-forward",
            flush=True,
        )

        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "v18_archive_walkforward_lab.py"
                ),
            ],
            cwd=ROOT,
            check=False,
        )

        print(
            f"FOLLOWUP_WALKFORWARD_RC="
            f"{result.returncode}",
            flush=True,
        )

    print("RECURSIVE_ARCHIVE_CENSUS_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
