#!/usr/bin/env python3
import argparse
import json
import math
import re
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/root/skynet")
DATA = ROOT / "data"
SAFE = ROOT / "safe_exports"
LAB_DIR = SAFE / "lab_reports"

LOGS = [
    ROOT / "skynet_48h.log",
    ROOT / "skynet_12h.log",
    ROOT / "skynet_3h.log",
]

def ts():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

def f(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default

def pct(x):
    return f"{x:.1f}%"

def money(x):
    return f"{x:+.2f}$"

def avg(total, n):
    return total / n if n else 0.0

def run(cmd, timeout=12):
    try:
        p = subprocess.run(
            cmd,
            shell=True,
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return p.stdout.strip()
    except Exception as e:
        return f"RUN_ERROR {cmd}: {type(e).__name__}: {e}"

def header(name):
    return "\n" + "=" * 90 + f"\n{name}\n" + "=" * 90

def small_header(name):
    return "\n" + "-" * 80 + f"\n{name}\n" + "-" * 80

def parse_logs():
    close_re = re.compile(
        r"SHADOW_CLOSE \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| .*?"
        r"Net:(?P<net>[+-]?[0-9.]+)\$.*?"
        r"MFE:(?P<mfe>[+-]?[0-9.]+)% MAE:(?P<mae>[+-]?[0-9.]+)%"
    )

    dry_re = re.compile(
        r"DRY_LIVE_CLOSE \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| "
        r"LiveNet:(?P<net>[+-]?[0-9.]+)\$ ShadowNet:(?P<shadow>[+-]?[0-9.]+)\$ "
        r"Diff:(?P<diff>[+-]?[0-9.]+)\$.*?"
        r"MFE:(?P<mfe>[+-]?[0-9.]+)% MAE:(?P<mae>[+-]?[0-9.]+)%"
    )

    dry_re_loose = re.compile(
        r"DRY_LIVE_CLOSE \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| "
        r"LiveNet:(?P<net>[+-]?[0-9.]+)\$"
    )

    skip_re = re.compile(
        r"SKIP_TRACK_CLOSE \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| "
        r"original_skip=(?P<skip>[^|]+) \| HypoNet:(?P<net>[+-]?[0-9.]+)\$ \| "
        r"MFE:(?P<mfe>[+-]?[0-9.]+)% MAE:(?P<mae>[+-]?[0-9.]+)%"
    )

    open_re = re.compile(
        r"SHADOW_OPEN \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \|"
    )

    dry_open_re = re.compile(
        r"DRY_LIVE_OPEN \| (?P<strategy>[^|]+) \| (?P<symbol>[^|]+) \|"
    )

    strategy = defaultdict(lambda: {
        "n": 0, "net": 0.0, "wins": 0, "losses": 0, "mfe": 0.0, "mae": 0.0,
        "reasons": Counter(), "symbols": Counter(), "sym_net": defaultdict(float)
    })
    dry = defaultdict(lambda: {
        "n": 0, "net": 0.0, "shadow": 0.0, "diff": 0.0, "wins": 0, "losses": 0,
        "mfe": 0.0, "mae": 0.0, "reasons": Counter(), "symbols": Counter(), "sym_net": defaultdict(float)
    })
    skips = defaultdict(lambda: {
        "n": 0, "net": 0.0, "wins": 0, "losses": 0, "mfe": 0.0, "mae": 0.0,
        "reasons": Counter(), "symbols": Counter(), "sym_net": defaultdict(float)
    })
    opens = Counter()
    dry_opens = Counter()

    seen = set()

    for path in LOGS:
        if not path.exists():
            continue

        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = open_re.search(line)
            if m:
                opens[m.group("strategy").strip()] += 1

            m = dry_open_re.search(line)
            if m:
                dry_opens[m.group("strategy").strip()] += 1

            m = close_re.search(line)
            if m:
                key = ("shadow", line)
                if key in seen:
                    continue
                seen.add(key)

                s = m.group("strategy").strip()
                sym = m.group("symbol").strip()
                reason = m.group("reason").strip()
                net = f(m.group("net"))
                mfe = f(m.group("mfe"))
                mae = f(m.group("mae"))

                d = strategy[s]
                d["n"] += 1
                d["net"] += net
                d["wins"] += int(net > 0)
                d["losses"] += int(net <= 0)
                d["mfe"] += mfe
                d["mae"] += mae
                d["reasons"][reason] += 1
                d["symbols"][sym] += 1
                d["sym_net"][sym] += net
                continue

            m = dry_re.search(line) or dry_re_loose.search(line)
            if m:
                key = ("dry", line)
                if key in seen:
                    continue
                seen.add(key)

                s = m.group("strategy").strip()
                sym = m.group("symbol").strip()
                reason = m.group("reason").strip()
                net = f(m.group("net"))
                shadow = f(m.groupdict().get("shadow"))
                diff = f(m.groupdict().get("diff"))
                mfe = f(m.groupdict().get("mfe"))
                mae = f(m.groupdict().get("mae"))

                d = dry[s]
                d["n"] += 1
                d["net"] += net
                d["shadow"] += shadow
                d["diff"] += diff
                d["wins"] += int(net > 0)
                d["losses"] += int(net <= 0)
                d["mfe"] += mfe
                d["mae"] += mae
                d["reasons"][reason] += 1
                d["symbols"][sym] += 1
                d["sym_net"][sym] += net
                continue

            m = skip_re.search(line)
            if m:
                key = ("skip", line)
                if key in seen:
                    continue
                seen.add(key)

                skip = m.group("skip").strip()
                sym = m.group("symbol").strip()
                reason = m.group("reason").strip()
                net = f(m.group("net"))
                mfe = f(m.group("mfe"))
                mae = f(m.group("mae"))

                d = skips[skip]
                d["n"] += 1
                d["net"] += net
                d["wins"] += int(net > 0)
                d["losses"] += int(net <= 0)
                d["mfe"] += mfe
                d["mae"] += mae
                d["reasons"][reason] += 1
                d["symbols"][sym] += 1
                d["sym_net"][sym] += net

    return strategy, dry, skips, opens, dry_opens

def render_strategy_block(title, data, limit=40, with_shadow=False):
    out = [header(title)]
    rows = []
    for s, d in data.items():
        if d["n"]:
            rows.append((d["net"], s, d))

    if not rows:
        out.append("[EMPTY]")
        return "\n".join(out)

    for net, s, d in sorted(rows, reverse=True)[:limit]:
        n = d["n"]
        wr = d["wins"] / n * 100
        avg_net = d["net"] / n
        avg_mfe = d["mfe"] / n
        avg_mae = d["mae"] / n

        extra = ""
        if with_shadow:
            extra = f" shadow={money(d['shadow'])} diff={money(d['diff'])}"

        best = sorted(d["sym_net"].items(), key=lambda x: x[1], reverse=True)[:5]
        worst = sorted(d["sym_net"].items(), key=lambda x: x[1])[:5]

        out.append(
            f"{s:42s} n={n:4d} net={money(d['net']):>8s} avg={money(avg_net):>8s} "
            f"wr={wr:5.1f}% mfe={avg_mfe:+.2f}% mae={avg_mae:+.2f}%{extra} "
            f"reasons={dict(d['reasons'])}"
        )
        out.append(f"   best_symbols ={best}")
        out.append(f"   worst_symbols={worst}")

    return "\n".join(out)

def render_skip_block(skips):
    out = [header("SKIP / HYPOTHETICAL TRACKING")]
    rows = []
    for s, d in skips.items():
        if d["n"]:
            rows.append((d["net"], s, d))

    if not rows:
        out.append("[EMPTY]")
        return "\n".join(out)

    for net, s, d in sorted(rows, reverse=True)[:50]:
        n = d["n"]
        out.append(
            f"{s[:46]:46s} n={n:4d} hypoNet={money(d['net']):>8s} avg={money(d['net']/n):>8s} "
            f"wr={d['wins']/n*100:5.1f}% mfe={d['mfe']/n:+.2f}% mae={d['mae']/n:+.2f}% "
            f"reasons={dict(d['reasons'])} symbols={dict(d['symbols'].most_common(8))}"
        )

    return "\n".join(out)

def connect_readonly(path: Path):
    if not path.exists():
        return None
    uri = f"file:{path}?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True, timeout=5)
        con.row_factory = sqlite3.Row
        return con
    except Exception:
        try:
            con = sqlite3.connect(str(path), timeout=5)
            con.row_factory = sqlite3.Row
            return con
        except Exception:
            return None

def sql_one(con, q, args=()):
    try:
        return con.execute(q, args).fetchone()
    except Exception:
        return None

def sql_all(con, q, args=()):
    try:
        return con.execute(q, args).fetchall()
    except Exception:
        return []

def render_recorder():
    db = DATA / "skynet_recorder.sqlite3"
    out = [header("RECORDER / LIVE CANDIDATES")]
    con = connect_readonly(db)
    if not con:
        out.append(f"[NO DB] {db}")
        return "\n".join(out)

    r = sql_one(con, "SELECT COUNT(*) n FROM candidate_events")
    out.append(f"candidate_events={r['n'] if r else 0}")

    r = sql_one(con, """
        SELECT
          AVG(spread_bps) avg_spread,
          AVG(price_change) avg_pc,
          AVG(vol_ratio) avg_vol,
          AVG(oi_change) avg_oi,
          MIN(time_iso) first_time,
          MAX(time_iso) last_time
        FROM candidate_events
    """)
    if r:
        out.append(
            f"first={r['first_time']} last={r['last_time']} "
            f"avg_spread={f(r['avg_spread']):.2f} avg_pc={f(r['avg_pc']):+.3f}% "
            f"avg_vol={f(r['avg_vol']):.2f} avg_oi={f(r['avg_oi']):+.2f}%"
        )

    out.append(small_header("Top symbols by candidate count"))
    rows = sql_all(con, """
        SELECT clean_symbol, COUNT(*) n, AVG(spread_bps) spread, AVG(price_change) pc,
               AVG(vol_ratio) vol, AVG(oi_change) oi
        FROM candidate_events
        GROUP BY clean_symbol
        ORDER BY n DESC
        LIMIT 30
    """)
    for r in rows:
        out.append(
            f"{r['clean_symbol']:12s} n={r['n']:4d} spread={f(r['spread']):6.2f} "
            f"pc={f(r['pc']):+6.3f}% vol={f(r['vol']):6.2f} oi={f(r['oi']):+7.2f}%"
        )

    out.append(small_header("Recent candidates"))
    rows = sql_all(con, """
        SELECT time_iso, clean_symbol, price_change, vol_ratio, oi_change, trend_15m,
               btc_5m_change, score, structure_risk, depth_ok, depth_reason, spread_bps
        FROM candidate_events
        ORDER BY ts DESC
        LIMIT 25
    """)
    for r in rows:
        out.append(
            f"{r['time_iso']} {r['clean_symbol']:10s} pc={f(r['price_change']):+5.2f}% "
            f"vol={f(r['vol_ratio']):5.1f} oi={f(r['oi_change']):+6.2f}% "
            f"trend15={f(r['trend_15m']):+5.2f}% btc5={f(r['btc_5m_change']):+5.2f}% "
            f"score={r['score']} srisk={r['structure_risk']} depth={r['depth_ok']} "
            f"reason={r['depth_reason']} spread={f(r['spread_bps']):.2f}"
        )

    con.close()
    return "\n".join(out)

def render_v17():
    db = DATA / "v17_microstructure.sqlite3"
    out = [header("V17 MICROSTRUCTURE EDGE")]
    con = connect_readonly(db)
    if not con:
        out.append(f"[NO DB] {db}")
        return "\n".join(out)

    r = sql_one(con, """
        SELECT COUNT(*) n,
               AVG(long_net_5m) long_avg,
               SUM(long_net_5m) long_sum,
               AVG(short_net_5m) short_avg,
               SUM(short_net_5m) short_sum,
               AVG(max_up_5m) mfe,
               AVG(max_down_5m) mae,
               AVG(close_5m) close_avg
        FROM signals
        WHERE long_net_5m IS NOT NULL AND short_net_5m IS NOT NULL
    """)
    if r:
        out.append(
            f"closed={r['n']} LONG sum={money(f(r['long_sum']))} avg={money(f(r['long_avg']))} | "
            f"SHORT sum={money(f(r['short_sum']))} avg={money(f(r['short_avg']))} | "
            f"avg_mfe={f(r['mfe']):+.3f}% avg_mae={f(r['mae']):+.3f}% close_avg={f(r['close_avg']):+.3f}%"
        )

    buckets = [
        ("spread<=2", "spread_bps <= 2"),
        ("spread<=3", "spread_bps <= 3"),
        ("spread 3..7", "spread_bps > 3 AND spread_bps <= 7"),
        ("spread>7", "spread_bps > 7"),
        ("rank<=40", "current_turnover_rank <= 40"),
        ("rank<=80", "current_turnover_rank <= 80"),
        ("rank>150", "current_turnover_rank > 150"),
        ("pc_pos", "price_change > 0"),
        ("pc_neg", "price_change < 0"),
        ("pc_abs>=0.7", "ABS(price_change) >= 0.7"),
        ("oi_pos", "oi_change > 0"),
        ("oi_neg", "oi_change < 0"),
        ("imb_bid", "imb_5 > 0.2"),
        ("imb_ask", "imb_5 < -0.2"),
        ("wall_pos", "wall_skew > 0"),
        ("wall_neg", "wall_skew < 0"),
    ]

    out.append(small_header("Simple buckets"))
    for name, where in buckets:
        r = sql_one(con, f"""
            SELECT COUNT(*) n,
                   AVG(long_net_5m) long_avg, SUM(long_net_5m) long_sum,
                   AVG(short_net_5m) short_avg, SUM(short_net_5m) short_sum,
                   AVG(max_up_5m) mfe, AVG(max_down_5m) mae
            FROM signals
            WHERE long_net_5m IS NOT NULL AND short_net_5m IS NOT NULL AND {where}
        """)
        if r and r["n"]:
            out.append(
                f"{name:14s} n={r['n']:4d} "
                f"L_avg={money(f(r['long_avg'])):>8s} L_sum={money(f(r['long_sum'])):>8s} "
                f"S_avg={money(f(r['short_avg'])):>8s} S_sum={money(f(r['short_sum'])):>8s} "
                f"mfe={f(r['mfe']):+.2f}% mae={f(r['mae']):+.2f}%"
            )

    combo_defs = []
    for pc_name, pc_where in [
        ("PC_NEG", "price_change < 0"),
        ("PC_POS", "price_change > 0"),
        ("PC_ABS070", "ABS(price_change) >= 0.7"),
        ("PC_SMALL", "ABS(price_change) < 0.3"),
    ]:
        for sp_name, sp_where in [
            ("SP2", "spread_bps <= 2"),
            ("SP3", "spread_bps <= 3"),
            ("SP7", "spread_bps <= 7"),
            ("SP12", "spread_bps <= 12"),
        ]:
            for rank_name, rank_where in [
                ("R40", "current_turnover_rank <= 40"),
                ("R80", "current_turnover_rank <= 80"),
                ("R150", "current_turnover_rank <= 150"),
            ]:
                for vol_name, vol_where in [
                    ("V3", "vol_ratio >= 3"),
                    ("V5", "vol_ratio >= 5"),
                    ("V8", "vol_ratio >= 8"),
                ]:
                    combo_defs.append((
                        f"{pc_name}|{sp_name}|{rank_name}|{vol_name}",
                        f"{pc_where} AND {sp_where} AND {rank_where} AND {vol_where}"
                    ))

    rows = []
    for name, where in combo_defs:
        r = sql_one(con, f"""
            SELECT COUNT(*) n,
                   AVG(long_net_5m) long_avg, SUM(long_net_5m) long_sum,
                   AVG(short_net_5m) short_avg, SUM(short_net_5m) short_sum,
                   SUM(CASE WHEN long_net_5m > 0 THEN 1 ELSE 0 END) long_wins,
                   SUM(CASE WHEN short_net_5m > 0 THEN 1 ELSE 0 END) short_wins,
                   AVG(max_up_5m) mfe, AVG(max_down_5m) mae
            FROM signals
            WHERE long_net_5m IS NOT NULL AND short_net_5m IS NOT NULL AND {where}
        """)
        if not r or r["n"] < 30:
            continue
        n = r["n"]
        rows.append((f(r["long_sum"]), "LONG", name, r))
        rows.append((f(r["short_sum"]), "SHORT", name, r))

    out.append(small_header("Top V17 combo buckets by sum net, min_n=30"))
    for total, side, name, r in sorted(rows, reverse=True)[:40]:
        n = r["n"]
        if side == "LONG":
            avgv = f(r["long_avg"])
            sumv = f(r["long_sum"])
            wr = f(r["long_wins"]) / n * 100
        else:
            avgv = f(r["short_avg"])
            sumv = f(r["short_sum"])
            wr = f(r["short_wins"]) / n * 100
        out.append(
            f"{side:5s} {name:26s} n={n:4d} sum={money(sumv):>8s} avg={money(avgv):>8s} "
            f"wr={wr:5.1f}% mfe={f(r['mfe']):+.2f}% mae={f(r['mae']):+.2f}%"
        )

    con.close()
    return "\n".join(out)

def render_v18():
    db = DATA / "v18_micro_paths.sqlite3"
    out = [header("V18 PATH RECORDER")]
    con = connect_readonly(db)
    if not con:
        out.append(f"[NO DB] {db}")
        return "\n".join(out)

    r = sql_one(con, """
        SELECT COUNT(*) n,
               SUM(CASE WHEN closed=1 THEN 1 ELSE 0 END) closed_n,
               AVG(max_up) avg_up,
               AVG(max_down) avg_down,
               AVG(close_pct) avg_close,
               AVG(spread_bps) avg_spread
        FROM signals
    """)
    if r:
        out.append(
            f"signals={r['n']} closed={r['closed_n']} avg_up={f(r['avg_up']):+.3f}% "
            f"avg_down={f(r['avg_down']):+.3f}% avg_close={f(r['avg_close']):+.3f}% "
            f"avg_spread={f(r['avg_spread']):.2f}bps"
        )

    out.append(small_header("V18 simple buckets, closed only"))
    buckets = [
        ("spread<=3", "spread_bps <= 3"),
        ("spread 3..7", "spread_bps > 3 AND spread_bps <= 7"),
        ("spread>7", "spread_bps > 7"),
        ("rank<=40", "rank <= 40"),
        ("rank<=80", "rank <= 80"),
        ("pc_pos", "price_change > 0"),
        ("pc_neg", "price_change < 0"),
        ("oi_pos", "oi_change > 0"),
        ("oi_neg", "oi_change < 0"),
    ]
    for name, where in buckets:
        r = sql_one(con, f"""
            SELECT COUNT(*) n, AVG(max_up) up, AVG(max_down) down, AVG(close_pct) closep
            FROM signals
            WHERE closed=1 AND {where}
        """)
        if r and r["n"]:
            out.append(
                f"{name:12s} n={r['n']:4d} up={f(r['up']):+.3f}% down={f(r['down']):+.3f}% close={f(r['closep']):+.3f}%"
            )

    con.close()
    return "\n".join(out)

def render_config_and_system():
    out = [header("CONFIG / SYSTEM SNAPSHOT")]
    out.append(run("git log --oneline --decorate --max-count=5"))
    out.append("")
    out.append(run("git status --short"))
    out.append("")
    out.append(run("systemctl is-active skynet.service || true"))
    out.append("")
    out.append(run("systemctl status skynet.service --no-pager -l | head -25 || true"))

    code = r'''
import skynet_config as cfg
names = [
"BOT_VERSION","LIVE_ENABLED","LIVE_DRY_RUN","LIVE_DRY_TRACKS",
"REAL_TRADING_ENABLED","REAL_TRADING_ARMED","REAL_STRATEGY",
"COMMISSION_RATE","SPREAD_BPS","SLIPPAGE_BPS","DRY_RUN_EXECUTION_SLIPPAGE_BPS",
"SMART_V2_CORE_TOP","SMART_V2_MID_TOP","SMART_V2_SPREAD_LIMIT_BPS","SMART_V2_CORE_RISK_GATE_ENABLED",
"META_V12_SPREAD_LIMIT_BPS","META_V12_MAX_BRISK","META_V12_MAX_FALSE_BREAKOUTS",
"TG_TARGET",
]
for n in names:
    print(f"{n}={getattr(cfg,n,None)}")
'''
    out.append(small_header("Important config"))
    out.append(run(f"{ROOT}/.venv/bin/python - <<'PY'\n{code}\nPY"))
    return "\n".join(out)

def build_report():
    strategy, dry, skips, opens, dry_opens = parse_logs()

    out = []
    out.append(f"SKYNET LAB REPORT UTC={ts()}")
    out.append("Goal: find robust positive edge before real trading. Real remains disabled.")
    out.append(render_config_and_system())

    out.append(header("OPEN COUNTERS FROM LOGS"))
    out.append("shadow_opens=" + str(dict(opens.most_common(30))))
    out.append("dry_live_opens=" + str(dict(dry_opens.most_common(30))))

    out.append(render_strategy_block("DRY LIVE CLOSED TRADES", dry, with_shadow=True))
    out.append(render_strategy_block("SHADOW CLOSED TRADES", strategy, with_shadow=False))
    out.append(render_skip_block(skips))
    out.append(render_recorder())
    out.append(render_v17())
    out.append(render_v18())

    out.append(header("READ THIS FIRST / CURRENT DECISION"))
    out.append(
        "1) Real trading stays OFF until dry-live is positive and stable.\n"
        "2) Current important dry tracks: SMART_V2_STRICT_CLEAN_MO1, SMART_V2_STRICT_OI_MO1, META_V12_EXEC_SAFE_MO1.\n"
        "3) V17 global edge is negative in both LONG and SHORT; only small buckets may be useful.\n"
        "4) Next work should be: kill toxic selectors, compare long continuation vs short/fade in research only, improve reporting.\n"
        "5) Do not trust isolated green trades; use this report + context pack."
    )

    return "\n".join(out) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    text = build_report()

    if args.stdout:
        print(text)
        return

    LAB_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else LAB_DIR / f"skynet_lab_report_{ts()}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8", errors="ignore")
    print(out_path)

if __name__ == "__main__":
    main()
