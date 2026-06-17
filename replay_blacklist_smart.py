import zipfile, glob, os, csv
from collections import defaultdict

FILES = sorted(glob.glob("/root/skynet/data/backtest/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))
if not FILES:
    FILES = sorted(glob.glob("/root/skynet/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))

HARD_BLACKLIST = {
    "ALLO_USDT",
    "XRP_USDT",
    "AAVE_USDT",
    "INJ_USDT",
    "PUMPFUN_USDT",
    "ENA_USDT",
    "DOT_USDT",
    "CHZ_USDT",
    "JTO_USDT",
    "HBAR_USDT",
    "ETHFI_USDT",
    "ZEN_USDT",
}

SOFT_BLACKLIST = HARD_BLACKLIST | {
    "ADA_USDT",
    "UNI_USDT",
    "BNB_USDT",
    "ARB_USDT",
    "BCH_USDT",
}

def f(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def load_csv_from_zip(z, key):
    names = [n for n in z.namelist() if key in n]
    if not names:
        return []
    data = z.open(names[0]).read().decode("utf-8").splitlines()
    return list(csv.DictReader(data))

def summarize(rows):
    net = sum(f(r.get("net")) for r in rows)
    trades = len(rows)
    wins = sum(1 for r in rows if f(r.get("net")) > 0)
    sl = sum(1 for r in rows if r.get("reason") == "SL")
    avg = net / trades if trades else 0.0
    wr = wins / trades * 100 if trades else 0.0
    avg_mfe = sum(f(r.get("mfe")) for r in rows) / trades if trades else 0.0
    return net, trades, avg, wr, sl, avg_mfe

all_blocks = []

for path in FILES[-30:]:
    with zipfile.ZipFile(path) as z:
        summaries = load_csv_from_zip(z, "summary")
        samples = load_csv_from_zip(z, "accepted_sample")

    # Берём только main-кандидата, который нас интересует
    samples = [
        r for r in samples
        if r.get("smart_mode") == "V2_STRICT"
        and str(r.get("max_open")) in ("1", "1.0")
        and r.get("combo") in (
            "FILTERED_055|CLEAN_EXEC|WAIT1_CLOSE",
            "FILTERED_055|OI0_CLEAN|WAIT1_CLOSE",
            "FILTERED_055|BTC0_CLEAN|WAIT1_CLOSE",
        )
    ]

    if not samples:
        continue

    for combo in sorted(set(r["combo"] for r in samples)):
        rows = [r for r in samples if r["combo"] == combo]
        hard = [r for r in rows if r.get("symbol") not in HARD_BLACKLIST]
        soft = [r for r in rows if r.get("symbol") not in SOFT_BLACKLIST]

        all_blocks.append((os.path.basename(path), combo, "RAW", *summarize(rows)))
        all_blocks.append((os.path.basename(path), combo, "HARD_BL", *summarize(hard)))
        all_blocks.append((os.path.basename(path), combo, "SOFT_BL", *summarize(soft)))

print("=== PER ZIP / COMBO ===")
for fname, combo, mode, net, trades, avg, wr, sl, avg_mfe in all_blocks:
    print(f"{fname} | {combo:<36} | {mode:<7} net={net:+.2f}$ tr={trades:<3} avg={avg:+.3f}$ WR={wr:5.1f}% SL={sl:<3} MFE={avg_mfe:.2f}%")

print("\n=== AGGREGATED BY COMBO/MODE ===")
agg = defaultdict(list)
for fname, combo, mode, net, trades, avg, wr, sl, avg_mfe in all_blocks:
    agg[(combo, mode)].append((net, trades, sl))

for (combo, mode), xs in sorted(agg.items()):
    net = sum(x[0] for x in xs)
    trades = sum(x[1] for x in xs)
    sl = sum(x[2] for x in xs)
    avg = net / trades if trades else 0.0
    print(f"{combo:<36} | {mode:<7} net={net:+.2f}$ tr={trades:<4} avg={avg:+.3f}$ SL={sl}")
