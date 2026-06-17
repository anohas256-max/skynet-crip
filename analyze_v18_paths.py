import sqlite3
import json
from pathlib import Path
from collections import defaultdict

DB = Path("/root/skynet/data/v18_micro_paths.sqlite3")

NOTIONAL = 30.0
MIN_N = 30

DELAYS = [0, 20, 40, 60, 90]
TPS = [0.25, 0.40, 0.60, 0.80, 1.20]
SLS = [0.20, 0.30, 0.50, 0.80]

FEE_PROFILES = {
    "MEXC_TAKER": {
        "fee_side": 0.0008,
        "slippage_bps_side": 5.0,
        "spread_mult": 1.0,
    },
    "LOWER_TAKER": {
        "fee_side": 0.00055,
        "slippage_bps_side": 4.0,
        "spread_mult": 1.0,
    },
    "MAKER_ENTRY_TAKER_EXIT": {
        "fee_open": 0.0006,
        "fee_close": 0.0008,
        "slippage_bps_side": 2.0,
        "spread_mult": 0.5,
    },
    "GOOD_MAKER_PROFILE": {
        "fee_open": 0.0002,
        "fee_close": 0.00055,
        "slippage_bps_side": 1.5,
        "spread_mult": 0.35,
    },
}


def f(row, key, default=0.0):
    try:
        v = row[key]
        if v is None:
            return default
        return float(v)
    except Exception:
        return default


def i(row, key, default=999999):
    try:
        v = row[key]
        if v is None:
            return default
        return int(v)
    except Exception:
        return default


def parse_path(row):
    try:
        path = json.loads(row["path_json"] or "[]")
        out = []
        for p in path:
            if isinstance(p, list) and len(p) >= 2:
                out.append((float(p[0]), float(p[1])))
        return out
    except Exception:
        return []


def cost_pct(row, profile):
    spread_bps = max(0.0, f(row, "spread_bps", 999.0))
    spread_pct = (spread_bps / 100.0) * profile.get("spread_mult", 1.0)

    if "fee_side" in profile:
        fee_pct = profile["fee_side"] * 2.0 * 100.0
    else:
        fee_pct = (profile["fee_open"] + profile["fee_close"]) * 100.0

    slip_pct = (profile["slippage_bps_side"] * 2.0) / 100.0
    return fee_pct + slip_pct + spread_pct


def net_from_move(row, move_pct, profile):
    return NOTIONAL * ((move_pct - cost_pct(row, profile)) / 100.0)


def entry_index(path, delay):
    for idx, (age, pct) in enumerate(path):
        if age >= delay:
            return idx
    return None


def trade_mode_ok(row, side, mode, entry_pct):
    pc = f(row, "price_change")
    imb = f(row, "imb_5")
    wall = f(row, "wall_skew")
    spread = f(row, "spread_bps", 999)
    rank = i(row, "rank")

    if mode == "ANY":
        return True

    if mode == "CONTINUATION":
        if side == "LONG":
            return entry_pct >= 0.10 and spread <= 5 and rank <= 150
        return entry_pct <= -0.10 and spread <= 5 and rank <= 150

    if mode == "CLEAN_LONG":
        return side == "LONG" and pc > 0 and entry_pct >= 0.05 and spread <= 3 and rank <= 80 and imb > 0

    if mode == "FAILED_PUMP_SHORT":
        return side == "SHORT" and pc >= 0.20 and entry_pct <= 0.05 and spread <= 8

    if mode == "BOOK_SHORT":
        return side == "SHORT" and pc > 0 and entry_pct <= 0.10 and imb < 0 and wall < 0 and spread <= 8

    if mode == "FAILED_DUMP_LONG":
        return side == "LONG" and pc <= -0.20 and entry_pct >= -0.05 and spread <= 8

    if mode == "LIQUID_ONLY":
        return spread <= 3 and rank <= 80

    return False


def simulate(row, side, delay, tp, sl, profile, mode):
    path = parse_path(row)
    if len(path) < 4:
        return None

    idx = entry_index(path, delay)
    if idx is None or idx >= len(path) - 1:
        return None

    entry_pct = path[idx][1]

    if not trade_mode_ok(row, side, mode, entry_pct):
        return None

    reason = "TIME"
    move = None

    for age, pct in path[idx + 1:]:
        rel = pct - entry_pct

        if side == "LONG":
            if rel <= -sl:
                move = -sl
                reason = "SL"
                break
            if rel >= tp:
                move = tp
                reason = "TP"
                break
        else:
            if rel >= sl:
                move = -sl
                reason = "SL"
                break
            if rel <= -tp:
                move = tp
                reason = "TP"
                break

    if move is None:
        final_rel = path[-1][1] - entry_pct
        move = final_rel if side == "LONG" else -final_rel

    return net_from_move(row, move, profile), reason, entry_pct, move


def metrics(rows, side, delay, tp, sl, profile_name, mode):
    profile = FEE_PROFILES[profile_name]

    vals = []
    reasons = defaultdict(int)
    entry_pcts = []
    moves = []

    for row in rows:
        res = simulate(row, side, delay, tp, sl, profile, mode)
        if res is None:
            continue

        net, reason, entry_pct, move = res
        vals.append(net)
        reasons[reason] += 1
        entry_pcts.append(entry_pct)
        moves.append(move)

    n = len(vals)
    if n < MIN_N:
        return None

    pos = sum(x for x in vals if x > 0)
    neg = -sum(x for x in vals if x < 0)

    return {
        "n": n,
        "sum": sum(vals),
        "avg": sum(vals) / n,
        "wr": sum(1 for x in vals if x > 0) / n * 100.0,
        "pf": pos / neg if neg > 0 else 999.0,
        "tp_n": reasons["TP"],
        "sl_n": reasons["SL"],
        "time_n": reasons["TIME"],
        "avg_entry_pct": sum(entry_pcts) / n,
        "avg_move": sum(moves) / n,
    }


def print_top(title, results, limit=50):
    print("\n" + title)
    print("-" * len(title))

    if not results:
        print("EMPTY")
        return

    results = sorted(results, key=lambda x: (x["sum"], x["avg"], x["pf"]), reverse=True)

    for r in results[:limit]:
        print(
            f"{r['profile']:22s} {r['side']:5s} delay={r['delay']:>2}s "
            f"tp={r['tp']:.2f} sl={r['sl']:.2f} n={r['n']:4d} "
            f"sum={r['sum']:+8.2f}$ avg={r['avg']:+.4f}$ "
            f"wr={r['wr']:5.1f}% pf={r['pf']:.2f} "
            f"TP={r['tp_n']:3d} SL={r['sl_n']:3d} TIME={r['time_n']:3d} "
            f"entry={r['avg_entry_pct']:+.3f}% move={r['avg_move']:+.3f}% | {r['mode']}"
        )


con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

rows = con.execute("""
SELECT *
FROM signals
WHERE closed=1
  AND path_json IS NOT NULL
  AND path_json != ''
""").fetchall()

print("=== V18 PATH ANALYSIS ===")
print("db =", DB)
print("closed_path_rows =", len(rows))
print("MIN_N =", MIN_N)

if len(rows) < 150:
    print("Мало закрытых path-сигналов. Пусть V18 ещё пишет. Нормально запускать после 500+ closed.")
    raise SystemExit(0)

modes = [
    "ANY",
    "CONTINUATION",
    "CLEAN_LONG",
    "FAILED_PUMP_SHORT",
    "BOOK_SHORT",
    "FAILED_DUMP_LONG",
    "LIQUID_ONLY",
]

results = []

for profile_name in FEE_PROFILES:
    for side in ["LONG", "SHORT"]:
        for delay in DELAYS:
            for tp in TPS:
                for sl in SLS:
                    for mode in modes:
                        m = metrics(rows, side, delay, tp, sl, profile_name, mode)
                        if not m:
                            continue

                        results.append({
                            "profile": profile_name,
                            "side": side,
                            "delay": delay,
                            "tp": tp,
                            "sl": sl,
                            "mode": mode,
                            **m,
                        })

print_top("=== TOP ALL RESULTS ===", results)

print_top(
    "=== TOP MEXC_TAKER ONLY ===",
    [r for r in results if r["profile"] == "MEXC_TAKER"]
)

print_top(
    "=== TOP LOWER FEE / MAKER SENSITIVITY ===",
    [r for r in results if r["profile"] != "MEXC_TAKER"]
)

positive = [r for r in results if r["sum"] > 0 and r["pf"] >= 1.05]
print_top("=== POSITIVE ONLY PF>=1.05 ===", positive)

print("\n=== DECISION ===")
best_mexc = sorted([r for r in results if r["profile"] == "MEXC_TAKER"], key=lambda x: x["sum"], reverse=True)[0]
print(
    f"BEST_MEXC: {best_mexc['side']} delay={best_mexc['delay']} tp={best_mexc['tp']} sl={best_mexc['sl']} "
    f"mode={best_mexc['mode']} n={best_mexc['n']} sum={best_mexc['sum']:+.2f}$ "
    f"avg={best_mexc['avg']:+.4f}$ pf={best_mexc['pf']:.2f}"
)

if best_mexc["sum"] <= 0:
    print("MEXC_TAKER_EDGE = NO")
else:
    print("MEXC_TAKER_EDGE = MAYBE")

best_any = sorted(results, key=lambda x: x["sum"], reverse=True)[0]
print(
    f"BEST_ANY_PROFILE: {best_any['profile']} {best_any['side']} delay={best_any['delay']} "
    f"tp={best_any['tp']} sl={best_any['sl']} mode={best_any['mode']} "
    f"n={best_any['n']} sum={best_any['sum']:+.2f}$ avg={best_any['avg']:+.4f}$ pf={best_any['pf']:.2f}"
)
