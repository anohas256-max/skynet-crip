#!/usr/bin/env bash
set -u

cd /root/skynet
source .venv/bin/activate

START_UTC=$(date -u +%Y%m%d_%H%M%S)
OUTDIR="/root/skynet/global_6h_research_${START_UTC}"
mkdir -p "$OUTDIR"

echo "=== GLOBAL 6H RESEARCH PUSH START ===" | tee "$OUTDIR/00_start.txt"
date -u | tee -a "$OUTDIR/00_start.txt"

echo
echo "=== SAFETY CHECK: REAL MUST BE OFF ===" | tee "$OUTDIR/01_safety.txt"
grep -nE 'REAL_TRADING_ENABLED|REAL_TRADING_ARMED|LIVE_DRY_RUN|MAKER_SHORT_V1_ENABLED|DEPTH_THIN_ESCAPE_ENABLED|DEPTH_THIN_ESCAPE_V2_ENABLED' /root/skynet/.env skynet_config.py 2>/dev/null | tee -a "$OUTDIR/01_safety.txt"

if grep -q '^REAL_TRADING_ENABLED=true' /root/skynet/.env 2>/dev/null; then
  echo "ABORT: REAL_TRADING_ENABLED=true in .env" | tee -a "$OUTDIR/01_safety.txt"
  exit 1
fi

if grep -q '^REAL_TRADING_ARMED=true' /root/skynet/.env 2>/dev/null; then
  echo "ABORT: REAL_TRADING_ARMED=true in .env" | tee -a "$OUTDIR/01_safety.txt"
  exit 1
fi

echo
echo "=== SERVICE STATUS ===" | tee "$OUTDIR/02_service_start.txt"
systemctl status skynet.service --no-pager -l | sed -n '1,100p' | tee -a "$OUTDIR/02_service_start.txt"

run_lab () {
  local name="$1"
  local seconds="$2"
  local cmd="$3"
  local ts
  ts=$(date -u +%Y%m%d_%H%M%S)
  local log="$OUTDIR/${ts}_${name}.txt"

  echo
  echo "=== RUN $name timeout=${seconds}s ===" | tee "$log"
  date -u | tee -a "$log"
  echo "CMD: $cmd" | tee -a "$log"

  timeout "${seconds}s" bash -lc "$cmd" >> "$log" 2>&1
  local rc=$?

  echo "RC=$rc" | tee -a "$log"
  echo "--- tail ---" | tee -a "$log"
  tail -120 "$log" | tee -a "$OUTDIR/99_live_tail.txt" >/dev/null || true
}

snapshot () {
  local cycle="$1"
  local ts
  ts=$(date -u +%Y%m%d_%H%M%S)

  {
    echo "======================================================================"
    echo "GLOBAL 6H SNAPSHOT cycle=$cycle utc=$ts"
    echo "======================================================================"
    echo
    echo "=== SERVICE ==="
    systemctl status skynet.service --no-pager -l | sed -n '1,70p'
    echo
    echo "=== CURRENT LOG COUNTS ==="
    for f in skynet_3h.log skynet_12h.log skynet_48h.log; do
      echo "--- $f ---"
      [ -f "$f" ] || continue
      echo -n "lines="; wc -l < "$f"
      echo -n "SHADOW_CLOSE="; grep -c 'SHADOW_CLOSE' "$f" || true
      echo -n "SKIP_TRACK_CLOSE="; grep -c 'SKIP_TRACK_CLOSE' "$f" || true
      echo -n "DRY_LIVE_CLOSE="; grep -c 'DRY_LIVE_CLOSE' "$f" || true
      echo -n "DEPTH_THIN="; grep -c 'DEPTH_THIN' "$f" || true
      echo -n "SPREAD_WIDE="; grep -c 'SPREAD_WIDE' "$f" || true
    done
    echo
    echo "=== LAST 160 INTERESTING LINES ==="
    grep -hE 'SHADOW_CLOSE|SKIP_TRACK_CLOSE|DRY_LIVE_CLOSE|WOULD_TP|WOULD_SL|DEPTH_THIN|SPREAD_WIDE|XPL|NEAR|REAL_ENABLED|LIVE_DRY_RUN' skynet_3h.log skynet_12h.log skynet_48h.log 2>/dev/null | tail -160 || true
  } > "$OUTDIR/${ts}_snapshot_cycle_${cycle}.txt"
}

make_decision_summary () {
  local ts
  ts=$(date -u +%Y%m%d_%H%M%S)
  local out="$OUTDIR/${ts}_GLOBAL_DECISION_SUMMARY.txt"

  {
    echo "======================================================================"
    echo "GLOBAL 6H DECISION SUMMARY UTC=$ts"
    echo "======================================================================"
    echo
    echo "Goal: find something actionable for next real-readiness push."
    echo "Real trading must remain OFF unless explicit later manual decision."
    echo
    echo "=== SAFETY ==="
    grep -nE 'REAL_TRADING_ENABLED|REAL_TRADING_ARMED|LIVE_DRY_RUN|MAKER_SHORT_V1_ENABLED|DEPTH_THIN_ESCAPE_ENABLED|DEPTH_THIN_ESCAPE_V2_ENABLED' /root/skynet/.env skynet_config.py 2>/dev/null | head -160
    echo
    echo "=== CLEAN AUDIT LATEST ==="
    cat clean_since_checkpoint_audit_latest.txt 2>/dev/null || true
    echo
    echo "=== LIVE SETUP AUDIT KEY LINES ==="
    grep -hE 'SHADOW STRATEGIES|BEST SYMBOLS|WORST SYMBOLS|SETUP BUCKETS|FALSE NEGATIVE|SPREAD_WIDE|DEPTH_THIN|XPL|NEAR|PUMPFUN|JUP|ENA|MANTA|ROBUST|NO ROBUST' live_setup_audit_latest.txt 2>/dev/null | head -260 || true
    echo
    echo "=== XPL/NEAR SIGNATURE KEY LINES ==="
    grep -hE 'GROUP TOTALS|BUCKET CONTRAST|GOOD|TOXIC|DECISION|XPL|NEAR|rank|spread|imb|ask5|vol' xpl_near_signature_lab_latest.txt 2>/dev/null | head -260 || true
    echo
    echo "=== DEPTH THIN KEY LINES ==="
    grep -hE 'DEPTH|WOULD|sum=|wr=|NO|BEST|WORST|DECISION' depth_thin_escape_lab_latest.txt 2>/dev/null | head -220 || true
    echo
    echo "=== FALSE NEGATIVE KEY LINES ==="
    grep -hE 'WOULD_TP|WOULD_SL|SPREAD_WIDE|REJECT_RULES|XPL|NEAR|sum=|avg=|wr=|pf=|DECISION' false_negative_filter_lab_latest.txt 2>/dev/null | head -260 || true
    echo
    echo "=== HIGH FREQ / COST / EDGE KEY LINES ==="
    grep -hE 'ROBUST|NO ROBUST|cost|fee|spread|maker|taker|avg|sum|pf|DECISION' high_freq_opportunity_lab_latest.txt fee_intelligence_lab_latest.txt offline_edge_hunter_latest.txt 2>/dev/null | head -300 || true
    echo
    echo "=== RAW RESULT FILES ==="
    find "$OUTDIR" -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM %9s %p\n' | sort
    echo
    echo "=== MY RULE FOR NEXT STEP ==="
    echo "1) If clean audit still has <10 outcomes: no real, keep collecting."
    echo "2) If SPREAD_WIDE false-negatives stay positive across clean data: build tiny SPREAD_WIDE_ESCAPE shadow lane only."
    echo "3) If XPL/NEAR signature is symbol-only: do not build a strategy from it."
    echo "4) If DEPTH_THIN appears: keep hard-kill; no escape."
    echo "5) If no robust edge after 6h battery: pivot from 1m pump scalping to external/cross-venue/catalyst scanner."
  } > "$out"

  cp "$out" /root/skynet/global_6h_decision_summary_latest.txt
  echo "$out"
}

echo
echo "=== START 12 CYCLES, 30 MIN EACH ==="

for cycle in $(seq 1 12); do
  echo
  echo "======================================================================"
  echo "CYCLE $cycle / 12"
  echo "======================================================================"
  date -u

  snapshot "$cycle"

  run_lab "clean_since_checkpoint_audit" 60 "python clean_since_checkpoint_audit.py"
  run_lab "live_setup_audit" 120 "python live_setup_audit_now.py"
  run_lab "xpl_near_signature_lab" 120 "python xpl_near_signature_lab.py"
  run_lab "depth_thin_escape_lab" 120 "python depth_thin_escape_lab.py"
  run_lab "false_negative_filter_lab" 180 "python false_negative_filter_lab.py"
  run_lab "dynamic_filter_intelligence_lab" 180 "python dynamic_filter_intelligence_lab.py"
  run_lab "high_freq_opportunity_lab" 240 "python high_freq_opportunity_lab.py"
  run_lab "fee_intelligence_lab" 120 "python fee_intelligence_lab.py"
  run_lab "spreadwide_dedupe" 180 "python analyze_spreadwide_dedupe.py"
  run_lab "offline_edge_hunter" 600 "python offline_edge_hunter.py"

  SUMMARY=$(make_decision_summary)
  echo "summary=$SUMMARY"

  cp clean_since_checkpoint_audit_latest.txt "$OUTDIR/latest_clean_since_checkpoint_audit.txt" 2>/dev/null || true
  cp live_setup_audit_latest.txt "$OUTDIR/latest_live_setup_audit.txt" 2>/dev/null || true
  cp xpl_near_signature_lab_latest.txt "$OUTDIR/latest_xpl_near_signature_lab.txt" 2>/dev/null || true
  cp depth_thin_escape_lab_latest.txt "$OUTDIR/latest_depth_thin_escape_lab.txt" 2>/dev/null || true
  cp false_negative_filter_lab_latest.txt "$OUTDIR/latest_false_negative_filter_lab.txt" 2>/dev/null || true
  cp high_freq_opportunity_lab_latest.txt "$OUTDIR/latest_high_freq_opportunity_lab.txt" 2>/dev/null || true
  cp fee_intelligence_lab_latest.txt "$OUTDIR/latest_fee_intelligence_lab.txt" 2>/dev/null || true
  cp offline_edge_hunter_latest.txt "$OUTDIR/latest_offline_edge_hunter.txt" 2>/dev/null || true

  tar -czf "/root/skynet/global_6h_research_latest.tar.gz" -C "$(dirname "$OUTDIR")" "$(basename "$OUTDIR")"

  python tg_send_any.py "$SUMMARY" "SKYNET global 6h decision summary cycle $cycle/12" || true

  if [ "$cycle" -lt 12 ]; then
    echo "sleep 30m..."
    sleep 1800
  fi
done

echo
echo "=== FINAL PACK ==="
FINAL_SUMMARY=$(make_decision_summary)
tar -czf "/root/skynet/global_6h_research_${START_UTC}.tar.gz" -C "$(dirname "$OUTDIR")" "$(basename "$OUTDIR")"
cp "/root/skynet/global_6h_research_${START_UTC}.tar.gz" "/root/skynet/global_6h_research_latest.tar.gz"

python tg_send_any.py "$FINAL_SUMMARY" "SKYNET FINAL global 6h decision summary" || true
python tg_send_any.py "/root/skynet/global_6h_research_latest.tar.gz" "SKYNET global 6h research archive" || true
python skynet_context_pack.py --send || true

echo "DONE: /root/skynet/global_6h_research_latest.tar.gz"
