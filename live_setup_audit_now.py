#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
LOGS = [
    ROOT / "skynet_3h.log",
    ROOT / "skynet_12h.log",
    ROOT / "skynet_48h.log",
]
OUT = ROOT / "live_setup_audit_latest.txt"

def ff(x, d=0.0):
    try:
        if x is None:
            return d
        return float(x)
    except Exception:
        return d

def ii(x, d=999999):
    try:
        if x is None or x == "-":
            return d
        return int(float(x))
    except Exception:
        return d

def stat(vals):
    vals = list(vals)
    n = len(vals)
    if not n:
        return dict(n=0, sum=0, avg=0, wr=0, pf=0, best=0, worst=0)
    s = sum(vals)
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    return dict(
        n=n,
        sum=s,
        avg=s/n,
        wr=sum(v > 0 for v in vals) / n * 100,
        pf=(pos / neg if neg > 0 else (999 if pos > 0 else 0)),
        best=max(vals),
        worst=min(vals),
    )

def line(name, vals):
    st = stat(vals)
    return (
        f"{name:<76} "
        f"n={st['n']:4d} sum={st['sum']:+8.2f}$ avg={st['avg']:+7.3f}$ "
        f"wr={st['wr']:5.1f}% pf={st['pf']:6.2f} "
        f"best={st['best']:+6.2f}$ worst={st['worst']:+6.2f}$"
    )

candidate_re = re.compile(
    r"\] (?P<sym>[A-Z0-9]+) \| Vol:x(?P<vol>[0-9.]+) \| Price:(?P<pc>[+-]?[0-9.]+)% \| "
    r"OI:(?P<oi>[+-]?[0-9.]+)% \| Trend15M:(?P<trend>[+-]?[0-9.]+)% \| "
    r"BTC_5M:(?P<btc>[+-]?[0-9.]+)% \| Score:(?P<score>[+-]?\d+) \| "
    r"Struct:(?P<struct>\d+) \| BRisk:(?P<brisk>\d+) FB:(?P<fb>\d+) .*? Rank:(?P<rank>\d+|-)"
)

depth_re = re.compile(
    r"DEPTH_(?:OK|SKIP) \| (?P<sym>[A-Z0-9]+).*?spread=(?P<spread>[0-9.]+)bps "
    r"\| bid5=\$(?P<bid5>[0-9.]+) ask5=\$(?P<ask5>[0-9.]+) imb5=(?P<imb5>[+-]?[0-9.]+)"
)

shadow_close_re = re.compile(
    r"SHADOW_CLOSE \| (?P<strategy>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<reason>[^|]+) \| "
    r".*?(?:FinalNet|Net):(?P<net>[+-]?\d+\.\d+)\$.*?"
    r"MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

dry_close_re = re.compile(
    r"DRY_LIVE_CLOSE \| (?P<strategy>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<reason>[^|]+) \| "
    r"LiveNet:(?P<net>[+-]?\d+\.\d+)\$.*?"
    r"MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

skip_close_re = re.compile(
    r"SKIP_TRACK_CLOSE \| (?P<strategy>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<outcome>[^|]+) \| "
    r"original_skip=(?P<skip>[^|]+) \| HypoNet:(?P<net>[+-]?\d+\.\d+)\$ \| "
    r"MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

def buckets(ctx):
    b = []
    pc = abs(ff(ctx.get("pc")))
    vol = ff(ctx.get("vol"))
    oi = ff(ctx.get("oi"))
    trend = ff(ctx.get("trend"))
    btc = ff(ctx.get("btc"))
    score = ii(ctx.get("score"), 0)
    struct = ii(ctx.get("struct"), 999)
    brisk = ii(ctx.get("brisk"), 999)
    fb = ii(ctx.get("fb"), 999)
    rank = ii(ctx.get("rank"), 999999)
    spread = ff(ctx.get("spread"), 999)
    bid5 = ff(ctx.get("bid5"))
    ask5 = ff(ctx.get("ask5"))
    imb5 = ff(ctx.get("imb5"))

    for name, ok in [
        ("rank<=20", rank <= 20),
        ("rank<=50", rank <= 50),
        ("rank<=100", rank <= 100),
        ("pc>=0.30", pc >= 0.30),
        ("pc>=0.50", pc >= 0.50),
        ("pc>=0.70", pc >= 0.70),
        ("vol>=8", vol >= 8),
        ("vol>=12", vol >= 12),
        ("oi>0", oi > 0),
        ("oi>=1", oi >= 1),
        ("trend>0", trend > 0),
        ("trend>=0.5", trend >= 0.5),
        ("btc>0", btc > 0),
        ("score>=4", score >= 4),
        ("score>=5", score >= 5),
        ("struct<=2", struct <= 2),
        ("brisk<=2", brisk <= 2),
        ("fb<=1", fb <= 1),
        ("spread<=2", spread <= 2),
        ("spread<=5", spread <= 5),
        ("bid5>=5000", bid5 >= 5000),
        ("ask5>=5000", ask5 >= 5000),
        ("imb5>=0", imb5 >= 0),
        ("imb5<=-0.10", imb5 <= -0.10),
    ]:
        if ok:
            b.append(name)
    return b

def main():
    last_ctx = {}
    seen_lines = set()

    by_strategy = defaultdict(list)
    by_symbol = defaultdict(list)
    by_reason = defaultdict(list)
    by_setup = defaultdict(list)
    by_strategy_symbol = defaultdict(list)

    skip_by_reason = defaultdict(list)
    skip_by_symbol = defaultdict(list)
    skip_good = defaultdict(list)
    skip_bad = defaultdict(list)

    dry_by_strategy = defaultdict(list)
    dry_by_symbol = defaultdict(list)

    mfe_by_symbol = defaultdict(list)
    mae_by_symbol = defaultdict(list)

    lines_read = 0
    closes = 0
    skips = 0
    dry_closes = 0

    for path in LOGS:
        if not path.exists():
            continue

        for raw in path.read_text(errors="ignore").splitlines():
            if raw in seen_lines:
                continue
            seen_lines.add(raw)
            lines_read += 1

            m = candidate_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d.pop("sym")
                last_ctx.setdefault(sym, {}).update({
                    "vol": ff(d.get("vol")),
                    "pc": ff(d.get("pc")),
                    "oi": ff(d.get("oi")),
                    "trend": ff(d.get("trend")),
                    "btc": ff(d.get("btc")),
                    "score": ii(d.get("score"), 0),
                    "struct": ii(d.get("struct")),
                    "brisk": ii(d.get("brisk")),
                    "fb": ii(d.get("fb")),
                    "rank": ii(d.get("rank")),
                })
                continue

            m = depth_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d.pop("sym")
                last_ctx.setdefault(sym, {}).update({
                    "spread": ff(d.get("spread"), 999),
                    "bid5": ff(d.get("bid5")),
                    "ask5": ff(d.get("ask5")),
                    "imb5": ff(d.get("imb5")),
                })
                continue

            m = dry_close_re.search(raw)
            if m:
                d = m.groupdict()
                strat = d["strategy"].strip()
                sym = d["sym"].strip()
                reason = d["reason"].strip()
                net = ff(d["net"])
                mfe = ff(d["mfe"])
                mae = ff(d["mae"])
                dry_closes += 1
                dry_by_strategy[strat].append(net)
                dry_by_symbol[sym].append(net)
                by_reason["DRY:" + reason].append(net)
                mfe_by_symbol[sym].append(mfe)
                mae_by_symbol[sym].append(mae)
                continue

            m = shadow_close_re.search(raw)
            if m:
                d = m.groupdict()
                strat = d["strategy"].strip()
                sym = d["sym"].strip()
                reason = d["reason"].strip()
                net = ff(d["net"])
                mfe = ff(d["mfe"])
                mae = ff(d["mae"])
                closes += 1

                by_strategy[strat].append(net)
                by_symbol[sym].append(net)
                by_reason[reason].append(net)
                by_strategy_symbol[f"{strat} | {sym}"].append(net)
                mfe_by_symbol[sym].append(mfe)
                mae_by_symbol[sym].append(mae)

                ctx = last_ctx.get(sym, {})
                for b in buckets(ctx):
                    by_setup[b].append(net)
                continue

            m = skip_close_re.search(raw)
            if m:
                d = m.groupdict()
                strat = d["strategy"].strip()
                sym = d["sym"].strip()
                outcome = d["outcome"].strip()
                skip = d["skip"].strip()
                net = ff(d["net"])
                mfe = ff(d["mfe"])
                mae = ff(d["mae"])
                skips += 1

                key = f"{skip} -> {outcome}"
                skip_by_reason[key].append(net)
                skip_by_symbol[f"{sym} | {skip} -> {outcome}"].append(net)

                if net > 0:
                    skip_good[skip].append(net)
                else:
                    skip_bad[skip].append(net)

                mfe_by_symbol[sym].append(mfe)
                mae_by_symbol[sym].append(mae)

    out = []
    out.append("=" * 120)
    out.append(f"LIVE SETUP AUDIT UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    out.append("=" * 120)
    out.append("Goal: find actual live/shadow winners, losers, false negatives, and toxic symbols.")
    out.append("Diagnostics only. Real trading remains OFF.")
    out.append(f"logs={[str(p) for p in LOGS if p.exists()]}")
    out.append(f"unique_lines={lines_read} shadow_closes={closes} dry_closes={dry_closes} skip_closes={skips}")
    out.append("")

    sections = [
        ("DRY LIVE STRATEGIES", dry_by_strategy, 1, True),
        ("SHADOW STRATEGIES", by_strategy, 1, True),
        ("BEST SYMBOLS BY CLOSED NET", by_symbol, 1, True),
        ("WORST SYMBOLS BY CLOSED NET", by_symbol, 1, False),
        ("BEST STRATEGY+SYMBOL", by_strategy_symbol, 1, True),
        ("WORST STRATEGY+SYMBOL", by_strategy_symbol, 1, False),
        ("CLOSE REASONS", by_reason, 1, True),
        ("SETUP BUCKETS", by_setup, 2, True),
        ("FALSE NEGATIVE SKIPS THAT WOULD HAVE PAID", skip_good, 1, True),
        ("SKIPS THAT WERE GOOD TO AVOID", skip_bad, 1, False),
        ("SKIP REASON OUTCOMES BEST", skip_by_reason, 1, True),
        ("SKIP REASON OUTCOMES WORST", skip_by_reason, 1, False),
        ("SKIP SYMBOL OUTCOMES BEST", skip_by_symbol, 1, True),
        ("SKIP SYMBOL OUTCOMES WORST", skip_by_symbol, 1, False),
    ]

    for title, data, min_n, desc in sections:
        out.append("")
        out.append("=" * 120)
        out.append(title)
        out.append("=" * 120)

        rows = [(k, v) for k, v in data.items() if len(v) >= min_n]
        rows.sort(key=lambda kv: (sum(kv[1]), len(kv[1])), reverse=desc)

        for k, vals in rows[:60]:
            out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("SYMBOL MFE/MAE SNAPSHOT")
    out.append("=" * 120)

    rows = []
    for sym, mfes in mfe_by_symbol.items():
        maes = mae_by_symbol.get(sym, [])
        if not mfes:
            continue
        rows.append((
            sum(mfes) / len(mfes),
            sym,
            len(mfes),
            sum(mfes) / len(mfes),
            sum(maes) / len(maes) if maes else 0,
        ))
    rows.sort(reverse=True)

    for _, sym, n, avg_mfe, avg_mae in rows[:60]:
        out.append(f"{sym:<12} n={n:4d} avg_mfe={avg_mfe:+6.2f}% avg_mae={avg_mae:+6.2f}%")

    out.append("")
    out.append("=" * 120)
    out.append("NEXT DECISION RULE")
    out.append("=" * 120)
    out.append("If one strategy+setup has positive net and at least 3-5 examples, create a new shadow lane from that.")
    out.append("If only one symbol carries all profit, do not call it a strategy; treat it as symbol episode.")
    out.append("If skip_good is large for a specific skip reason, create a tiny escape shadow, not a real trade.")

    OUT.write_text("\n".join(out))
    print(OUT)
    print("\n".join(out[:260]))

if __name__ == "__main__":
    main()
