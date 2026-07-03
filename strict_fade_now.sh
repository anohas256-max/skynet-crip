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
journalctl -u skynet-v18-fade-db-shadow -n 120 --no-pager -l 2>/dev/null \
  | grep -E 'START|V18_FADE_DB_OPEN|V18_FADE_DB_CLOSE|LOOP_EXCEPTION|TRACEBACK|ERROR' \
  | tail -100 || true

echo
echo "=== DECISION HINT ==="
CLOSES=$(grep -E '^opened=' v18_fade_db_shadow_report_latest.txt 2>/dev/null | sed -E 's/.*closed=([0-9]+).*/\1/' || echo 0)
NET=$(grep -E '^opened=' v18_fade_db_shadow_report_latest.txt 2>/dev/null | sed -E 's/.*net=\$([+-]?[0-9.\-]+).*/\1/' || echo 0)

echo "closes=${CLOSES:-0}"
echo "net=${NET:-0}"

if [ "${CLOSES:-0}" -lt 20 ]; then
  echo "ACTION=COLLECT_MORE_CLOSES"
  echo "next_check_command: cd /root/skynet && ./strict_fade_now.sh"
elif [ "${CLOSES:-0}" -ge 20 ]; then
  echo "ACTION=ANALYZE_20_PLUS"
  echo "command: cd /root/skynet && source .venv/bin/activate && python v18_fade_db_shadow_analyze.py && cat v18_fade_db_shadow_analysis_latest.txt"
fi
