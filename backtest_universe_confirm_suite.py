import os
import csv
import json
import zipfile
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# ============================================================
# SKYNET UNIVERSE + CONFIRM-WAIT SUITE
#
# Tests what can significantly improve winrate/profit:
# 1) dynamic universe instead of fixed current top30
# 2) confirmation wait 1/2/3 minutes
# 3) stronger market-regime filters
# 4) ATR5_B exit, because it was the best dynamic SL/TP result
#
# Does NOT trade.
# Does NOT touch skynet_main.py.
# ============================================================

load_dotenv("/root/skynet/.env")

ROOT = Path("/root/skynet")
OUT_DIR = ROOT / "data" / "backtest" / "universe_confirm_suite"

ENTRY_CASES = [
    {
        "entry_case": "BASE_PC055_VOL25_SCORE5_INIT_RUG015",
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.55,
        "max_vol": 25.0,
        "rug": -0.15,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    {
        "entry_case": "BASE_PLUS_BTC0_PC055_VOL25_SCORE5_INIT_RUG015",
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.55,
        "max_vol": 25.0,
        "rug": -0.15,
        "min_trend15": -999.0,
        "min_btc5": 0.0,
    },
    {
        "entry_case": "BASE_PLUS_TREND040_PC055_VOL25_SCORE5_INIT_RUG015",
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.55,
        "max_vol": 25.0,
        "rug": -0.15,
        "min_trend15": 0.40,
        "min_btc5": -999.0,
    },
    {
        "entry_case": "RELAXED_PC065_VOL35_SCORE5_INIT_RUG015",
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "rug": -0.15,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
]

CONFIRM_MODES = [
    "WAIT1_CLOSE",
    "WAIT2_FIRST_CLOSE",
    "WAIT3_FIRST_CLOSE",
    "WAIT2_BREAK_HIGH",
    "WAIT3_BREAK_HIGH",
]

UNIVERSE_MODES = [
    "STATIC_ALL",
    "DYN_TURNOVER_TOP20",
    "DYN_TURNOVER_TOP30",
    "DYN_TURNOVER_TOP40",
    "DYN_ACTIVITY_TOP20",
    "DYN_ACTIVITY_TOP30",
    "DYN_ACTIVITY_TOP40",
]


def utc_iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def day_key(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def parse_target(value):
    value = str(value).strip()
    if value.startswith("-") and value[1:].isdigit():
        return int(value)
    if value.isdigit():
        return int(value)
    return value


def parse_list_int(s):
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]


def parse_list_str(s):
    return [x.strip() for x in str(s).split(",") if x.strip()]


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def row_volume(row):
    # backtest_1m rows usually contain v, but keep robust fallbacks.
    for key in ("v", "volume", "vol", "base_volume"):
        if key in row:
            try:
                return float(row[key])
            except Exception:
                pass
    return 0.0


def quote_turnover(row):
    c = float(row.get("c", 0.0) or 0.0)
    v = row_volume(row)
    return max(0.0, c * v)


def range_pct(row):
    c = float(row.get("c", 0.0) or 0.0)
    if c <= 0:
        return 0.0
    return max(0.0, (float(row.get("h", c)) - float(row.get("l", c))) / c * 100.0)


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def pre_range_pct(bt, rows, entry_i, lookback):
    start = max(0, entry_i - lookback)
    if entry_i <= start:
        return 0.0
    sub = rows[start:entry_i]
    if not sub:
        return 0.0
    hi = max(r["h"] for r in sub)
    lo = min(r["l"] for r in sub)
    close = rows[entry_i]["c"]
    if close <= 0:
        return 0.0
    return (hi - lo) / close * 100.0


def atr5b_params(bt, rows, entry_i):
    rng5 = pre_range_pct(bt, rows, entry_i, 5)
    rng10 = pre_range_pct(bt, rows, entry_i, 10)

    sl = clamp(rng5 * 0.85, 0.40, 0.85)
    partial = clamp(sl * 1.50, 0.70, 1.10)
    tp = clamp(sl * 4.50, 2.00, 3.20)
    stop = clamp(sl * 0.25, 0.08, 0.20)

    return {
        "sl": sl,
        "partial_at": partial,
        "partial_size": 0.50,
        "runner_tp": tp,
        "runner_stop": stop,
        "time": 45,
        "pre_range5": rng5,
        "pre_range10": rng10,
    }


def simulate_atr5b(bt, rows, entry_i):
    p = atr5b_params(bt, rows, entry_i)
    entry = rows[entry_i]["c"]

    max_profit = 0.0
    max_loss = 0.0
    partial_done = False

    for j in range(entry_i + 1, min(entry_i + int(p["time"]) + 1, len(rows))):
        held = j - entry_i
        r = rows[j]
        high_pct = bt.pct(r["h"], entry)
        low_pct = bt.pct(r["l"], entry)
        close_pct = bt.pct(r["c"], entry)

        max_profit = max(max_profit, high_pct)
        max_loss = min(max_loss, low_pct)

        if not partial_done and low_pct <= -p["sl"]:
            return {
                "reason": "SL",
                "exit_pct": -p["sl"],
                "mfe": max_profit,
                "mae": max_loss,
                "held": held,
                **p,
            }

        if partial_done:
            if low_pct <= p["runner_stop"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_stop"]
                return {
                    "reason": "DYN_RUNNER_STOP",
                    "exit_pct": weighted,
                    "mfe": max_profit,
                    "mae": max_loss,
                    "held": held,
                    **p,
                }

            if high_pct >= p["runner_tp"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_tp"]
                return {
                    "reason": "DYN_RUNNER_TP",
                    "exit_pct": weighted,
                    "mfe": max_profit,
                    "mae": max_loss,
                    "held": held,
                    **p,
                }

        if not partial_done and high_pct >= p["partial_at"]:
            partial_done = True

    last_i = min(entry_i + int(p["time"]), len(rows) - 1)
    close_pct = bt.pct(rows[last_i]["c"], entry)

    if partial_done:
        weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * close_pct
        reason = "DYN_TIME_PARTIAL"
    else:
        weighted = close_pct
        reason = "TIME"

    return {
        "reason": reason,
        "exit_pct": weighted,
        "mfe": max_profit,
        "mae": max_loss,
        "held": last_i - entry_i,
        **p,
    }


def build_daily_universe(symbols, rows_by_symbol, top_values):
    # Uses previous-day full candles as proxy for daily active universe.
    # Because we don't have historical MEXC listing snapshots, this still has survivorship bias,
    # but it is much closer than static current top30.
    daily_scores = {}

    for symbol in symbols:
        rows = rows_by_symbol.get(symbol, [])
        by_day = {}
        for r in rows:
            d = day_key(r["t"])
            by_day.setdefault(d, {"turnover": 0.0, "activity": 0.0, "n": 0})
            tv = quote_turnover(r)
            rp = range_pct(r)
            by_day[d]["turnover"] += tv
            # activity = turnover adjusted by realized movement; avoids purely dead high-cap names.
            by_day[d]["activity"] += tv * (1.0 + min(rp, 5.0) / 100.0)
            by_day[d]["n"] += 1

        for d, vals in by_day.items():
            daily_scores.setdefault(d, {})
            daily_scores[d][symbol] = vals

    universes = {}
    days = sorted(daily_scores.keys())

    for d in days:
        records = []
        for symbol, vals in daily_scores[d].items():
            records.append({
                "symbol": symbol,
                "turnover": vals["turnover"],
                "activity": vals["activity"],
                "n": vals["n"],
            })

        by_turnover = sorted(records, key=lambda x: x["turnover"], reverse=True)
        by_activity = sorted(records, key=lambda x: x["activity"], reverse=True)

        universes[d] = {}
        for n in top_values:
            universes[d][f"DYN_TURNOVER_TOP{n}"] = {r["symbol"] for r in by_turnover[:n]}
            universes[d][f"DYN_ACTIVITY_TOP{n}"] = {r["symbol"] for r in by_activity[:n]}
        universes[d]["STATIC_ALL"] = set(symbols)

    return universes


def apply_entry_case(bt, rows, raw, entry_case, confirm_mode):
    if raw.get("score", -999) < entry_case["min_score"]:
        return None
    if entry_case["need_initiative"] and not raw.get("initiative", 0):
        return None
    if raw.get("price_change", 999.0) > entry_case["max_pc"]:
        return None
    if raw.get("vol_ratio", 999.0) > entry_case["max_vol"]:
        return None
    if raw.get("trend15", 0.0) < entry_case["min_trend15"]:
        return None
    if raw.get("btc5", 0.0) < entry_case["min_btc5"]:
        return None

    i = raw["i"]
    sig = rows[i]
    sig_close = sig["c"]
    sig_high = sig["h"]

    if sig_close <= 0:
        return None

    max_wait = 1
    require_break_high = False

    if confirm_mode == "WAIT1_CLOSE":
        max_wait = 1
    elif confirm_mode == "WAIT2_FIRST_CLOSE":
        max_wait = 2
    elif confirm_mode == "WAIT3_FIRST_CLOSE":
        max_wait = 3
    elif confirm_mode == "WAIT2_BREAK_HIGH":
        max_wait = 2
        require_break_high = True
    elif confirm_mode == "WAIT3_BREAK_HIGH":
        max_wait = 3
        require_break_high = True
    else:
        max_wait = 1

    min_low = 999.0
    entry_i = None

    for k in range(1, max_wait + 1):
        if i + k >= len(rows):
            break
        n = rows[i + k]
        low_from_signal = bt.pct(n["l"], sig_close)
        min_low = min(min_low, low_from_signal)

        if min_low <= entry_case["rug"]:
            return None

        if require_break_high:
            ok = n["c"] > sig_high
        else:
            ok = n["c"] > sig_close

        if ok:
            entry_i = i + k
            break

    if entry_i is None:
        return None

    s = dict(raw)
    s["entry_case"] = entry_case["entry_case"]
    s["confirm_mode"] = confirm_mode
    s["confirm_delay_min"] = entry_i - i
    s["confirm_min_low"] = min_low
    s["i"] = entry_i
    s["t"] = rows[entry_i]["t"]
    s["entry"] = rows[entry_i]["c"]
    return s


def apply_max_open(records, max_open):
    open_until = []
    accepted = []
    skipped = 0

    for r in sorted(records, key=lambda x: (x["entry_t"], x["symbol"])):
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
    for k in ["SL", "TIME", "DYN_RUNNER_STOP", "DYN_RUNNER_TP", "DYN_TIME_PARTIAL"]:
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

    if out["trades"] > 0:
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

    max_open_values = parse_list_int(args.max_open) or [1, 2, 3]
    universe_modes = parse_list_str(args.universe_modes) or UNIVERSE_MODES
    confirm_modes = parse_list_str(args.confirm_modes) or CONFIRM_MODES

    print(f"🚀 SKYNET UNIVERSE+CONFIRM SUITE | days={args.days} broad_top={args.broad_top} max_open={max_open_values}")
    print(f"Costs: spread={bt.SPREAD_BPS}bps slippage={bt.SLIPPAGE_BPS}bps")
    print(f"Universe modes: {universe_modes}")
    print(f"Confirm modes: {confirm_modes}")

    async with aiohttp.ClientSession() as session:
        if args.symbols:
            symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
            symbols = [s if s.endswith("_USDT") else f"{s}_USDT" for s in symbols]
        else:
            symbols = await bt.get_top_symbols(session, args.broad_top)

        symbols = [s for s in symbols if s != "BTC_USDT"]

        print(f"Symbols: {len(symbols)}")
        print("Downloading BTC context...")
        btc_rows = await bt.download_klines(session, "BTC_USDT", start_ts, end_ts, use_cache=not args.no_cache)
        btc_close_by_t, btc_times = bt.prepare_btc_context(btc_rows)

        rows_by_symbol = {}
        raw_signals_by_symbol = {}

        for idx, symbol in enumerate(symbols, 1):
            print(f"[{idx}/{len(symbols)}] {symbol} downloading/generating...")
            rows = await bt.download_klines(session, symbol, start_ts, end_ts, use_cache=not args.no_cache)
            if len(rows) < 200:
                print(f"  skip candles={len(rows)}")
                continue
            raw = bt.generate_signals(symbol, rows, btc_close_by_t, btc_times)
            rows_by_symbol[symbol] = rows
            raw_signals_by_symbol[symbol] = raw
            print(f"  candles={len(rows)} raw_signals={len(raw)}")
            await asyncio.sleep(0.05)

    daily_universe = build_daily_universe(list(rows_by_symbol.keys()), rows_by_symbol, top_values=[20, 30, 40, 50])

    all_summary = []
    all_trades = []
    records_by_key = {}

    for symbol, raw_signals in raw_signals_by_symbol.items():
        rows = rows_by_symbol[symbol]

        for raw in raw_signals:
            d = day_key(raw["t"])

            for universe_mode in universe_modes:
                allowed = daily_universe.get(d, {}).get(universe_mode, set())
                if symbol not in allowed:
                    continue

                for entry_case in ENTRY_CASES:
                    for confirm_mode in confirm_modes:
                        s = apply_entry_case(bt, rows, raw, entry_case, confirm_mode)
                        if not s:
                            continue

                        result = simulate_atr5b(bt, rows, s["i"])
                        exit_i = min(s["i"] + int(result["held"]), len(rows) - 1)
                        gross, net, costs = bt.calc_net_pnl(result["exit_pct"])

                        rec = {
                            "universe_mode": universe_mode,
                            "entry_case": entry_case["entry_case"],
                            "confirm_mode": confirm_mode,
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
                            "confirm_delay_min": s.get("confirm_delay_min", 0),
                            "confirm_min_low": s.get("confirm_min_low", 0.0),
                            "reason": result["reason"],
                            "exit_pct": result["exit_pct"],
                            "mfe": result["mfe"],
                            "mae": result["mae"],
                            "held": result["held"],
                            "sl": result["sl"],
                            "partial_at": result["partial_at"],
                            "runner_tp": result["runner_tp"],
                            "runner_stop": result["runner_stop"],
                            "time_stop": result["time"],
                            "pre_range5": result.get("pre_range5", 0.0),
                            "gross": gross,
                            "net": net,
                            "costs": costs,
                        }

                        key = (universe_mode, entry_case["entry_case"], confirm_mode)
                        records_by_key.setdefault(key, []).append(rec)

    for (universe_mode, entry_case, confirm_mode), records in records_by_key.items():
        for max_open in max_open_values:
            accepted, skipped = apply_max_open(records, max_open)
            sm = summarize(accepted, skipped)
            sm.update({
                "universe_mode": universe_mode,
                "entry_case": entry_case,
                "confirm_mode": confirm_mode,
                "max_open": max_open,
                "days": args.days,
                "broad_top": args.broad_top,
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
    run_dir = OUT_DIR / f"universe_confirm_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / f"universe_confirm_summary_{stamp}.csv"
    trades_path = run_dir / f"universe_confirm_trades_{stamp}.csv"
    manifest_path = run_dir / "manifest.json"
    zip_path = run_dir / f"UNIVERSE_CONFIRM_RESULTS_{stamp}.zip"

    summary_fields = [
        "universe_mode", "entry_case", "confirm_mode", "max_open", "days", "broad_top", "spread_bps", "slippage_bps",
        "trades", "skipped_by_maxopen", "wins", "losses", "winrate",
        "gross", "net", "costs", "avg_net", "avg_mfe", "avg_mae",
        "SL", "TIME", "DYN_RUNNER_STOP", "DYN_RUNNER_TP", "DYN_TIME_PARTIAL",
    ]
    trade_fields = [
        "universe_mode", "entry_case", "confirm_mode", "max_open", "time", "symbol",
        "score", "price_change", "vol_ratio", "trend15", "btc5", "structure", "initiative",
        "confirm_delay_min", "confirm_min_low",
        "reason", "exit_pct", "mfe", "mae", "held",
        "sl", "partial_at", "runner_tp", "runner_stop", "time_stop", "pre_range5",
        "gross", "net", "costs", "entry_t", "exit_t",
    ]

    write_csv(summary_path, all_summary, summary_fields)
    write_csv(trades_path, all_trades, trade_fields)

    manifest = {
        "created_utc": stamp,
        "days": args.days,
        "broad_top": args.broad_top,
        "symbols": args.symbols,
        "max_open": max_open_values,
        "universe_modes": universe_modes,
        "confirm_modes": confirm_modes,
        "entry_cases": ENTRY_CASES,
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

    print("\n=== TOP RESULTS ===")
    for r in all_summary[:30]:
        print(
            f"{r['universe_mode']:<22} MO:{r['max_open']} {r['entry_case']:<45} {r['confirm_mode']:<18} "
            f"Net:{r['net']:+.2f}$ Tr:{r['trades']} WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$"
        )

    print("\nZIP:", zip_path)

    if args.send_tg:
        caption = (
            f"📦 SKYNET UNIVERSE+CONFIRM SUITE\n"
            f"days={args.days} broad_top={args.broad_top} symbols={args.symbols or '-'}\n"
            f"max_open={args.max_open}\n"
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
    p.add_argument("--broad-top", type=int, default=40)
    p.add_argument("--symbols", default="")
    p.add_argument("--max-open", default="1,2,3")
    p.add_argument("--universe-modes", default=",".join(UNIVERSE_MODES))
    p.add_argument("--confirm-modes", default=",".join(CONFIRM_MODES))
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
