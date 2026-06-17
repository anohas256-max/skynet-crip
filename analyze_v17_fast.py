import sqlite3
from pathlib import Path
from collections import defaultdict

DB = Path("/root/skynet/data/v17_microstructure.sqlite3")

NOTIONAL = 30.0
TAKER_FEE = 0.0008
SLIPPAGE_BPS = 5.0

TP = 0.8
SL = 0.5
MIN_N = 20


def cost_pct(spread_bps):
    return (TAKER_FEE * 2 * 100.0) + ((SLIPPAGE_BPS * 2) / 100.0) + (max(0.0, spread_bps) / 100.0)


def net_from_move(move_pct, spread_bps):
    return NOTIONAL * ((move_pct - cost_pct(spread_bps)) / 100.0)


def sim(row, side):
    max_up = float(row["max_up_5m"] or 0)
    max_down = float(row["max_down_5m"] or 0)
    close = float(row["close_5m"] or 0)
    spread = float(row["spread_bps"] or 999)

    if side == "LONG":
        if max_down <= -SL:
            move = -SL
            reason = "SL"
        elif max_up >= TP:
            move = TP
            reason = "TP"
        else:
            move = close
            reason = "TIME"
    else:
        if max_up >= SL:
            move = -SL
            reason = "SL"
        elif max_down <= -TP:
            move = TP
            reason = "TP"
        else:
            move = -close
            reason = "TIME"

    return net_from_move(move, spread), reason


def calc(rows, side):
    vals = []
    reasons = defaultdict(int)

    close_key = "long_net_5m" if side == "LONG" else "short_net_5m"
    close_vals = []

    for r in rows:
        v, reason = sim(r, side)
        vals.append(v)
        reasons[reason] += 1
        close_vals.append(float(r[close_key] or 0))

    n = len(rows)
    if n == 0:
        return None

    pos = sum(x for x in vals if x > 0)
    neg = -sum(x for x in vals if x < 0)

    return {
        "n": n,
        "sum": sum(vals),
        "avg": sum(vals) / n,
        "wr": sum(1 for x in vals if x > 0) / n * 100,
        "pf": pos / neg if neg > 0 else 999,
        "tp": reasons["TP"],
        "sl": reasons["SL"],
        "time": reasons["TIME"],
        "close_sum": sum(close_vals),
        "close_avg": sum(close_vals) / n,
        "mfe": sum(float(r["max_up_5m"] or 0) for r in rows) / n,
        "mae": sum(float(r["max_down_5m"] or 0) for r in rows) / n,
    }


def show(title, items, limit=40):
    print("\n" + title)
    print("-" * len(title))
    items = [x for x in items if x["n"] >= MIN_N]
    items.sort(key=lambda x: (x["sum"], x["avg"]), reverse=True)

    if not items:
        print("EMPTY")
        return

    for x in items[:limit]:
        print(
            f"{x['side']:5s} n={x['n']:4d} sim={x['sum']:+8.2f}$ avg={x['avg']:+.4f}$ "
            f"wr={x['wr']:5.1f}% pf={x['pf']:.2f} TP={x['tp']:3d} SL={x['sl']:3d} TIME={x['time']:3d} "
            f"close={x['close_sum']:+8.2f}$ mfe={x['mfe']:+.2f}% mae={x['mae']:+.2f}% | {x['rule']}"
        )


def rule_filter(rows, fn):
    return [r for r in rows if fn(r)]


def fnum(r, k, d=0):
    try:
        return float(r[k] if r[k] is not None else d)
    except Exception:
        return d


def inum(r, k, d=999999):
    try:
        return int(r[k] if r[k] is not None else d)
    except Exception:
        return d


con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

rows = con.execute("SELECT * FROM signals WHERE closed=1").fetchall()

print("=== V17 FAST ANALYSIS ===")
print("rows =", len(rows))
print("TP =", TP, "SL =", SL, "MIN_N =", MIN_N)

for side in ["LONG", "SHORT"]:
    m = calc(rows, side)
    print(
        f"ALL {side}: n={m['n']} sim={m['sum']:+.2f}$ avg={m['avg']:+.4f}$ "
        f"wr={m['wr']:.1f}% pf={m['pf']:.2f} close={m['close_sum']:+.2f}$"
    )

rules = []

# Базовые buckets
for sp in [2, 3, 5, 8, 12]:
    rules.append((f"spread<={sp}", lambda r, sp=sp: fnum(r, "spread_bps", 999) <= sp))

for rank in [20, 40, 80, 150]:
    rules.append((f"rank<={rank}", lambda r, rank=rank: inum(r, "current_turnover_rank") <= rank))

for vol in [3, 5, 8, 12, 20]:
    rules.append((f"vol>={vol}", lambda r, vol=vol: fnum(r, "vol_ratio") >= vol))

rules += [
    ("pc>0", lambda r: fnum(r, "price_change") > 0),
    ("pc<0", lambda r: fnum(r, "price_change") < 0),
    ("pc>=0.30", lambda r: fnum(r, "price_change") >= 0.30),
    ("pc<=-0.30", lambda r: fnum(r, "price_change") <= -0.30),
    ("abs_pc>=0.70", lambda r: abs(fnum(r, "price_change")) >= 0.70),
    ("oi>0", lambda r: fnum(r, "oi_change") > 0),
    ("oi<0", lambda r: fnum(r, "oi_change") < 0),
    ("oi>=1", lambda r: fnum(r, "oi_change") >= 1),
    ("oi<=-1", lambda r: fnum(r, "oi_change") <= -1),
    ("imb5>0", lambda r: fnum(r, "imb_5") > 0),
    ("imb5<0", lambda r: fnum(r, "imb_5") < 0),
    ("imb5>=0.20", lambda r: fnum(r, "imb_5") >= 0.20),
    ("imb5<=-0.20", lambda r: fnum(r, "imb_5") <= -0.20),
    ("wall>0", lambda r: fnum(r, "wall_skew") > 0),
    ("wall<0", lambda r: fnum(r, "wall_skew") < 0),
]

single_results = []
for name, fn in rules:
    rs = rule_filter(rows, fn)
    for side in ["LONG", "SHORT"]:
        m = calc(rs, side)
        if m:
            single_results.append({"rule": name, "side": side, **m})

show("=== SINGLE FILTER BUCKETS ===", single_results)

# Ручные осмысленные комбинации, без безумного перебора.
combo_rules = [
    ("LONG clean continuation: pc>0 spread<=3 rank<=80 imb5>0",
     lambda r: fnum(r,"price_change") > 0 and fnum(r,"spread_bps",999) <= 3 and inum(r,"current_turnover_rank") <= 80 and fnum(r,"imb_5") > 0),

    ("LONG strong book: pc>0 spread<=5 rank<=80 imb5>=0.20 wall>=0",
     lambda r: fnum(r,"price_change") > 0 and fnum(r,"spread_bps",999) <= 5 and inum(r,"current_turnover_rank") <= 80 and fnum(r,"imb_5") >= 0.20 and fnum(r,"wall_skew") >= 0),

    ("LONG top liquid: pc>0 spread<=3 rank<=40 vol>=5",
     lambda r: fnum(r,"price_change") > 0 and fnum(r,"spread_bps",999) <= 3 and inum(r,"current_turnover_rank") <= 40 and fnum(r,"vol_ratio") >= 5),

    ("LONG no chase: 0<pc<0.70 spread<=3 rank<=80",
     lambda r: 0 < fnum(r,"price_change") < 0.70 and fnum(r,"spread_bps",999) <= 3 and inum(r,"current_turnover_rank") <= 80),

    ("SHORT fake pump: pc>0 spread<=8 imb5<0 wall<0",
     lambda r: fnum(r,"price_change") > 0 and fnum(r,"spread_bps",999) <= 8 and fnum(r,"imb_5") < 0 and fnum(r,"wall_skew") < 0),

    ("SHORT pump no book: pc>=0.30 spread<=8 imb5<=-0.20",
     lambda r: fnum(r,"price_change") >= 0.30 and fnum(r,"spread_bps",999) <= 8 and fnum(r,"imb_5") <= -0.20),

    ("SHORT pump oi down: pc>0 spread<=8 oi<0",
     lambda r: fnum(r,"price_change") > 0 and fnum(r,"spread_bps",999) <= 8 and fnum(r,"oi_change") < 0),

    ("SHORT red continuation: pc<0 spread<=5 imb5<0",
     lambda r: fnum(r,"price_change") < 0 and fnum(r,"spread_bps",999) <= 5 and fnum(r,"imb_5") < 0),

    ("SHORT rug continuation: pc<=-0.30 spread<=5 rank<=150",
     lambda r: fnum(r,"price_change") <= -0.30 and fnum(r,"spread_bps",999) <= 5 and inum(r,"current_turnover_rank") <= 150),

    ("SHORT overheat: abs_pc>=0.70 spread<=8 rank<=150",
     lambda r: abs(fnum(r,"price_change")) >= 0.70 and fnum(r,"spread_bps",999) <= 8 and inum(r,"current_turnover_rank") <= 150),
]

combo_results = []
for name, fn in combo_rules:
    rs = rule_filter(rows, fn)
    for side in ["LONG", "SHORT"]:
        m = calc(rs, side)
        if m:
            combo_results.append({"rule": name, "side": side, **m})

show("=== TARGETED COMBO RULES ===", combo_results)

# Символы: кто реально тащит/сливает.
by_sym = defaultdict(list)
for r in rows:
    by_sym[r["clean_symbol"]].append(r)

sym_results = []
for sym, rs in by_sym.items():
    if len(rs) < 10:
        continue
    for side in ["LONG", "SHORT"]:
        m = calc(rs, side)
        if m:
            sym_results.append({"rule": sym, "side": side, **m})

show("=== SYMBOL BUCKETS ===", sym_results, limit=60)
