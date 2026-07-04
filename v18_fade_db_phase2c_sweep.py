#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

DB = Path("/root/skynet/data/v18_micro_paths.sqlite3")

START = "2026-07-03T18:43:47"
BLACKLIST = {"ALLO", "XPL"}

# shadow model copied from current service idea:
# SHORT after pump, TP/SL checked on already recorded path fields if available.
# If future path fields are missing, this script still prints candidate counts.
TP = 3.0
SL = 0.3
COST_PCT = 0.03

PC_MINS = [0.3, 0.5, 0.7, 0.9]
VOL_MINS = [8, 10, 12, 15, 20]
SPREAD_MAXS = [1.0, 2.0, 3.0]
RANK_MAXS = [10, 20, 30, 50]

def pick(row, *names):
    keys = row.keys()
    for n in names:
        if n in keys:
            return row[n]
    return None

def simulate_short(row):
    """
    Best effort:
    - if v18 path columns exist, use them;
    - otherwise only count candidate and mark no_result.
    """
    price = pick(row, "price", "entry_price")
    if price is None:
        return None

    # v18_micro_paths.sqlite3 actual columns:
    # max_up    = maximum move UP after signal, bad for SHORT
    # max_down  = maximum move DOWN after signal, good for SHORT
    # close_pct = final pct move after TTL/window; positive means price up, negative means price down
    max_up = pick(row, "max_up", "max_up_5m", "max_up_pct", "max_adverse_pct", "short_mae_5m")
    max_down = pick(row, "max_down", "max_down_5m", "max_down_pct", "max_favorable_pct", "short_mfe_5m")
    close_5m = pick(row, "close_pct", "close_5m", "close_5m_pct", "short_net_5m")

    # For SHORT:
    # favorable = price down => max_down is usually negative percent.
    # adverse = price up => max_up is positive percent.
    if max_up is None or max_down is None or close_5m is None:
        return None

    adverse = float(max_up)
    favorable = abs(float(max_down))
    close = float(close_5m)

    if adverse >= SL:
        gross_pct = -SL
        reason = "SL"
    elif favorable >= TP:
        gross_pct = TP
        reason = "TP"
    else:
        gross_pct = -close
        reason = "TIME"

    net_pct = gross_pct - COST_PCT
    return net_pct, reason

def pf(vals):
    pos = sum(x for x in vals if x > 0)
    neg = -sum(x for x in vals if x < 0)
    if neg == 0:
        return 999.0 if pos > 0 else 0.0
    return pos / neg

def main():
    if not DB.exists():
        raise SystemExit(f"missing db: {DB}")

    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row

    cols = [r[1] for r in con.execute("PRAGMA table_info(signals)").fetchall()]
    print("====================================================================================================")
    print(f"V18 FADE DB PHASE2C SWEEP UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    print("====================================================================================================")
    print("db=", DB)
    print("start=", START)
    print("columns=", ",".join(cols))
    print()

    rows = con.execute("""
        SELECT *
        FROM signals
        WHERE time_iso >= ?
          AND clean_symbol NOT IN ('ALLO','XPL')
        ORDER BY id ASC
    """, (START,)).fetchall()

    print(f"rows_since_start_ex_blacklist={len(rows)}")
    print()

    results = []
    for pc_min in PC_MINS:
        for vol_min in VOL_MINS:
            for spread_max in SPREAD_MAXS:
                for rank_max in RANK_MAXS:
                    cand = []
                    vals = []
                    reasons = defaultdict(int)

                    for r in rows:
                        sym = str(r["clean_symbol"])
                        if sym in BLACKLIST:
                            continue

                        pc = r["price_change"]
                        vol = r["vol_ratio"]
                        spread = r["spread_bps"]
                        rank = r["rank"] if "rank" in r.keys() else r["current_turnover_rank"] if "current_turnover_rank" in r.keys() else None

                        if pc is None or vol is None or spread is None or rank is None:
                            continue

                        if float(pc) >= pc_min and float(vol) >= vol_min and float(spread) <= spread_max and int(rank) <= rank_max:
                            cand.append(r)
                            sim = simulate_short(r)
                            if sim is not None:
                                net_pct, reason = sim
                                vals.append(net_pct)
                                reasons[reason] += 1

                    n = len(cand)
                    sim_n = len(vals)
                    net = sum(vals)
                    avg = net / sim_n if sim_n else 0.0
                    wr = 100.0 * sum(1 for x in vals if x > 0) / sim_n if sim_n else 0.0
                    p = pf(vals) if sim_n else 0.0
                    results.append((sim_n, n, net, avg, wr, p, pc_min, vol_min, spread_max, rank_max, dict(reasons)))

    print("=== TOP BY CANDIDATE COUNT ===")
    for sim_n, n, net, avg, wr, p, pc_min, vol_min, spread_max, rank_max, reasons in sorted(results, key=lambda x: (-x[1], x[6], x[7], x[8], x[9]))[:40]:
        print(f"pc>={pc_min:<3} vol>={vol_min:<2} spread<={spread_max:<3} rank<={rank_max:<2} candidates={n:4d} simulated={sim_n:4d} net_pct={net:+8.3f} avg={avg:+7.4f} WR={wr:5.1f}% PF={p:6.2f} reasons={reasons}")

    print()
    print("=== TOP BY SIM NET, n>=10 ===")
    top = [x for x in results if x[0] >= 10]
    for sim_n, n, net, avg, wr, p, pc_min, vol_min, spread_max, rank_max, reasons in sorted(top, key=lambda x: (x[2], x[3]), reverse=True)[:40]:
        print(f"pc>={pc_min:<3} vol>={vol_min:<2} spread<={spread_max:<3} rank<={rank_max:<2} candidates={n:4d} simulated={sim_n:4d} net_pct={net:+8.3f} avg={avg:+7.4f} WR={wr:5.1f}% PF={p:6.2f} reasons={reasons}")

    print()
    print("=== RECENT PHASE2C-COMPATIBLE ROWS ===")
    for r in con.execute("""
        SELECT id, time_iso, clean_symbol,
               ROUND(price_change,3) AS pc,
               ROUND(vol_ratio,1) AS vol,
               ROUND(spread_bps,2) AS spread,
               rank
        FROM signals
        WHERE time_iso >= ?
          AND price_change >= 0.50
          AND vol_ratio >= 15
          AND spread_bps <= 3
          AND rank <= 30
          AND clean_symbol NOT IN ('ALLO','XPL')
        ORDER BY id DESC
        LIMIT 80
    """, (START,)):
        print(dict(r))

if __name__ == "__main__":
    main()
