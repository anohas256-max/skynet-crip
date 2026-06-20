#!/usr/bin/env python3
import re
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
LOGS = [ROOT / "skynet_3h.log", ROOT / "skynet_12h.log", ROOT / "skynet_48h.log"]
OUT_DIR = ROOT / "safe_exports" / "research_reports"

def ts():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

def sf(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default

open_re = re.compile(
    r"RESEARCH_FADE_V1_OPEN \| (?P<profile>[^|]+) \| SHORT \| (?P<symbol>[^|]+) \| .*?"
    r"pc=(?P<pc>[+-]?[0-9.]+)% vol=x(?P<vol>[0-9.]+) "
    r"spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>[0-9]+) "
    r"imb5=(?P<imb>[+-]?[0-9.]+)"
)

# backward compatibility for old open lines without profile
old_open_re = re.compile(
    r"RESEARCH_FADE_V1_OPEN \| SHORT \| (?P<symbol>[^|]+) \| .*?"
    r"pc=(?P<pc>[+-]?[0-9.]+)% vol=x(?P<vol>[0-9.]+) "
    r"spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>[0-9]+) "
    r"imb5=(?P<imb>[+-]?[0-9.]+)"
)

close_re = re.compile(
    r"RESEARCH_FADE_V1_CLOSE \| (?P<profile>[^|]+) \| SHORT \| (?P<symbol>[^|]+) \| (?P<reason>[^|]+) \| .*?"
    r"Move:(?P<move>[+-]?[0-9.]+)% \| Gross:(?P<gross>[+-]?[0-9.]+)\$ "
    r"Net:(?P<net>[+-]?[0-9.]+)\$ Costs:(?P<costs>[0-9.]+)\$ \| "
    r"MFE:(?P<mfe>[+-]?[0-9.]+)% MAE:(?P<mae>[+-]?[0-9.]+)% .*?"
    r"pc=(?P<pc>[+-]?[0-9.]+)% vol=x(?P<vol>[0-9.]+) "
    r"spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>[0-9]+) imb5=(?P<imb>[+-]?[0-9.]+)"
)

def main(stdout=False):
    seen = set()
    opens = []
    closes = []

    for path in LOGS:
        if not path.exists():
            continue
        for line in path.read_text(errors="ignore").splitlines():
            mo = open_re.search(line)
            if mo:
                key = ("o", line)
                if key not in seen:
                    seen.add(key)
                    d = mo.groupdict()
                    opens.append(d)
                continue

            moo = old_open_re.search(line)
            if moo:
                key = ("o", line)
                if key not in seen:
                    seen.add(key)
                    d = moo.groupdict()
                    d["profile"] = "OLD_STRICT"
                    opens.append(d)
                continue

            mc = close_re.search(line)
            if mc:
                key = ("c", line)
                if key not in seen:
                    seen.add(key)
                    closes.append(mc.groupdict())

    by_profile = defaultdict(list)
    for c in closes:
        by_profile[c.get("profile", "UNKNOWN")].append(c)

    lines = []
    lines.append("=" * 90)
    lines.append(f"RESEARCH FADE V1 LIVE SHADOW REPORT UTC={ts()}")
    lines.append("=" * 90)
    lines.append(f"opens={len(opens)} closes={len(closes)} active_estimate={max(0, len(opens)-len(closes))}")
    lines.append("profiles_v3=CORE_SP2_ASK10,CORE_SP3_ASK20,HF_SP5_ASK10,SPIKE_SP7; old STRICT/MID/WIDE are historical if present")

    if len(opens) > 0 and len(closes) == 0:
        lines.append("WARNING: fade has opens but zero closes. Check direct polling / TTL close wiring.")

    for profile in sorted(set([o.get("profile", "?") for o in opens]) | set(by_profile.keys())):
        profile_opens = [o for o in opens if o.get("profile") == profile]
        profile_closes = by_profile.get(profile, [])
        n = len(profile_closes)
        total_net = sum(sf(x["net"]) for x in profile_closes)
        total_gross = sum(sf(x["gross"]) for x in profile_closes)
        total_costs = sum(sf(x["costs"]) for x in profile_closes)
        wins = sum(1 for x in profile_closes if sf(x["net"]) > 0)
        wr = wins / n * 100 if n else 0.0

        sym_net = defaultdict(float)
        sym_n = Counter()
        reasons = Counter()

        for x in profile_closes:
            sym = x["symbol"].strip()
            sym_net[sym] += sf(x["net"])
            sym_n[sym] += 1
            reasons[x["reason"].strip()] += 1

        best = sorted(sym_net.items(), key=lambda x: x[1], reverse=True)[:10]
        worst = sorted(sym_net.items(), key=lambda x: x[1])[:10]

        lines.append("")
        lines.append(f"[{profile}] opens={len(profile_opens)} closes={n} active_estimate={max(0, len(profile_opens)-n)}")
        lines.append(f"net={total_net:+.2f}$ gross={total_gross:+.2f}$ costs=-{total_costs:.2f}$ wr={wr:.1f}% reasons={dict(reasons)}")
        lines.append(f"best_symbols={[(s, round(v, 3), sym_n[s]) for s, v in best]}")
        lines.append(f"worst_symbols={[(s, round(v, 3), sym_n[s]) for s, v in worst]}")

    lines.append("")
    lines.append("RECENT CLOSES:")
    for x in closes[-60:]:
        lines.append(
            f"{x.get('profile','?'):7s} {x['symbol']:10s} net={sf(x['net']):+6.2f}$ move={sf(x['move']):+5.2f}% "
            f"mfe={sf(x['mfe']):+5.2f}% mae={sf(x['mae']):+5.2f}% "
            f"pc={sf(x['pc']):+5.2f}% vol=x{sf(x['vol']):4.1f} spread={sf(x['spread']):4.1f} "
            f"rank={x['rank']} imb5={sf(x['imb']):+4.2f}"
        )

    text = "\n".join(lines) + "\n"

    if stdout:
        print(text)
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"research_fade_live_report_{ts()}.txt"
    out.write_text(text, encoding="utf-8", errors="ignore")
    print(out)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()
    main(stdout=args.stdout)
