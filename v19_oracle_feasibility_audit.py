#!/usr/bin/env python3
from __future__ import annotations

import math
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import v19_dynamic_structure_audit as audit

ROOT = Path('/root/skynet')
REPORT = ROOT / 'v19_oracle_feasibility_latest.txt'
DECISION_AGES = (5, 15, 30, 60)
EXIT_AGES = (60, 120, 180, 300)
MAX_LATENESS = 5.0
NOTIONAL = 12.0
STRESS_COST = 0.26
HARD_COST = 0.36


def utc(ts: float | None = None) -> str:
    if ts is None:
        ts = time.time()
    return datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def sf(value: Any) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except Exception:
        return None


def latency_ok(record: dict[str, Any], decision_age: int, exit_age: int) -> bool:
    for age in (decision_age, exit_age):
        snap = record['snapshots'].get(age)
        if not snap:
            return False
        actual = sf(snap.get('actual_age'))
        if actual is None:
            return False
        late = actual - age
        if late < -0.25 or late > MAX_LATENESS:
            return False
    return True


def exact_trade(record: dict[str, Any], decision_age: int, exit_age: int, direction: str) -> dict[str, Any] | None:
    decision = record['snapshots'].get(decision_age)
    exit_snap = record['snapshots'].get(exit_age)
    if not decision or not exit_snap:
        return None

    dbid = sf(decision.get('bid1'))
    dask = sf(decision.get('ask1'))
    ebid = sf(exit_snap.get('bid1'))
    eask = sf(exit_snap.get('ask1'))

    if direction == 'LONG':
        if dask is None or ebid is None or dask <= 0 or ebid <= 0:
            return None
        gross_pct = (ebid - dask) / dask * 100.0
    else:
        if dbid is None or eask is None or dbid <= 0 or eask <= 0:
            return None
        gross_pct = (dbid - eask) / dbid * 100.0

    return {
        'signal_id': int(record['signal_id']),
        'symbol': str(record['symbol']),
        'decision_ts': float(decision['ts']),
        'exit_ts': float(exit_snap['ts']),
        'direction': direction,
        'gross_pct': gross_pct,
        'stress': (gross_pct - STRESS_COST) * NOTIONAL / 100.0,
        'hard': (gross_pct - HARD_COST) * NOTIONAL / 100.0,
    }


def fold_count(trades: list[dict[str, Any]], key: str) -> tuple[int, list[dict[str, Any]]]:
    parts = audit.chronological_parts(trades, 6)
    metrics = [audit.metric(part, key) for part in parts]
    positive = sum(row['n'] > 0 and row['sum'] > 0 for row in metrics)
    return positive, metrics


def evaluate(records: list[dict[str, Any]], decision_age: int, exit_age: int) -> dict[str, Any]:
    longs = []
    shorts = []
    oracle_all = []
    oracle_selective = []
    rejected = 0
    opportunity_stress = 0
    opportunity_hard = 0

    for record in records:
        if not latency_ok(record, decision_age, exit_age):
            rejected += 1
            continue

        long_trade = exact_trade(record, decision_age, exit_age, 'LONG')
        short_trade = exact_trade(record, decision_age, exit_age, 'SHORT')
        if long_trade is None or short_trade is None:
            rejected += 1
            continue

        longs.append(long_trade)
        shorts.append(short_trade)

        best = long_trade if long_trade['gross_pct'] >= short_trade['gross_pct'] else short_trade
        oracle_all.append(best)

        if best['stress'] > 0:
            opportunity_stress += 1
            oracle_selective.append(best)
        if best['hard'] > 0:
            opportunity_hard += 1

    long_exec = audit.simulate_execution(longs)
    short_exec = audit.simulate_execution(shorts)
    oracle_exec = audit.simulate_execution(oracle_all)
    selective_exec = audit.simulate_execution(oracle_selective)

    oracle_stress = audit.metric(oracle_exec, 'stress')
    oracle_hard = audit.metric(oracle_exec, 'hard')
    positive_folds, _ = fold_count(oracle_exec, 'stress')
    usable = len(oracle_all)

    return {
        'decision_age': decision_age,
        'exit_age': exit_age,
        'usable': usable,
        'rejected': rejected,
        'long_stress': audit.metric(long_exec, 'stress'),
        'long_hard': audit.metric(long_exec, 'hard'),
        'short_stress': audit.metric(short_exec, 'stress'),
        'short_hard': audit.metric(short_exec, 'hard'),
        'oracle_stress': oracle_stress,
        'oracle_hard': oracle_hard,
        'selective_stress': audit.metric(selective_exec, 'stress'),
        'selective_hard': audit.metric(selective_exec, 'hard'),
        'opportunity_stress_share': opportunity_stress / usable if usable else 0.0,
        'opportunity_hard_share': opportunity_hard / usable if usable else 0.0,
        'oracle_positive_folds': positive_folds,
    }


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix='v19_oracle_', dir='/tmp'))
    db = tmp / 'v19.sqlite3'

    try:
        audit.snapshot_database(db)
        records, _ = audit.load_records(db)
        clustered = audit.cluster_events(records)

        results = []
        for decision_age in DECISION_AGES:
            for exit_age in EXIT_AGES:
                if exit_age > decision_age:
                    results.append(evaluate(clustered, decision_age, exit_age))

        lines = [
            '=' * 150,
            f'SKYNET V19 ORACLE FEASIBILITY AUDIT UTC={utc()}',
            '=' * 150,
            'Purpose: determine whether the anomaly path contains enough executable movement after costs.',
            'ORACLE_DIRECTION_ALL chooses the better future side for every event and is NOT tradable.',
            'ORACLE_SELECTIVE also skips every future loser and is an impossible upper bound.',
            f'stress_cost={STRESS_COST:.2f}% hard_cost={HARD_COST:.2f}% notional=${NOTIONAL:.2f}',
            'Execution uses recorded bid/ask, max_open=1, symbol cooldown=180s.',
            'REAL_TRADING=OFF.',
            '',
            f'quality_records={len(records)}',
            f'clustered_records={len(clustered)}',
            '',
        ]

        for row in results:
            lines.extend([
                '-' * 150,
                f"DECISION={row['decision_age']}s EXIT={row['exit_age']}s usable={row['usable']} latency_or_missing={row['rejected']}",
                'FIXED_LONG_STRESS  ' + audit.fmt_metric(row['long_stress']),
                'FIXED_LONG_HARD    ' + audit.fmt_metric(row['long_hard']),
                'FIXED_SHORT_STRESS ' + audit.fmt_metric(row['short_stress']),
                'FIXED_SHORT_HARD   ' + audit.fmt_metric(row['short_hard']),
                'ORACLE_ALL_STRESS  ' + audit.fmt_metric(row['oracle_stress']),
                'ORACLE_ALL_HARD    ' + audit.fmt_metric(row['oracle_hard']),
                f"ORACLE_POSITIVE_FOLDS={row['oracle_positive_folds']}/6",
                f"FUTURE_OPPORTUNITY_SHARE stress={row['opportunity_stress_share']:.1%} hard={row['opportunity_hard_share']:.1%}",
                'ORACLE_SELECTIVE_STRESS ' + audit.fmt_metric(row['selective_stress']),
                'ORACLE_SELECTIVE_HARD   ' + audit.fmt_metric(row['selective_hard']),
            ])

        robust_oracle = [
            row for row in results
            if row['oracle_stress']['sum'] > 0
            and row['oracle_hard']['sum'] > 0
            and row['oracle_stress']['leave_best'] > 0
            and row['oracle_hard']['leave_best'] > 0
            and row['oracle_positive_folds'] >= 5
        ]

        fixed_positive = [
            row for row in results
            if (
                row['long_hard']['sum'] > 0 and row['long_hard']['leave_best'] > 0
            ) or (
                row['short_hard']['sum'] > 0 and row['short_hard']['leave_best'] > 0
            )
        ]

        lines.extend([
            '',
            '=' * 150,
            'FINAL DIAGNOSIS',
            '=' * 150,
            f'ROBUST_ORACLE_CELLS={len(robust_oracle)}',
            f'FIXED_DIRECTION_HARD_POSITIVE_CELLS={len(fixed_positive)}',
        ])

        if not robust_oracle:
            lines.extend([
                'DIAGNOSIS=INSUFFICIENT_EXECUTABLE_MOVEMENT_AFTER_COSTS',
                'Even future-perfect direction is not robust enough across the tested horizons.',
                'Stop directional model research on this signal family.',
            ])
        elif not fixed_positive:
            lines.extend([
                'DIAGNOSIS=MOVEMENT_EXISTS_BUT_DIRECTION_IS_NOT_PREDICTABLE_BY_CURRENT_MODELS',
                'The next admissible target is opportunity/direction classification with a frozen future split.',
                'Do not tune another same-sample directional regression.',
            ])
        else:
            lines.extend([
                'DIAGNOSIS=FIXED_DIRECTION_CELL_REQUIRES_STRICT_UNTOUCHED_CONFIRMATION',
                'No automatic candidate is created by this diagnostic.',
            ])

        lines.extend(['REAL_DECISION=BLOCKED', 'REAL_TRADING=OFF'])
        REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(REPORT.read_text(encoding='utf-8'))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
