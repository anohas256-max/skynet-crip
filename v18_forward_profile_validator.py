#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
LOG = ROOT / "v18_fade_db_shadow.log"
OUT = ROOT / "v18_forward_profile_validator_latest.txt"

MIN_CLOSES = 20
GOOD_PF = 1.25
BAD_PF = 1.15

CLOSE_RE = re.compile(
    r"V18_FADE_DB_CLOSE .*? \| (?P<sym>[A-Z0-9]+) \| (?P<reason>TP|SL|TIME) \| "
    r".*?gross=\$(?P<gross>[+-]?[0-9.]+) net=\$(?P<net>[+-]?[0-9.]+) cost=\$(?P<cost>[0-9.]+) "
    r"age=(?P<age>[0-9.]+)s"
)

START_RE = re.compile(r"START \| (?P<rest>.*)")

def pf(vals):
    gp = sum(x for x in vals if x > 0)
    gl = -sum(x for x in vals if x < 0)
    if gl == 0 and gp > 0:
        return 999.0
    if gl == 0:
        return 0.0
    return gp / gl

def main():
    rows = []
    starts = []

    if LOG.exists():
        for line in LOG.read_text(errors="ignore").splitlines():
            ms = START_RE.search(line)
            if ms:
                starts.append(line.strip())

            mc = CLOSE_RE.search(line)
            if mc:
                rows.append({
                    "sym": mc.group("sym"),
                    "reason": mc.group("reason"),
                    "gross": float(mc.group("gross")),
                    "net": float(mc.group("net")),
                    "cost": float(mc.group("cost")),
                    "age": float(mc.group("age")),
                })

    vals = [r["net"] for r in rows]
    n = len(rows)
    net = sum(vals)
    gross = sum(r["gross"] for r in rows)
    cost = sum(r["cost"] for r in rows)
    wr = 100.0 * sum(1 for x in vals if x > 0) / n if n else 0.0
    pfx = pf(vals)
    sl = sum(1 for r in rows if r["reason"] == "SL")
    timec = sum(1 for r in rows if r["reason"] == "TIME")
    tp = sum(1 for r in rows if r["reason"] == "TP")

    if n < MIN_CLOSES:
        decision = f"COLLECTING: need {MIN_CLOSES - n} more closes before decision."
    elif net <= 0 or pfx < BAD_PF:
        decision = "BAD_FORWARD: profile failed after commission. Do NOT use real; tighten/stop."
    elif net > 0 and pfx >= GOOD_PF:
        decision = "GOOD_FORWARD_STAGE1: continue to 50 closes. Real still OFF."
    else:
        decision = "GRAY_ZONE: positive but weak. Continue shadow only."

    lines = []
    lines.append("=" * 100)
    lines.append(f"V18 FORWARD PROFILE VALIDATOR UTC={datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("=" * 100)
    lines.append("")
    lines.append("LATEST START:")
    lines.append(starts[-1] if starts else "NO START FOUND")
    lines.append("")
    lines.append("CURRENT FORWARD STATS, NET AFTER COMMISSION:")
    lines.append(
        f"closes={n} net=${net:+.4f} gross=${gross:+.4f} cost=${cost:.4f} "
        f"WR={wr:.1f}% PF={pfx:.2f} SL={sl} TIME={timec} TP={tp}"
    )
    lines.append("")
    lines.append(f"DECISION: {decision}")
    lines.append("")
    lines.append("REAL_TRADING must remain OFF.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
