import os
import csv
import json
import zipfile
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, deque
from dotenv import load_dotenv

load_dotenv("/root/skynet/.env")

ROOT = Path("/root/skynet")
OUT_DIR = ROOT / "data" / "backtest" / "smart_universe_v2_grid"
COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.0004"))

DEFAULT_FAMILIES = ["FILTERED_055"]
DEFAULT_GUARDS = ["CLEAN_EXEC", "OI0_CLEAN", "BTC0_CLEAN"]
DEFAULT_CONFIRMS = ["WAIT1_CLOSE"]

# V2 idea:
# CORE rank <= core_top: can trade normal guarded candidate.
# MID core_top+1..mid_top: trade only if symbol proves quality OR current signal is very strong.
# EXPLORE mid_top+1..top: never trade, only monitor outcomes to build future whitelist/blacklist.
# STATIC_TOP60/80/100 are included as baselines inside the same top150/top200 download.

V2_MODES = {
    "CORE_ONLY": {"desc": "rank <= core_top only"},
    "STATIC_TOP60": {"desc": "baseline static rank <= 60"},
    "STATIC_TOP80": {"desc": "baseline static rank <= 80"},
    "STATIC_TOP100": {"desc": "baseline static rank <= 100"},
    "V2_BALANCED": {
        "desc": "core + mid with quality or strong cold signal; explore monitor-only",
        "cold_policy": "strong",
        "min_obs": 2,
        "min_avg_net": -0.02,
        "max_sl_rate": 0.60,
        "min_avg_mfe": 0.35,
        "max_bad_streak": 2,
        "cooldown_hours": 12,
    },
    "V2_STRICT": {
        "desc": "core + mid strict whitelist; explore monitor-only",
        "cold_policy": "ultra",
        "min_obs": 2,
        "min_avg_net": 0.00,
        "max_sl_rate": 0.55,
        "min_avg_mfe": 0.45,
        "max_bad_streak": 1,
        "cooldown_hours": 24,
    },
    "V2_AGGRESSIVE": {
        "desc": "core + mid allows clean cold signals; explore monitor-only",
        "cold_policy": "clean",
        "min_obs": 2,
        "min_avg_net": -0.05,
        "max_sl_rate": 0.65,
        "min_avg_mfe": 0.30,
        "max_bad_streak": 2,
        "cooldown_hours": 8,
    },
    "V2_WHITELIST": {
        "desc": "core + mid only proven whitelist, except ultra cold; explore monitor-only",
        "cold_policy": "ultra",
        "min_obs": 3,
        "min_avg_net": 0.02,
        "max_sl_rate": 0.50,
        "min_avg_mfe": 0.50,
        "max_bad_streak": 1,
        "cooldown_hours": 24,
    },
}


def parse_target(value):
    value = str(value).strip()
    if value.startswith("-") and value[1:].isdigit():
        return int(value)
    if value.isdigit():
        return int(value)
    return value


def parse_list_int(s):
    return [int(x.strip()) for x in str(s).split(",") if x.strip()]


def parse_list_str(s, default):
    if not s:
        return default
    return [x.strip().upper() for x in str(s).split(",") if x.strip()]


def utc_iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def calc_net(margin, leverage, exit_pct, spread_bps, slippage_bps):
    notional = margin * leverage
    gross = notional * (exit_pct / 100.0)
    commission = notional * COMMISSION_RATE * 2
    spread = notional * (spread_bps / 10000.0)
    slippage = notional * (slippage_bps / 10000.0) * 2
    costs = commission + spread + slippage
    return gross, gross - costs, costs


def clean_candidate(e):
    return (
        e.get("score", 0) >= 4
        and e.get("btc5", -999) >= -0.05
        and e.get("oi", -999) >= -0.50
        and e.get("structure", 999) <= 2
        and e.get("breakout_risk_score", 999) <= 4
        and e.get("false_breakouts_15m", 999) <= 3
    )


def strong_candidate(e):
    return (
        e.get("score", 0) >= 5
        and e.get("btc5", -999) >= 0.0
        and e.get("oi", -999) >= 0.0
        and e.get("structure", 999) <= 1
        and e.get("breakout_risk_score", 999) <= 3
        and e.get("false_breakouts_15m", 999) <= 1
    )


def ultra_candidate(e):
    return (
        e.get("score", 0) >= 6
        and e.get("btc5", -999) >= 0.10
        and e.get("oi", -999) >= 0.50
        and e.get("structure", 999) <= 1
        and e.get("breakout_risk_score", 999) <= 2
        and e.get("false_breakouts_15m", 999) <= 1
        and e.get("price_change", 999) <= 0.65
    )


class SymbolQuality:
    def __init__(self, maxlen=10):
        self.items = deque(maxlen=maxlen)
        self.bad_streak = 0
        self.cooldown_until = 0

    def update(self, e, params):
        net = e["net"]
        mfe = e["mfe"]
        reason = e["reason"]

        bad = (reason == "SL" and mfe < 0.25) or (net < 0 and mfe < 0.20)
        good = net > 0

        if bad:
            self.bad_streak += 1
            if self.bad_streak >= params.get("max_bad_streak", 2):
                self.cooldown_until = e["exit_t"] + int(params.get("cooldown_hours", 12) * 3600)
        elif good:
            self.bad_streak = max(0, self.bad_streak - 1)

        self.items.append({
            "net": net,
            "mfe": mfe,
            "reason": reason,
            "bad": bad,
            "good": good,
        })

    def features(self):
        n = len(self.items)
        if n == 0:
            return {
                "obs": 0,
                "avg_net": 0.0,
                "avg_mfe": 0.0,
                "sl_rate": 0.0,
                "good_rate": 0.0,
                "bad_streak": self.bad_streak,
                "cooldown_until": self.cooldown_until,
            }

        avg_net = sum(x["net"] for x in self.items) / n
        avg_mfe = sum(x["mfe"] for x in self.items) / n
        sl_rate = sum(1 for x in self.items if x["reason"] == "SL") / n
        good_rate = sum(1 for x in self.items if x["good"]) / n

        return {
            "obs": n,
            "avg_net": avg_net,
            "avg_mfe": avg_mfe,
            "sl_rate": sl_rate,
            "good_rate": good_rate,
            "bad_streak": self.bad_streak,
            "cooldown_until": self.cooldown_until,
        }


def v2_allow(e, mode_name, params, quality, core_top, mid_top):
    rank = int(e.get("rank", 999999))

    if mode_name == "CORE_ONLY":
        return (rank <= core_top), "CORE" if rank <= core_top else "OUTSIDE_CORE"

    if mode_name == "STATIC_TOP60":
        return (rank <= 60), "STATIC_TOP60" if rank <= 60 else "OUTSIDE_TOP60"

    if mode_name == "STATIC_TOP80":
        return (rank <= 80), "STATIC_TOP80" if rank <= 80 else "OUTSIDE_TOP80"

    if mode_name == "STATIC_TOP100":
        return (rank <= 100), "STATIC_TOP100" if rank <= 100 else "OUTSIDE_TOP100"

    # V2 smart modes.
    if rank <= core_top:
        return True, "CORE"

    # explore zone is monitor-only: no real/paper entry, but outcome still updates quality.
    if rank > mid_top:
        return False, "EXPLORE_MONITOR_ONLY"

    q = quality.features()

    if q["cooldown_until"] and e["entry_t"] < q["cooldown_until"]:
        if ultra_candidate(e):
            return True, "COOLDOWN_ULTRA_OVERRIDE"
        return False, "COOLDOWN"

    if q["bad_streak"] >= params.get("max_bad_streak", 2):
        if ultra_candidate(e):
            return True, "BAD_STREAK_ULTRA_OVERRIDE"
        return False, "BAD_STREAK"

    # Cold symbol: do not spend money learning on weak signals.
    if q["obs"] < params.get("min_obs", 2):
        policy = params.get("cold_policy", "strong")
        if policy == "clean" and clean_candidate(e):
            return True, "MID_COLD_CLEAN"
        if policy == "strong" and strong_candidate(e):
            return True, "MID_COLD_STRONG"
        if policy == "ultra" and ultra_candidate(e):
            return True, "MID_COLD_ULTRA"
        return False, "MID_COLD_REJECT"

    quality_ok = (
        q["avg_net"] >= params.get("min_avg_net", 0.0)
        and q["sl_rate"] <= params.get("max_sl_rate", 0.60)
        and q["avg_mfe"] >= params.get("min_avg_mfe", 0.35)
        and clean_candidate(e)
    )

    if quality_ok:
        return True, "MID_QUALITY_OK"

    # Strong current signal can override mediocre quality, but not awful quality.
    if strong_candidate(e) and q["sl_rate"] <= min(0.75, params.get("max_sl_rate", 0.60) + 0.15):
        return True, "MID_STRONG_OVERRIDE"

    return False, "MID_QUALITY_REJECT"


def apply_max_open(records, max_open):
    open_until = []
    accepted = []
    skipped = 0

    for r in records:
        t = r["entry_t"]
        open_until = [x for x in open_until if x > t]
        if len(open_until) >= max_open:
            skipped += 1
            continue
        accepted.append(r)
        open_until.append(r["exit_t"])

    return accepted, skipped


def summarize(records, skipped_by_maxopen, rejects):
    out = {
        "trades": 0, "wins": 0, "losses": 0,
        "gross": 0.0, "net": 0.0, "costs": 0.0,
        "avg_net": 0.0, "winrate": 0.0,
        "avg_mfe": 0.0, "avg_mae": 0.0,
        "skipped_by_maxopen": skipped_by_maxopen,
        "smart_rejects": rejects,
    }
    for k in ["SL", "TIME", "TIME_PARTIAL", "RUNNER_STOP", "RUNNER_TP"]:
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
        out["avg_mfe"] /= n
        out["avg_mae"] /= n
    return out


def rolling_eval(events, mode_name, params, core_top, mid_top, max_open):
    quality = defaultdict(SymbolQuality)
    pending_updates = []
    accepted_raw = []
    rejects = 0
    allow_counts = defaultdict(int)
    reject_counts = defaultdict(int)

    events = sorted(events, key=lambda x: (x["entry_t"], x["symbol"]))

    for e in events:
        t = e["entry_t"]

        ready = [x for x in pending_updates if x["exit_t"] <= t]
        pending_updates = [x for x in pending_updates if x["exit_t"] > t]

        for u in ready:
            quality[u["symbol"]].update(u, params)

        allow, reason = v2_allow(e, mode_name, params, quality[e["symbol"]], core_top, mid_top)

        # Always monitor outcome for symbol passport learning.
        pending_updates.append(e)

        if not allow:
            rejects += 1
            reject_counts[reason] += 1
            continue

        allow_counts[reason] += 1
        rr = dict(e)
        rr["smart_mode"] = mode_name
        rr["smart_reason"] = reason
        accepted_raw.append(rr)

    accepted, skipped = apply_max_open(accepted_raw, max_open)
    sm = summarize(accepted, skipped, rejects)
    return sm, accepted, dict(allow_counts), dict(reject_counts)


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
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
    import aiohttp
    import backtest_1m as bt
    import backtest_hybrid_harvest_grid as hh

    max_open_values = parse_list_int(args.max_open)
    families = parse_list_str(args.families, DEFAULT_FAMILIES)
    guards = parse_list_str(args.guards, DEFAULT_GUARDS)
    confirms = parse_list_str(args.confirms, DEFAULT_CONFIRMS)
    modes = parse_list_str(args.modes, list(V2_MODES.keys()))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.end:
        end_ts = int(datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc).timestamp())
    else:
        end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = end_ts - args.days * 24 * 3600

    print(f"🚀 SKYNET SMART UNIVERSE V2 GRID | days={args.days} top={args.top} core={args.core_top} mid={args.mid_top}")
    print(f"Margin=${args.margin} lev={args.leverage}x notional=${args.margin * args.leverage:.2f}")
    print(f"Costs: spread={args.spread_bps}bps slippage={args.slippage_bps}bps commission={COMMISSION_RATE}")
    print(f"Families={families}")
    print(f"Guards={guards}")
    print(f"Confirms={confirms}")
    print(f"Modes={modes}")

    async with aiohttp.ClientSession() as session:
        if args.symbols:
            symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
            symbols = [s if s.endswith("_USDT") else f"{s}_USDT" for s in symbols]
        else:
            symbols = await bt.get_top_symbols(session, args.top)

        symbols = [s for s in symbols if s != "BTC_USDT"]
        rank_by_symbol = {s: i + 1 for i, s in enumerate(symbols)}

        print(f"Symbols: {len(symbols)}")
        print("Downloading BTC context...")
        btc_rows = await bt.download_klines(session, "BTC_USDT", start_ts, end_ts, use_cache=not args.no_cache)
        btc_close_by_t, btc_times = bt.prepare_btc_context(btc_rows)

        events_by_combo = defaultdict(list)
        symbol_event_counts = defaultdict(int)

        for idx, symbol in enumerate(symbols, 1):
            print(f"[{idx}/{len(symbols)}] {symbol} downloading/generating...")
            rows = await bt.download_klines(session, symbol, start_ts, end_ts, use_cache=not args.no_cache)
            if len(rows) < 200:
                print(f"  skip candles={len(rows)}")
                continue

            raw_signals = bt.generate_signals(symbol, rows, btc_close_by_t, btc_times)
            print(f"  candles={len(rows)} raw_signals={len(raw_signals)}")

            for raw in raw_signals:
                s = hh.enrich_raw(rows, raw)
                if not s:
                    continue

                for family in families:
                    if not hh.family_rule(family, s):
                        continue

                    for guard in guards:
                        if not hh.guard_rule(guard, s):
                            continue

                        for confirm in confirms:
                            entry = hh.apply_confirm(bt, rows, s, confirm)
                            if not entry:
                                continue

                            entry_i = entry["entry_i"]
                            result = hh.simulate_atr5b(bt, rows, entry_i)
                            exit_i = min(entry_i + int(result["held"]), len(rows) - 1)
                            gross, net, costs = calc_net(
                                args.margin,
                                args.leverage,
                                result["exit_pct"],
                                args.spread_bps,
                                args.slippage_bps,
                            )

                            combo = f"{family}|{guard}|{confirm}"
                            e = {
                                "combo": combo,
                                "family": family,
                                "guard": guard,
                                "confirm": confirm,
                                "symbol": symbol,
                                "clean_symbol": symbol.replace("_USDT", ""),
                                "rank": rank_by_symbol.get(symbol, 999999),
                                "time": utc_iso(entry["entry_t"]),
                                "entry_t": entry["entry_t"],
                                "exit_t": rows[exit_i]["t"],
                                "score": entry["score"],
                                "price_change": entry["price_change"],
                                "vol_ratio": entry["vol_ratio"],
                                "trend15": entry["trend15"],
                                "btc5": entry["btc5"],
                                "oi": entry["oi"],
                                "structure": entry["structure"],
                                "initiative": entry["initiative"],
                                "confirm_move_pct": entry.get("confirm_move_pct", 0.0),
                                "breakout_risk_score": entry.get("breakout_risk_score", 0),
                                "false_breakouts_15m": entry.get("false_breakouts_15m", 0),
                                "red_volume_share_10m": entry.get("red_volume_share_10m", 0.0),
                                "ema9_slope_3m_pct": entry.get("ema9_slope_3m_pct", 0.0),
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
                            events_by_combo[combo].append(e)
                            symbol_event_counts[symbol] += 1

            await asyncio.sleep(0.03)

    summaries = []
    accepted_sample = []
    reason_rows = []

    for combo, events in events_by_combo.items():
        family, guard, confirm = combo.split("|")
        print(f"Combo {combo}: candidates={len(events)}")

        for mode_name in modes:
            if mode_name not in V2_MODES:
                continue

            params = dict(V2_MODES[mode_name])

            for mo in max_open_values:
                sm, accepted, allow_counts, reject_counts = rolling_eval(
                    events,
                    mode_name,
                    params,
                    int(args.core_top),
                    int(args.mid_top),
                    mo,
                )

                sm.update({
                    "combo": combo,
                    "family": family,
                    "guard": guard,
                    "confirm": confirm,
                    "smart_mode": mode_name,
                    "mode_desc": params.get("desc", ""),
                    "core_top": args.core_top,
                    "mid_top": args.mid_top,
                    "max_open": mo,
                    "days": args.days,
                    "top": args.top,
                    "margin": args.margin,
                    "leverage": args.leverage,
                    "notional": args.margin * args.leverage,
                    "spread_bps": args.spread_bps,
                    "slippage_bps": args.slippage_bps,
                    "monthly_pct_on_40": sm["net"] / 40.0 * 100.0,
                })
                summaries.append(sm)

                for r in accepted[:400]:
                    rr = dict(r)
                    rr["smart_mode"] = mode_name
                    rr["max_open"] = mo
                    accepted_sample.append(rr)

                for reason, cnt in allow_counts.items():
                    reason_rows.append({
                        "type": "ALLOW",
                        "combo": combo,
                        "smart_mode": mode_name,
                        "max_open": mo,
                        "reason": reason,
                        "count": cnt,
                    })
                for reason, cnt in reject_counts.items():
                    reason_rows.append({
                        "type": "REJECT",
                        "combo": combo,
                        "smart_mode": mode_name,
                        "max_open": mo,
                        "reason": reason,
                        "count": cnt,
                    })

    summaries.sort(key=lambda x: (x["net"], x["trades"]), reverse=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_DIR / f"smart_universe_v2_grid_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / f"smart_universe_v2_summary_{stamp}.csv"
    sample_path = run_dir / f"smart_universe_v2_accepted_sample_{stamp}.csv"
    reasons_path = run_dir / f"smart_universe_v2_reason_counts_{stamp}.csv"
    symbols_path = run_dir / f"smart_universe_v2_symbol_candidate_counts_{stamp}.csv"
    manifest_path = run_dir / "manifest.json"
    zip_path = run_dir / f"SMART_UNIVERSE_V2_GRID_RESULTS_{stamp}.zip"

    summary_fields = [
        "combo", "family", "guard", "confirm", "smart_mode", "mode_desc",
        "core_top", "mid_top", "max_open", "days", "top",
        "margin", "leverage", "notional", "spread_bps", "slippage_bps",
        "trades", "smart_rejects", "skipped_by_maxopen",
        "wins", "losses", "winrate", "gross", "net", "costs", "avg_net",
        "monthly_pct_on_40", "avg_mfe", "avg_mae",
        "SL", "TIME", "TIME_PARTIAL", "RUNNER_STOP", "RUNNER_TP",
    ]
    sample_fields = [
        "combo", "smart_mode", "max_open", "smart_reason", "time", "symbol", "rank",
        "score", "price_change", "vol_ratio", "trend15", "btc5", "oi", "structure",
        "initiative", "confirm_move_pct", "breakout_risk_score", "false_breakouts_15m",
        "reason", "exit_pct", "mfe", "mae", "held", "net", "costs", "entry_t", "exit_t",
    ]
    reason_fields = ["type", "combo", "smart_mode", "max_open", "reason", "count"]

    write_csv(summary_path, summaries, summary_fields)
    write_csv(sample_path, accepted_sample, sample_fields)
    write_csv(reasons_path, reason_rows, reason_fields)
    write_csv(
        symbols_path,
        [{"symbol": s, "candidate_events": c} for s, c in sorted(symbol_event_counts.items(), key=lambda x: x[1], reverse=True)],
        ["symbol", "candidate_events"],
    )

    manifest = {
        "created_utc": stamp,
        "suite": "SMART_UNIVERSE_V2_GRID",
        "days": args.days,
        "top": args.top,
        "core_top": args.core_top,
        "mid_top": args.mid_top,
        "margin": args.margin,
        "leverage": args.leverage,
        "spread_bps": args.spread_bps,
        "slippage_bps": args.slippage_bps,
        "families": families,
        "guards": guards,
        "confirms": confirms,
        "modes": modes,
        "max_open": max_open_values,
        "v2_modes": V2_MODES,
        "notes": "Rank > mid_top is explore-monitor-only in V2 smart modes. Symbol quality updates only after hypothetical exit_t <= current signal time.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in [summary_path, sample_path, reasons_path, symbols_path, manifest_path]:
            z.write(p, p.name)

    print("\n=== TOP SMART UNIVERSE V2 RESULTS ===")
    for r in summaries[:70]:
        print(
            f"{r['combo']:<42} {r['smart_mode']:<13} MO:{r['max_open']} "
            f"Net:{r['net']:+.2f}$ On40:{r['monthly_pct_on_40']:+.1f}% "
            f"Tr:{r['trades']} WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$ "
            f"SL:{r['SL']} PTP:{r['TIME_PARTIAL'] + r['RUNNER_STOP'] + r['RUNNER_TP']} "
            f"Reject:{r['smart_rejects']}"
        )

    print("\nZIP:", zip_path)

    if args.send_tg:
        caption = (
            f"📦 SKYNET SMART UNIVERSE V2 GRID\n"
            f"days={args.days} top={args.top} core={args.core_top} mid={args.mid_top} "
            f"margin={args.margin} lev={args.leverage}x\n"
            f"spread={args.spread_bps} slip={args.slippage_bps}"
        )
        try:
            await send_to_tg(zip_path, caption, args.tg_target)
            print("📤 Sent to Telegram")
        except Exception as e:
            print(f"⚠️ Telegram send failed: {type(e).__name__}: {e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--top", type=int, default=150)
    p.add_argument("--core-top", type=int, default=30)
    p.add_argument("--mid-top", type=int, default=70)
    p.add_argument("--symbols", default="")
    p.add_argument("--max-open", default="1,2")
    p.add_argument("--margin", type=float, default=3.0)
    p.add_argument("--leverage", type=int, default=10)
    p.add_argument("--spread-bps", type=float, default=2.0)
    p.add_argument("--slippage-bps", type=float, default=3.0)
    p.add_argument("--families", default="")
    p.add_argument("--guards", default="")
    p.add_argument("--confirms", default="")
    p.add_argument("--modes", default="")
    p.add_argument("--end", default=None)
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--send-tg", action="store_true")
    p.add_argument("--tg-target", default=os.getenv("TG_TARGET", "-1002953234396"))
    args = p.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
