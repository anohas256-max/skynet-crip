#!/bin/bash
cd /root/skynet || exit 1
source .venv/bin/activate

LOG_DIR="/root/skynet/data/backtest/run_breakout_score4_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/run_breakout_score4_${STAMP}.log"

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
  sleep 10
}

echo "SCORE4 BREAKOUT TEST START UTC $(date -u)" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"
df -h / | tee -a "$LOG_FILE"

python -m py_compile backtest_breakout_risk_score4_suite.py 2>&1 | tee -a "$LOG_FILE"

run_step "SCORE4 top30 focused normal" \
  python backtest_breakout_risk_score4_suite.py \
    --days 30 \
    --top 30 \
    --max-open 1,2 \
    --confirm-modes WAIT1_CLOSE \
    --risk-modes NO_FILTER,NO_FALSE_BREAKOUT,COMBO_BALANCED,EMA_OK \
    --send-tg

run_step "SCORE4 top30 focused pessimistic" \
  python backtest_breakout_risk_score4_suite.py \
    --days 30 \
    --top 30 \
    --max-open 1,2 \
    --confirm-modes WAIT1_CLOSE \
    --risk-modes NO_FILTER,NO_FALSE_BREAKOUT,COMBO_BALANCED,EMA_OK \
    --spread-bps 3 \
    --slippage-bps 5 \
    --send-tg

run_step "SCORE4 top35 focused normal" \
  python backtest_breakout_risk_score4_suite.py \
    --days 30 \
    --top 35 \
    --max-open 1,2 \
    --confirm-modes WAIT1_CLOSE \
    --risk-modes NO_FILTER,NO_FALSE_BREAKOUT,COMBO_BALANCED,EMA_OK \
    --send-tg

echo "SCORE4 BREAKOUT TEST DONE UTC $(date -u)" | tee -a "$LOG_FILE"
echo "Log saved: $LOG_FILE" | tee -a "$LOG_FILE"
