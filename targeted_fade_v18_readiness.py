#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "targeted_fade_v18_readiness_latest.txt"

# V17 robust-ish candidates, checked properly on V18:
# fade SHORT only after positive pump, not abs move.
RULES = [
    ("SHORT_PC030_SP3_R150_V5", 0.30, 3.0, 150, 5.0),
    ("SHORT_PC030_SP2_R150_V5", 0.30, 2.0, 150, 5.0),
    ("SHORT_PC050_SP3_R150_V5", 0.50, 3.0, 150, 5.0),
    ("SHORT_PC070_SP3_R150_V8", 0.70, 3.0, 150, 8.0),
    ("SHORT_PC030_SP5_R80_V8",  0.30, 5.0, 80,  8.0),
]

TP_SL = [
    (0.5, 0.3),
    (0.75, 0.3),
    (1.0, 0.3),
    (1.5, 0.3),
    (2.0, 0.3),
    (3.0, 0.3),
    (1.0, 0.5),
    (2.0, 0.5),
    (3.0, 0.5),
]

COSTS = [0.03, 0.05, 0.10, 0.17, 0.29]

MIN_ALL = 60
MIN_TRAIN = 35
MIN_TEST = 15

def fmt(st):
    if not st or st["n"] == 0:
        return "n=0"
    return (
        f"n={st['n']:5d} sum={st['sum']:+9.2f}% avg={st['avg']:+8.4f}% "
        f"wr={st['wr']:5.1f}% pf={st['pf']:6.2f} "
        f"tp={st['tp']:4d} sl={st['sl']:4d} time={st['time']:4d}"
    )

def calc_stats(con, where_sql, params, tp, sl, cost):
    # Conservative SHORT:
    # if SL and TP both touched, SL wins.
    # SHORT loses when max_up >= SL.
    # SHORT wins when abs(max_down) >= TP.
    q = f"""
    WITH x AS (
      SELECT
        CASE
          WHEN max_up >= ? THEN -? - ?
          WHEN ABS(max_down) >= ? THEN ? - ?
          ELSE -COALESCE(close_pct, 0) - ?
        END AS net,
        CASE
          WHEN max_up >= ? THEN 'SL'
          WHEN ABS(max_down) >= ? THEN 'TP'
          ELSE 'TIME'
        END AS reason
      FROM signals
      WHERE {where_sql}
    )
    SELECT
      COUNT(*) AS n,
      COALESCE(SUM(net),0) AS sum_net,
      COALESCE(AVG(net),0) AS avg_net,
      COALESCE(AVG(CASE WHEN net > 0 THEN 1.0 ELSE 0.0 END),0) AS wr,
      COALESCE(SUM(CASE WHEN net > 0 THEN net ELSE 0 END),0) AS pos_sum,
      COALESCE(SUM(CASE WHEN net < 0 THEN -net ELSE 0 END),0) AS neg_sum,
      SUM(CASE WHEN reason='TP' THEN 1 ELSE 0 END) AS tp_n,
      SUM(CASE WHEN reason='SL' THEN 1 ELSE 0 END) AS sl_n,
      SUM(CASE WHEN reason='TIME' THEN 1 ELSE 0 END) AS time_n
    FROM x
    """
    row = con.execute(q, [sl, sl, cost, tp, tp, cost, cost, sl, tp] + list(params)).fetchone()
    n = int(row["n"] or 0)
    pos = float(row["pos_sum"] or 0)
    neg = float(row["neg_sum"] or 0)
    pf = pos / neg if neg > 0 else 999 if pos > 0 else 0
    return {
        "n": n,
        "sum": float(row["sum_net"] or 0),
        "avg": float(row["avg_net"] or 0),
        "wr": float(row["wr"] or 0) * 100,
        "pf": pf,
        "tp": int(row["tp_n"] or 0),
        "sl": int(row["sl_n"] or 0),
        "time": int(row["time_n"] or 0),
    }

def symbol_stats(con, where_sql, params, tp, sl, cost):
    q = f"""
    WITH x AS (
      SELECT
        clean_symbol AS symbol,
        CASE
          WHEN max_up >= ? THEN -? - ?
          WHEN ABS(max_down) >= ? THEN ? - ?
          ELSE -COALESCE(close_pct, 0) - ?
        END AS net
      FROM signals
      WHERE {where_sql}
    )
    SELECT
      symbol,
      COUNT(*) AS n,
      SUM(net) AS sum_net,
      AVG(net) AS avg_net,
      AVG(CASE WHEN net > 0 THEN 1.0 ELSE 0 END) AS wr
    FROM x
    GROUP BY symbol
    HAVING n >= 2
    ORDER BY sum_net DESC
    LIMIT 12
    """
    rows = con.execute(q, [sl, sl, cost, tp, tp, cost, cost] + list(params)).fetchall()
    return rows

def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    row = con.execute("SELECT COUNT(*) n, MIN(id) min_id, MAX(id) max_id FROM signals").fetchone()
    total = int(row["n"])
    min_id = int(row["min_id"])
    max_id = int(row["max_id"])
    split_id = min_id + int((max_id - min_id) * 0.70)

    results = []

    for name, pc, spread, rank, vol in RULES:
        base_where = """
          price_change >= ?
          AND vol_ratio >= ?
          AND spread_bps <= ?
          AND rank <= ?
          AND closed = 1
        """
        base_params = [pc, vol, spread, rank]

        for tp, sl in TP_SL:
            for cost in COSTS:
                all_st = calc_stats(con, base_where, base_params, tp, sl, cost)
                tr_st = calc_stats(con, base_where + " AND id <= ?", base_params + [split_id], tp, sl, cost)
                te_st = calc_stats(con, base_where + " AND id > ?", base_params + [split_id], tp, sl, cost)

                robust = (
                    all_st["n"] >= MIN_ALL and tr_st["n"] >= MIN_TRAIN and te_st["n"] >= MIN_TEST
                    and all_st["sum"] > 0 and tr_st["sum"] > 0 and te_st["sum"] > 0
                    and all_st["avg"] > 0.005
                    and all_st["pf"] > 1.05
                    and te_st["pf"] > 1.02
                )

                score = all_st["sum"] + tr_st["sum"] * 0.5 + te_st["sum"] * 2.0 + all_st["pf"]
                results.append((robust, score, name, pc, spread, rank, vol, tp, sl, cost, all_st, tr_st, te_st, base_where, base_params))

    results.sort(key=lambda x: (x[0], x[1]), reverse=True)

    lines = []
    lines.append("=" * 120)
    lines.append(f"TARGETED FADE V18 READINESS FAST SQL UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 120)
    lines.append(f"db={DB}")
    lines.append(f"rows={total} split_id={split_id}")
    lines.append("Goal: verify V17 fade-short rules on V18 path recorder using positive pump only.")
    lines.append("Real remains OFF.")
    lines.append("")

    robust_count = sum(1 for r in results if r[0])
    lines.append(f"robust_count={robust_count}")
    lines.append("")

    lines.append("=== ROBUST CONFIGS ===")
    if robust_count == 0:
        lines.append("NO ROBUST CONFIGS.")
    else:
        for r in results:
            robust, score, name, pc, spread, rank, vol, tp, sl, cost, all_st, tr_st, te_st, where_sql, params = r
            if not robust:
                continue
            lines.append("")
            lines.append(f"[ROBUST] score={score:.2f} {name} TP={tp} SL={sl} cost={cost}")
            lines.append("  ALL   " + fmt(all_st))
            lines.append("  TRAIN " + fmt(tr_st))
            lines.append("  TEST  " + fmt(te_st))
            syms = symbol_stats(con, where_sql, params, tp, sl, cost)
            lines.append("  symbols:")
            for s in syms:
                lines.append(
                    f"    {s['symbol']:<12} n={int(s['n']):4d} "
                    f"sum={float(s['sum_net']):+8.2f}% avg={float(s['avg_net']):+7.4f}% "
                    f"wr={float(s['wr'] or 0)*100:5.1f}%"
                )

    lines.append("")
    lines.append("=== TOP 40 ALL CONFIGS ===")
    for r in results[:40]:
        robust, score, name, pc, spread, rank, vol, tp, sl, cost, all_st, tr_st, te_st, where_sql, params = r
        tag = "ROBUST" if robust else "weak"
        lines.append("")
        lines.append(f"[{tag}] score={score:.2f} {name} TP={tp} SL={sl} cost={cost}")
        lines.append("  ALL   " + fmt(all_st))
        lines.append("  TRAIN " + fmt(tr_st))
        lines.append("  TEST  " + fmt(te_st))

    lines.append("")
    lines.append("=" * 120)
    lines.append("DECISION")
    lines.append("=" * 120)
    if robust_count:
        lines.append("V18 confirms at least one fade-short candidate. Next step: one shadow-only live lane from exact best config.")
    else:
        lines.append("V18 does NOT confirm V17 fade-short edge. Do not make this real.")
        lines.append("Taker-scalper remains rejected. Next serious path: external/catalyst/cross-market/funding/OI source or true maker book simulator.")

    OUT.write_text("\n".join(lines))
    print("\n".join(lines))
    con.close()

if __name__ == "__main__":
    main()
