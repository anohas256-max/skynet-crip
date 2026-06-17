import zipfile
import glob
import os
import csv
from collections import defaultdict

FILES = sorted(glob.glob("/root/skynet/data/backtest/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))
if not FILES:
    FILES = sorted(glob.glob("/root/skynet/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))

COMBOS = {
    "FILTERED_055|CLEAN_EXEC|WAIT1_CLOSE",
    "FILTERED_055|OI0_CLEAN|WAIT1_CLOSE",
    "FILTERED_055|BTC0_CLEAN|WAIT1_CLOSE",
}

def f(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def i(x, default=0):
    try:
        return int(float(x))
    except Exception:
        return default

def load_csv_from_zip(z, key):
    names = [n for n in z.namelist() if key in n]
    if not names:
        return []
    data = z.open(names[0]).read().decode("utf-8").splitlines()
    return list(csv.DictReader(data))

def is_bad(r):
    net = f(r.get("net"))
    mfe = f(r.get("mfe"))
    reason = r.get("reason", "")
    return (reason == "SL" and mfe < 0.35) or (net < 0 and mfe < 0.25)

def is_good(r):
    return f(r.get("net")) > 0 and f(r.get("mfe")) >= 0.80

def is_ultra(r):
    return (
        f(r.get("score")) >= 6
        and f(r.get("btc5")) >= 0.10
        and f(r.get("oi")) >= 0.50
        and f(r.get("structure")) <= 1
        and f(r.get("breakout_risk_score")) <= 2
        and f(r.get("false_breakouts_15m")) <= 1
        and f(r.get("price_change")) <= 0.65
    )

class State:
    def __init__(self):
        self.bad_streak = 0
        self.quarantine_until = 0

    def update(self, r, cooldown_hours):
        if is_bad(r):
            self.bad_streak += 1
            if self.bad_streak >= 2:
                self.quarantine_until = i(r.get("exit_t")) + cooldown_hours * 3600
        elif is_good(r):
            self.bad_streak = max(0, self.bad_streak - 1)

def summarize(rows):
    net = sum(f(r.get("net")) for r in rows)
    trades = len(rows)
    wins = sum(1 for r in rows if f(r.get("net")) > 0)
    sl = sum(1 for r in rows if r.get("reason") == "SL")
    avg = net / trades if trades else 0.0
    wr = wins / trades * 100.0 if trades else 0.0
    mfe = sum(f(r.get("mfe")) for r in rows) / trades if trades else 0.0
    return {
        "net": net,
        "trades": trades,
        "wins": wins,
        "sl": sl,
        "avg": avg,
        "wr": wr,
        "mfe": mfe,
    }

def replay(rows, cooldown_hours, allow_ultra):
    rows = sorted(rows, key=lambda r: (i(r.get("entry_t")), r.get("symbol", "")))

    states = defaultdict(State)
    pending = []
    taken = []
    skipped_q = 0
    ultra_overrides = 0

    for r in rows:
        t = i(r.get("entry_t"))

        ready = [x for x in pending if i(x.get("exit_t")) <= t]
        pending = [x for x in pending if i(x.get("exit_t")) > t]

        for old in ready:
            states[old.get("symbol", "")].update(old, cooldown_hours)

        sym = r.get("symbol", "")
        st = states[sym]
        in_quarantine = st.quarantine_until and t < st.quarantine_until

        # Важно: даже если скипнули, outcome всё равно мониторим.
        pending.append(r)

        if in_quarantine:
            if allow_ultra and is_ultra(r):
                ultra_overrides += 1
                taken.append(r)
            else:
                skipped_q += 1
                continue
        else:
            taken.append(r)

    s = summarize(taken)
    s["skipped_q"] = skipped_q
    s["ultra_overrides"] = ultra_overrides
    return s

blocks = []

for path in FILES[-30:]:
    with zipfile.ZipFile(path) as z:
        samples = load_csv_from_zip(z, "accepted_sample")

    samples = [
        r for r in samples
        if r.get("smart_mode") == "V2_STRICT"
        and str(r.get("max_open")) in ("1", "1.0")
        and r.get("combo") in COMBOS
    ]

    if not samples:
        continue

    for combo in sorted(set(r["combo"] for r in samples)):
        rows = [r for r in samples if r["combo"] == combo]

        raw = summarize(rows)
        raw["skipped_q"] = 0
        raw["ultra_overrides"] = 0
        blocks.append((os.path.basename(path), combo, "RAW", raw))

        for h in (12, 24, 48):
            blocks.append((os.path.basename(path), combo, f"Q{h}", replay(rows, h, False)))
            blocks.append((os.path.basename(path), combo, f"Q{h}_ULTRA", replay(rows, h, True)))

print("=== AGGREGATED BY COMBO/MODE ===")

agg = defaultdict(lambda: {"net": 0.0, "trades": 0, "wins": 0, "sl": 0, "mfe_sum": 0.0, "skipped_q": 0, "ultra": 0})

for fname, combo, mode, s in blocks:
    key = (combo, mode)
    agg[key]["net"] += s["net"]
    agg[key]["trades"] += s["trades"]
    agg[key]["wins"] += s["wins"]
    agg[key]["sl"] += s["sl"]
    agg[key]["mfe_sum"] += s["mfe"] * s["trades"]
    agg[key]["skipped_q"] += s["skipped_q"]
    agg[key]["ultra"] += s["ultra_overrides"]

for (combo, mode), s in sorted(agg.items()):
    tr = s["trades"]
    avg = s["net"] / tr if tr else 0.0
    wr = s["wins"] / tr * 100.0 if tr else 0.0
    mfe = s["mfe_sum"] / tr if tr else 0.0

    print(
        f"{combo:<36} | {mode:<9} "
        f"net={s['net']:+.2f}$ tr={tr:<4} avg={avg:+.3f}$ "
        f"WR={wr:5.1f}% SL={s['sl']:<4} MFE={mfe:.2f}% "
        f"skipQ={s['skipped_q']:<4} ultra={s['ultra']}"
    )
