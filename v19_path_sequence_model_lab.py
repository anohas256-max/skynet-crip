#!/usr/bin/env python3
from __future__ import annotations

import json, math, shutil, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import v19_dynamic_structure_audit as audit

ROOT = Path('/root/skynet')
DB = ROOT / 'data/v19_dynamic_snapshots.sqlite3'
REPORT = ROOT / 'v19_path_sequence_model_latest.txt'
CANDIDATE = ROOT / 'v19_path_sequence_frozen_candidate.json'
AGES = (5, 15, 30, 60, 300)
FEATURE_AGES = (5, 15, 30, 60)
ALPHAS = (3.0, 10.0, 30.0)
PRIMARY = 10.0
THRESHOLD = 0.45
MAX_LATE = 5.0
NOTIONAL = 12.0
STRESS_COST = 0.26
HARD_COST = 0.36
FOLDS = 5


def utc(ts: float | None = None) -> str:
    ts = time.time() if ts is None else ts
    return datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def sf(v: Any, default: float | None = None) -> float | None:
    try:
        x = float(v)
        return x if math.isfinite(x) else default
    except Exception:
        return default


def pct(a: float | None, b: float | None) -> float:
    return 0.0 if a is None or b is None or a <= 0 else (b - a) / a * 100.0


def mid(s: dict[str, Any]) -> float | None:
    return audit.midpoint(sf(s.get('bid1')), sf(s.get('ask1')))


def build_sample(r: dict[str, Any]) -> dict[str, Any] | None:
    for age in AGES:
        s = r['snapshots'].get(age)
        actual = None if not s else sf(s.get('actual_age'))
        if not s or actual is None or actual - age < -0.25 or actual - age > MAX_LATE:
            return None

    entry_mid = audit.midpoint(sf(r.get('entry_bid1')), sf(r.get('entry_ask1')))
    if entry_mid is None or entry_mid <= 0:
        return None

    snaps = r['snapshots']
    rets, spr, imb, wall, depth = {}, {}, {}, {}, {}
    for age in FEATURE_AGES:
        s = snaps[age]
        m = mid(s)
        if m is None:
            return None
        rets[age] = pct(entry_mid, m)
        spr[age] = sf(s.get('spread_bps'), 0.0) or 0.0
        imb[age] = sf(s.get('imb20'), 0.0) or 0.0
        wall[age] = sf(s.get('wall_skew'), 0.0) or 0.0
        d = (sf(s.get('bid20_usd'), 0.0) or 0.0) + (sf(s.get('ask20_usd'), 0.0) or 0.0)
        depth[age] = math.log1p(max(d, 0.0))

    s5, s60, s300 = snaps[5], snaps[60], snaps[300]
    x = np.asarray([
        rets[5], rets[15], rets[30], rets[60],
        rets[15]-rets[5], rets[30]-rets[15], rets[60]-rets[30],
        *[spr[a] for a in FEATURE_AGES], spr[60]-spr[5],
        *[imb[a] for a in FEATURE_AGES], imb[60]-imb[5],
        *[wall[a] for a in FEATURE_AGES], wall[60]-wall[5],
        *[depth[a] for a in FEATURE_AGES], depth[60]-depth[5],
        pct(sf(s5.get('hold_vol')), sf(s60.get('hold_vol'))),
        pct(sf(s5.get('btc_price')), sf(s60.get('btc_price'))),
        float(r['price_change']), math.log1p(max(float(r['vol_ratio']), 0.0)), float(r['rank'])
    ], dtype=float)
    if not np.all(np.isfinite(x)):
        return None

    m60, m300 = mid(s60), mid(s300)
    if m60 is None or m300 is None:
        return None

    return {
        'signal_id': int(r['signal_id']), 'symbol': str(r['symbol']),
        'decision_ts': float(s60['ts']), 'exit_ts': float(s300['ts']),
        'decision_bid': sf(s60.get('bid1')), 'decision_ask': sf(s60.get('ask1')),
        'exit_bid': sf(s300.get('bid1')), 'exit_ask': sf(s300.get('ask1')),
        'x': x, 'target': pct(m60, m300)
    }


def fit(rows: list[dict[str, Any]], alpha: float) -> dict[str, np.ndarray]:
    x = np.vstack([r['x'] for r in rows]); y = np.asarray([r['target'] for r in rows])
    lo = np.quantile(x, .01, axis=0); hi = np.quantile(x, .99, axis=0)
    xc = np.clip(x, lo, hi); mean = xc.mean(0); scale = xc.std(0)
    scale = np.where(scale < 1e-9, 1.0, scale)
    z = (xc - mean) / scale; design = np.column_stack([np.ones(len(z)), z])
    penalty = np.eye(design.shape[1]); penalty[0, 0] = 0.0
    beta = np.linalg.pinv(design.T @ design + alpha * penalty) @ (design.T @ y)
    return {'lo': lo, 'hi': hi, 'mean': mean, 'scale': scale, 'beta': beta}


def predict(model: dict[str, np.ndarray], rows: list[dict[str, Any]]) -> np.ndarray:
    x = np.vstack([r['x'] for r in rows])
    z = (np.clip(x, model['lo'], model['hi']) - model['mean']) / model['scale']
    return np.column_stack([np.ones(len(z)), z]) @ model['beta']


def make_trade(r: dict[str, Any], p: float, fold: int) -> dict[str, Any] | None:
    if p > 0:
        direction, entry, exit_price = 'LONG', r['decision_ask'], r['exit_bid']
        if entry is None or exit_price is None or entry <= 0: return None
        gross = (exit_price - entry) / entry * 100.0
    else:
        direction, entry, exit_price = 'SHORT', r['decision_bid'], r['exit_ask']
        if entry is None or exit_price is None or entry <= 0: return None
        gross = (entry - exit_price) / entry * 100.0
    return {
        'signal_id': r['signal_id'], 'symbol': r['symbol'], 'decision_ts': r['decision_ts'],
        'exit_ts': r['exit_ts'], 'direction': direction, 'prediction': p, 'fold': fold,
        'gross_pct': gross,
        'stress': (gross - STRESS_COST) * NOTIONAL / 100.0,
        'hard': (gross - HARD_COST) * NOTIONAL / 100.0,
    }


def bounds(n: int) -> list[tuple[int, int, int]]:
    first = max(200, int(n * .40))
    if first >= n: return []
    step = max(1, (n - first) // FOLDS)
    out, start = [], first
    for fold in range(1, FOLDS + 1):
        end = n if fold == FOLDS else min(n, start + step)
        if start < end: out.append((fold, start, end))
        start = end
    return out


def run(samples: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    raw = []
    for fold, start, end in bounds(len(samples)):
        model = fit(samples[:start], alpha)
        for row, pred in zip(samples[start:end], predict(model, samples[start:end])):
            pred = float(pred)
            if abs(pred) < THRESHOLD: continue
            trade = make_trade(row, pred, fold)
            if trade: raw.append(trade)
    selected = audit.simulate_execution(raw)
    stress = audit.metric(selected, 'stress'); hard = audit.metric(selected, 'hard')
    fold_metrics = [audit.metric([t for t in selected if t['fold'] == i], 'stress') for i in range(1, FOLDS + 1)]
    pos_folds = sum(m['n'] > 0 and m['sum'] > 0 for m in fold_metrics)
    halves = [audit.metric(p, 'stress') for p in audit.chronological_parts(selected, 2)]
    pos_halves = sum(m['n'] > 0 and m['sum'] > 0 for m in halves)
    passed = (
        stress['n'] >= 20 and stress['symbols'] >= 8 and stress['sum'] > 0 and stress['pf'] >= 1.20
        and stress['leave_best'] > 0 and stress['positive_share'] <= .45
        and hard['sum'] > 0 and hard['pf'] >= 1.05 and hard['leave_best'] > 0
        and pos_folds >= 4 and pos_halves == 2
    )
    return {'selected': selected, 'stress': stress, 'hard': hard, 'folds': fold_metrics,
            'positive_folds': pos_folds, 'positive_halves': pos_halves, 'passed': passed}


def main() -> None:
    temp = Path(tempfile.mkdtemp(prefix='v19_sequence_', dir='/tmp'))
    snap = temp / 'v19.sqlite3'
    try:
        audit.snapshot_database(snap)
        records, _ = audit.load_records(snap)
        clustered = audit.cluster_events(records)
        samples, rejected = [], 0
        for record in clustered:
            sample = build_sample(record)
            if sample is None: rejected += 1
            else: samples.append(sample)
        samples.sort(key=lambda r: (r['decision_ts'], r['signal_id']))
        if len(samples) < 250:
            raise RuntimeError(f'Insufficient samples: {len(samples)}')

        results = {a: run(samples, a) for a in ALPHAS}
        primary = results[PRIMARY]
        pass_count = sum(r['passed'] for r in results.values())

        lines = [
            '=' * 130,
            f'SKYNET V19 PATH-SEQUENCE WALK-FORWARD UTC={utc()}',
            '=' * 130,
            'Fixed ridge family; features 5/15/30/60s; decision 60s; exact exit 300s.',
            f'threshold={THRESHOLD:.2f}% stress_cost={STRESS_COST:.2f}% hard_cost={HARD_COST:.2f}%',
            'Execution: recorded bid/ask, max_open=1, cooldown=180s.',
            'REAL_TRADING=OFF.', '',
            f'quality_records={len(records)}', f'clustered_records={len(clustered)}',
            f'latency_or_feature_rejected={rejected}', f'usable_sequence_samples={len(samples)}',
            f'sample_start={utc(samples[0]["decision_ts"])}', f'sample_end={utc(samples[-1]["decision_ts"])}', ''
        ]
        for alpha in ALPHAS:
            r = results[alpha]
            lines += [
                f'RIDGE_ALPHA={alpha:g} PRIMARY={int(alpha == PRIMARY)} PASS={int(r["passed"])}',
                f'executed={len(r["selected"])}',
                'STRESS ' + audit.fmt_metric(r['stress']),
                'HARD   ' + audit.fmt_metric(r['hard']),
                f'POSITIVE_FOLDS={r["positive_folds"]}/{FOLDS}',
                f'POSITIVE_HALVES={r["positive_halves"]}/2',
            ]
            for i, f in enumerate(r['folds'], 1):
                lines.append(f'  F{i} n={f["n"]} sum=${f["sum"]:+.5f} PF={f["pf"]:.2f}')
            lines.append('')

        if primary['passed'] and pass_count >= 2:
            model = fit(samples, PRIMARY); cutoff = time.time()
            payload = {
                'version': 1, 'created_utc': utc(), 'cutoff_ts': cutoff, 'cutoff_utc': utc(cutoff),
                'model_family': 'V19_FIXED_PATH_SEQUENCE_RIDGE', 'alpha': PRIMARY,
                'prediction_threshold_pct': THRESHOLD, 'decision_age': 60, 'exit_age': 300,
                'maximum_snapshot_lateness_seconds': MAX_LATE, 'stress_cost_pct': STRESS_COST,
                'hard_cost_pct': HARD_COST, 'notional_usd': NOTIONAL,
                'forward_limit': {'maximum_hours': 24, 'maximum_executed_trades': 20},
                'lower': model['lo'].tolist(), 'upper': model['hi'].tolist(),
                'mean': model['mean'].tolist(), 'scale': model['scale'].tolist(),
                'beta': model['beta'].tolist(),
                'promotion_policy': 'Manual exact-shadow review only; real remains blocked.'
            }
            CANDIDATE.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
            decision = 'FORWARD_CANDIDATE_CREATED'
        else:
            CANDIDATE.unlink(missing_ok=True)
            decision = 'NO_WALK_FORWARD_EDGE'

        lines += ['=' * 130, f'SEQUENCE_MODEL_DECISION={decision}',
                  f'SENSITIVITY_PASSES={pass_count}/{len(ALPHAS)}',
                  'REAL_DECISION=BLOCKED', 'REAL_TRADING=OFF']
        REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(REPORT.read_text(encoding='utf-8'))
    finally:
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == '__main__':
    main()
