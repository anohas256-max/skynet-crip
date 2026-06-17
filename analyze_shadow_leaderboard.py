import re
from collections import defaultdict, Counter
from pathlib import Path

LOGS = [
    Path("/root/skynet/skynet_48h.log"),
    Path("/root/skynet/skynet_12h.log"),
    Path("/root/skynet/skynet_3h.log"),
]

close_re = re.compile(
    r"SHADOW_CLOSE \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| .*?"
    r"Net:(?P<net>[+-]?[0-9.]+)\$.*?"
    r"MFE:(?P<mfe>[+-]?[0-9.]+)% MAE:(?P<mae>[+-]?[0-9.]+)%"
)

dry_re = re.compile(
    r"DRY_LIVE_CLOSE \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| "
    r"LiveNet:(?P<net>[+-]?[0-9.]+)\$.*?"
)

skip_re = re.compile(
    r"SKIP_TRACK_CLOSE \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| "
    r"original_skip=(?P<skip>[^|]+) \| HypoNet:(?P<net>[+-]?[0-9.]+)\$ \| "
    r"MFE:(?P<mfe>[+-]?[0-9.]+)% MAE:(?P<mae>[+-]?[0-9.]+)%"
)

def f(x):
    try:
        return float(x)
    except Exception:
        return 0.0

strategy = defaultdict(lambda: {
    "n": 0, "net": 0.0, "wins": 0, "mfe": 0.0, "mae": 0.0,
    "reasons": Counter(), "symbols": Counter(), "sym_net": defaultdict(float)
})

dry = defaultdict(lambda: {"n": 0, "net": 0.0, "wins": 0, "reasons": Counter()})
skips = defaultdict(lambda: {"n": 0, "net": 0.0, "wins": 0, "mfe": 0.0, "mae": 0.0, "reasons": Counter(), "symbols": Counter()})

seen = set()

for path in LOGS:
    if not path.exists():
        continue

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = close_re.search(line)
        if m:
            key = ("shadow", line)
            if key in seen:
                continue
            seen.add(key)

            s = m.group("strategy").strip()
            sym = m.group("symbol").strip()
            reason = m.group("reason").strip()
            net = f(m.group("net"))
            mfe = f(m.group("mfe"))
            mae = f(m.group("mae"))

            d = strategy[s]
            d["n"] += 1
            d["net"] += net
            d["wins"] += int(net > 0)
            d["mfe"] += mfe
            d["mae"] += mae
            d["reasons"][reason] += 1
            d["symbols"][sym] += 1
            d["sym_net"][sym] += net
            continue

        m = dry_re.search(line)
        if m:
            key = ("dry", line)
            if key in seen:
                continue
            seen.add(key)

            s = m.group("strategy").strip()
            reason = m.group("reason").strip()
            net = f(m.group("net"))

            d = dry[s]
            d["n"] += 1
            d["net"] += net
            d["wins"] += int(net > 0)
            d["reasons"][reason] += 1
            continue

        m = skip_re.search(line)
        if m:
            key = ("skip", line)
            if key in seen:
                continue
            seen.add(key)

            skip = m.group("skip").strip()
            sym = m.group("symbol").strip()
            reason = m.group("reason").strip()
            net = f(m.group("net"))
            mfe = f(m.group("mfe"))
            mae = f(m.group("mae"))

            d = skips[skip]
            d["n"] += 1
            d["net"] += net
            d["wins"] += int(net > 0)
            d["mfe"] += mfe
            d["mae"] += mae
            d["reasons"][reason] += 1
            d["symbols"][sym] += 1

print("=== SHADOW STRATEGY LEADERBOARD ===")
rows = []
for s, d in strategy.items():
    if d["n"] == 0:
        continue
    rows.append((d["net"], s, d))

for net, s, d in sorted(rows, reverse=True)[:40]:
    n = d["n"]
    wr = d["wins"] / n * 100
    avg = d["net"] / n
    avg_mfe = d["mfe"] / n
    avg_mae = d["mae"] / n
    best_syms = sorted(d["sym_net"].items(), key=lambda x: x[1], reverse=True)[:5]
    worst_syms = sorted(d["sym_net"].items(), key=lambda x: x[1])[:5]
    print(f"{s:38s} n={n:3d} net={d['net']:+.2f}$ avg={avg:+.3f}$ wr={wr:5.1f}% mfe={avg_mfe:+.2f}% mae={avg_mae:+.2f}% reasons={dict(d['reasons'])}")
    print("   best :", best_syms)
    print("   worst:", worst_syms)

print()
print("=== DRY LIVE ===")
for s, d in sorted(dry.items(), key=lambda x: x[1]["net"], reverse=True):
    n = d["n"]
    if n:
        print(f"{s:38s} n={n:3d} net={d['net']:+.2f}$ avg={d['net']/n:+.3f}$ wr={d['wins']/n*100:5.1f}% reasons={dict(d['reasons'])}")

print()
print("=== SKIP REASON HYPOTHETICAL ===")
rows = []
for skip, d in skips.items():
    if d["n"]:
        rows.append((d["net"], skip, d))

for net, skip, d in sorted(rows, reverse=True)[:30]:
    n = d["n"]
    print(f"{skip:32s} n={n:3d} hypoNet={d['net']:+.2f}$ avg={d['net']/n:+.3f}$ wr={d['wins']/n*100:5.1f}% mfe={d['mfe']/n:+.2f}% mae={d['mae']/n:+.2f}% reasons={dict(d['reasons'])} symbols={dict(d['symbols'].most_common(8))}")
