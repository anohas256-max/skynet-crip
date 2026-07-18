#!/usr/bin/env python3
"""Bounded, chronological Binance lead/context audit; research only, never live trading."""
from __future__ import annotations

import bisect
import csv
import math
import pickle
import sqlite3
import statistics
import sys
import traceback
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/root/skynet")
DB = ROOT / "data/v19_dynamic_snapshots.sqlite3"
DATA = ROOT / "data/binance_lead_audit"
CACHE = Path("/tmp/v20_binance_lead_audit_cache")
REPORT = ROOT / "v20_binance_lead_audit_latest.txt"
CONSOLE = ROOT / "v20_binance_lead_audit_console.txt"
CORRECTION_REPORT = ROOT / "v20_binance_lead_audit_correction_latest.txt"
CORRECTION = False
DATE = "2026-07-16"
SYMBOLS = ("ESPORTSUSDT", "SKYAIUSDT", "BANKUSDT", "TACUSDT", "KAITOUSDT", "BASEDUSDT", "EIGENUSDT", "SOXLUSDT", "NEARUSDT", "MANTRAUSDT", "ONDOUSDT", "LDOUSDT", "ALLOUSDT", "ENAUSDT", "REUSDT", "SYNUSDT", "SLXUSDT", "UNIUSDT")
WINDOWS = (5, 10, 15, 30, 60)
RULE_WINDOWS = WINDOWS  # Correction: complete the originally specified fixed window set.
PERCENTILES = (0.50, 0.75)  # Fixed before data evaluation.
ENTRY_AGES = (5, 15, 30, 60)
EXIT_AGE = 300
NOTIONAL = 12.0
STRESS_COST = 0.26
HARD_COST = 0.36
COOLDOWN = 180.0


def pct(values, q):
    values = sorted(values)
    if not values:
        return 0.0
    pos = (len(values) - 1) * q
    lo, hi = int(pos), math.ceil(pos)
    return values[lo] if lo == hi else values[lo] * (hi - pos) + values[hi] * (pos - lo)


def pf(values):
    gain = sum(v for v in values if v > 0)
    loss = -sum(v for v in values if v < 0)
    return 999.0 if loss == 0 and gain > 0 else (gain / loss if loss else 0.0)


def metric(trades, key):
    values = [t[key] for t in trades]
    if not values:
        return dict(n=0, pnl=0.0, pf=0.0, wr=0.0, symbols=0, leave_best=0.0, best="-", concentration=0.0)
    by_symbol = defaultdict(float)
    for t in trades:
        by_symbol[t["symbol"]] += t[key]
    best, best_pnl = max(by_symbol.items(), key=lambda x: x[1])
    positive = sum(max(v, 0.0) for v in by_symbol.values())
    return dict(n=len(values), pnl=sum(values), pf=pf(values), wr=100 * sum(v > 0 for v in values) / len(values), symbols=len(by_symbol), leave_best=sum(values)-best_pnl, best=best, concentration=(max(best_pnl, 0.0) / positive if positive else 0.0))


def parts(trades, n):
    ordered = sorted(trades, key=lambda t: (t["entry_ts"], t["signal_id"]))
    return [ordered[round(len(ordered)*i/n):round(len(ordered)*(i+1)/n)] for i in range(n)]


def fmt(m):
    return f"n={m['n']} PnL=${m['pnl']:+.5f} PF={m['pf']:.2f} WR={m['wr']:.1f}% symbols={m['symbols']} leave_best=${m['leave_best']:+.5f} best={m['best']} concentration={m['concentration']:.1%}"


def load_events():
    start = datetime.fromisoformat(DATE + "T00:00:00+00:00").timestamp()
    end = start + 86400
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    good = con.execute("""SELECT s.* FROM signals s JOIN (SELECT signal_id FROM snapshots WHERE status='OK' AND target_age IN (5,15,30,60,300) GROUP BY signal_id HAVING COUNT(DISTINCT target_age)=5) x ON x.signal_id=s.signal_id WHERE s.entry_ts>=? AND s.entry_ts<? ORDER BY s.entry_ts, s.signal_id""", (start, end)).fetchall()
    ids = [r["signal_id"] for r in good]
    snapshots = defaultdict(dict)
    if ids:
        marks = ",".join("?" for _ in ids)
        for r in con.execute(f"SELECT signal_id,target_age,ts,bid1,ask1,actual_age FROM snapshots WHERE status='OK' AND target_age IN (5,15,30,60,300) AND signal_id IN ({marks})", ids):
            snapshots[r["signal_id"]][r["target_age"]] = dict(r)
    con.close()
    events = []
    rejects = defaultdict(int)
    for r in good:
        base = str(r["clean_symbol"] or r["symbol"] or "").replace("_USDT", "").replace("-USDT", "").upper()
        symbol = base if base.endswith("USDT") else base + "USDT"
        if symbol not in SYMBOLS:
            rejects["binance_symbol_unavailable"] += 1
            continue
        path = snapshots[r["signal_id"]]
        if any(a not in path for a in (*ENTRY_AGES, EXIT_AGE)):
            rejects["missing_exact_mexc_snapshot"] += 1
            continue
        if any(not path[a]["bid1"] or not path[a]["ask1"] or path[a]["bid1"] <= 0 or path[a]["ask1"] <= 0 for a in (*ENTRY_AGES, EXIT_AGE)):
            rejects["invalid_exact_mexc_bid_ask"] += 1
            continue
        events.append(dict(signal_id=r["signal_id"], entry_ts=float(r["entry_ts"]), symbol=symbol, snaps=path))
    return events, len(good), rejects


def load_binance(symbols=SYMBOLS):
    result, checks = {}, []
    CACHE.mkdir(parents=True, exist_ok=True)
    day_start_ms = int(datetime.fromisoformat(DATE + "T00:00:00+00:00").timestamp() * 1000)
    day_end_ms = day_start_ms + 86400000
    for symbol in symbols:
        archive = DATA / f"{symbol}-aggTrades-{DATE}.zip"
        if not archive.exists() or archive.stat().st_size == 0:
            raise RuntimeError(f"missing archive {archive}")
        cache = CACHE / f"{symbol}-{DATE}.pickle"
        if cache.exists() and cache.stat().st_mtime >= archive.stat().st_mtime:
            with cache.open("rb") as f:
                ts, price, total_prefix, buy_prefix = pickle.load(f)
        else:
            with zipfile.ZipFile(archive) as z:
                names = [n for n in z.namelist() if n.endswith(".csv")]
                if len(names) != 1:
                    raise RuntimeError(f"invalid zip contents {archive.name}: {names}")
                ts, price, qty, buy = [], [], [], []
                with z.open(names[0]) as raw:
                    reader = csv.reader((line.decode("utf-8") for line in raw))
                    header = next(reader, None)
                    if not header or "transact_time" not in header:
                        raise RuntimeError(f"missing Binance aggTrades header in {archive.name}")
                    idx = {x: i for i, x in enumerate(header)}
                    for row in reader:
                        t = int(row[idx["transact_time"]])
                        ts.append(t); price.append(float(row[idx["price"]])); qty.append(float(row[idx["quantity"]])); buy.append(row[idx["is_buyer_maker"]].lower() == "false")
            total_prefix, buy_prefix = [0.0], [0.0]
            for q, is_buy in zip(qty, buy):
                total_prefix.append(total_prefix[-1] + q)
                buy_prefix.append(buy_prefix[-1] + (q if is_buy else 0.0))
            with cache.open("wb") as f:
                pickle.dump((ts, price, total_prefix, buy_prefix), f, protocol=pickle.HIGHEST_PROTOCOL)
        if not ts or ts != sorted(ts) or min(ts) < day_start_ms or max(ts) >= day_end_ms or max(ts) < 10**12:
            raise RuntimeError(f"timestamp/unit/alignment failure {symbol}: n={len(ts)} min={min(ts) if ts else '-'} max={max(ts) if ts else '-'}")
        result[symbol] = (ts, price, total_prefix, buy_prefix)
        checks.append((symbol, archive.stat().st_size, len(ts), min(ts), max(ts)))
    return result, checks


def context(data, event):
    ts, price, total_prefix, buy_prefix = data[event["symbol"]]
    anchor = int(event["entry_ts"] * 1000)
    end = bisect.bisect_right(ts, anchor)
    if end == 0:
        return None
    out = {}
    for w in WINDOWS:
        begin = bisect.bisect_left(ts, anchor - w*1000)
        if begin == end or begin == 0:
            return None
        # Uses observed trades only: last trade at/before each boundary; no MEXC interpolation.
        ret = (price[end-1] / price[begin-1] - 1.0) * 100.0
        buys = buy_prefix[end] - buy_prefix[begin]
        total_volume = total_prefix[end] - total_prefix[begin]
        sells = total_volume - buys
        total = buys + sells
        imb = (buys - sells) / total if total else 0.0
        prior_begin = bisect.bisect_left(ts, anchor - 2*w*1000)
        current_count, prior_count = end-begin, begin-prior_begin
        current_volume = total_prefix[end] - total_prefix[begin]
        prior_volume = total_prefix[begin] - total_prefix[prior_begin]
        out[w] = dict(ret=ret, buy=buys, sell=sells, imb=imb, trade_accel=(current_count / prior_count - 1.0 if prior_count else 0.0), volume_accel=(current_volume / prior_volume - 1.0 if prior_volume else 0.0), agree=(ret > 0 and imb > 0) or (ret < 0 and imb < 0))
    return out


def prepare(events, data):
    usable, rejects = [], defaultdict(int)
    for e in events:
        c = context(data, e)
        if c is None:
            rejects["insufficient_binance_pre_signal_history"] += 1
        else:
            e["ctx"] = c; usable.append(e)
    return usable, rejects


def cluster_by_symbol(events, seconds=60.0):
    """The prior V19/probe-style per-symbol dedupe; all input rows update last_seen."""
    selected, last_seen = [], {}
    for event in sorted(events, key=lambda x: (x["entry_ts"], x["signal_id"])):
        previous = last_seen.get(event["symbol"])
        last_seen[event["symbol"]] = event["entry_ts"]
        if previous is None or event["entry_ts"] - previous > seconds:
            selected.append(event)
    return selected


def db_date_signal_count():
    start = datetime.fromisoformat(DATE + "T00:00:00+00:00").timestamp()
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        return int(con.execute("SELECT COUNT(*) FROM signals WHERE entry_ts>=? AND entry_ts<?", (start, start + 86400)).fetchone()[0])
    finally:
        con.close()


def thresholds(train, window, mode, q):
    if mode == "return": return (pct([abs(e["ctx"][window]["ret"]) for e in train], q),)
    if mode == "imbalance": return (pct([abs(e["ctx"][window]["imb"]) for e in train], q),)
    return (pct([abs(e["ctx"][window]["ret"]) for e in train], q), pct([abs(e["ctx"][window]["imb"]) for e in train], q))


def raw_trades(events, window, mode, threshold, entry_age):
    rows = []
    for e in events:
        x = e["ctx"][window]
        direction = 0
        if mode == "return" and abs(x["ret"]) >= threshold[0]: direction = 1 if x["ret"] > 0 else -1 if x["ret"] < 0 else 0
        elif mode == "imbalance" and abs(x["imb"]) >= threshold[0]: direction = 1 if x["imb"] > 0 else -1 if x["imb"] < 0 else 0
        elif mode == "agree" and x["agree"] and abs(x["ret"]) >= threshold[0] and abs(x["imb"]) >= threshold[1]: direction = 1 if x["ret"] > 0 else -1
        if not direction: continue
        entry, exit_ = e["snaps"][entry_age], e["snaps"][EXIT_AGE]
        entry_px = float(entry["ask1"] if direction > 0 else entry["bid1"])
        exit_px = float(exit_["bid1"] if direction > 0 else exit_["ask1"])
        gross = ((exit_px-entry_px)/entry_px*100.0) * direction
        rows.append({**e, "direction": direction, "entry_ts": float(entry["ts"]), "exit_ts": float(exit_["ts"]), "gross": gross, "stress": (gross-STRESS_COST)*NOTIONAL/100.0, "hard": (gross-HARD_COST)*NOTIONAL/100.0})
    return rows


def execute(rows):
    selected, busy, last = [], -float("inf"), {}
    for t in sorted(rows, key=lambda z: (z["entry_ts"], z["signal_id"])):
        if t["entry_ts"] < busy or t["entry_ts"] - last.get(t["symbol"], -float("inf")) < COOLDOWN: continue
        selected.append(t); busy = t["exit_ts"]; last[t["symbol"]] = t["entry_ts"]
    return selected


def evaluation(rows):
    chosen = execute(rows); half = [metric(x, "hard") for x in parts(chosen, 2)]; quarters = [metric(x, "hard") for x in parts(chosen, 4)]
    return dict(trades=chosen, stress=metric(chosen, "stress"), hard=metric(chosen, "hard"), halves=half, quarters=quarters)


def validation_pass(e):
    return e["hard"]["n"] >= 30 and e["hard"]["symbols"] >= 8 and e["hard"]["pnl"] > 0 and e["hard"]["leave_best"] > 0 and e["stress"]["pnl"] > 0 and all(x["n"] and x["pnl"] > 0 for x in e["halves"])


def final_pass(e):
    return e["hard"]["n"] >= 50 and e["hard"]["pnl"] > 0 and e["hard"]["pf"] >= 1.20 and e["hard"]["leave_best"] > 0 and e["stress"]["pnl"] > 0 and sum(x["n"] and x["pnl"] > 0 for x in e["quarters"]) >= 3 and e["hard"]["concentration"] <= 0.50


def main():
    title = "SKYNET V20 BINANCE LEAD/CONTEXT CORRECTION AUDIT" if CORRECTION else "SKYNET V20 BINANCE LEAD/CONTEXT AUDIT"
    lines = [title, "REAL_TRADING_ENABLED=false REAL_TRADING_ARMED=false LIVE_DRY_RUN=true", f"date={DATE} db={DB}", "Execution: exact recorded MEXC bid/ask entries 5/15/30/60s; exact recorded exit 300s; notional=$12; stress=0.26%; hard=0.36%; max_open=1; cooldown=180s.", "Predeclared rule family: windows=5,10,15,30,60 seconds; modes=return sign, taker-imbalance sign, return/imbalance agreement; train-only thresholds=50th,75th percentile."]
    try:
        events, db_events, e_reject = load_events(); data, checks = load_binance(); usable, c_reject = prepare(events, data)
    except Exception as exc:
        lines += [f"DATA_ERROR={type(exc).__name__}: {exc}", "BINANCE_LEAD_DECISION=STOP_DATA_INVALID"]
        REPORT.write_text("\n".join(lines)+"\n"); CONSOLE.write_text(REPORT.read_text()); print("\n".join(lines)); return
    lines += ["", "FILE_AND_TIMESTAMP_CHECKS"]
    lines += [f"{s} bytes={b} rows={n} timestamp_ms_min={lo} timestamp_ms_max={hi}" for s,b,n,lo,hi in checks]
    clustered = cluster_by_symbol(events)
    lines += [f"timestamp_unit=milliseconds; Binance rows are sorted and within UTC {DATE}; MEXC signal/snapshot timestamps are Unix seconds; Binance context ends at/before signal timestamp; MEXC bid/ask are never interpolated.", f"MEXC_DB_DATE_EVENTS_CURRENT={db_date_signal_count()}", f"MEXC_DB_DATE_EVENTS_WITH_REQUIRED_SNAPSHOT_STATUSES={db_events}", f"MATCHED_EVENTS={len(usable)}", f"UNIQUE_MATCHED_SIGNAL_ID={len({e['signal_id'] for e in usable})}", f"DUPLICATE_MATCHED_SIGNAL_ID={len(usable)-len({e['signal_id'] for e in usable})}", f"PROBE_RECONCILIATION: probe_MEXC_EVENTS=5014; current_DB_date_events={db_date_signal_count()}; current_available_exact_snapshot_events={len(events)}; current_60s_symbol_clustered_available_events={len(clustered)}; current_post_history_unclustered_matched={len(usable)}", "COUNT_CAUSE: preliminary COVERED_EVENTS used a 60s per-symbol deduped coverage count; V20 MATCHED_EVENTS is unclustered after the Binance pre-signal-history filter. On the current DB, removing the 60s dedupe changes 1370 to 2253 (+883), then the 58 pre-signal-history rejections produce 2195. The remaining 1370 versus probe 1368 (+2) is explained by the DB changing from probe_MEXC_EVENTS=5014 to current_DB_date_events; no probe source/snapshot was retained to identify those two historical rows.", "MISSING_OR_REJECTED=" + ", ".join(f"{k}={v}" for k,v in sorted((e_reject|c_reject).items()))]
    if len(usable) < 120:
        lines += ["BINANCE_LEAD_DECISION=STOP_INSUFFICIENT_OVERLAP"]
        REPORT.write_text("\n".join(lines)+"\n"); CONSOLE.write_text(REPORT.read_text()); print("\n".join(lines)); return
    n = len(usable); train, validation, final = usable[:n//2], usable[n//2:n*3//4], usable[n*3//4:]
    lines += [f"SPLIT train={len(train)} validation={len(validation)} untouched_final={len(final)}"]
    candidates = []
    for w in RULE_WINDOWS:
        for mode in ("return", "imbalance", "agree"):
            for q in PERCENTILES:
                th = thresholds(train, w, mode, q); name = f"w={w}s mode={mode} train_pct={int(q*100)} thresholds=" + "/".join(f"{x:.6g}" for x in th)
                ev = evaluation(raw_trades(validation, w, mode, th, 15))
                candidates.append((name,w,mode,q,th,ev))
    lines += ["", "VALIDATION_CANDIDATES (entry_delay=15s)"]
    for name,*_,ev in candidates:
        lines += [f"{name} PASS={int(validation_pass(ev))}", "  STRESS "+fmt(ev["stress"]), "  HARD   "+fmt(ev["hard"]), "  hard_halves="+"; ".join(fmt(x) for x in ev["halves"])]
    duplicate_configs = sum(len(ev["trades"]) != len({t["signal_id"] for t in ev["trades"]}) for *_, ev in candidates)
    lines += [f"DUPLICATE_SIGNAL_ID_IN_VALIDATION_CONFIGURATIONS={duplicate_configs} (checked across {len(candidates)} configurations)"]
    passed = [x for x in candidates if validation_pass(x[-1])]
    if not passed:
        lines += ["", "FINAL_UNTOUCHED_TEST=NOT_OPENED", "FINAL_ENTRY_DELAY_RESULTS_5S_15S_30S_60S=NOT_EVALUATED (validation gate failed; untouched final remains closed)", "BINANCE_LEAD_DECISION=STOP_NO_VALIDATION_EDGE"]
        REPORT.write_text("\n".join(lines)+"\n"); CONSOLE.write_text(REPORT.read_text()); print("\n".join(lines)); return
    selected = max(passed, key=lambda x: (x[-1]["hard"]["pnl"], x[-1]["hard"]["leave_best"], x[-1]["stress"]["pnl"]))
    name,w,mode,q,th,_ = selected
    lines += ["", "SELECTED_ON_VALIDATION="+name, "FINAL_UNTOUCHED_TEST=OPENED_ONCE"]
    final_by_delay = {}
    for age in ENTRY_AGES:
        ev = evaluation(raw_trades(final,w,mode,th,age)); final_by_delay[age] = ev
        lines += [f"FINAL entry_delay={age}s", "  STRESS "+fmt(ev["stress"]), "  HARD   "+fmt(ev["hard"]), "  hard_quarters="+"; ".join(fmt(x) for x in ev["quarters"])]
    primary = final_by_delay[15]
    decision = "FINAL_TEST_PASS" if final_pass(primary) else "FINAL_TEST_FAIL"
    lines += [f"FINAL_15S_GATE_PASS={int(final_pass(primary))}", f"BINANCE_LEAD_DECISION={decision}"]
    REPORT.write_text("\n".join(lines)+"\n"); CONSOLE.write_text(REPORT.read_text()); print("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--warm-cache" and sys.argv[2] in SYMBOLS:
        load_binance((sys.argv[2],))
        raise SystemExit(0)
    if "--correction" in sys.argv:
        CORRECTION = True
        REPORT = CORRECTION_REPORT
    with CONSOLE.open("w") as console:
        previous_stdout = sys.stdout
        sys.stdout = console
        try:
            main()
        except Exception:
            traceback.print_exc(file=console)
            console.flush()
            raise
        finally:
            sys.stdout = previous_stdout
