import zipfile, glob, os, csv
from collections import defaultdict

files = sorted(glob.glob("/root/skynet/data/backtest/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))
if not files:
    files = sorted(glob.glob("/root/skynet/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))

print("Found zips:", len(files))
if not files:
    raise SystemExit("No SMART_UNIVERSE_V2_GRID_RESULTS zips found")

rows = []

for p in files[-20:]:
    with zipfile.ZipFile(p) as z:
        sample_name = [n for n in z.namelist() if "accepted_sample" in n][0]
        summary_name = [n for n in z.namelist() if "summary" in n][0]

        for r in csv.DictReader(z.open(sample_name).read().decode("utf-8").splitlines()):
            if r.get("smart_mode") != "V2_STRICT":
                continue
            if r.get("max_open") not in ("1", "1.0"):
                continue
            if "FILTERED_055|CLEAN_EXEC|WAIT1_CLOSE" not in r.get("combo", ""):
                continue
            try:
                r["_net"] = float(r.get("net", 0))
                r["_mfe"] = float(r.get("mfe", 0))
                r["_mae"] = float(r.get("mae", 0))
                r["_rank"] = int(float(r.get("rank", 9999)))
            except Exception:
                continue
            r["_zip"] = os.path.basename(p)
            rows.append(r)

print("Rows:", len(rows))

by_sym = defaultdict(list)
for r in rows:
    by_sym[r["symbol"]].append(r)

stats = []
for sym, rs in by_sym.items():
    n = len(rs)
    net = sum(x["_net"] for x in rs)
    avg = net / n
    sl = sum(1 for x in rs if x.get("reason") == "SL")
    wr = sum(1 for x in rs if x["_net"] > 0) / n * 100
    avg_mfe = sum(x["_mfe"] for x in rs) / n
    worst = min(x["_net"] for x in rs)
    best = max(x["_net"] for x in rs)
    avg_rank = sum(x["_rank"] for x in rs) / n
    stats.append((net, avg, n, sl, wr, avg_mfe, worst, best, avg_rank, sym))

print("\n=== WORST SYMBOLS ===")
for net, avg, n, sl, wr, avg_mfe, worst, best, avg_rank, sym in sorted(stats)[:30]:
    print(f"{sym:<16} net={net:+.3f}$ avg={avg:+.3f}$ n={n:<3} SL={sl:<3} WR={wr:5.1f}% MFE={avg_mfe:.2f}% worst={worst:+.3f}$ rank={avg_rank:.1f}")

print("\n=== BEST SYMBOLS ===")
for net, avg, n, sl, wr, avg_mfe, worst, best, avg_rank, sym in sorted(stats, reverse=True)[:30]:
    print(f"{sym:<16} net={net:+.3f}$ avg={avg:+.3f}$ n={n:<3} SL={sl:<3} WR={wr:5.1f}% MFE={avg_mfe:.2f}% best={best:+.3f}$ rank={avg_rank:.1f}")

bad = [s for net, avg, n, sl, wr, avg_mfe, worst, best, avg_rank, s in stats if n >= 2 and net < -0.10 and avg_mfe < 0.60]
good = [s for net, avg, n, sl, wr, avg_mfe, worst, best, avg_rank, s in stats if n >= 2 and net > 0.10 and avg_mfe >= 0.60]

print("\n=== BLACKLIST CANDIDATES ===")
print(",".join(sorted(bad)) if bad else "-")

print("\n=== WHITELIST CANDIDATES ===")
print(",".join(sorted(good)) if good else "-")
