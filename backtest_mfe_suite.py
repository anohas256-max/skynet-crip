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
# SKYNET MFE SUITE
#
# Purpose:
# - Test whether we can loosen entry filters and rely more on early MFE behavior.
# - Historical/candle-only test. No real trading. Does not touch skynet_main.py.
#
# Requires:
#   /root/skynet/backtest_1m.py
#
# Main idea:
# - MFE is NOT used before entry. That would be future leak.
# - MFE is used only after entry:
#     fast validate after 1-2 candles,
#     micro-lock after MFE reaches +0.30/+0.40,
#     partial-runner after +0.80.
# ============================================================

load_dotenv("/root/skynet/.env")

ROOT = Path("/root/skynet")
OUT_DIR = ROOT / "data" / "backtest" / "mfe_suite"

ENTRY_CASES_CORE = [
    # Baseline from the first plus direction.
    {
        "entry_case": "CONFIRM_INIT_SCORE5_PC055_VOL25_RUG015",
        "confirm": "NO_RUG_CLOSE_1",
        "rug": -0.15,
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.55,
        "max_vol": 25.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    # Slightly looser price/volume.
    {
        "entry_case": "CONFIRM_INIT_SCORE5_PC065_VOL35_RUG015",
        "confirm": "NO_RUG_CLOSE_1",
        "rug": -0.15,
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    # Looser score, still initiative + confirmation.
    {
        "entry_case": "CONFIRM_INIT_SCORE4_PC065_VOL35_RUG015",
        "confirm": "NO_RUG_CLOSE_1",
        "rug": -0.15,
        "min_score": 4,
        "need_initiative": 1,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    # No initiative requirement: tests whether MFE guard can clean wider main-like signals.
    {
        "entry_case": "CONFIRM_MAIN_SCORE5_PC065_VOL35_RUG015",
        "confirm": "NO_RUG_CLOSE_1",
        "rug": -0.15,
        "min_score": 5,
        "need_initiative": 0,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    # Immediate initiative: tests loosening confirmation and relying on MFE management.
    {
        "entry_case": "IMMEDIATE_INIT_SCORE5_PC065_VOL35",
        "confirm": "NONE",
        "rug": -0.15,
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    # Immediate wider main-like: dangerous, but useful diagnostic.
    {
        "entry_case": "IMMEDIATE_MAIN_SCORE5_PC065_VOL35",
        "confirm": "NONE",
        "rug": -0.15,
        "min_score": 5,
        "need_initiative": 0,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
]

ENTRY_CASES_WIDE = ENTRY_CASES_CORE + [
    {
        "entry_case": "CONFIRM_INIT_SCORE5_PC075_VOL45_RUG020",
        "confirm": "NO_RUG_CLOSE_1",
        "rug": -0.20,
        "min_score": 5,
        "need_initiative": 1,
        "max_pc": 0.75,
        "max_vol": 45.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    {
        "entry_case": "CONFIRM_MAIN_SCORE4_PC065_VOL35_RUG015",
        "confirm": "NO_RUG_CLOSE_1",
        "rug": -0.15,
        "min_score": 4,
        "need_initiative": 0,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    {
        "entry_case": "IMMEDIATE_INIT_SCORE4_PC065_VOL35",
        "confirm": "NONE",
        "rug": -0.15,
        "min_score": 4,
        "need_initiative": 1,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
    {
        "entry_case": "IMMEDIATE_MAIN_SCORE4_PC065_VOL35",
        "confirm": "NONE",
        "rug": -0.15,
        "min_score": 4,
        "need_initiative": 0,
        "max_pc": 0.65,
        "max_vol": 35.0,
        "min_trend15": -999.0,
        "min_btc5": -999.0,
    },
]

EXIT_MODES = [
    # Previous best dynamic exit: partial 50% at +0.8, runner to +2.0, runner stop +0.10.
    "DYN08_BASE",
    # Add early MFE validation.
    "MFE_1M_010_NEG010_DYN08",
    "MFE_2M_020_ANY_DYN08",
    "MFE_2M_030_ANY_DYN08",
    # Add micro-lock once trade proves minimum MFE.
    "LOCK030_DYN08",
    "LOCK040_DYN08",
    # Combined: early validation + lock.
    "MFE_1M_010_NEG010_LOCK030_DYN08",
    "MFE_2M_020_ANY_LOCK030_DYN08",
]

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

def parse_list_str(s):
    return [x.strip() for x in str(s).split(",") if x.strip()]

def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

def apply_entry_case(bt, symbol, rows, raw_signal, case):
    if raw_signal.get("score", -999) < case["min_score"]:
        return None
    if case["need_initiative"] and not raw_signal.get("initiative", 0):
        return None
    if raw_signal.get("price_change", 999.0) > case["max_pc"]:
        return None
    if raw_signal.get("vol_ratio", 999.0) > case["max_vol"]:
        return None
    if raw_signal.get("trend15", 0.0) < case["min_trend15"]:
        return None
    if raw_signal.get("btc5", 0.0) < case["min_btc5"]:
        return None

    i = raw_signal["i"]
    confirm = case["confirm"].upper()

    if confirm == "NONE":
        s = dict(raw_signal)
        s["entry_case"] = case["entry_case"]
        s["confirm_delay_min"] = 0
        return s

    if i + 1 >= len(rows):
        return None

    sig = rows[i]
    n1 = rows[i + 1]
    sig_close = sig["c"]
    sig_high = sig["h"]

    if sig_close <= 0:
        return None

    low_from_sig_close = bt.pct(n1["l"], sig_close)
    entry_i = None

    if confirm == "NO_RUG_CLOSE_1":
        if low_from_sig_close > case["rug"] and n1["c"] > sig_close:
            entry_i = i + 1

    elif confirm == "CLOSE_1":
        if n1["c"] > sig_close:
            entry_i = i + 1

    elif confirm == "BREAK_HIGH_1":
        if n1["c"] > sig_high:
            entry_i = i + 1

    else:
        return None

    if entry_i is None:
        return None

    s = dict(raw_signal)
    s["original_signal_i"] = i
    s["original_signal_t"] = raw_signal["t"]
    s["entry_case"] = case["entry_case"]
    s["confirm_mode"] = confirm
    s["confirm_delay_min"] = entry_i - i
    s["i"] = entry_i
    s["t"] = rows[entry_i]["t"]
    s["entry"] = rows[entry_i]["c"]
    return s

def exit_params(mode):
    params = {
        "partial_at": 0.80,
        "partial_size": 0.50,
        "runner_tp": 2.00,
        "runner_stop": 0.10,
        "time": 35,
        "mfe_guard": None,
        "lock_trigger": None,
        "lock_stop": 0.00,
    }

    if "MFE_1M_010_NEG010" in mode:
        params["mfe_guard"] = {"held": 1, "mfe_lt": 0.10, "close_lte": -0.10}
    elif "MFE_2M_020_ANY" in mode:
        params["mfe_guard"] = {"held": 2, "mfe_lt": 0.20, "close_lte": None}
    elif "MFE_2M_030_ANY" in mode:
        params["mfe_guard"] = {"held": 2, "mfe_lt": 0.30, "close_lte": None}

    if "LOCK030" in mode:
        params["lock_trigger"] = 0.30
    elif "LOCK040" in mode:
        params["lock_trigger"] = 0.40

    return params

def simulate_mfe_exit(bt, rows, entry_i, mode):
    p = exit_params(mode)
    entry = rows[entry_i]["c"]

    max_profit = 0.0
    max_loss = 0.0
    partial_done = False
    lock_armed = False

    for j in range(entry_i + 1, min(entry_i + p["time"] + 1, len(rows))):
        held = j - entry_i
        r = rows[j]
        high_pct = bt.pct(r["h"], entry)
        low_pct = bt.pct(r["l"], entry)
        close_pct = bt.pct(r["c"], entry)

        max_profit = max(max_profit, high_pct)
        max_loss = min(max_loss, low_pct)

        # Full SL before partial. Conservative intrabar ordering.
        if not partial_done and low_pct <= -bt.SL:
            return {"reason": "SL", "exit_pct": -bt.SL, "mfe": max_profit, "mae": max_loss, "held": held}

        # Early MFE validation guard.
        g = p["mfe_guard"]
        if g and not partial_done and held >= g["held"]:
            if max_profit < g["mfe_lt"]:
                if g["close_lte"] is None or close_pct <= g["close_lte"]:
                    return {"reason": "MFE_GUARD", "exit_pct": close_pct, "mfe": max_profit, "mae": max_loss, "held": held}

        # Arm lock only after proven MFE.
        if p["lock_trigger"] is not None and not lock_armed and max_profit >= p["lock_trigger"]:
            lock_armed = True

        # Micro lock before partial.
        if not partial_done and lock_armed and low_pct <= p["lock_stop"]:
            return {"reason": "MFE_LOCK", "exit_pct": p["lock_stop"], "mfe": max_profit, "mae": max_loss, "held": held}

        # Runner rules after partial.
        if partial_done:
            if low_pct <= p["runner_stop"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_stop"]
                return {"reason": "DYN_RUNNER_STOP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held}
            if high_pct >= p["runner_tp"]:
                weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * p["runner_tp"]
                return {"reason": "DYN_RUNNER_TP", "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": held}

        # Arm partial.
        if not partial_done and high_pct >= p["partial_at"]:
            partial_done = True

    last_i = min(entry_i + p["time"], len(rows) - 1)
    close_pct = bt.pct(rows[last_i]["c"], entry)

    if partial_done:
        weighted = p["partial_size"] * p["partial_at"] + (1.0 - p["partial_size"]) * close_pct
        reason = "DYN_TIME_PARTIAL"
    else:
        weighted = close_pct
        reason = "TIME"

    return {"reason": reason, "exit_pct": weighted, "mfe": max_profit, "mae": max_loss, "held": last_i - entry_i}

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

    reason_keys = [
        "SL", "TIME", "MFE_GUARD", "MFE_LOCK",
        "DYN_RUNNER_STOP", "DYN_RUNNER_TP", "DYN_TIME_PARTIAL"
    ]
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
    exit_modes = parse_list_str(args.exit_modes) or EXIT_MODES
    entry_cases = ENTRY_CASES_CORE if args.suite == "core" else ENTRY_CASES_WIDE

    print(f"🚀 SKYNET MFE SUITE | days={args.days} top={args.top} max_open={max_open_values} suite={args.suite}")
    print(f"Costs: spread={bt.SPREAD_BPS}bps slippage={bt.SLIPPAGE_BPS}bps")
    print(f"Entry cases: {len(entry_cases)} | Exit modes: {exit_modes}")

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

    all_summary = []
    all_trades = []

    for case in entry_cases:
        records_by_key = {}

        for symbol, raw_signals in raw_signals_by_symbol.items():
            rows = rows_by_symbol[symbol]

            for raw in raw_signals:
                s = apply_entry_case(bt, symbol, rows, raw, case)
                if not s:
                    continue

                for exit_mode in exit_modes:
                    result = simulate_mfe_exit(bt, rows, s["i"], exit_mode)
                    exit_i = min(s["i"] + int(result["held"]), len(rows) - 1)
                    gross, net, costs = bt.calc_net_pnl(result["exit_pct"])

                    rec = {
                        "entry_case": case["entry_case"],
                        "confirm": case["confirm"],
                        "symbol": symbol,
                        "time": utc_iso(s["t"]),
                        "entry_t": s["t"],
                        "exit_t": rows[exit_i]["t"],
                        "exit_mode": exit_mode,
                        "score": s.get("score", 0),
                        "price_change": s.get("price_change", 0.0),
                        "vol_ratio": s.get("vol_ratio", 0.0),
                        "trend15": s.get("trend15", 0.0),
                        "btc5": s.get("btc5", 0.0),
                        "structure": s.get("structure", 0),
                        "initiative": s.get("initiative", 0),
                        "confirm_delay_min": s.get("confirm_delay_min", 0),
                        "reason": result["reason"],
                        "exit_pct": result["exit_pct"],
                        "mfe": result["mfe"],
                        "mae": result["mae"],
                        "held": result["held"],
                        "gross": gross,
                        "net": net,
                        "costs": costs,
                    }
                    key = (case["entry_case"], exit_mode)
                    records_by_key.setdefault(key, []).append(rec)

        for (entry_case, exit_mode), records in records_by_key.items():
            for max_open in max_open_values:
                accepted, skipped = apply_max_open(records, max_open)
                sm = summarize(accepted, skipped)
                sm.update({
                    "entry_case": entry_case,
                    "exit_mode": exit_mode,
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

        print(f"✅ Entry case done: {case['entry_case']}")

    all_summary.sort(key=lambda x: x["net"], reverse=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_DIR / f"mfe_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / f"mfe_summary_{stamp}.csv"
    trades_path = run_dir / f"mfe_trades_{stamp}.csv"
    manifest_path = run_dir / "manifest.json"
    zip_path = run_dir / f"MFE_RESULTS_{stamp}.zip"

    summary_fields = [
        "entry_case", "exit_mode", "max_open", "days", "top", "spread_bps", "slippage_bps",
        "trades", "skipped_by_maxopen", "wins", "losses", "winrate",
        "gross", "net", "costs", "avg_net", "avg_mfe", "avg_mae",
        "SL", "TIME", "MFE_GUARD", "MFE_LOCK", "DYN_RUNNER_STOP", "DYN_RUNNER_TP", "DYN_TIME_PARTIAL"
    ]
    trade_fields = [
        "entry_case", "confirm", "max_open", "time", "symbol", "exit_mode",
        "score", "price_change", "vol_ratio", "trend15", "btc5", "structure", "initiative", "confirm_delay_min",
        "reason", "exit_pct", "mfe", "mae", "held", "gross", "net", "costs",
        "entry_t", "exit_t"
    ]

    write_csv(summary_path, all_summary, summary_fields)
    write_csv(trades_path, all_trades, trade_fields)

    manifest = {
        "created_utc": stamp,
        "days": args.days,
        "top": args.top,
        "symbols": args.symbols,
        "max_open": max_open_values,
        "suite": args.suite,
        "exit_modes": exit_modes,
        "spread_bps": bt.SPREAD_BPS,
        "slippage_bps": bt.SLIPPAGE_BPS,
        "entry_cases": entry_cases,
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
            f"{r['entry_case']:<45} MO:{r['max_open']} {r['exit_mode']:<32} "
            f"Net:{r['net']:+.2f}$ Tr:{r['trades']} SkipMO:{r['skipped_by_maxopen']} "
            f"WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$"
        )

    print("\nZIP:", zip_path)

    if args.send_tg:
        caption = (
            f"📦 SKYNET MFE SUITE\n"
            f"days={args.days} top={args.top} symbols={args.symbols or '-'}\n"
            f"max_open={args.max_open} suite={args.suite}\n"
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
    p.add_argument("--max-open", default="1,2,3")
    p.add_argument("--suite", choices=["core", "wide"], default="core")
    p.add_argument("--exit-modes", default=",".join(EXIT_MODES))
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
