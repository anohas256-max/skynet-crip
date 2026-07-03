#!/usr/bin/env bash
set -u

cd /root/skynet || exit 1
source .venv/bin/activate || exit 1

echo "=== STRICT FADE NOW UTC=$(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="

python v18_fade_db_shadow_report.py || true
cat v18_fade_db_shadow_report_latest.txt 2>/dev/null || true

echo
python v18_fade_db_shadow_analyze.py || true
cat v18_fade_db_shadow_analysis_latest.txt 2>/dev/null || true

echo
echo "=== RECENT DB FADE JOURNAL ==="
journalctl -u skynet-v18-fade-db-shadow -n 140 --no-pager -l 2>/dev/null \
  | grep -E 'START|V18_FADE_DB_OPEN|V18_FADE_DB_CLOSE|LOOP_EXCEPTION|TRACEBACK|ERROR' \
  | tail -120 || true

echo
echo "=== DECISION HINT ==="
python3 - <<'PY'
import re
from pathlib import Path

report = Path("v18_fade_db_shadow_report_latest.txt").read_text(errors="ignore") if Path("v18_fade_db_shadow_report_latest.txt").exists() else ""
analysis = Path("v18_fade_db_shadow_analysis_latest.txt").read_text(errors="ignore") if Path("v18_fade_db_shadow_analysis_latest.txt").exists() else ""

m = re.search(r"opens=(\d+)\s+closes=(\d+).*?net=\$([+-]?[0-9.]+)", report, re.S)
opens = closes = 0
net = 0.0
if m:
    opens = int(m.group(1))
    closes = int(m.group(2))
    net = float(m.group(3))

pf = None
avg = None
m2 = re.search(r"=== TOTAL ===.*?n=\s*\d+\s+net=\$\s*[+-]?[0-9.]+\s+avg=\$([+-]?[0-9.]+).*?PF=\s*([0-9.]+)", analysis, re.S)
if m2:
    avg = float(m2.group(1))
    pf = float(m2.group(2))

print(f"opens={opens}")
print(f"closes={closes}")
print(f"net={net:+.4f}")
print(f"avg={avg if avg is not None else 'NA'}")
print(f"pf={pf if pf is not None else 'NA'}")

if closes < 20:
    print("ACTION=COLLECT_MORE_CLOSES")
    print("next_check_command: cd /root/skynet && ./strict_fade_now.sh")
    print("criteria: до 20 closes параметры не меняем, real не обсуждаем")
elif net <= 0 or (pf is not None and pf < 1.15):
    print("ACTION=CLOSE_PHASE2B_AS_REAL_CANDIDATE")
    print("next_command: cd /root/skynet && source .venv/bin/activate && systemctl stop skynet-v18-fade-db-shadow.service")
    print("criteria: closes>=20 and net<=0/PF<1.15")
elif pf is not None and pf > 1.25 and avg is not None and avg > 0.01:
    print("ACTION=CONTINUE_TO_50_CLOSES")
    print("next_check_command: cd /root/skynet && ./strict_fade_now.sh")
else:
    print("ACTION=WEAK_EDGE_CONTINUE_ONLY_RESEARCH")
    print("next_check_command: cd /root/skynet && ./strict_fade_now.sh")
PY
