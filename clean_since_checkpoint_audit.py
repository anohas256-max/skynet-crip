#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
LOGS = [ROOT / "skynet_3h.log", ROOT / "skynet_12h.log", ROOT / "skynet_48h.log"]
OUT = ROOT / "clean_since_checkpoint_audit_latest.txt"

close_re = re.compile(
    r"SHADOW_CLOSE \| (?P<strategy>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<reason>[^|]+) \| "
    r".*?(?:FinalNet|Net):(?P<net>[+-]?\d+\.\d+)\$.*?MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

skip_re = re.compile(
    r"SKIP_TRACK_CLOSE \| (?P<strategy>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<outcome>[^|]+) \| "
    r"original_skip=(?P<skip>[^|]+) \| HypoNet:(?P<net>[+-]?\d+\.\d+)\$ \| "
    r"MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

def f(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def stat(vals):
    if not vals:
        return "n=0 sum=+0.00$ avg=+0.000$ wr=0.0% pf=0.00"
    s = sum(vals)
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    pf = pos / neg if neg > 0 else 999 if pos > 0 else 0
    wr = sum(v > 0 for v in vals) / len(vals) * 100
    return f"n={len(vals)} sum={s:+.2f}$ avg={s/len(vals):+.3f}$ wr={wr:.1f}% pf={pf:.2f}"

def main():
    seen = set()
    closes = []
    skips = []

    by_strategy = defaultdict(list)
    by_symbol = defaultdict(list)
    by_skip = defaultdict(list)
    by_skip_symbol = defaultdict(list)

    line_count = 0

    for p in LOGS:
        if not p.exists():
            continue
        for raw in p.read_text(errors="ignore").splitlines():
            if raw in seen:
                continue
            seen.add(raw)
            line_count += 1

            m = close_re.search(raw)
            if m:
                d = m.groupdict()
                net = f(d["net"])
                rec = (d["strategy"].strip(), d["sym"].strip(), d["reason"].strip(), net, f(d["mfe"]), f(d["mae"]))
                closes.append(rec)
                by_strategy[rec[0]].append(net)
                by_symbol[rec[1]].append(net)
                continue

            m = skip_re.search(raw)
            if m:
                d = m.groupdict()
                net = f(d["net"])
                key = f"{d['skip'].strip()} -> {d['outcome'].strip()}"
                symkey = f"{d['sym'].strip()} | {key}"
                skips.append((key, d["sym"].strip(), net, f(d["mfe"]), f(d["mae"])))
                by_skip[key].append(net)
                by_skip_symbol[symkey].append(net)

    out = []
    out.append("=" * 120)
    out.append(f"CLEAN SINCE CHECKPOINT AUDIT UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    out.append("=" * 120)
    out.append("Reads only current skynet_3h/12h/48h after checkpoint. Old archived logs ignored.")
    out.append("Diagnostics only. Real trading OFF.")
    out.append(f"unique_lines={line_count} shadow_closes={len(closes)} skip_closes={len(skips)}")
    out.append("")

    if len(closes) + len(skips) < 5:
        out.append("NOT ENOUGH CLEAN DATA YET.")
        out.append("Need at least 5-10 closes/skips after checkpoint before making decisions.")
    else:
        out.append("SHADOW BY STRATEGY")
        for k, vals in sorted(by_strategy.items(), key=lambda kv: sum(kv[1]), reverse=True):
            out.append(f"{k:<70} {stat(vals)}")

        out.append("")
        out.append("SHADOW BY SYMBOL")
        for k, vals in sorted(by_symbol.items(), key=lambda kv: sum(kv[1]), reverse=True):
            out.append(f"{k:<20} {stat(vals)}")

        out.append("")
        out.append("SKIP OUTCOMES")
        for k, vals in sorted(by_skip.items(), key=lambda kv: sum(kv[1]), reverse=True):
            out.append(f"{k:<90} {stat(vals)}")

        out.append("")
        out.append("SKIP SYMBOL OUTCOMES")
        for k, vals in sorted(by_skip_symbol.items(), key=lambda kv: sum(kv[1]), reverse=True)[:80]:
            out.append(f"{k:<100} {stat(vals)}")

    OUT.write_text("\n".join(out))
    print(OUT)
    print("\n".join(out))

if __name__ == "__main__":
    main()
