#!/usr/bin/env bash
set -u

cd /root/skynet || exit 1
source .venv/bin/activate || exit 1

NOW="$(date -u +%Y%m%d_%H%M%S_UTC)"
OUTDIR="/root/skynet/report_exports/phase2d_24h"
mkdir -p "$OUTDIR"

SUMMARY="$OUTDIR/phase2d_auto_summary_${NOW}.txt"

{
  echo "===================================================================================================="
  echo "SKYNET PHASE2D 24H AUTO MONITOR UTC=$NOW"
  echo "===================================================================================================="
  echo

  echo "=== SERVICE STATUS ==="
  systemctl is-active skynet-v18-fade-db-shadow.service || true
  systemctl status skynet-v18-fade-db-shadow.service --no-pager -l | sed -n '1,80p' || true
  echo

  if ! systemctl is-active --quiet skynet-v18-fade-db-shadow.service; then
    echo "SERVICE_ACTION=RESTART"
    systemctl restart skynet-v18-fade-db-shadow.service || true
    sleep 8
  else
    echo "SERVICE_ACTION=OK_ACTIVE"
  fi

  echo
  echo "=== SAFETY ENV ==="
  grep -E '^(REAL_TRADING_ENABLED|REAL_TRADING_ARMED|LIVE_DRY_RUN|CLEAN_CORE_ONLY|V18_FADE_DB_PC_MIN|V18_FADE_DB_PC_MAX|V18_FADE_DB_VOL_MIN|V18_FADE_DB_SPREAD_MAX|V18_FADE_DB_RANK_MAX)=' .env || true

  echo
  echo "=== JOURNAL TAIL ==="
  journalctl -u skynet-v18-fade-db-shadow -n 120 --no-pager -l \
    | grep -E 'START|V18_FADE_DB_OPEN|V18_FADE_DB_CLOSE|LOOP_EXCEPTION|TRACEBACK|ERROR' \
    | tail -120 || true

  echo
  echo "=== REGENERATE REPORT ==="
  python v18_fade_db_shadow_report.py || true
  cat v18_fade_db_shadow_report_latest.txt || true

  echo
  echo "=== REGENERATE ANALYSIS ==="
  python v18_fade_db_shadow_analyze.py || true
  cat v18_fade_db_shadow_analysis_latest.txt || true

  echo
  echo "=== METRICS PARSE ==="
  python3 - <<'PY'
import re
from pathlib import Path

report = Path("v18_fade_db_shadow_report_latest.txt").read_text(errors="ignore") if Path("v18_fade_db_shadow_report_latest.txt").exists() else ""
analysis = Path("v18_fade_db_shadow_analysis_latest.txt").read_text(errors="ignore") if Path("v18_fade_db_shadow_analysis_latest.txt").exists() else ""

m = re.search(r"opens=(\d+)\s+closes=(\d+).*?TP=(\d+)\s+SL=(\d+)\s+TIME=(\d+).*?WR=([0-9.]+)%\s+net=\$([+-]?[0-9.]+)", report, re.S)
a = re.search(r"=== TOTAL ===.*?n=\s*(\d+)\s+net=\$\s*([+-]?[0-9.]+)\s+avg=\$([+-]?[0-9.]+).*?PF=\s*([0-9.]+)", analysis, re.S)

opens=closes=tp=sl=time=0
wr=net=avg=pf=0.0

if m:
    opens=int(m.group(1)); closes=int(m.group(2)); tp=int(m.group(3)); sl=int(m.group(4)); time=int(m.group(5)); wr=float(m.group(6)); net=float(m.group(7))
if a:
    avg=float(a.group(3)); pf=float(a.group(4))

print(f"METRIC opens={opens}")
print(f"METRIC closes={closes}")
print(f"METRIC tp={tp}")
print(f"METRIC sl={sl}")
print(f"METRIC time={time}")
print(f"METRIC wr={wr:.1f}")
print(f"METRIC net={net:+.4f}")
print(f"METRIC avg={avg:+.5f}")
print(f"METRIC pf={pf:.2f}")

if closes == 0:
    print("DECISION=COLLECTING_NO_CLOSES_YET")
elif closes < 10:
    print("DECISION=COLLECTING_UNDER_10_CLOSES")
elif closes >= 10 and (net <= 0 or pf < 1.15):
    print("DECISION=FAIL_EDGE_WEAK_BUT_KEEP_SERVICE_FOR_STATS_REAL_OFF")
elif closes >= 10 and net > 0 and pf > 1.25 and avg > 0.01:
    print("DECISION=PASS_CONTINUE_COLLECTING")
else:
    print("DECISION=WEAK_CONTINUE_RESEARCH_ONLY")
PY

  echo
  echo "=== DB MATCH COUNT LAST 24H FOR PHASE2D PROFILE ==="
  sqlite3 /root/skynet/data/v18_micro_paths.sqlite3 "
  SELECT COUNT(*)
  FROM signals
  WHERE time_iso >= datetime('now','-24 hours')
    AND price_change >= 0.30
    AND vol_ratio >= 12
    AND spread_bps <= 2
    AND rank <= 50
    AND clean_symbol NOT IN ('ALLO','XPL');
  " || true

  echo
  echo "=== RECENT MATCHING DB ROWS ==="
  sqlite3 /root/skynet/data/v18_micro_paths.sqlite3 "
  SELECT id, time_iso, clean_symbol,
         ROUND(price_change,3) pc,
         ROUND(vol_ratio,1) vol,
         ROUND(spread_bps,2) spread,
         rank,
         ROUND(max_up,3) max_up,
         ROUND(max_down,3) max_down,
         ROUND(close_pct,3) close_pct
  FROM signals
  WHERE time_iso >= datetime('now','-24 hours')
    AND price_change >= 0.30
    AND vol_ratio >= 12
    AND spread_bps <= 2
    AND rank <= 50
    AND clean_symbol NOT IN ('ALLO','XPL')
  ORDER BY id DESC
  LIMIT 40;
  " || true

} | tee "$SUMMARY"

cp -f v18_fade_db_shadow_report_latest.txt "$OUTDIR/report_${NOW}.txt" 2>/dev/null || true
cp -f v18_fade_db_shadow_analysis_latest.txt "$OUTDIR/analysis_${NOW}.txt" 2>/dev/null || true
cp -f phase2d_gate_latest.txt "$OUTDIR/gate_${NOW}.txt" 2>/dev/null || true

python tg_send_any.py "$SUMMARY" "SKYNET phase2D 24h auto summary" || true
python tg_send_any.py v18_fade_db_shadow_report_latest.txt "SKYNET phase2D auto report" || true
python tg_send_any.py v18_fade_db_shadow_analysis_latest.txt "SKYNET phase2D auto analysis" || true

# context pack only every 3 hours to avoid spam/heavy sends
HOUR="$(date -u +%H)"
if [ $((10#$HOUR % 3)) -eq 0 ]; then
  python skynet_context_pack.py --send || true
fi

# keep disk sane
find "$OUTDIR" -type f -mtime +7 -delete 2>/dev/null || true
