import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

LOGS = [Path("skynet_3h.log"), Path("skynet_12h.log"), Path("skynet_48h.log")]

# Current configured model from skynet_config.py:
# COMMISSION_RATE=0.0008 per side
# SPREAD_BPS=3
# SLIPPAGE_BPS=5 per side
SCENARIOS = {
    "CURRENT_CFG_TAKER_HEAVY": {
        "commission_per_side_bps": 8.0,
        "spread_bps": 3.0,
        "slippage_per_side_bps": 5.0,
    },
    "MEXC_TAKER_002_EST": {
        "commission_per_side_bps": 2.0,
        "spread_bps": 3.0,
        "slippage_per_side_bps": 5.0,
    },
    "MEXC_TAKER_002_LOW_SLIP": {
        "commission_per_side_bps": 2.0,
        "spread_bps": 2.0,
        "slippage_per_side_bps": 2.0,
    },
    "MAKER_FIRST_EST": {
        "commission_per_side_bps": 0.0,
        "spread_bps": 1.0,
        "slippage_per_side_bps": 1.0,
    },
}

DEFAULT_MARGIN = 3.0
DEFAULT_LEVERAGE = 4.0
DEFAULT_NOTIONAL = DEFAULT_MARGIN * DEFAULT_LEVERAGE

shadow_close_re = re.compile(
    r"SHADOW_CLOSE \| (?P<strat>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<reason>[^|]+) \| "
    r".*?Gross:(?P<gross>[+-]?\d+\.\d+)\$ Net:(?P<net>[+-]?\d+\.\d+)\$ Cost:(?P<cost>\d+\.\d+)\$ "
    r".*?MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

fade_close_re = re.compile(
    r"RESEARCH_FADE_V1_CLOSE \| (?P<profile>[^|]+) \| SHORT \| (?P<sym>[A-Z0-9]+) \| (?P<reason>[^|]+) "
    r".*?Move:(?P<move>[+-]?\d+\.\d+)% \| Gross:(?P<gross>[+-]?\d+\.\d+)\$ Net:(?P<net>[+-]?\d+\.\d+)\$ Costs:(?P<cost>\d+\.\d+)\$ "
    r".*?MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

def scenario_cost_bps(s):
    return s["commission_per_side_bps"] * 2 + s["spread_bps"] + s["slippage_per_side_bps"] * 2

def scenario_cost_usd(s, notional=DEFAULT_NOTIONAL):
    return notional * scenario_cost_bps(s) / 10000.0

def metrics(vals):
    n = len(vals)
    s = sum(vals)
    avg = s / n if n else 0.0
    wr = sum(v > 0 for v in vals) / n * 100 if n else 0.0
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    pf = pos / neg if neg > 0 else (999 if pos > 0 else 0)
    return n, s, avg, wr, pf

def line(name, vals):
    n, s, avg, wr, pf = metrics(vals)
    return f"{name:<65} n={n:4d} sum={s:+8.2f}$ avg={avg:+7.3f}$ wr={wr:5.1f}% pf={pf:6.2f}"

def main():
    rows = []

    for path in LOGS:
        if not path.exists():
            continue

        for raw in path.read_text(errors="ignore").splitlines():
            m = shadow_close_re.search(raw)
            if m:
                d = m.groupdict()
                rows.append({
                    "kind": "LONG_SHADOW",
                    "lane": d["strat"].strip(),
                    "sym": d["sym"],
                    "reason": d["reason"].strip(),
                    "gross": float(d["gross"]),
                    "net": float(d["net"]),
                    "cost": float(d["cost"]),
                    "mfe": float(d["mfe"]),
                    "mae": float(d["mae"]),
                })
                continue

            m = fade_close_re.search(raw)
            if m:
                d = m.groupdict()
                rows.append({
                    "kind": "FADE_SHORT",
                    "lane": d["profile"].strip(),
                    "sym": d["sym"],
                    "reason": d["reason"].strip(),
                    "gross": float(d["gross"]),
                    "net": float(d["net"]),
                    "cost": float(d["cost"]),
                    "mfe": float(d["mfe"]),
                    "mae": float(d["mae"]),
                })
                continue

    by_lane_net = defaultdict(list)
    by_lane_gross = defaultdict(list)
    by_lane_cost = defaultdict(list)
    by_symbol_net = defaultdict(list)

    scenario_lane = {name: defaultdict(list) for name in SCENARIOS}
    scenario_symbol = {name: defaultdict(list) for name in SCENARIOS}

    cost_killed = []
    weak_mfe = []

    for r in rows:
        key = f"{r['kind']} | {r['lane']}"
        by_lane_net[key].append(r["net"])
        by_lane_gross[key].append(r["gross"])
        by_lane_cost[key].append(r["cost"])
        by_symbol_net[r["sym"]].append(r["net"])

        if r["gross"] > 0 and r["net"] <= 0:
            cost_killed.append(r)

        if r["mfe"] < 0.35:
            weak_mfe.append(r)

        for name, s in SCENARIOS.items():
            # approximate repricing: keep observed gross, replace modeled cost
            cost = scenario_cost_usd(s)
            new_net = r["gross"] - cost
            scenario_lane[name][key].append(new_net)
            scenario_symbol[name][r["sym"]].append(new_net)

    out = []
    out.append("=" * 120)
    out.append(f"FEE INTELLIGENCE LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    out.append("=" * 120)
    out.append("Goal: understand whether strategies are losing because signal is bad or because fees/slippage eat small moves.")
    out.append(f"default_notional=${DEFAULT_NOTIONAL:.2f} margin=${DEFAULT_MARGIN:.2f} lev={DEFAULT_LEVERAGE:.1f}x")
    out.append(f"closed_rows={len(rows)}")
    out.append("")

    out.append("=" * 120)
    out.append("BREAKEVEN COST SCENARIOS")
    out.append("=" * 120)
    for name, s in SCENARIOS.items():
        bps = scenario_cost_bps(s)
        usd = scenario_cost_usd(s)
        out.append(
            f"{name:<30} breakeven={bps:5.1f}bps = {bps/100:.3f}% move | "
            f"cost=${usd:.4f} per roundtrip on ${DEFAULT_NOTIONAL:.2f} notional | "
            f"commission_side={s['commission_per_side_bps']}bps spread={s['spread_bps']}bps slip_side={s['slippage_per_side_bps']}bps"
        )

    out.append("")
    out.append("=" * 120)
    out.append("CURRENT OBSERVED NET BY LANE")
    out.append("=" * 120)
    rows_lane = sorted(by_lane_net.items(), key=lambda kv: sum(kv[1]), reverse=True)
    for k, vals in rows_lane[:80]:
        gross_vals = by_lane_gross[k]
        cost_vals = by_lane_cost[k]
        out.append(
            line(k, vals)
            + f" | gross_sum={sum(gross_vals):+.2f}$ cost_sum={sum(cost_vals):.2f}$"
        )

    out.append("")
    out.append("=" * 120)
    out.append("WHAT IF FEES WERE DIFFERENT? BY LANE")
    out.append("=" * 120)
    for scenario, data in scenario_lane.items():
        out.append("")
        out.append(f"--- {scenario} ---")
        rows2 = sorted(data.items(), key=lambda kv: sum(kv[1]), reverse=True)
        for k, vals in rows2[:40]:
            out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("COST-KILLED TRADES: GROSS > 0 BUT NET <= 0")
    out.append("=" * 120)
    cost_killed.sort(key=lambda r: r["gross"], reverse=True)
    for r in cost_killed[:120]:
        out.append(
            f"{r['kind']:<12} {r['lane']:<38} {r['sym']:<8} gross={r['gross']:+.2f}$ "
            f"net={r['net']:+.2f}$ cost={r['cost']:.2f}$ mfe={r['mfe']:+.2f}% mae={r['mae']:+.2f}% reason={r['reason']}"
        )

    out.append("")
    out.append("=" * 120)
    out.append("WEAK MFE TRADES: MFE < 0.35%")
    out.append("=" * 120)
    for r in weak_mfe[:160]:
        out.append(
            f"{r['kind']:<12} {r['lane']:<38} {r['sym']:<8} gross={r['gross']:+.2f}$ "
            f"net={r['net']:+.2f}$ cost={r['cost']:.2f}$ mfe={r['mfe']:+.2f}% mae={r['mae']:+.2f}% reason={r['reason']}"
        )

    out.append("")
    out.append("=" * 120)
    out.append("SYMBOLS CURRENT NET")
    out.append("=" * 120)
    sym_rows = sorted(by_symbol_net.items(), key=lambda kv: sum(kv[1]), reverse=True)
    out.append("--- best ---")
    for k, vals in sym_rows[:60]:
        out.append(line(k, vals))
    out.append("--- worst ---")
    for k, vals in sym_rows[-60:]:
        out.append(line(k, vals))

    text = "\n".join(out)

    outdir = Path("safe_exports/fee_lab")
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"fee_intelligence_lab_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}.txt"
    fp.write_text(text)
    (outdir / "latest_fee_intelligence_lab.txt").write_text(text)

    print(fp)
    print(text[:18000])

if __name__ == "__main__":
    main()
