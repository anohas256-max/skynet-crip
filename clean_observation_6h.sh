#!/usr/bin/env bash
set -u
cd /root/skynet
source .venv/bin/activate

START=$(date -u +%Y%m%d_%H%M%S)
OUTDIR="/root/skynet/clean_observation_6h_${START}"
mkdir -p "$OUTDIR"

for i in $(seq 1 12); do
  TS=$(date -u +%Y%m%d_%H%M%S)
  {
    echo "============================================================"
    echo "CLEAN OBSERVATION CYCLE $i/12 UTC=$TS"
    echo "============================================================"
    echo
    echo "=== SAFETY ==="
    grep -nE 'REAL_TRADING_ENABLED|REAL_TRADING_ARMED|LIVE_DRY_RUN|MAKER_SHORT_V1_ENABLED|DEPTH_THIN_ESCAPE' /root/skynet/.env skynet_config.py 2>/dev/null | head -120
    echo
    echo "=== CLEAN AUDIT ==="
    timeout 1m python clean_since_checkpoint_audit.py
    echo
    echo "=== LIVE SETUP AUDIT ==="
    timeout 2m python live_setup_audit_now.py
    echo
    echo "=== FALSE NEGATIVE FILTER LAB ==="
    timeout 2m python false_negative_filter_lab.py
    echo
    echo "=== DYNAMIC FILTER LAB ==="
    timeout 2m python dynamic_filter_intelligence_lab.py
    echo
    echo "=== LAST INTERESTING LINES ==="
    grep -hE 'SHADOW_CLOSE|SKIP_TRACK_CLOSE|DRY_LIVE_CLOSE|SELECTOR_PICK|SELECTOR_RESULT|WOULD_TP|WOULD_SL|WOULD_TIME|REAL_ENABLED|LIVE_DRY_RUN' skynet_3h.log skynet_12h.log skynet_48h.log 2>/dev/null | tail -180 || true
  } > "$OUTDIR/${TS}_cycle_${i}.txt" 2>&1

  cp clean_since_checkpoint_audit_latest.txt "$OUTDIR/latest_clean_since_checkpoint_audit.txt" 2>/dev/null || true
  cp live_setup_audit_latest.txt "$OUTDIR/latest_live_setup_audit.txt" 2>/dev/null || true

  {
    echo "============================================================"
    echo "CLEAN OBSERVATION SUMMARY UTC=$TS cycle=$i/12"
    echo "============================================================"
    cat clean_since_checkpoint_audit_latest.txt 2>/dev/null || true
    echo
    echo "=== KEY LIVE AUDIT ==="
    grep -hE 'SHADOW STRATEGIES|BEST SYMBOLS|WORST SYMBOLS|FALSE NEGATIVE|SKIPS THAT|SKIP OUTCOMES|sum=|avg=|wr=|pf=' live_setup_audit_latest.txt 2>/dev/null | head -260 || true
    echo
    echo "=== RULE ==="
    echo "No real unless clean window has >=20 outcomes, positive net, positive PF, and no single-symbol dependency."
  } > /root/skynet/clean_observation_6h_summary_latest.txt

  python tg_send_any.py /root/skynet/clean_observation_6h_summary_latest.txt "SKYNET clean observation cycle $i/12" || true

  tar -czf /root/skynet/clean_observation_6h_latest.tar.gz -C "$(dirname "$OUTDIR")" "$(basename "$OUTDIR")"

  [ "$i" -lt 12 ] && sleep 1800
done

python tg_send_any.py /root/skynet/clean_observation_6h_latest.tar.gz "SKYNET clean observation 6h archive" || true
python skynet_context_pack.py --send || true
