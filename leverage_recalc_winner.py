import os, csv, zipfile, glob, json
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv("/root/skynet/.env")

ROOT = Path("/root/skynet")
OUT = ROOT / "data" / "backtest" / "leverage_recalc"
OUT.mkdir(parents=True, exist_ok=True)

COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.0004"))

CASES = [
    {"case": "M3_L4_BASE", "margin": 3.0, "leverage": 4},
    {"case": "M3_L10", "margin": 3.0, "leverage": 10},
    {"case": "M4_L10", "margin": 4.0, "leverage": 10},
]

zip_candidates = []
zip_candidates += glob.glob("/root/skynet/data/backtest/winner_exit_grid/**/WINNER_EXIT_GRID_RESULTS_*.zip", recursive=True)
zip_candidates += glob.glob("/root/skynet/**/WINNER_EXIT_GRID_RESULTS_*.zip", recursive=True)
zip_candidates = sorted(set(zip_candidates), key=lambda p: os.path.getmtime(p), reverse=True)

if not zip_candidates:
    raise SystemExit("❌ Не нашел WINNER_EXIT_GRID_RESULTS_*.zip на сервере. Сначала нужен winner_exit_grid.")

latest = zip_candidates[0]
print("Using:", latest)

stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
work = OUT / f"leverage_recalc_{stamp}"
work.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(latest, "r") as z:
    z.extractall(work)

trade_files = list(work.glob("*trades*.csv"))
if not trade_files:
    raise SystemExit("❌ В ZIP не нашел trades csv")

trades_file = trade_files[0]
rows = []
with trades_file.open("r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        if row.get("exit_name") != "ATR5B_ORIGINAL_T45":
            continue
        rows.append(row)

if not rows:
    raise SystemExit("❌ Нет сделок ATR5B_ORIGINAL_T45")

def calc_net(margin, leverage, exit_pct, spread_bps, slippage_bps):
    notional = margin * leverage
    gross = notional * (exit_pct / 100.0)
    commission = notional * COMMISSION_RATE * 2
    spread = notional * (spread_bps / 10000.0)
    slippage = notional * (slippage_bps / 10000.0) * 2
    costs = commission + spread + slippage
    return gross, gross - costs, costs

def summarize(filtered, margin, leverage, spread_bps, slippage_bps):
    out = {
        "trades": 0, "wins": 0, "losses": 0,
        "gross": 0.0, "net": 0.0, "costs": 0.0,
        "avg_net": 0.0, "winrate": 0.0,
        "avg_mfe": 0.0, "avg_mae": 0.0,
        "SL": 0, "TIME": 0, "TIME_PARTIAL": 0, "RUNNER_STOP": 0, "RUNNER_TP": 0, "BE": 0, "MICRO_LOCK": 0,
    }
    for row in filtered:
        exit_pct = float(row["exit_pct"])
        gross, net, costs = calc_net(margin, leverage, exit_pct, spread_bps, slippage_bps)
        out["trades"] += 1
        out["gross"] += gross
        out["net"] += net
        out["costs"] += costs
        out["avg_mfe"] += float(row.get("mfe", 0) or 0)
        out["avg_mae"] += float(row.get("mae", 0) or 0)
        reason = row.get("reason", "")
        if reason in out:
            out[reason] += 1
        if net > 0:
            out["wins"] += 1
        elif net < 0:
            out["losses"] += 1
    if out["trades"]:
        out["avg_net"] = out["net"] / out["trades"]
        out["winrate"] = out["wins"] / out["trades"] * 100.0
        out["avg_mfe"] /= out["trades"]
        out["avg_mae"] /= out["trades"]
    return out

summary = []
detail = []

for cost_name, spread_bps, slippage_bps in [
    ("normal", 2.0, 3.0),
    ("pessimistic", 3.0, 5.0),
]:
    for max_open in [1, 2]:
        filtered_mo = [x for x in rows if str(x.get("max_open")) == str(max_open)]
        for case in CASES:
            sm = summarize(filtered_mo, case["margin"], case["leverage"], spread_bps, slippage_bps)
            rec = {
                "cost_mode": cost_name,
                "case": case["case"],
                "margin": case["margin"],
                "leverage": case["leverage"],
                "notional": case["margin"] * case["leverage"],
                "max_open": max_open,
                "spread_bps": spread_bps,
                "slippage_bps": slippage_bps,
                **sm,
                "monthly_pct_on_40": sm["net"] / 40.0 * 100.0,
            }
            summary.append(rec)

summary.sort(key=lambda x: (x["cost_mode"], x["max_open"], -x["net"]))

summary_path = work / f"leverage_recalc_summary_{stamp}.csv"
fields = [
    "cost_mode", "case", "margin", "leverage", "notional", "max_open",
    "spread_bps", "slippage_bps", "trades", "wins", "losses", "winrate",
    "gross", "net", "costs", "avg_net", "monthly_pct_on_40",
    "avg_mfe", "avg_mae", "SL", "TIME", "TIME_PARTIAL", "RUNNER_STOP", "RUNNER_TP", "BE", "MICRO_LOCK"
]
with summary_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for row in summary:
        w.writerow(row)

print("\n=== LEVERAGE RECALC SUMMARY ===")
for r in summary:
    print(
        f"{r['cost_mode']:<11} {r['case']:<10} MO:{r['max_open']} "
        f"Notional:${r['notional']:.0f} Net:{r['net']:+.2f}$ "
        f"MonthOn40:{r['monthly_pct_on_40']:+.1f}% "
        f"Tr:{r['trades']} WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$"
    )

manifest = work / "manifest.json"
manifest.write_text(json.dumps({
    "source_zip": latest,
    "created_utc": stamp,
    "commission_rate": COMMISSION_RATE,
    "cases": CASES,
}, ensure_ascii=False, indent=2), encoding="utf-8")

out_zip = work / f"LEVERAGE_RECALC_WINNER_{stamp}.zip"
with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(summary_path, summary_path.name)
    z.write(manifest, manifest.name)

print("\nZIP:", out_zip)

# Telegram send
try:
    from telethon import TelegramClient
    api_id = int(os.getenv("API_ID", "0"))
    api_hash = os.getenv("API_HASH", "")
    target = os.getenv("TG_TARGET", "-1002953234396")
    if api_id and api_hash:
        import asyncio
        async def send():
            async with TelegramClient("backtest_sender_session", api_id, api_hash) as client:
                await client.send_file(int(target), str(out_zip), caption="📦 LEVERAGE RECALC WINNER | ATR5B_ORIGINAL_T45 | M3/M4 x4/x10")
        asyncio.run(send())
        print("📤 Sent to Telegram")
    else:
        print("TG skipped: API_ID/API_HASH missing")
except Exception as e:
    print("TG send failed:", type(e).__name__, e)
