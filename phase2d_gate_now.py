#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

REPORT = Path("v18_fade_db_shadow_report_latest.txt")
ANALYSIS = Path("v18_fade_db_shadow_analysis_latest.txt")

def run(cmd):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True)

run("python v18_fade_db_shadow_report.py")
run("python v18_fade_db_shadow_analyze.py")

report = REPORT.read_text(errors="ignore") if REPORT.exists() else ""
analysis = ANALYSIS.read_text(errors="ignore") if ANALYSIS.exists() else ""

m = re.search(r"opens=(\d+)\s+closes=(\d+).*?WR=([0-9.]+)%\s+net=\$([+-]?[0-9.]+)", report, re.S)
a = re.search(r"=== TOTAL ===.*?n=\s*(\d+)\s+net=\$\s*([+-]?[0-9.]+)\s+avg=\$([+-]?[0-9.]+).*?PF=\s*([0-9.]+)", analysis, re.S)

opens = closes = 0
wr = net = avg = pf = 0.0

if m:
    opens = int(m.group(1))
    closes = int(m.group(2))
    wr = float(m.group(3))
    net = float(m.group(4))

if a:
    avg = float(a.group(3))
    pf = float(a.group(4))

print("=" * 100)
print("PHASE2D GATE", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
print("=" * 100)
print(f"opens={opens}")
print(f"closes={closes}")
print(f"net=${net:+.4f}")
print(f"avg=${avg:+.5f}")
print(f"wr={wr:.1f}%")
print(f"pf={pf:.2f}")
print()

if closes < 10:
    print("ACTION=KEEP_RUNNING_TO_10_CLOSES")
    print("reason=sample_too_small_but_positive")
    raise SystemExit(0)

if closes >= 10 and (net <= 0 or pf < 1.15):
    print("ACTION=STOP_PHASE2D")
    print("reason=failed_10_close_gate")
    run("systemctl stop skynet-v18-fade-db-shadow.service")
    raise SystemExit(2)

if closes >= 10 and net > 0 and pf > 1.25 and avg > 0.01:
    print("ACTION=CONTINUE_TO_25_CLOSES")
    print("reason=passed_10_close_gate")
    raise SystemExit(0)

print("ACTION=KEEP_RESEARCH_ONLY_WEAK_EDGE")
print("reason=positive_but_not_strong_enough")
