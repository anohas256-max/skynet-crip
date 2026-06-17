import zipfile, glob, os, csv
from collections import defaultdict, deque

FILES = sorted(glob.glob("/root/skynet/data/backtest/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))
if not FILES:
    FILES = sorted(glob.glob("/root/skynet/**/SMART_UNIVERSE_V2_GRID_RESULTS_*.zip", recursive=True))

COMBOS = {
    "FILTERED_055|CLEAN_EXEC|WAIT1_CLOSE",
    "FILTERED_055|OI0_CLEAN|WAIT1_CLOSE",
    "FILTERED_055|BTC0_CLEAN|WAIT1_CLOSE",
}

def f(x, d=0.0):
    try: return float(x)
    except Exception: return d

def i(x, d=0):
    try: return int(float(x))
    except Exception: return d

def load_csv(z, key):
    names = [n for n in z.namelist() if key in n]
    if not names:
        return []
    return list(csv.DictReader(z.open(names[0]).read().decode("utf-8").splitlines()))

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
    def __init__(self, win):
        self.last = deque(maxlen=win)
        self.cooldown_until = 0

    def update(self, r, cooldown_h, mode):
        net = f(r.get("net"))
        mfe = f(r.get("mfe"))
        sl = 1 if r.get("reason") == "SL" else 0

        self.last.append({"net": net, "mfe": mfe, "sl": sl})

        if len(self.last) < 2:
            return

        n = len(self.last)
        avg_net = sum(x["net"] for x in self.last) / n
        avg_mfe = sum(x["mfe"] for x in self.last) / n
        sl_rate = sum(x["sl"] for x in self.last) / n

        toxic = False

        if mode == "T1_FAST":
            toxic = sl_rate >= 0.50 or avg_net < -0.03 or avg_mfe < 0.55

        elif mode == "T2_BALANCED":
            toxic = (sl_rate >= 0.50 and avg_net < 0.02) or avg_net < -0.05 or (avg_mfe < 0.60 and avg_net <= 0)

        elif mode == "T3_STRICT":
            toxic = (sl_rate >= 0.67 and avg_net < 0.00) or avg_net < -0.08

        elif mode == "T4_ONE_SL":
            toxic = self.last[-1]["sl"] == 1 and self.last[-1]["mfe"] < 0.80

        if toxic:
            self.cooldown_until = i(r.get("exit_t")) + cooldown_h * 3600

def summarize(rows):
    net = sum(f(r.get("net")) for r in rows)
    tr = len(rows)
    wins = sum(1 for r in rows if f(r.get("net")) > 0)
    sl = sum(1 for r in rows if r.get("reason") == "SL")
    avg = net / tr if tr else 0
    wr = wins / tr * 100 if tr else 0
    mfe = sum(f(r.get("mfe")) for r in rows) / tr if tr else 0
    return net, tr, avg, wr, sl, mfe

def replay(rows, mode, cooldown_h, win, allow_ultra):
    rows = sorted(rows, key=lambda r: (i(r.get("entry_t")), r.get("symbol", "")))

    states = defaultdict(lambda: State(win))
    pending = []
    taken = []
    skipq = 0
    ultra = 0

    for r in rows:
        t = i(r.get("entry_t"))

        ready = [x for x in pending if i(x.get("exit_t")) <= t]
        pending = [x for x in pending if i(x.get("exit_t")) > t]

        for old in ready:
            states[old.get("symbol", "")].update(old, cooldown_h, mode)

        sym = r.get("symbol", "")
        st = states[sym]
        in_q = st.cooldown_until and t < st.cooldown_until

        # monitor outcome even if skipped
        pending.append(r)

        if in_q:
            if allow_ultra and is_ultra(r):
                ultra += 1
                taken.append(r)
            else:
                skipq += 1
                continue
        else:
            taken.append(r)

    net, tr, avg, wr, sl, mfe = summarize(taken)
    return {
        "net": net, "trades": tr, "avg": avg, "wr": wr,
        "sl": sl, "mfe": mfe, "skipq": skipq, "ultra": ultra
    }

blocks = []

for path in FILES[-30:]:
    with zipfile.ZipFile(path) as z:
        samples = load_csv(z, "accepted_sample")

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

        net, tr, avg, wr, sl, mfe = summarize(rows)
        blocks.append((combo, "RAW", {"net":net,"trades":tr,"avg":avg,"wr":wr,"sl":sl,"mfe":mfe,"skipq":0,"ultra":0}))

        for mode in ["T1_FAST", "T2_BALANCED", "T3_STRICT", "T4_ONE_SL"]:
            for h in [12, 24]:
                blocks.append((combo, f"{mode}_Q{h}", replay(rows, mode, h, 4, False)))
                blocks.append((combo, f"{mode}_Q{h}_U", replay(rows, mode, h, 4, True)))

agg = defaultdict(lambda: {"net":0.0,"trades":0,"wins_est":0,"sl":0,"mfe_sum":0.0,"skipq":0,"ultra":0})

for combo, mode, s in blocks:
    k = (combo, mode)
    agg[k]["net"] += s["net"]
    agg[k]["trades"] += s["trades"]
    agg[k]["sl"] += s["sl"]
    agg[k]["mfe_sum"] += s["mfe"] * s["trades"]
    agg[k]["skipq"] += s["skipq"]
    agg[k]["ultra"] += s["ultra"]

print("=== AGGREGATED BY COMBO/MODE ===")
for (combo, mode), s in sorted(agg.items()):
    tr = s["trades"]
    avg = s["net"] / tr if tr else 0
    mfe = s["mfe_sum"] / tr if tr else 0
    print(
        f"{combo:<36} | {mode:<18} "
        f"net={s['net']:+.2f}$ tr={tr:<4} avg={avg:+.3f}$ "
        f"SL={s['sl']:<4} MFE={mfe:.2f}% skipQ={s['skipq']:<4} ultra={s['ultra']}"
    )
