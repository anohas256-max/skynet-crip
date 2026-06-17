#!/bin/bash
cd /root/skynet || exit 1
source .venv/bin/activate

LOG_DIR="/root/skynet/data/backtest/v13_core_mid_focus_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/v13_core_mid_focus_${STAMP}.log"

run_step () {
  NAME="$1"
  shift
  echo "" | tee -a "$LOG_FILE"
  echo "==================================================" | tee -a "$LOG_FILE"
  echo "START: $NAME | UTC $(date -u)" | tee -a "$LOG_FILE"
  echo "CMD: $*" | tee -a "$LOG_FILE"
  echo "==================================================" | tee -a "$LOG_FILE"

  nice -n 15 "$@" 2>&1 | tee -a "$LOG_FILE"
  CODE=${PIPESTATUS[0]}

  echo "END: $NAME | code=$CODE | UTC $(date -u)" | tee -a "$LOG_FILE"
  sleep 8
}

echo "V13 CORE/MID FOCUS START UTC $(date -u)" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"
df -h / | tee -a "$LOG_FILE"

python -m py_compile backtest_smart_universe_v2_grid.py 2>&1 | tee -a "$LOG_FILE"

for CORE in 20 30 40; do
  for MID in 50 70 90; do
    run_step "V2_STRICT top150 pessimistic core${CORE} mid${MID}" \
      python backtest_smart_universe_v2_grid.py \
        --days 30 \
        --top 150 \
        --core-top "$CORE" \
        --mid-top "$MID" \
        --max-open 1,2 \
        --margin 3 \
        --leverage 10 \
        --families FILTERED_055 \
        --guards CLEAN_EXEC,OI0_CLEAN,BTC0_CLEAN \
        --confirms WAIT1_CLOSE \
        --modes CORE_ONLY,V2_STRICT,V2_WHITELIST \
        --spread-bps 3 \
        --slippage-bps 5 \
        --send-tg
  done
done

echo "V13 CORE/MID FOCUS DONE UTC $(date -u)" | tee -a "$LOG_FILE"
echo "LOG: $LOG_FILE" | tee -a "$LOG_FILE"
