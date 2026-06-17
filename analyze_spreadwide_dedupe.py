import re
from pathlib import Path
from collections import defaultdict, Counter

LOGS = [
    Path("/root/skynet/skynet_48h.log"),
    Path("/root/skynet/skynet_12h.log"),
    Path("/root/skynet/skynet_3h.log"),
]

rx = re.compile(
    r"\[(?P<t>\d\d:\d\d:\d\d)\] SKIP_TRACK_CLOSE \| "
    r"(?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| "
    r"original_skip=(?P<skip>[^|]+) \| HypoNet:(?P<net>[+-]?[0-9.]+)\$ \| "
    r"MFE:(?P<mfe>[+-]?[0-9.]+)% MAE:(?P<mae>[+-]?[0-9.]+)%"
)

def f(x):
    try:
        return float(x)
    except Exception:
        return 0.0

events = {}

for path in LOGS:
    if not path.exists():
        continue

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = rx.search(line)
        if not m:
            continue

        skip = m.group("skip").strip()
        if not skip.startswith("SPREAD_WIDE"):
            continue

        t = m.group("t")
        sym = m.group("symbol").strip()
        reason = m.group("reason").strip()
        net = f(m.group("net"))
        mfe = f(m.group("mfe"))
        mae = f(m.group("mae"))

        # Дедуп: один и тот же symbol + close-second + skip reason = один market-событие,
        # даже если его посчитали 10 стратегий.
        key = (t, sym, skip)

        if key not in events:
            events[key] = {
                "t": t,
                "symbol": sym,
                "skip": skip,
                "reason": reason,
                "net": net,
                "mfe": mfe,
                "mae": mae,
                "copies": 1,
                "strategies": set([m.group("strategy").strip()]),
            }
        else:
            e = events[key]
            e["copies"] += 1
            e["strategies"].add(m.group("strategy").strip())
            # Берём худший net среди дублей, чтобы не самообмануться.
            if net < e["net"]:
                e["net"] = net
                e["reason"] = reason
                e["mfe"] = mfe
                e["mae"] = mae

rows = list(events.values())

print("=== SPREAD_WIDE DEDUP SUMMARY ===")
print("unique_events =", len(rows))

if not rows:
    raise SystemExit

net = sum(r["net"] for r in rows)
wins = [r for r in rows if r["net"] > 0]
losses = [r for r in rows if r["net"] <= 0]
wr = len(wins) / len(rows) * 100
avg = net / len(rows)
avg_mfe = sum(r["mfe"] for r in rows) / len(rows)
avg_mae = sum(r["mae"] for r in rows) / len(rows)

print(f"net={net:+.2f}$ avg={avg:+.3f}$ wr={wr:.1f}% avgMFE={avg_mfe:+.2f}% avgMAE={avg_mae:+.2f}%")
print()

by_symbol = defaultdict(lambda: {"n": 0, "net": 0.0, "wins": 0, "mfe": 0.0, "mae": 0.0})
by_skip = defaultdict(lambda: {"n": 0, "net": 0.0, "wins": 0, "mfe": 0.0, "mae": 0.0})
reasons = Counter()

for r in rows:
    reasons[r["reason"]] += 1

    s = by_symbol[r["symbol"]]
    s["n"] += 1
    s["net"] += r["net"]
    s["wins"] += int(r["net"] > 0)
    s["mfe"] += r["mfe"]
    s["mae"] += r["mae"]

    k = by_skip[r["skip"]]
    k["n"] += 1
    k["net"] += r["net"]
    k["wins"] += int(r["net"] > 0)
    k["mfe"] += r["mfe"]
    k["mae"] += r["mae"]

print("reasons =", dict(reasons))
print()

print("=== BY SYMBOL ===")
for sym, d in sorted(by_symbol.items(), key=lambda x: x[1]["net"], reverse=True):
    n = d["n"]
    print(f"{sym:10s} n={n:3d} net={d['net']:+.2f}$ avg={d['net']/n:+.3f}$ wr={d['wins']/n*100:5.1f}% mfe={d['mfe']/n:+.2f}% mae={d['mae']/n:+.2f}%")

print()
print("=== BY EXACT SPREAD SKIP ===")
for skip, d in sorted(by_skip.items(), key=lambda x: x[1]["net"], reverse=True)[:40]:
    n = d["n"]
    print(f"{skip:32s} n={n:3d} net={d['net']:+.2f}$ avg={d['net']/n:+.3f}$ wr={d['wins']/n*100:5.1f}% mfe={d['mfe']/n:+.2f}% mae={d['mae']/n:+.2f}%")

print()
print("=== WORST UNIQUE EVENTS ===")
for r in sorted(rows, key=lambda x: x["net"])[:20]:
    print(f"{r['t']} {r['symbol']:10s} {r['skip']:30s} {r['reason']:12s} net={r['net']:+.2f}$ mfe={r['mfe']:+.2f}% mae={r['mae']:+.2f}% copies={r['copies']}")

print()
print("=== BEST UNIQUE EVENTS ===")
for r in sorted(rows, key=lambda x: x["net"], reverse=True)[:20]:
    print(f"{r['t']} {r['symbol']:10s} {r['skip']:30s} {r['reason']:12s} net={r['net']:+.2f}$ mfe={r['mfe']:+.2f}% mae={r['mae']:+.2f}% copies={r['copies']}")
