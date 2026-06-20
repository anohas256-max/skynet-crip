import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

LOGS = [Path("skynet_3h.log"), Path("skynet_12h.log"), Path("skynet_48h.log")]

skip_close_re = re.compile(
    r"SKIP_TRACK_CLOSE \| ([^|]+) \| ([A-Z0-9]+) \| ([^|]+) \| original_skip=([^|]+) \| HypoNet:([+-]?\d+\.\d+)\$ \| MFE:([+-]?\d+\.\d+)% MAE:([+-]?\d+\.\d+)%"
)

shadow_close_re = re.compile(
    r"SHADOW_CLOSE \| ([^|]+) \| ([A-Z0-9]+) \| ([^|]+) \| .*?(?:FinalNet|Net):([+-]?\d+\.\d+)\$.*?MFE:([+-]?\d+\.\d+)% MAE:([+-]?\d+\.\d+)%"
)

def stat(vals):
    n = len(vals)
    if not n:
        return 0, 0, 0, 0, 0
    s = sum(vals)
    avg = s / n
    wr = sum(v > 0 for v in vals) / n * 100
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    pf = pos / neg if neg > 0 else (999 if pos > 0 else 0)
    return n, s, avg, wr, pf

def line(name, vals):
    n, s, avg, wr, pf = stat(vals)
    return f"{name:<70} n={n:4d} sum={s:+8.2f}$ avg={avg:+7.3f}$ wr={wr:5.1f}% pf={pf:5.2f}"

def main():
    skip_by_reason = defaultdict(list)
    skip_by_reason_strategy = defaultdict(list)
    skip_by_symbol = defaultdict(list)

    opened_by_strategy = defaultdict(list)
    opened_by_symbol = defaultdict(list)
    opened_reason = Counter()

    lines_read = 0

    for path in LOGS:
        if not path.exists():
            continue

        for raw in path.read_text(errors="ignore").splitlines():
            lines_read += 1

            m = skip_close_re.search(raw)
            if m:
                strat, sym, outcome, reason, net, mfe, mae = m.groups()
                net = float(net)
                key = f"{reason.strip()} -> {outcome.strip()}"
                skip_by_reason[key].append(net)
                skip_by_reason_strategy[f"{reason.strip()} | {strat.strip()} -> {outcome.strip()}"].append(net)
                skip_by_symbol[f"{sym} | {reason.strip()} -> {outcome.strip()}"].append(net)
                continue

            m = shadow_close_re.search(raw)
            if m:
                strat, sym, reason, net, mfe, mae = m.groups()
                net = float(net)
                opened_by_strategy[strat.strip()].append(net)
                opened_by_symbol[sym].append(net)
                opened_reason[reason.strip()] += 1
                continue

    out = []
    out.append("=" * 120)
    out.append(f"FALSE NEGATIVE FILTER LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    out.append("=" * 120)
    out.append("Goal: find filters that reject potentially good trades.")
    out.append("This is diagnostics only. Real trading remains OFF.")
    out.append(f"logs={[str(p) for p in LOGS if p.exists()]} lines_read={lines_read}")
    out.append("")

    out.append("=" * 120)
    out.append("SKIP FILTERS: BEST COUNTERFACTUALS")
    out.append("=" * 120)
    rows = sorted(skip_by_reason.items(), key=lambda kv: (sum(kv[1]), len(kv[1])), reverse=True)
    for k, vals in rows[:50]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("SKIP FILTERS: WORST / CORRECTLY AVOIDED")
    out.append("=" * 120)
    for k, vals in rows[-50:]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("FALSE NEGATIVE BY STRATEGY")
    out.append("=" * 120)
    rows = sorted(skip_by_reason_strategy.items(), key=lambda kv: (sum(kv[1]), len(kv[1])), reverse=True)
    for k, vals in rows[:80]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("SKIPPED SYMBOLS THAT WOULD HAVE PAID")
    out.append("=" * 120)
    rows = sorted(skip_by_symbol.items(), key=lambda kv: sum(kv[1]), reverse=True)
    for k, vals in rows[:60]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("SKIPPED SYMBOLS THAT WERE GOOD TO AVOID")
    out.append("=" * 120)
    for k, vals in rows[-60:]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("ACTUAL OPENED STRATEGIES")
    out.append("=" * 120)
    rows = sorted(opened_by_strategy.items(), key=lambda kv: (sum(kv[1]), len(kv[1])), reverse=True)
    for k, vals in rows[:80]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("ACTUAL OPENED SYMBOLS")
    out.append("=" * 120)
    rows = sorted(opened_by_symbol.items(), key=lambda kv: sum(kv[1]), reverse=True)
    out.append("--- best ---")
    for k, vals in rows[:50]:
        out.append(line(k, vals))
    out.append("--- worst ---")
    for k, vals in rows[-50:]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 120)
    out.append("CLOSE REASONS")
    out.append("=" * 120)
    for k, v in opened_reason.most_common(50):
        out.append(f"{k:<50} {v}")

    text = "\n".join(out)
    outdir = Path("safe_exports/filter_lab")
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"false_negative_filter_lab_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}.txt"
    fp.write_text(text)

    latest = outdir / "latest_false_negative_filter_lab.txt"
    latest.write_text(text)

    print(fp)
    print(text[:12000])

if __name__ == "__main__":
    main()
