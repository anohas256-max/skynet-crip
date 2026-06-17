import sqlite3
from pathlib import Path
from itertools import product

DB = Path("/root/skynet/data/v17_microstructure.sqlite3")

NOTIONAL = 30.0
TAKER_FEE = 0.0008
SLIPPAGE_BPS = 5.0

MIN_N = 30


def cost_pct(spread_bps):
    # fee roundtrip + slippage roundtrip + spread
    return (TAKER_FEE * 2.0 * 100.0) + ((SLIPPAGE_BPS * 2.0) / 100.0) + (max(0.0, spread_bps) / 100.0)


def net_from_pct(move_pct, spread_bps):
    return NOTIONAL * ((move_pct - cost_pct(spread_bps)) / 100.0)


def sim_trade(row, side, tp, sl):
    """
    Conservative sim from 5m MFE/MAE only.
    If both TP and SL could have touched, assume SL first.
    """
    max_up = float(row["max_up_5m"] or 0.0)
    max_down = float(row["max_down_5m"] or 0.0)
    close = float(row["close_5m"] or 0.0)
    spread = float(row["spread_bps"] or 999.0)

    if side == "LONG":
        if max_down <= -sl:
            move = -sl
            reason = "SL"
        elif max_up >= tp:
            move = tp
            reason = "TP"
        else:
            move = close
            reason = "TIME"
    else:
        if max_up >= sl:
            move = -sl
            reason = "SL"
        elif max_down <= -tp:
            move = tp
            reason = "TP"
        else:
            move = -close
            reason = "TIME"

    return net_from_pct(move, spread), reason


def metrics(rows, side, tp=0.8, sl=0.5):
    if not rows:
        return None

    close_key = "long_net_5m" if side == "LONG" else "short_net_5m"
    close_vals = [float(r[close_key] or 0.0) for r in rows]

    sim_vals = []
    reasons = {"TP": 0, "SL": 0, "TIME": 0}
    for r in rows:
        v, reason = sim_trade(r, side, tp, sl)
        sim_vals.append(v)
        reasons[reason] += 1

    wins = sum(1 for x in sim_vals if x > 0)
    gross_pos = sum(x for x in sim_vals if x > 0)
    gross_neg = -sum(x for x in sim_vals if x < 0)
    pf = gross_pos / gross_neg if gross_neg > 0 else 999.0

    return {
        "n": len(rows),
        "close_sum": sum(close_vals),
        "close_avg": sum(close_vals) / len(rows),
        "sim_sum": sum(sim_vals),
        "sim_avg": sum(sim_vals) / len(rows),
        "wr": wins / len(rows) * 100.0,
        "pf": pf,
        "tp": reasons["TP"],
        "sl": reasons["SL"],
        "time": reasons["TIME"],
        "mfe": sum(float(r["max_up_5m"] or 0.0) for r in rows) / len(rows),
        "mae": sum(float(r["max_down_5m"] or 0.0) for r in rows) / len(rows),
    }


def bucket_name(row):
    pc = float(row["price_change"] or 0.0)
    sp = float(row["spread_bps"] or 999.0)
    rank = int(row["current_turnover_rank"] or 999999)
    oi = float(row["oi_change"] or 0.0)
    imb = float(row["imb_5"] or 0.0)

    if abs(pc) < 0.30:
        pc_b = "pc_abs_008_030"
    elif abs(pc) < 0.70:
        pc_b = "pc_abs_030_070"
    elif abs(pc) < 1.50:
        pc_b = "pc_abs_070_150"
    else:
        pc_b = "pc_abs_150_plus"

    if sp <= 2:
        sp_b = "sp_0_2"
    elif sp <= 5:
        sp_b = "sp_2_5"
    elif sp <= 10:
        sp_b = "sp_5_10"
    else:
        sp_b = "sp_10_plus"

    if rank <= 20:
        r_b = "rank_1_20"
    elif rank <= 50:
        r_b = "rank_21_50"
    elif rank <= 100:
        r_b = "rank_51_100"
    else:
        r_b = "rank_100_plus"

    if oi >= 1:
        oi_b = "oi_pos_1plus"
    elif oi >= 0:
        oi_b = "oi_pos_0_1"
    elif oi <= -1:
        oi_b = "oi_neg_1plus"
    else:
        oi_b = "oi_neg_0_1"

    if imb >= 0.30:
        imb_b = "imb_bid_strong"
    elif imb >= 0:
        imb_b = "imb_bid_light"
    elif imb <= -0.30:
        imb_b = "imb_ask_strong"
    else:
        imb_b = "imb_ask_light"

    return pc_b, sp_b, r_b, oi_b, imb_b


def filter_rows(rows, pc_mode, spread_max, rank_max, vol_min, oi_mode, imb_mode, wall_mode):
    out = []

    for r in rows:
        pc = float(r["price_change"] or 0.0)
        sp = float(r["spread_bps"] or 999.0)
        rank = int(r["current_turnover_rank"] or 999999)
        vol = float(r["vol_ratio"] or 0.0)
        oi = float(r["oi_change"] or 0.0)
        imb = float(r["imb_5"] or 0.0)
        wall = float(r["wall_skew"] or 0.0)

        if pc_mode == "PC_POS" and pc <= 0:
            continue
        if pc_mode == "PC_NEG" and pc >= 0:
            continue
        if pc_mode == "PC_POS_030" and pc < 0.30:
            continue
        if pc_mode == "PC_NEG_030" and pc > -0.30:
            continue
        if pc_mode == "PC_ABS_070" and abs(pc) < 0.70:
            continue

        if sp > spread_max:
            continue
        if rank > rank_max:
            continue
        if vol < vol_min:
            continue

        if oi_mode == "OI_POS" and oi < 0:
            continue
        if oi_mode == "OI_POS_1" and oi < 1:
            continue
        if oi_mode == "OI_NEG" and oi > 0:
            continue
        if oi_mode == "OI_NEG_1" and oi > -1:
            continue

        if imb_mode == "IMB_POS" and imb < 0:
            continue
        if imb_mode == "IMB_POS_02" and imb < 0.20:
            continue
        if imb_mode == "IMB_NEG" and imb > 0:
            continue
        if imb_mode == "IMB_NEG_02" and imb > -0.20:
            continue

        if wall_mode == "WALL_POS" and wall < 0:
            continue
        if wall_mode == "WALL_NEG" and wall > 0:
            continue

        out.append(r)

    return out


def print_table(title, rows):
    print("\n" + title)
    print("-" * len(title))
    for x in rows[:40]:
        print(
            f"{x['side']:5s} n={x['n']:4d} sim={x['sim_sum']:+8.2f}$ avg={x['sim_avg']:+.4f}$ "
            f"wr={x['wr']:5.1f}% pf={x['pf']:.2f} TP={x['tp']:3d} SL={x['sl']:3d} TIME={x['time']:3d} "
            f"close={x['close_sum']:+8.2f}$ mfe={x['mfe']:+.2f}% mae={x['mae']:+.2f}% | {x['rule']}"
        )


con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

rows = con.execute("""
SELECT *
FROM signals
WHERE closed = 1
""").fetchall()

print("=== V17 MICRO EDGE ANALYSIS ===")
print("rows =", len(rows))
print("min_n =", MIN_N)

if len(rows) < 100:
    print("Too few rows. Let recorder run longer.")
    raise SystemExit(0)

print("\n=== BASIC CLOSE DIRECTION ===")
for side in ["LONG", "SHORT"]:
    m = metrics(rows, side, tp=0.8, sl=0.5)
    print(
        f"{side}: n={m['n']} closeSum={m['close_sum']:+.2f}$ closeAvg={m['close_avg']:+.4f}$ "
        f"simSum={m['sim_sum']:+.2f}$ simAvg={m['sim_avg']:+.4f}$ wr={m['wr']:.1f}% pf={m['pf']:.2f}"
    )

# Simple categorical buckets.
bucket_map = {}
for r in rows:
    for b in bucket_name(r):
        bucket_map.setdefault(b, []).append(r)

bucket_results = []
for b, rs in bucket_map.items():
    if len(rs) < MIN_N:
        continue
    for side in ["LONG", "SHORT"]:
        m = metrics(rs, side, tp=0.8, sl=0.5)
        bucket_results.append({"rule": b, "side": side, **m})

bucket_results.sort(key=lambda x: (x["sim_sum"], x["sim_avg"]), reverse=True)
print_table("=== TOP SIMPLE BUCKETS BY CONSERVATIVE TP0.8/SL0.5 ===", bucket_results)

# Rule search.
pc_modes = ["ANY", "PC_POS", "PC_NEG", "PC_POS_030", "PC_NEG_030", "PC_ABS_070"]
spread_maxes = [2, 3, 5, 8, 12, 999]
rank_maxes = [20, 40, 80, 150, 999999]
vol_mins = [3, 5, 8, 12, 20]
oi_modes = ["ANY", "OI_POS", "OI_POS_1", "OI_NEG", "OI_NEG_1"]
imb_modes = ["ANY", "IMB_POS", "IMB_POS_02", "IMB_NEG", "IMB_NEG_02"]
wall_modes = ["ANY", "WALL_POS", "WALL_NEG"]

results = []

for side in ["LONG", "SHORT"]:
    for pc_mode, spread_max, rank_max, vol_min, oi_mode, imb_mode, wall_mode in product(
        pc_modes, spread_maxes, rank_maxes, vol_mins, oi_modes, imb_modes, wall_modes
    ):
        rs = filter_rows(rows, pc_mode, spread_max, rank_max, vol_min, oi_mode, imb_mode, wall_mode)
        if len(rs) < MIN_N:
            continue

        m = metrics(rs, side, tp=0.8, sl=0.5)
        if m["pf"] < 1.05:
            continue

        rule = (
            f"{pc_mode} spread<={spread_max} rank<={rank_max} vol>={vol_min} "
            f"{oi_mode} {imb_mode} {wall_mode}"
        )
        results.append({"rule": rule, "side": side, **m})

# Deduplicate near-identical by side+n+sim_sum rounded.
seen = set()
dedup = []
for r in sorted(results, key=lambda x: (x["sim_sum"], x["sim_avg"], x["n"]), reverse=True):
    key = (r["side"], r["n"], round(r["sim_sum"], 2), round(r["sim_avg"], 4))
    if key in seen:
        continue
    seen.add(key)
    dedup.append(r)

print_table("=== TOP COMBO RULES BY CONSERVATIVE TP0.8/SL0.5 ===", dedup)

print("\n=== TOP CLOSE-ONLY RULES ===")
close_results = []
for side in ["LONG", "SHORT"]:
    close_key = "long_net_5m" if side == "LONG" else "short_net_5m"
    for pc_mode, spread_max, rank_max, vol_min, oi_mode, imb_mode, wall_mode in product(
        pc_modes, spread_maxes, rank_maxes, vol_mins, oi_modes, imb_modes, wall_modes
    ):
        rs = filter_rows(rows, pc_mode, spread_max, rank_max, vol_min, oi_mode, imb_mode, wall_mode)
        if len(rs) < MIN_N:
            continue
        vals = [float(r[close_key] or 0.0) for r in rs]
        s = sum(vals)
        avg = s / len(vals)
        if avg <= 0:
            continue
        close_results.append({
            "side": side,
            "n": len(rs),
            "sum": s,
            "avg": avg,
            "wr": sum(1 for v in vals if v > 0) / len(vals) * 100.0,
            "rule": f"{pc_mode} spread<={spread_max} rank<={rank_max} vol>={vol_min} {oi_mode} {imb_mode} {wall_mode}",
        })

for x in sorted(close_results, key=lambda x: (x["sum"], x["avg"]), reverse=True)[:40]:
    print(
        f"{x['side']:5s} n={x['n']:4d} close={x['sum']:+8.2f}$ avg={x['avg']:+.4f}$ "
        f"wr={x['wr']:5.1f}% | {x['rule']}"
    )
