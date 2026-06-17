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
OUT_DIR = ROOT / "data" / "backtest" / "maxopen_suite"

DYN_MODES_DEFAULT = [
    "DYN_08_50_TP20_STOP010",
    "DYN_07_50_TP20_STOP010",
    "DYN_06_50_TP20_STOP010",
    "FAST_FAIL",
    "BASE",
]

STRATEGIES_DEFAULT = [
    "INITIATIVE_CONTEXT",
    "MAIN_CONTEXT_STRICT",
]

CONFIRM_CASES_CORE = [
    {"case": "NO_RUG_CLOSE_RUG015_PC055_VOL25", "confirm": "NO_RUG_CLOSE_1", "rug": -0.15, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "NO_RUG_CLOSE_RUG015_PC065_VOL25", "confirm": "NO_RUG_CLOSE_1", "rug": -0.15, "max_pc": 0.65, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "NO_RUG_CLOSE_RUG020_PC055_VOL25", "confirm": "NO_RUG_CLOSE_1", "rug": -0.20, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
]

CONFIRM_CASES_WIDE = CONFIRM_CASES_CORE + [
    {"case": "NO_RUG_CLOSE_RUG010_PC055_VOL25", "confirm": "NO_RUG_CLOSE_1", "rug": -0.10, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "NO_RUG_CLOSE_RUG025_PC055_VOL25", "confirm": "NO_RUG_CLOSE_1", "rug": -0.25, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "CLOSE_PC055_VOL25", "confirm": "CLOSE_1", "rug": -0.20, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "BREAK_HIGH_PC055_VOL25", "confirm": "BREAK_HIGH_1", "rug": -0.20, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "NO_RUG_BREAK_HIGH_PC055_VOL25", "confirm": "NO_RUG_BREAK_HIGH_1", "rug": -0.20, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "NO_RUG_CLOSE_RUG015_PC045_VOL25", "confirm": "NO_RUG_CLOSE_1", "rug": -0.15, "max_pc": 0.45, "max_vol": 25.0, "min_score": -999, "blacklist": ""},
    {"case": "NO_RUG_CLOSE_RUG015_PC055_VOL18", "confirm": "NO_RUG_CLOSE_1", "rug": -0.15, "max_pc": 0.55, "max_vol": 18.0, "min_score": -999, "blacklist": ""},
    {"case": "NO_RUG_CLOSE_RUG015_PC055_VOL25_TOXIC5_BL", "confirm": "NO_RUG_CLOSE_1", "rug": -0.15, "max_pc": 0.55, "max_vol": 25.0, "min_score": -999, "blacklist": "RENDER,ONDO,INJ,XRP,WLD"},
]

def utc_iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def parse_list_int(s):
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]

def parse_list_str(s):
    return [x.strip() for x in str(s).split(",") if x.strip()]

def parse_target(value):
    value = str(value).strip()
    if value.startswith("-") and value[1:].isdigit():
        return int(value)
    if value.isdigit():
        return int(value)
    return value

def dynamic_params(mode):
    return {
        "DYN_05_50_TP15_STOP000": {"partial_at": 0.50, "partial_size": 0.50, "runner_tp": 1.50, "runner_stop": 0.00, "time": 30},
        "DYN_06_50_TP15_STOP005": {"partial_at": 0.60, "partial_size": 0.50, "runner_tp": 1.50, "runner_stop": 0.05, "time": 30},
        "DYN_06_50_TP20_STOP010": {"partial_at": 0.60, "partial_size": 0.50, "runner_tp": 2.00, "runner_stop": 0.10, "time": 35},
        "DYN_06_60_TP20_STOP010": {"partial_at": 0.60, "partial_size": 0.60, "runner_tp": 2.00, "runner_stop": 0.10, "time": 35},
        "DYN_07_50_TP20_STOP010": {"partial_at": 0.70, "partial_size": 0.50, "runner_tp": 2.00, "runner_stop": 0.10, "time": 35},
        "DYN_07_60_TP20_STOP010": {"partial_at": 0.70, "partial_size": 0.60, "runner_tp": 2.00, "runner_stop": 0.10, "time": 35},
        "DYN_07_70_TP20_STOP010": {"partial_at": 0.70, "partial_size": 0.70, "runner_tp": 2.00, "runner_stop": 0.10, "time": 35},
        "DYN_08_50_TP20_STOP010": {"partial_at": 0.80, "partial_size": 0.50, "runner_tp": 2.00, "runner_stop": 0.10, "time": 35},
        "DYN_08_50_TP25_STOP015": {"partial_at": 0.80, "partial_size": 0.50, "runner_tp": 2.50, "runner_stop": 0.15, "time": 45},
    }.get(mode)

def simulate_dynamic(bt, rows, entry_i, mode):
    p = dynamic_params(mode)
    if not p:
        return bt.simulate_trade(rows, entry_i, mode)

    entry = rows[entry_i]["c"]
    max_profit = 0.0
    max_loss = 0.0
    partial_done = False
    partial_at = p["partial_at"]
    partial_size = p["partial_size"]
    runner_tp = p["runner_tp"]
    runner_stop = p["runner_stop"]
    time_stop_min = p["time"]

    for j in range(entry_i + 1, min(entry_i + time_stop_min + 1, len(rows))):
        held = j - entry_i
        r = rows[j]
        high_pct = bt.pct(r["h"], entry)
        low_pct = bt.pct(r["l"], entry)
        close_pct = bt.pct(r["c"], entry)
        max_profit = max(max_profit, high_pct)
        max_loss = min(max_loss, low_pct)

        if not partial_done and low_pct <= -bt.SL:
            return {"reason": "SL", "exit_pct": -bt.SL, "mfe": max_profit, "mae": max_loss, "held": held}

        if not partial_done and held >= bt.FAST_FAIL_MIN:
            if max_profit < bt.FAST_FAIL_MFE and close_pct <= bt.FAST_FAIL_PNL:
                return {"reason": "FAST_FAIL", "exit_pct": close_pct, "mfe": max_profit, "mae": max_loss, "held": held}

        if partial_done:
            if low_pct <= runner_stop:
                weighted = partial_size * partial_at + (1.0 - partial_size) * runner_stop
                return {"reason": "DYN_RUNNER_STOP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held}
            if high_pct >= runner_tp:
                weighted = partial_size * partial_at + (1.0 - partial_size) * runner_tp
                return {"reason": "DYN_RUNNER_TP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held}

        if not partial_done and high_pct >= partial_at:
            partial_done = True

    last_i = min(entry_i + time_stop_min, len(rows) - 1)
    close_pct = bt.pct(rows[last_i]["c"], entry)
    if partial_done:
        weighted = partial_size * partial_at + (1.0 - partial_size) * close_pct
        reason = "DYN_TIME_PARTIAL"
    else:
        weighted = close_pct
        reason = "TIME"
    return {"reason": reason, "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": last_i - entry_i}

def apply_confirmation(bt, symbol, rows, raw_signal, case):
    clean = symbol.replace("_USDT", "")
    blacklist = {x.strip().upper().replace("_USDT", "") for x in str(case.get("blacklist", "")).split(",") if x.strip()}
    if clean in blacklist:
        return None
    if raw_signal.get("score", -999) < case.get("min_score", -999):
        return None
    if raw_signal.get("price_change", 999.0) > case.get("max_pc", 999.0):
        return None
    if raw_signal.get("vol_ratio", 999.0) > case.get("max_vol", 999.0):
        return None

    i = raw_signal["i"]
    mode = case.get("confirm", "NONE").upper()
    if mode == "NONE":
        return dict(raw_signal)
    if i + 1 >= len(rows):
        return None

    sig = rows[i]
    n1 = rows[i + 1]
    sig_close = sig["c"]
    sig_high = sig["h"]
    if sig_close <= 0:
        return None

    n1_low_from_sig_close = bt.pct(n1["l"], sig_close)
    rug = case.get("rug", -0.20)
    entry_i = None

    if mode == "CLOSE_1":
        if n1["c"] > sig_close:
            entry_i = i + 1
    elif mode == "BREAK_HIGH_1":
        if n1["c"] > sig_high:
            entry_i = i + 1
    elif mode == "NO_RUG_CLOSE_1":
        if n1_low_from_sig_close > rug and n1["c"] > sig_close:
            entry_i = i + 1
    elif mode == "NO_RUG_BREAK_HIGH_1":
        if n1_low_from_sig_close > rug and n1["c"] > sig_high:
            entry_i = i + 1
    elif mode == "TWO_CLOSE":
        if i + 2 >= len(rows):
            return None
        n2 = rows[i + 2]
        if n1["c"] > sig_close and n2["c"] > n1["c"]:
            entry_i = i + 2
    elif mode == "PULLBACK_HOLD_BREAK":
        rng = sig["h"] - sig["l"]
        if rng <= 0:
            return None
        mid = sig["l"] + rng * 0.50
        if n1["l"] >= mid and n1["h"] > sig_high and n1["c"] > sig_close:
            entry_i = i + 1
    else:
        return dict(raw_signal)

    if entry_i is None:
        return None

    s = dict(raw_signal)
    s["original_signal_i"] = i
    s["original_signal_t"] = raw_signal["t"]
    s["confirm_case"] = case["case"]
    s["confirm_mode"] = mode
    s["confirm_delay_min"] = entry_i - i
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
    out = {"trades": 0, "wins": 0, "losses": 0, "gross": 0.0, "net": 0.0, "costs": 0.0,
           "avg_net": 0.0, "winrate": 0.0, "avg_mfe": 0.0, "avg_mae": 0.0,
           "skipped_by_maxopen": skipped_by_maxopen}
    reason_keys = ["TP", "SL", "TIME", "FAST_FAIL", "MICRO_LOCK", "BE_V2", "DYN_RUNNER_STOP", "DYN_RUNNER_TP", "DYN_TIME_PARTIAL"]
    for k in reason_keys:
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

def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

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

    strategies = parse_list_str(args.strategies) or STRATEGIES_DEFAULT
    modes = parse_list_str(args.modes) or DYN_MODES_DEFAULT
    max_open_values = parse_list_int(args.max_open) or [1, 2, 3]
    confirm_cases = CONFIRM_CASES_CORE if args.suite == "core" else CONFIRM_CASES_WIDE

    print(f"🚀 SKYNET MAX-OPEN SUITE | days={args.days} top={args.top} max_open={max_open_values}")
    print(f"Costs: spread={bt.SPREAD_BPS}bps slippage={bt.SLIPPAGE_BPS}bps")
    print(f"Strategies: {strategies}")
    print(f"Modes: {modes}")
    print(f"Confirm cases: {len(confirm_cases)}")

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

        raw_signals_by_symbol = {}
        rows_by_symbol = {}
        for idx, symbol in enumerate(symbols, 1):
            print(f"[{idx}/{len(symbols)}] {symbol} downloading/generating...")
            rows = await bt.download_klines(session, symbol, start_ts, end_ts, use_cache=not args.no_cache)
            if len(rows) < 200:
                print(f"  skip, candles={len(rows)}")
                continue
            raw = bt.generate_signals(symbol, rows, btc_close_by_t, btc_times)
            rows_by_symbol[symbol] = rows
            raw_signals_by_symbol[symbol] = raw
            print(f"  candles={len(rows)} raw_signals={len(raw)}")
            await asyncio.sleep(0.05)

    all_summary_rows = []
    all_trades_rows = []

    for case in confirm_cases:
        records_by_key = {}
        for symbol, raw_signals in raw_signals_by_symbol.items():
            rows = rows_by_symbol[symbol]
            for raw in raw_signals:
                s = apply_confirmation(bt, symbol, rows, raw, case)
                if not s:
                    continue
                for strategy in strategies:
                    if not bt.strategy_allows(strategy, s):
                        continue
                    for mode in modes:
                        result = simulate_dynamic(bt, rows, s["i"], mode)
                        exit_i = min(s["i"] + int(result["held"]), len(rows) - 1)
                        gross, net, costs = bt.calc_net_pnl(result["exit_pct"])
                        rec = {
                            "case": case["case"], "confirm": case["confirm"], "symbol": symbol,
                            "time": utc_iso(s["t"]), "entry_t": s["t"], "exit_t": rows[exit_i]["t"],
                            "strategy": strategy, "mode": mode,
                            "score": s.get("score", 0), "price_change": s.get("price_change", 0.0),
                            "vol_ratio": s.get("vol_ratio", 0.0), "trend15": s.get("trend15", 0.0),
                            "btc5": s.get("btc5", 0.0), "structure": s.get("structure", 0),
                            "initiative": s.get("initiative", 0), "reason": result["reason"],
                            "exit_pct": result["exit_pct"], "mfe": result["mfe"], "mae": result["mae"],
                            "held": result["held"], "gross": gross, "net": net, "costs": costs,
                        }
                        key = (case["case"], strategy, mode)
                        records_by_key.setdefault(key, []).append(rec)

        for (case_name, strategy, mode), records in records_by_key.items():
            for max_open in max_open_values:
                accepted, skipped = apply_max_open(records, max_open)
                sm = summarize(accepted, skipped)
                sm.update({"case": case_name, "strategy": strategy, "mode": mode, "max_open": max_open,
                           "days": args.days, "top": args.top,
                           "spread_bps": bt.SPREAD_BPS, "slippage_bps": bt.SLIPPAGE_BPS})
                all_summary_rows.append(sm)
                for r in accepted:
                    rr = dict(r)
                    rr["max_open"] = max_open
                    all_trades_rows.append(rr)
        print(f"✅ Case {case['case']} done")

    all_summary_rows.sort(key=lambda x: x["net"], reverse=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_DIR / f"maxopen_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / f"maxopen_summary_{stamp}.csv"
    trades_path = run_dir / f"maxopen_trades_{stamp}.csv"
    manifest_path = run_dir / "manifest.json"
    zip_path = run_dir / f"MAXOPEN_RESULTS_{stamp}.zip"

    summary_fields = ["case", "strategy", "mode", "max_open", "days", "top", "spread_bps", "slippage_bps",
                      "trades", "skipped_by_maxopen", "wins", "losses", "winrate", "gross", "net", "costs",
                      "avg_net", "avg_mfe", "avg_mae", "TP", "SL", "TIME", "FAST_FAIL", "MICRO_LOCK", "BE_V2",
                      "DYN_RUNNER_STOP", "DYN_RUNNER_TP", "DYN_TIME_PARTIAL"]
    trade_fields = ["case", "confirm", "max_open", "time", "symbol", "strategy", "mode", "score",
                    "price_change", "vol_ratio", "trend15", "btc5", "structure", "initiative",
                    "reason", "exit_pct", "mfe", "mae", "held", "gross", "net", "costs", "entry_t", "exit_t"]

    write_csv(summary_path, all_summary_rows, summary_fields)
    write_csv(trades_path, all_trades_rows, trade_fields)
    manifest = {
        "created_utc": stamp, "days": args.days, "top": args.top, "symbols": args.symbols,
        "max_open": max_open_values, "strategies": strategies, "modes": modes, "suite": args.suite,
        "spread_bps": bt.SPREAD_BPS, "slippage_bps": bt.SLIPPAGE_BPS,
        "confirm_cases": confirm_cases, "summary_file": summary_path.name, "trades_file": trades_path.name
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(summary_path, summary_path.name)
        z.write(trades_path, trades_path.name)
        z.write(manifest_path, manifest_path.name)

    print("\n=== TOP RESULTS ===")
    for r in all_summary_rows[:25]:
        print(f"{r['case']:<42} MO:{r['max_open']} {r['strategy']:<18} {r['mode']:<24} "
              f"Net:{r['net']:+.2f}$ Tr:{r['trades']} SkipMO:{r['skipped_by_maxopen']} "
              f"WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$")
    print("\nZIP:", zip_path)

    if args.send_tg:
        caption = (f"📦 SKYNET MAX-OPEN SUITE\n"
                   f"days={args.days} top={args.top} symbols={args.symbols or '-'}\n"
                   f"max_open={args.max_open} suite={args.suite}\n"
                   f"costs spread={bt.SPREAD_BPS} slip={bt.SLIPPAGE_BPS}")
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
    p.add_argument("--max-open", default="1,2,3")
    p.add_argument("--suite", choices=["core", "wide"], default="core")
    p.add_argument("--strategies", default=",".join(STRATEGIES_DEFAULT))
    p.add_argument("--modes", default=",".join(DYN_MODES_DEFAULT))
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
