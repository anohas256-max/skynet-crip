import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

LOGS = [Path("skynet_3h.log"), Path("skynet_12h.log"), Path("skynet_48h.log")]

skip_open_re = re.compile(
    r"SKIP_TRACK_OPEN \| (?P<strat>[^|]+) \| (?P<sym>[A-Z0-9]+) \| "
    r"reason=(?P<reason>[^|]+) \| entry=(?P<entry>[0-9.]+)"
)

skip_close_re = re.compile(
    r"SKIP_TRACK_CLOSE \| (?P<strat>[^|]+) \| (?P<sym>[A-Z0-9]+) \| "
    r"(?P<outcome>[^|]+) \| original_skip=(?P<reason>[^|]+) \| "
    r"HypoNet:(?P<net>[+-]?\d+\.\d+)\$ \| MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

shadow_close_re = re.compile(
    r"SHADOW_CLOSE \| (?P<strat>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<reason>[^|]+) \| "
    r".*?(?:FinalNet|Net):(?P<net>[+-]?\d+\.\d+)\$.*?"
    r"MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

selector_skip_re = re.compile(
    r"SELECTOR_RESULT \| (?P<strat>[^|]+) \| opened=\[\] \| candidates=(?P<cands>\d+) \| skips=(?P<skips>.+)"
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

def ff(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def ii(x, default=999):
    try:
        if x == "-":
            return default
        return int(float(x))
    except Exception:
        return default

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
    return f"{name:<80} n={n:4d} sum={s:+8.2f}$ avg={avg:+7.3f}$ wr={wr:5.1f}% pf={pf:6.2f}"

def classify_filter(vals):
    n, s, avg, wr, pf = metrics(vals)
    if n < 5:
        return "NEED_MORE_DATA"
    if s <= -1.0 and wr < 35:
        return "HARD_KILL_KEEP"
    if s < 0 and pf < 0.8:
        return "SOFT_PENALTY_OR_KEEP"
    if s > 0 and wr >= 50:
        return "ESCAPE_LANE_CANDIDATE"
    if abs(s) < 0.25:
        return "LOW_VALUE_FILTER_REVIEW"
    return "MIXED_DYNAMIC"

def bucket_features(ctx):
    rank = ctx.get("rank", 999)
    vol = ctx.get("vol", 0)
    pc = abs(ctx.get("pc", 0))
    score = ctx.get("score", 0)
    struct = ctx.get("struct", 999)
    brisk = ctx.get("brisk", 999)
    fb = ctx.get("fb", 999)
    spread = ctx.get("spread", 999)
    bid5 = ctx.get("bid5", 0)
    ask5 = ctx.get("ask5", 0)
    imb5 = ctx.get("imb5", 0)
    trend = ctx.get("trend", 0)
    btc = ctx.get("btc", 0)

    return [
        ("rank<=20", rank <= 20),
        ("rank<=40", rank <= 40),
        ("rank<=80", rank <= 80),
        ("vol>=8", vol >= 8),
        ("vol>=10", vol >= 10),
        ("vol>=15", vol >= 15),
        ("pc>=0.30", pc >= 0.30),
        ("pc>=0.50", pc >= 0.50),
        ("score>=3", score >= 3),
        ("score>=5", score >= 5),
        ("struct<=1", struct <= 1),
        ("struct<=3", struct <= 3),
        ("brisk<=2", brisk <= 2),
        ("fb<=1", fb <= 1),
        ("spread<=2", spread <= 2),
        ("spread<=3", spread <= 3),
        ("spread<=5", spread <= 5),
        ("bid5>=10000", bid5 >= 10000),
        ("ask5>=10000", ask5 >= 10000),
        ("imb5>=0", imb5 >= 0),
        ("imb5<=-0.10", imb5 <= -0.10),
        ("trend>0", trend > 0),
        ("btc>0", btc > 0),
    ]

def main():
    last_candidate = {}
    last_depth = {}

    filter_tax = defaultdict(list)
    filter_by_strategy = defaultdict(list)
    filter_by_symbol = defaultdict(list)
    feature_filter = defaultdict(list)

    actual_by_strategy = defaultdict(list)
    actual_by_symbol = defaultdict(list)
    actual_reason = Counter()

    selector_skip_counts = Counter()

    lines_read = 0

    for path in LOGS:
        if not path.exists():
            continue

        for raw in path.read_text(errors="ignore").splitlines():
            lines_read += 1

            m = candidate_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d["sym"]
                last_candidate[sym] = {
                    "vol": ff(d["vol"]),
                    "pc": ff(d["pc"]),
                    "oi": ff(d["oi"]),
                    "trend": ff(d["trend"]),
                    "btc": ff(d["btc"]),
                    "score": ii(d["score"]),
                    "struct": ii(d["struct"]),
                    "brisk": ii(d["brisk"]),
                    "fb": ii(d["fb"]),
                    "rank": ii(d["rank"]),
                }
                continue

            m = depth_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d["sym"]
                last_depth[sym] = {
                    "spread": ff(d["spread"]),
                    "bid5": ff(d["bid5"]),
                    "ask5": ff(d["ask5"]),
                    "imb5": ff(d["imb5"]),
                }
                continue

            m = selector_skip_re.search(raw)
            if m:
                skips = m.group("skips")
                for part in skips.split(","):
                    part = part.strip()
                    if ":" in part:
                        _, reason = part.split(":", 1)
                        selector_skip_counts[reason.strip()] += 1
                continue

            m = skip_close_re.search(raw)
            if m:
                d = m.groupdict()
                reason = d["reason"].strip()
                outcome = d["outcome"].strip()
                strat = d["strat"].strip()
                sym = d["sym"]
                net = ff(d["net"])

                # skipped trade counterfactual net:
                # positive = filter rejected something that would have paid
                # negative = filter saved us from bad trade
                key = f"{reason} -> {outcome}"
                filter_tax[key].append(net)
                filter_by_strategy[f"{reason} | {strat} -> {outcome}"].append(net)
                filter_by_symbol[f"{sym} | {reason} -> {outcome}"].append(net)

                ctx = {}
                ctx.update(last_candidate.get(sym, {}))
                ctx.update(last_depth.get(sym, {}))
                for fname, ok in bucket_features(ctx):
                    feature_filter[f"{reason} | {fname}={'Y' if ok else 'N'}"].append(net)
                continue

            m = shadow_close_re.search(raw)
            if m:
                d = m.groupdict()
                strat = d["strat"].strip()
                sym = d["sym"]
                reason = d["reason"].strip()
                net = ff(d["net"])
                actual_by_strategy[strat].append(net)
                actual_by_symbol[sym].append(net)
                actual_reason[reason] += 1
                continue

    out = []
    out.append("=" * 120)
    out.append(f"DYNAMIC FILTER INTELLIGENCE LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    out.append("=" * 120)
    out.append("Goal: replace dumb static filters with dynamic gates, penalties, and escape lanes.")
    out.append("Interpretation: positive skipped net = missed opportunity; negative skipped net = filter saved money.")
    out.append(f"logs={[str(p) for p in LOGS if p.exists()]} lines_read={lines_read}")
    out.append("")

    out.append("=" * 120)
    out.append("FILTER DECISION TABLE")
    out.append("=" * 120)
    rows = sorted(filter_tax.items(), key=lambda kv: sum(kv[1]), reverse=True)
    for k, vals in rows:
        n, s, avg, wr, pf = metrics(vals)
        out.append(f"{classify_filter(vals):<25} {line(k, vals)}")

    out.append("")
    out.append("=" * 120)
    out.append("FILTERS BY FEATURE BUCKETS, BEST ESCAPES, MIN N=3")
    out.append("=" * 120)
    rows = [(k, v) for k, v in feature_filter.items() if len(v) >= 3]
    rows.sort(key=lambda kv: (sum(kv[1]), sum(x > 0 for x in kv[1]) / len(kv[1])), reverse=True)
    for k, vals in rows[:100]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("FILTERS BY FEATURE BUCKETS, WORST / KEEP HARD, MIN N=3")
    out.append("=" * 120)
    rows.sort(key=lambda kv: sum(kv[1]))
    for k, vals in rows[:100]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("FILTER BY STRATEGY")
    out.append("=" * 120)
    rows = sorted(filter_by_strategy.items(), key=lambda kv: sum(kv[1]), reverse=True)
    for k, vals in rows[:120]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("FILTER BY SYMBOL")
    out.append("=" * 120)
    rows = sorted(filter_by_symbol.items(), key=lambda kv: sum(kv[1]), reverse=True)
    out.append("--- missed winners ---")
    for k, vals in rows[:80]:
        out.append(line(k, vals))
    out.append("--- correctly avoided losers ---")
    for k, vals in rows[-80:]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("ACTUAL STRATEGIES")
    out.append("=" * 120)
    rows = sorted(actual_by_strategy.items(), key=lambda kv: sum(kv[1]), reverse=True)
    for k, vals in rows[:80]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("SELECTOR RAW SKIP COUNTS")
    out.append("=" * 120)
    for k, v in selector_skip_counts.most_common(80):
        out.append(f"{k:<80} count={v}")

    text = "\n".join(out)
    outdir = Path("safe_exports/filter_lab")
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"dynamic_filter_intelligence_lab_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}.txt"
    fp.write_text(text)
    (outdir / "latest_dynamic_filter_intelligence_lab.txt").write_text(text)

    print(fp)
    print(text[:16000])

if __name__ == "__main__":
    main()
