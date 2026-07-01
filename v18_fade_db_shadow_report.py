#!/usr/bin/env python3
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
LOG = ROOT / "v18_fade_db_shadow.log"
STATE = ROOT / "v18_fade_db_shadow_state.json"
OUT = ROOT / "v18_fade_db_shadow_report_latest.txt"

text = LOG.read_text(errors="ignore") if LOG.exists() else ""

opens = len(re.findall(r"V18_FADE_DB_OPEN", text))
closes = re.findall(r"V18_FADE_DB_CLOSE .*? \| (TP|SL|TIME) \| .*? net=\$([+-]?[0-9.\\-]+)", text)

net = 0.0
tp = sl = tm = wins = losses = 0
for reason, n in closes:
    v = float(n)
    net += v
    if reason == "TP":
        tp += 1
    elif reason == "SL":
        sl += 1
    else:
        tm += 1
    if v > 0:
        wins += 1
    else:
        losses += 1

closed = len(closes)
wr = wins / closed * 100 if closed else 0.0

lines = []
lines.append("=" * 100)
lines.append(f"V18 FADE DB SHADOW QUICK REPORT UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
lines.append("=" * 100)
lines.append("real_trading=OFF")
lines.append(f"opens={opens} closes={closed} TP={tp} SL={sl} TIME={tm} wins={wins} losses={losses} WR={wr:.1f}% net=${net:+.4f}")
lines.append("")
lines.append("LAST EVENTS:")
for line in text.strip().splitlines()[-80:]:
    if "V18_FADE_DB_" in line or "LOOP_EXCEPTION" in line or "START" in line:
        lines.append(line)

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
