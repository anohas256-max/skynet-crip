import os
import csv
import json
import zipfile
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv("/root/skynet/.env")

ROOT = Path("/root/skynet")
OUT_DIR = ROOT / "data" / "backtest" / "winner_exit_grid"

ENTRY_NAME = "TREND030_PC065_VOL35_SCORE4_INIT_COMBO_BALANCED_WAIT1"
EXIT_SUITE_NAME = "WINNER_EXIT_GRID"

# Entry winner from latest grids:
# TREND030_PC065_VOL35_SCORE4_INIT + COMBO_BALANCED + WAIT1_CLOSE
ENTRY = {
    "min_score": 4,
    "need_initiative": 1,
    "max_pc": 0.65,
    "max_vol": 35.0,
    "min_trend15": 0.30,
    "min_btc5": -999.0,
}

# Focused exit grid. Not too huge, so VPS should survive.
# partial_mult/min/max decides first partial target from pre_range5.
# runner_stop is after partial. be/micro are live-compatible using observed MFE only.
EXIT_GRID = []
for partial_min in [0.45, 0.55, 0.65, 0.70]:
    for runner_stop in [0.00, 0.10, 0.20]:
        for time_stop in [20, 35, 45]:
            EXIT_GRID.append({
                "exit_name": f"P{partial_min:.2f}_RST{runner_stop:.2f}_T{time_stop}",
                "sl_mult": 0.85,
                "sl_min": 0.40,
                "sl_max": 0.85,
                "partial_mult": 1.00,
                "partial_min": partial_min,
                "partial_max": 0.90,
                "partial_size": 0.50,
                "runner_tp_mult": 4.50,
                "runner_tp_min": 2.00,
                "runner_tp_max": 3.20,
                "runner_stop": runner_stop,
                "time_stop": time_stop,
                "be_trigger": None,
                "be_stop": None,
                "micro_trigger": None,
                "micro_stop": None,
            })

# BE/micro-lock variants around the best-looking partial zones.
for partial_min in [0.45, 0.55, 0.65]:
    EXIT_GRID.append({
        "exit_name": f"P{partial_min:.2f}_BE055_010_T35",
        "sl_mult": 0.85,
        "sl_min": 0.40,
        "sl_max": 0.85,
        "partial_mult": 1.00,
        "partial_min": partial_min,
        "partial_max": 0.90,
        "partial_size": 0.50,
        "runner_tp_mult": 4.50,
        "runner_tp_min": 2.00,
        "runner_tp_max": 3.20,
        "runner_stop": 0.10,
        "time_stop": 35,
        "be_trigger": 0.55,
        "be_stop": 0.10,
        "micro_trigger": None,
        "micro_stop": None,
    })
    EXIT_GRID.append({
        "exit_name": f"P{partial_min:.2f}_ML045_000_T35",
        "sl_mult": 0.85,
        "sl_min": 0.40,
        "sl_max": 0.85,
        "partial_mult": 1.00,
        "partial_min": partial_min,
        "partial_max": 0.90,
        "partial_size": 0.50,
        "runner_tp_mult": 4.50,
        "runner_tp_min": 2.00,
        "runner_tp_max": 3.20,
        "runner_stop": 0.10,
        "time_stop": 35,
        "be_trigger": None,
        "be_stop": None,
        "micro_trigger": 0.45,
        "micro_stop": 0.00,
    })

# Original-ish ATR5_B baseline for direct comparison.
EXIT_GRID.append({
    "exit_name": "ATR5B_ORIGINAL_T45",
    "sl_mult": 0.85,
    "sl_min": 0.40,
    "sl_max": 0.85,
    "partial_mult": 1.50,
    "partial_min": 0.70,
    "partial_max": 1.10,
    "partial_size": 0.50,
    "runner_tp_mult": 4.50,
    "runner_tp_min": 2.00,
    "runner_tp_max": 3.20,
    "runner_stop": None,  # dynamic 0.25 * SL
    "runner_stop_min": 0.08,
    "runner_stop_max": 0.20,
    "time_stop": 45,
    "be_trigger": None,
    "be_stop": None,
    "micro_trigger": None,
    "micro_stop": None,
})


def utc_iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def parse_target(value):
    value = str(value).strip()
    if value.startswith("-") and value[1:].isdigit():
        return int(value)
    if value.isdigit():
        return int(value)
    return value


def parse_list_int(s):
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def pct(a, b):
    b = float(b or 0.0)
    if b <= 0:
        return 0.0
    return (float(a) - b) / b * 100.0


def row_volume(row):
    for key in ("v", "volume", "vol", "base_volume"):
        if key in row:
            try:
                return float(row[key])
            except Exception:
                pass
    return 0.0


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def ema(values, period):
    if not values:
        return []
    k = 2.0 / (period + 1.0)
    out = [float(values[0])]
    for v in values[1:]:
        out.append(float(v) * k + out[-1] * (1.0 - k))
    return out


def candle_stats(row):
    o = float(row.get("o", row.get("open", 0.0)) or 0.0)
    h = float(row.get("h", row.get("high", 0.0)) or 0.0)
    l = float(row.get("l", row.get("low", 0.0)) or 0.0)
    c = float(row.get("c", row.get("close", 0.0)) or 0.0)
    full = h - l
    if min(o, h, l, c) <= 0 or full <= 0:
        return {
            "is_red": 0, "body_ratio": 0.0, "upper_wick_ratio": 0.0,
            "lower_wick_ratio": 0.0, "close_position": 0.5,
            "range_pct": 0.0, "turnover": 0.0,
        }
    upper = h - max(o, c)
    lower = min(o, c) - l
    body = abs(c - o)
    return {
        "is_red": 1 if c < o else 0,
        "body_ratio": body / full,
        "upper_wick_ratio": max(0.0, upper / full),
        "lower_wick_ratio": max(0.0, lower / full),
        "close_position": (c - l) / full,
        "range_pct": (full / c) * 100.0,
        "turnover": c * row_volume(row),
    }


def compute_breakout_metrics(rows, signal_i):
    if signal_i < 2:
        return {}

    lb10 = rows[max(0, signal_i - 9):signal_i + 1]
    lb15 = rows[max(0, signal_i - 14):signal_i + 1]
    lb30 = rows[max(0, signal_i - 29):signal_i + 1]

    stats10 = [candle_stats(r) for r in lb10]

    total_turnover = sum(s["turnover"] for s in stats10)
    red_turnover = sum(s["turnover"] for s in stats10 if s["is_red"])
    red_volume_share_10m = red_turnover / total_turnover if total_turnover > 0 else 0.0

    rejection_count_10m = sum(1 for s in stats10 if s["upper_wick_ratio"] >= 0.45 and s["close_position"] <= 0.65)
    weak_close_count_10m = sum(1 for s in stats10 if s["close_position"] <= 0.45)
    upper_wick_pressure_10m = sum(s["upper_wick_ratio"] for s in stats10) / max(1, len(stats10))

    false_breakouts_15m = 0
    for idx in range(max(5, signal_i - 14), signal_i + 1):
        prev = rows[max(0, idx - 5):idx]
        if not prev:
            continue
        local_high = max(r["h"] for r in prev)
        s = candle_stats(rows[idx])
        if rows[idx]["h"] > local_high and s["close_position"] < 0.60:
            false_breakouts_15m += 1

    recent_flush_15m = 0
    for r in lb15:
        o = float(r.get("o", 0.0) or 0.0)
        l = float(r.get("l", 0.0) or 0.0)
        c = float(r.get("c", 0.0) or 0.0)
        if o > 0 and c > 0 and ((l - o) / o) * 100.0 <= -0.60:
            recent_flush_15m = 1
            break

    closes30 = [float(r["c"]) for r in lb30 if float(r.get("c", 0.0) or 0.0) > 0]
    ema9_vals = ema(closes30, 9)
    if len(ema9_vals) >= 4:
        close_vs_ema9_pct = pct(closes30[-1], ema9_vals[-1])
        ema9_slope_3m_pct = pct(ema9_vals[-1], ema9_vals[-4])
    else:
        close_vs_ema9_pct = 0.0
        ema9_slope_3m_pct = 0.0

    risk_score = 0
    if red_volume_share_10m >= 0.60:
        risk_score += 2
    if rejection_count_10m >= 2:
        risk_score += 2
    if false_breakouts_15m >= 2:
        risk_score += 2
    if recent_flush_15m:
        risk_score += 1
    if upper_wick_pressure_10m >= 0.30:
        risk_score += 1
    if weak_close_count_10m >= 4:
        risk_score += 1
    if ema9_slope_3m_pct < 0:
        risk_score += 1
    if close_vs_ema9_pct < -0.05:
        risk_score += 1

    return {
        "red_volume_share_10m": red_volume_share_10m,
        "rejection_count_10m": rejection_count_10m,
        "weak_close_count_10m": weak_close_count_10m,
        "upper_wick_pressure_10m": upper_wick_pressure_10m,
        "false_breakouts_15m": false_breakouts_15m,
        "recent_flush_15m": recent_flush_15m,
        "close_vs_ema9_pct": close_vs_ema9_pct,
        "ema9_slope_3m_pct": ema9_slope_3m_pct,
        "breakout_risk_score": risk_score,
    }


def passes_combo_balanced(metrics):
    return (
        metrics.get("breakout_risk_score", 999) <= 3
        and metrics.get("red_volume_share_10m", 1.0) < 0.68
        and metrics.get("rejection_count_10m", 99) <= 2
        and metrics.get("false_breakouts_15m", 99) <= 1
        and metrics.get("recent_flush_15m", 1) == 0
        and metrics.get("upper_wick_pressure_10m", 999.0) < 0.38
        and metrics.get("ema9_slope_3m_pct", -999.0) >= -0.02
        and metrics.get("close_vs_ema9_pct", -999.0) >= -0.10
    )


def apply_entry(bt, rows, raw):
    if raw.get("score", -999) < ENTRY["min_score"]:
        return None
    if ENTRY["need_initiative"] and not raw.get("initiative", 0):
        return None
    if raw.get("price_change", 999.0) > ENTRY["max_pc"]:
        return None
    if raw.get("vol_ratio", 999.0) > ENTRY["max_vol"]:
        return None
    if raw.get("trend15", 0.0) < ENTRY["min_trend15"]:
        return None
    if raw.get("btc5", 0.0) < ENTRY["min_btc5"]:
        return None

    i = raw["i"]
    if i + 1 >= len(rows):
        return None

    metrics = compute_breakout_metrics(rows, i)
    if not metrics or not passes_combo_balanced(metrics):
        return None

    sig = rows[i]
    sig_close = sig["c"]
    if sig_close <= 0:
        return None

    n = rows[i + 1]
    low_from_signal = bt.pct(n["l"], sig_close)
    if low_from_signal <= -0.15:
        return None
    if n["c"] <= sig_close:
        return None

    confirm_move_pct = bt.pct(n["c"], sig_close)
    if confirm_move_pct > 0.75:
        return None

    s = dict(raw)
    s.update(metrics)
    s["i"] = i + 1
    s["t"] = rows[i + 1]["t"]
    s["entry"] = rows[i + 1]["c"]
    s["confirm_delay_min"] = 1
    s["confirm_move_pct"] = confirm_move_pct
    s["confirm_min_low"] = low_from_signal
    return s


def pre_range_pct(rows, entry_i, lookback):
    start = max(0, entry_i - lookback)
    if entry_i <= start:
        return 0.0
    sub = rows[start:entry_i]
    if not sub:
        return 0.0
    hi = max(r["h"] for r in sub)
    lo = min(r["l"] for r in sub)
    close = rows[entry_i]["c"]
    return (hi - lo) / close * 100.0 if close > 0 else 0.0


def exit_params(rows, entry_i, cfg_exit):
    rng5 = pre_range_pct(rows, entry_i, 5)
    if rng5 <= 0:
        rng5 = 0.75

    sl = clamp(rng5 * cfg_exit["sl_mult"], cfg_exit["sl_min"], cfg_exit["sl_max"])
    partial = clamp(sl * cfg_exit["partial_mult"], cfg_exit["partial_min"], cfg_exit["partial_max"])
    runner_tp = clamp(sl * cfg_exit["runner_tp_mult"], cfg_exit["runner_tp_min"], cfg_exit["runner_tp_max"])
    if cfg_exit.get("runner_stop") is None:
        runner_stop = clamp(sl * 0.25, cfg_exit.get("runner_stop_min", 0.08), cfg_exit.get("runner_stop_max", 0.20))
    else:
        runner_stop = cfg_exit["runner_stop"]

    return {
        "sl": sl,
        "partial_at": partial,
        "partial_size": cfg_exit["partial_size"],
        "runner_tp": runner_tp,
        "runner_stop": runner_stop,
        "time_stop": cfg_exit["time_stop"],
        "pre_range5": rng5,
    }


def simulate_exit(bt, rows, entry_i, cfg_exit):
    p = exit_params(rows, entry_i, cfg_exit)
    entry = rows[entry_i]["c"]
    max_profit = 0.0
    max_loss = 0.0
    partial_done = False
    be_armed = False
    micro_armed = False

    for j in range(entry_i + 1, min(entry_i + int(p["time_stop"]) + 1, len(rows))):
        held = j - entry_i
        r = rows[j]
        high_pct = bt.pct(r["h"], entry)
        low_pct = bt.pct(r["l"], entry)
        close_pct = bt.pct(r["c"], entry)

        max_profit = max(max_profit, high_pct)
        max_loss = min(max_loss, low_pct)

        if cfg_exit.get("be_trigger") is not None and max_profit >= cfg_exit["be_trigger"]:
            be_armed = True
        if cfg_exit.get("micro_trigger") is not None and max_profit >= cfg_exit["micro_trigger"]:
            micro_armed = True

        # Conservative intrabar ordering: SL before good exits if both are touched.
        if not partial_done and low_pct <= -p["sl"]:
            return {"reason": "SL", "exit_pct": -p["sl"], "mfe": max_profit, "mae": max_loss, "held": held, **p}

        if micro_armed and not partial_done and low_pct <= cfg_exit.get("micro_stop", 0.0):
            return {"reason": "MICRO_LOCK", "exit_pct": cfg_exit.get("micro_stop", 0.0), "mfe": max_profit, "mae": max_loss, "held": held, **p}

        if be_armed and not partial_done and low_pct <= cfg_exit.get("be_stop", 0.0):
            return {"reason": "BE", "exit_pct": cfg_exit.get("be_stop", 0.0), "mfe": max_profit, "mae": max_loss, "held": held, **p}

        if partial_done:
            if low_pct <= p["runner_stop"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_stop"]
                return {"reason": "RUNNER_STOP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held, **p}

            if high_pct >= p["runner_tp"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_tp"]
                return {"reason": "RUNNER_TP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held, **p}

        if not partial_done and high_pct >= p["partial_at"]:
            partial_done = True

    last_i = min(entry_i + int(p["time_stop"]), len(rows) - 1)
    close_pct = bt.pct(rows[last_i]["c"], entry)

    if partial_done:
        weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * close_pct
        reason = "TIME_PARTIAL"
    else:
        weighted = close_pct
        reason = "TIME"

    return {"reason": reason, "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": last_i - entry_i, **p}


def apply_max_open(records, max_open):
    open_until = []
    accepted = []
    skipped = 0

    for r in sorted(records, key=lambda x: (x["entry_t"], x["symbol"], x["exit_name"])):
        t = r["entry_t"]
        open_until = [x for x in open_until if x > t]
        if len(open_until) >= max_open:
            skipped += 1
            continue
        accepted.append(r)
        open_until.append(r["exit_t"])

    return accepted, skipped


def summarize(records, skipped_by_maxopen=0):
    out = {
        "trades": 0, "wins": 0, "losses": 0,
        "gross": 0.0, "net": 0.0, "costs": 0.0,
        "avg_net": 0.0, "winrate": 0.0,
        "avg_mfe": 0.0, "avg_mae": 0.0,
        "skipped_by_maxopen": skipped_by_maxopen,
    }
    for k in ["SL", "TIME", "TIME_PARTIAL", "RUNNER_STOP", "RUNNER_TP", "BE", "MICRO_LOCK"]:
        out[k] = 0

    for r in records:
        out["trades"] += 1
        out["gross"] += r["gross"]
        out["net"] += r["net"]
        out["costs"] += r["costs"]
        out["avg_mfe"] += r["mfe"]
        out["avg_mae"] += r["mae"]
        out[r["reason"]] = out.get(r["reason"], 0) + 1
        if r["net"] > 0:
            out["wins"] += 1
        elif r["net"] < 0:
            out["losses"] += 1

    if out["trades"]:
        n = out["trades"]
        out["avg_net"] = out["net"] / n
        out["winrate"] = out["wins"] / n * 100.0
        out["avg_mfe"] = out["avg_mfe"] / n
        out["avg_mae"] = out["avg_mae"] / n
    return out


async def send_to_tg(zip_path, caption, target):
    from telethon import TelegramClient

    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    if not api_id or not api_hash:
        print("⚠️ Telegram skipped: API_ID/API_HASH missing.")
        return False

    session_name = os.getenv("BACKTEST_TG_SESSION", "backtest_sender_session")
    async with TelegramClient(session_name, int(api_id), api_hash) as client:
        await client.send_file(parse_target(target), str(zip_path), caption=caption)

    return True


async def run(args):
    import backtest_1m as bt
    import aiohttp

    if args.spread_bps is not None:
        bt.SPREAD_BPS = float(args.spread_bps)
    if args.slippage_bps is not None:
        bt.SLIPPAGE_BPS = float(args.slippage_bps)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    end_ts = int(datetime.now(timezone.utc).timestamp()) if not args.end else int(datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc).timestamp())
    start_ts = end_ts - args.days * 24 * 3600

    max_open_values = parse_list_int(args.max_open) or [1, 2]

    print(f"🚀 SKYNET WINNER EXIT GRID | days={args.days} top={args.top} max_open={max_open_values}")
    print(f"Costs: spread={bt.SPREAD_BPS}bps slippage={bt.SLIPPAGE_BPS}bps")
    print(f"Entry: {ENTRY_NAME}")
    print(f"Exit configs: {len(EXIT_GRID)}")

    async with aiohttp.ClientSession() as session:
        if args.symbols:
            symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
            symbols = [s if s.endswith("_USDT") else f"{s}_USDT" for s in symbols]
        else:
            symbols = await bt.get_top_symbols(session, args.top)
        symbols = [s for s in symbols if s != "BTC_USDT"]

        print(f"Symbols: {len(symbols)}")
        print("Downloading BTC context...")
        btc_rows = await bt.download_klines(session, "BTC_USDT", start_ts, end_ts, use_cache=not args.no_cache)
        btc_close_by_t, btc_times = bt.prepare_btc_context(btc_rows)

        rows_by_symbol = {}
        signals_by_symbol = {}

        for idx, symbol in enumerate(symbols, 1):
            print(f"[{idx}/{len(symbols)}] {symbol} downloading/generating...")
            rows = await bt.download_klines(session, symbol, start_ts, end_ts, use_cache=not args.no_cache)
            if len(rows) < 200:
                print(f"  skip candles={len(rows)}")
                continue
            raw = bt.generate_signals(symbol, rows, btc_close_by_t, btc_times)
            rows_by_symbol[symbol] = rows
            signals_by_symbol[symbol] = raw
            print(f"  candles={len(rows)} raw_signals={len(raw)}")
            await asyncio.sleep(0.05)

    records_by_key = {}
    all_trades = []
    all_summary = []

    eligible_count = 0
    for symbol, raw_signals in signals_by_symbol.items():
        rows = rows_by_symbol[symbol]
        for raw in raw_signals:
            s = apply_entry(bt, rows, raw)
            if not s:
                continue
            eligible_count += 1

            for exit_cfg in EXIT_GRID:
                result = simulate_exit(bt, rows, s["i"], exit_cfg)
                exit_i = min(s["i"] + int(result["held"]), len(rows) - 1)
                gross, net, costs = bt.calc_net_pnl(result["exit_pct"])

                rec = {
                    "entry_name": ENTRY_NAME,
                    "exit_name": exit_cfg["exit_name"],
                    "symbol": symbol,
                    "time": utc_iso(s["t"]),
                    "entry_t": s["t"],
                    "exit_t": rows[exit_i]["t"],
                    "score": s.get("score", 0),
                    "price_change": s.get("price_change", 0.0),
                    "vol_ratio": s.get("vol_ratio", 0.0),
                    "trend15": s.get("trend15", 0.0),
                    "btc5": s.get("btc5", 0.0),
                    "structure": s.get("structure", 0),
                    "initiative": s.get("initiative", 0),
                    "confirm_move_pct": s.get("confirm_move_pct", 0.0),
                    "breakout_risk_score": s.get("breakout_risk_score", 0),
                    "false_breakouts_15m": s.get("false_breakouts_15m", 0),
                    "red_volume_share_10m": s.get("red_volume_share_10m", 0.0),
                    "ema9_slope_3m_pct": s.get("ema9_slope_3m_pct", 0.0),
                    "reason": result["reason"],
                    "exit_pct": result["exit_pct"],
                    "mfe": result["mfe"],
                    "mae": result["mae"],
                    "held": result["held"],
                    "sl": result["sl"],
                    "partial_at": result["partial_at"],
                    "runner_tp": result["runner_tp"],
                    "runner_stop": result["runner_stop"],
                    "time_stop": result["time_stop"],
                    "pre_range5": result.get("pre_range5", 0.0),
                    "gross": gross,
                    "net": net,
                    "costs": costs,
                }
                records_by_key.setdefault(exit_cfg["exit_name"], []).append(rec)

    print(f"Eligible entry signals: {eligible_count}")

    for exit_name, records in records_by_key.items():
        for max_open in max_open_values:
            accepted, skipped = apply_max_open(records, max_open)
            sm = summarize(accepted, skipped)
            sm.update({
                "entry_name": ENTRY_NAME,
                "exit_name": exit_name,
                "max_open": max_open,
                "days": args.days,
                "top": args.top,
                "spread_bps": bt.SPREAD_BPS,
                "slippage_bps": bt.SLIPPAGE_BPS,
            })
            all_summary.append(sm)
            for r in accepted:
                rr = dict(r)
                rr["max_open"] = max_open
                all_trades.append(rr)

    all_summary.sort(key=lambda x: x["net"], reverse=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_DIR / f"winner_exit_grid_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / f"winner_exit_grid_summary_{stamp}.csv"
    trades_path = run_dir / f"winner_exit_grid_trades_{stamp}.csv"
    manifest_path = run_dir / "manifest.json"
    zip_path = run_dir / f"WINNER_EXIT_GRID_RESULTS_{stamp}.zip"

    summary_fields = [
        "entry_name", "exit_name", "max_open", "days", "top", "spread_bps", "slippage_bps",
        "trades", "skipped_by_maxopen", "wins", "losses", "winrate",
        "gross", "net", "costs", "avg_net", "avg_mfe", "avg_mae",
        "SL", "TIME", "TIME_PARTIAL", "RUNNER_STOP", "RUNNER_TP", "BE", "MICRO_LOCK",
    ]
    trade_fields = [
        "entry_name", "exit_name", "max_open", "time", "symbol",
        "score", "price_change", "vol_ratio", "trend15", "btc5", "structure", "initiative",
        "confirm_move_pct", "breakout_risk_score", "false_breakouts_15m",
        "red_volume_share_10m", "ema9_slope_3m_pct",
        "reason", "exit_pct", "mfe", "mae", "held",
        "sl", "partial_at", "runner_tp", "runner_stop", "time_stop", "pre_range5",
        "gross", "net", "costs", "entry_t", "exit_t",
    ]

    write_csv(summary_path, all_summary, summary_fields)
    write_csv(trades_path, all_trades, trade_fields)

    manifest = {
        "created_utc": stamp,
        "suite": EXIT_SUITE_NAME,
        "entry": ENTRY,
        "entry_name": ENTRY_NAME,
        "exit_grid_count": len(EXIT_GRID),
        "days": args.days,
        "top": args.top,
        "max_open": max_open_values,
        "spread_bps": bt.SPREAD_BPS,
        "slippage_bps": bt.SLIPPAGE_BPS,
        "summary_file": summary_path.name,
        "trades_file": trades_path.name,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(summary_path, summary_path.name)
        z.write(trades_path, trades_path.name)
        z.write(manifest_path, manifest_path.name)

    print("\n=== TOP EXIT RESULTS ===")
    for r in all_summary[:40]:
        print(
            f"{r['exit_name']:<24} MO:{r['max_open']} "
            f"Net:{r['net']:+.2f}$ Tr:{r['trades']} WR:{r['winrate']:.1f}% "
            f"Avg:{r['avg_net']:+.3f}$ PTP:{r['TIME_PARTIAL'] + r['RUNNER_STOP'] + r['RUNNER_TP']} "
            f"SL:{r['SL']} BE:{r['BE']} ML:{r['MICRO_LOCK']}"
        )

    print("\nZIP:", zip_path)

    if args.send_tg:
        caption = (
            f"📦 SKYNET WINNER EXIT GRID\n"
            f"entry={ENTRY_NAME}\n"
            f"days={args.days} top={args.top} max_open={args.max_open}\n"
            f"costs spread={bt.SPREAD_BPS} slip={bt.SLIPPAGE_BPS}"
        )
        try:
            await send_to_tg(zip_path, caption, args.tg_target)
            print("📤 Sent to Telegram")
        except Exception as e:
            print(f"⚠️ Telegram send failed: {type(e).__name__}: {e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--symbols", default="")
    p.add_argument("--max-open", default="1,2")
    p.add_argument("--spread-bps", type=float, default=None)
    p.add_argument("--slippage-bps", type=float, default=None)
    p.add_argument("--end", default=None)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--send-tg", action="store_true")
    p.add_argument("--tg-target", default=os.getenv("TG_TARGET", "-1002953234396"))
    args = p.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
