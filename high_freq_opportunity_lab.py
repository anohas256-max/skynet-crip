import re
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime, timezone

LOGS = [Path("skynet_3h.log"), Path("skynet_12h.log"), Path("skynet_48h.log")]

money_re = re.compile(r"(?:Net|FinalNet|HypoNet):([+-]?\d+\.\d+)\$")
shadow_open_re = re.compile(r"SHADOW_OPEN \| ([^|]+) \| ([A-Z0-9]+)")
shadow_close_re = re.compile(r"SHADOW_CLOSE \| ([^|]+) \| ([A-Z0-9]+) \| ([^|]+) \| .*?(?:FinalNet|Net):([+-]?\d+\.\d+)\$")
skip_open_re = re.compile(r"SKIP_TRACK_OPEN \| ([^|]+) \| ([A-Z0-9]+) \| reason=([^|]+)")
skip_close_re = re.compile(r"SKIP_TRACK_CLOSE \| ([^|]+) \| ([A-Z0-9]+) \| ([^|]+) \| original_skip=([^|]+) \| HypoNet:([+-]?\d+\.\d+)\$")
fade_open_re = re.compile(r"RESEARCH_FADE_V1_OPEN \| ([^|]+) \| SHORT \| ([A-Z0-9]+).*?pc=([+-]?\d+\.\d+)% vol=x([0-9.]+) spread=([0-9.]+)bps rank=(\d+) imb5=([+-]?\d+\.\d+)")
fade_close_re = re.compile(r"RESEARCH_FADE_V1_CLOSE \| ([^|]+) \| SHORT \| ([A-Z0-9]+) \| ([^|]+) .*?Net:([+-]?\d+\.\d+)\$ .*?MFE:([+-]?\d+\.\d+)% MAE:([+-]?\d+\.\d+)%")

def stat_line(name, vals):
    n = len(vals)
    s = sum(vals)
    wr = sum(1 for v in vals if v > 0) / n * 100 if n else 0
    avg = s / n if n else 0
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    pf = pos / neg if neg > 0 else 999 if pos > 0 else 0
    return f"{name:<42} n={n:4d} sum={s:+7.2f}$ avg={avg:+6.3f}$ wr={wr:5.1f}% pf={pf:5.2f}"

def main():
    strategy_net = defaultdict(list)
    symbol_net = defaultdict(list)
    close_reason = Counter()

    skip_reason_net = defaultdict(list)
    skip_symbol_net = defaultdict(list)
    skip_outcome = Counter()

    fade_profile_net = defaultdict(list)
    fade_symbol_net = defaultdict(list)
    fade_reason = Counter()

    lines_read = 0

    for path in LOGS:
        if not path.exists():
            continue
        for line in path.read_text(errors="ignore").splitlines():
            lines_read += 1

            m = shadow_close_re.search(line)
            if m:
                strat, sym, reason, net = m.group(1).strip(), m.group(2), m.group(3).strip(), float(m.group(4))
                strategy_net[strat].append(net)
                symbol_net[sym].append(net)
                close_reason[reason] += 1
                continue

            m = skip_close_re.search(line)
            if m:
                strat, sym, outcome, original_skip, net = m.group(1).strip(), m.group(2), m.group(3).strip(), m.group(4).strip(), float(m.group(5))
                key = f"{original_skip} -> {outcome}"
                skip_reason_net[key].append(net)
                skip_symbol_net[sym].append(net)
                skip_outcome[key] += 1
                continue

            m = fade_close_re.search(line)
            if m:
                profile, sym, reason, net, mfe, mae = m.group(1).strip(), m.group(2), m.group(3).strip(), float(m.group(4)), float(m.group(5)), float(m.group(6))
                fade_profile_net[profile].append(net)
                fade_symbol_net[sym].append(net)
                fade_reason[f"{profile}:{reason}"] += 1
                continue

    out = []
    out.append("="*100)
    out.append(f"HIGH FREQUENCY OPPORTUNITY LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    out.append("="*100)
    out.append(f"logs={', '.join(str(p) for p in LOGS if p.exists())} lines_read={lines_read}")
    out.append("")
    out.append("GOAL:")
    out.append("  Find ways to increase trade count without blindly choking all candidates.")
    out.append("  This is diagnostics only. Real trading remains OFF.")
    out.append("")

    out.append("="*100)
    out.append("SHADOW STRATEGIES BY NET, MIN N=2")
    out.append("="*100)
    rows = [(k, v) for k, v in strategy_net.items() if len(v) >= 2]
    rows.sort(key=lambda kv: (sum(kv[1]), sum(x > 0 for x in kv[1]) / len(kv[1])), reverse=True)
    for k, v in rows[:40]:
        out.append(stat_line(k, v))

    out.append("")
    out.append("="*100)
    out.append("SYMBOLS BY NET, MIN N=2")
    out.append("="*100)
    rows = [(k, v) for k, v in symbol_net.items() if len(v) >= 2]
    rows.sort(key=lambda kv: sum(kv[1]), reverse=True)
    out.append("--- best ---")
    for k, v in rows[:25]:
        out.append(stat_line(k, v))
    out.append("--- worst ---")
    for k, v in rows[-25:]:
        out.append(stat_line(k, v))

    out.append("")
    out.append("="*100)
    out.append("SKIP COUNTERFACTUALS")
    out.append("="*100)
    rows = [(k, v) for k, v in skip_reason_net.items()]
    rows.sort(key=lambda kv: sum(kv[1]), reverse=True)
    for k, v in rows[:40]:
        out.append(stat_line(k, v))

    out.append("")
    out.append("="*100)
    out.append("SKIPPED SYMBOLS BY HYPOTHETICAL NET, MIN N=1")
    out.append("="*100)
    rows = list(skip_symbol_net.items())
    rows.sort(key=lambda kv: sum(kv[1]), reverse=True)
    out.append("--- missed winners ---")
    for k, v in rows[:25]:
        out.append(stat_line(k, v))
    out.append("--- correctly avoided / toxic ---")
    for k, v in rows[-25:]:
        out.append(stat_line(k, v))

    out.append("")
    out.append("="*100)
    out.append("RESEARCH FADE LIVE")
    out.append("="*100)
    for k, v in sorted(fade_profile_net.items(), key=lambda kv: sum(kv[1]), reverse=True):
        out.append(stat_line(k, v))
    out.append("")
    out.append("--- fade symbols ---")
    for k, v in sorted(fade_symbol_net.items(), key=lambda kv: sum(kv[1]), reverse=True):
        out.append(stat_line(k, v))

    out.append("")
    out.append("="*100)
    out.append("CLOSE REASONS")
    out.append("="*100)
    for k, v in close_reason.most_common(30):
        out.append(f"{k:<40} {v}")

    text = "\n".join(out)
    outdir = Path("safe_exports/opportunity_lab")
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"high_freq_opportunity_lab_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}.txt"
    fp.write_text(text)
    print(fp)
    print(text[:6000])

if __name__ == "__main__":
    main()
