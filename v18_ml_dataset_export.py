#!/usr/bin/env python3
import csv
import sqlite3
from pathlib import Path

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
OUT = ROOT / "safe_exports" / "v18_ml_dataset.csv"


def q(x, d=0.0):
    try:
        if x is None:
            return d
        return float(x)
    except Exception:
        return d


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    rows = con.execute("""
        SELECT
            id, time_iso, clean_symbol, entry_price,
            price_change, vol_ratio, oi_change, rank, spread_bps,
            bid5_usd, ask5_usd, bid20_usd, ask20_usd,
            imb_5, imb_20, wall_skew,
            max_up, max_down, close_pct
        FROM signals
        WHERE closed = 1
          AND max_up IS NOT NULL
          AND max_down IS NOT NULL
          AND close_pct IS NOT NULL
        ORDER BY id
    """).fetchall()

    fields = [
        "id", "time_iso", "symbol",
        "price_change", "abs_price_change", "vol_ratio", "oi_change", "rank", "spread_bps",
        "bid5_usd", "ask5_usd", "bid20_usd", "ask20_usd",
        "imb_5", "imb_20", "wall_skew",
        "max_up", "max_down", "close_pct",
        "long_tp_first_conservative", "long_sl_conservative", "long_net_pct",
        "short_tp_first_conservative", "short_sl_conservative", "short_net_pct",
    ]

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for r in rows:
            max_up = q(r["max_up"])
            max_down = q(r["max_down"])
            close_pct = q(r["close_pct"])

            # Conservative: if both TP and SL touched, count SL.
            long_hit_tp = max_up >= 0.80
            long_hit_sl = max_down <= -0.50
            if long_hit_tp and not long_hit_sl:
                long_gross = 0.80
                long_tp = 1
                long_sl = 0
            elif long_hit_sl:
                long_gross = -0.50
                long_tp = 0
                long_sl = 1
            else:
                long_gross = close_pct
                long_tp = 0
                long_sl = 0

            short_hit_tp = max_down <= -0.80
            short_hit_sl = max_up >= 0.50
            if short_hit_tp and not short_hit_sl:
                short_gross = 0.80
                short_tp = 1
                short_sl = 0
            elif short_hit_sl:
                short_gross = -0.50
                short_tp = 0
                short_sl = 1
            else:
                short_gross = -close_pct
                short_tp = 0
                short_sl = 0

            w.writerow({
                "id": r["id"],
                "time_iso": r["time_iso"],
                "symbol": r["clean_symbol"],
                "price_change": q(r["price_change"]),
                "abs_price_change": abs(q(r["price_change"])),
                "vol_ratio": q(r["vol_ratio"]),
                "oi_change": q(r["oi_change"]),
                "rank": q(r["rank"], 999),
                "spread_bps": q(r["spread_bps"], 999),
                "bid5_usd": q(r["bid5_usd"]),
                "ask5_usd": q(r["ask5_usd"]),
                "bid20_usd": q(r["bid20_usd"]),
                "ask20_usd": q(r["ask20_usd"]),
                "imb_5": q(r["imb_5"]),
                "imb_20": q(r["imb_20"]),
                "wall_skew": q(r["wall_skew"]),
                "max_up": max_up,
                "max_down": max_down,
                "close_pct": close_pct,
                "long_tp_first_conservative": long_tp,
                "long_sl_conservative": long_sl,
                "long_net_pct": long_gross - 0.29,
                "short_tp_first_conservative": short_tp,
                "short_sl_conservative": short_sl,
                "short_net_pct": short_gross - 0.29,
            })

    con.close()

    print(f"OUT={OUT}")
    print(f"ROWS={len(rows)}")
    print(f"SIZE={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
