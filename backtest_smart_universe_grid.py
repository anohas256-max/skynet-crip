import os
import csv
import json
import zipfile
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from collections import deque, defaultdict
from dotenv import load_dotenv

load_dotenv("/root/skynet/.env")

ROOT = Path("/root/skynet")
OUT_DIR = ROOT / "data" / "backtest" / "smart_universe_grid"
COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.0004"))

DEFAULT_FAMILIES = ["FILTERED_055"]
DEFAULT_GUARDS = ["CLEAN_EXEC", "OI0_CLEAN", "BTC0_CLEAN"]
DEFAULT_CONFIRMS = ["WAIT1_CLOSE"]

SMART_MODES = {
    "STATIC_ALL": {
        "desc": "no smart filtering inside downloaded topN",
        "core_top": 999999,
        "cold": "allow",
        "min_avg_net": -999.0,
        "max_sl_rate": 1.0,
        "max_bad_streak": 999,
        "min_avg_mfe": 0.0,
        "cooldown_hours": 0,
    },
    "CORE_ONLY": {
        "desc": "only rank <= core_top",
        "core_only": True,
        "cold": "deny",
    },
    "SMART_A": {
        "desc": "balanced: cold strong-only, rolling symbol quality",
        "cold": "strong",
        "min_avg_net": -0.04,
        "max_sl_rate": 0.65,
        "max_bad_streak": 2,
        "min_avg_mfe": 0.35,
        "cooldown_hours": 12,
    },
    "SMART_B": {
        "desc": "strict: requires better rolling stats",
        "cold": "strong",
        "min_avg_net": 0.00,
        "max_sl_rate": 0.58,
        "max_bad_streak": 1,
        "min_avg_mfe": 0.45,
        "cooldown_hours": 24,
    },
    "SMART_C": {
        "desc": "aggressive: lets more symbols prove themselves",
        "cold": "clean",
        "min_avg_net": -0.08,
        "max_sl_rate": 0.72,
        "max_bad_streak": 2,
        "min_avg_mfe": 0.30,
        "cooldown_hours": 8,
    },
    "SMART_D": {
        "desc": "BTC/OI focused exploration",
        "cold": "btc_oi",
        "min_avg_net": -0.06,
        "max_sl_rate": 0.68,
        "max_bad_streak": 2,
        "min_avg_mfe": 0.35,
        "cooldown_hours": 12,
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


def calc_net(margin, leverage, exit_pct, spread_bps, slippage_bps):
    notional = margin * leverage
    gross = notional * (exit_pct / 100.0)
    commission = notional * COMMISSION_RATE * 2
    spread = notional * (spread_bps / 10000.0)
    slippage = notional * (slippage_bps / 10000.0) * 2
    costs = commission + spread + slippage
    return gross, gross - costs, costs


def strong_candidate(e):
    return (
        e.get("score", 0) >= 5
        and e.get("btc5", -999) >= 0.0
        and e.get("oi", -999) >= 0.0
        and e.get("structure", 999) <= 1
        and e.get("breakout_risk_score", 999) <= 3
        and e.get("false_breakouts_15m", 999) <= 1
    )


def clean_candidate(e):
    return (
        e.get("score", 0) >= 4
        and e.get("btc5", -999) >= -0.05
        and e.get("oi", -999) >= -0.50
        and e.get("structure", 999) <= 2
        and e.get("breakout_risk_score", 999) <= 4
        and e.get("false_breakouts_15m", 999) <= 3
    )


def btc_oi_candidate(e):
    return (
        e.get("score", 0) >= 4
        and e.get("btc5", -999) >= 0.0
        and e.get("oi", -999) >= 0.0
        and e.get("structure", 999) <= 2
        and e.get("breakout_risk_score", 999) <= 4
    )


class SymbolQuality:
    def __init__(self, maxlen=8):
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


def smart_allow(e, mode_name, params, quality, core_top):
    rank = int(e.get("rank", 999999))

    if mode_name == "STATIC_ALL":
        return True, "STATIC_ALL"

    if rank <= core_top:
        return True, "CORE"

    if mode_name == "CORE_ONLY":
        return False, "OUTSIDE_CORE"

    q = quality.features()

    if q["cooldown_until"] and e["entry_t"] < q["cooldown_until"]:
        if strong_candidate(e):
            return True, "COOLDOWN_OVERRIDE_STRONG"
        return False, "COOLDOWN"

    if q["obs"] == 0:
        cold = params.get("cold", "strong")
        if cold == "allow":
            return True, "COLD_ALLOW"
        if cold == "strong" and strong_candidate(e):
            return True, "COLD_STRONG"
        if cold == "clean" and clean_candidate(e):
            return True, "COLD_CLEAN"
        if cold == "btc_oi" and btc_oi_candidate(e):
            return True, "COLD_BTC_OI"
        return False, "COLD_REJECT"

    if q["bad_streak"] >= params.get("max_bad_streak", 2):
        if strong_candidate(e):
            return True, "BAD_STREAK_OVERRIDE_STRONG"
        return False, "BAD_STREAK"

    quality_ok = (
        q["avg_net"] >= params.get("min_avg_net", -0.04)
        and q["sl_rate"] <= params.get("max_sl_rate", 0.65)
    )

    mfe_ok = (
        q["avg_mfe"] >= params.get("min_avg_mfe", 0.35)
        and q["sl_rate"] <= min(0.75, params.get("max_sl_rate", 0.65) + 0.10)
        and clean_candidate(e)
    )

    if quality_ok:
        return True, "QUALITY_OK"
    if mfe_ok:
        return True, "MFE_OK"

    if strong_candidate(e) and q["sl_rate"] <= 0.80:
        return True, "STRONG_OVERRIDE"

    return False, "QUALITY_REJECT"


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


def rolling_eval(events, mode_name, params, core_top, max_open):
    # Separate quality state per symbol. We update with all monitored candidate outcomes
    # once their hypothetical trade would be over. This is live-compatible if recorder
    # continues tracking skipped candidates.
    quality = defaultdict(SymbolQuality)
    pending_updates = []
    accepted_raw = []
    rejects = 0
    allow_reason_counts = defaultdict(int)
    reject_reason_counts = defaultdict(int)

    events = sorted(events, key=lambda x: (x["entry_t"], x["symbol"]))

    for e in events:
        t = e["entry_t"]

        ready = [x for x in pending_updates if x["exit_t"] <= t]
        pending_updates = [x for x in pending_updates if x["exit_t"] > t]

        for u in ready:
            quality[u["symbol"]].update(u, params)

        allow, reason = smart_allow(e, mode_name, params, quality[e["symbol"]], core_top)

        # Schedule monitoring update even if skipped. In live, this means
        # we keep watching candidate outcomes for symbol-quality learning.
        pending_updates.append(e)

        if not allow:
            rejects += 1
            reject_reason_counts[reason] += 1
            continue

        allow_reason_counts[reason] += 1
        rr = dict(e)
        rr["smart_mode"] = mode_name
        rr["smart_reason"] = reason
        accepted_raw.append(rr)

    accepted, skipped = apply_max_open(accepted_raw, max_open)
    sm = summarize(accepted, skipped, rejects)

    return sm, accepted, dict(allow_reason_counts), dict(reject_reason_counts)


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
    modes = parse_list_str(args.modes, list(SMART_MODES.keys()))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.end:
        end_ts = int(datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc).timestamp())
    else:
        end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = end_ts - args.days * 24 * 3600

    print(f"🚀 SKYNET SMART UNIVERSE GRID | days={args.days} top={args.top} core_top={args.core_top}")
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
    allow_rows = []
    reject_rows = []

    for combo, events in events_by_combo.items():
        family, guard, confirm = combo.split("|")
        print(f"Combo {combo}: candidates={len(events)}")

        for mode_name in modes:
            if mode_name not in SMART_MODES:
                continue

            params = dict(SMART_MODES[mode_name])
            core_top = int(args.core_top)

            for mo in max_open_values:
                sm, accepted, allow_counts, reject_counts = rolling_eval(events, mode_name, params, core_top, mo)
                sm.update({
                    "combo": combo,
                    "family": family,
                    "guard": guard,
                    "confirm": confirm,
                    "smart_mode": mode_name,
                    "mode_desc": params.get("desc", ""),
                    "core_top": core_top,
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

                # Keep output disk small: store only top accepted sample, not all gigantic candidates.
                for r in accepted[:500]:
                    rr = dict(r)
                    rr["smart_mode"] = mode_name
                    rr["max_open"] = mo
                    accepted_sample.append(rr)

                for reason, cnt in allow_counts.items():
                    allow_rows.append({
                        "combo": combo,
                        "smart_mode": mode_name,
                        "max_open": mo,
                        "reason": reason,
                        "count": cnt,
                    })
                for reason, cnt in reject_counts.items():
                    reject_rows.append({
                        "combo": combo,
                        "smart_mode": mode_name,
                        "max_open": mo,
                        "reason": reason,
                        "count": cnt,
                    })

    summaries.sort(key=lambda x: (x["net"], x["trades"]), reverse=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_DIR / f"smart_universe_grid_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / f"smart_universe_summary_{stamp}.csv"
    sample_path = run_dir / f"smart_universe_accepted_sample_{stamp}.csv"
    reasons_path = run_dir / f"smart_universe_reason_counts_{stamp}.csv"
    manifest_path = run_dir / "manifest.json"
    zip_path = run_dir / f"SMART_UNIVERSE_GRID_RESULTS_{stamp}.zip"

    summary_fields = [
        "combo", "family", "guard", "confirm", "smart_mode", "mode_desc",
        "core_top", "max_open", "days", "top", "margin", "leverage", "notional",
        "spread_bps", "slippage_bps", "trades", "smart_rejects", "skipped_by_maxopen",
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
    reason_fields = ["combo", "smart_mode", "max_open", "reason", "count"]

    write_csv(summary_path, summaries, summary_fields)
    write_csv(sample_path, accepted_sample, sample_fields)
    write_csv(reasons_path, allow_rows + reject_rows, reason_fields)

    symbol_counts_path = run_dir / f"smart_universe_symbol_candidate_counts_{stamp}.csv"
    write_csv(
        symbol_counts_path,
        [{"symbol": s, "rank": 0, "candidate_events": c} for s, c in sorted(symbol_event_counts.items(), key=lambda x: x[1], reverse=True)],
        ["symbol", "rank", "candidate_events"],
    )

    manifest = {
        "created_utc": stamp,
        "suite": "SMART_UNIVERSE_GRID",
        "days": args.days,
        "top": args.top,
        "core_top": args.core_top,
        "margin": args.margin,
        "leverage": args.leverage,
        "spread_bps": args.spread_bps,
        "slippage_bps": args.slippage_bps,
        "families": families,
        "guards": guards,
        "confirms": confirms,
        "modes": modes,
        "max_open": max_open_values,
        "smart_modes": SMART_MODES,
        "notes": "Symbol quality is updated only after hypothetical outcome exit_t <= current signal time. Skipped candidates are still monitored for future symbol-quality learning.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in [summary_path, sample_path, reasons_path, symbol_counts_path, manifest_path]:
            z.write(p, p.name)

    print("\n=== TOP SMART UNIVERSE RESULTS ===")
    for r in summaries[:60]:
        print(
            f"{r['combo']:<42} {r['smart_mode']:<10} MO:{r['max_open']} "
            f"Net:{r['net']:+.2f}$ On40:{r['monthly_pct_on_40']:+.1f}% "
            f"Tr:{r['trades']} WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$ "
            f"SL:{r['SL']} PTP:{r['TIME_PARTIAL'] + r['RUNNER_STOP'] + r['RUNNER_TP']} "
            f"Reject:{r['smart_rejects']}"
        )

    print("\nZIP:", zip_path)

    if args.send_tg:
        caption = (
            f"📦 SKYNET SMART UNIVERSE GRID\n"
            f"days={args.days} top={args.top} core={args.core_top} margin={args.margin} lev={args.leverage}x\n"
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
    p.add_argument("--top", type=int, default=100)
    p.add_argument("--core-top", type=int, default=30)
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
