#!/bin/bash
# Sequential breakout-risk tests.
# Does NOT trade.
# Lighter than universe sweeps. Safe-ish for 2GB VPS with swap.

cd /root/skynet || exit 1
source .venv/bin/activate

LOG_DIR="/root/skynet/data/backtest/run_breakout_risk_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/run_breakout_risk_${STAMP}.log"

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
  if [ "$CODE" -ne 0 ]; then
    echo "WARNING: step failed, continuing." | tee -a "$LOG_FILE"
  fi

  sleep 10
}

echo "SKYNET BREAKOUT RISK RUN START UTC $(date -u)" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"
df -h / | tee -a "$LOG_FILE"

python -m py_compile backtest_breakout_risk_suite.py 2>&1 | tee -a "$LOG_FILE"

# 1) Main useful sweep: top30, normal costs.
run_step "BREAKOUT_RISK 30d top30 normal" \
  python backtest_breakout_risk_suite.py \
    --days 30 \
    --top 30 \
    --max-open 1,2 \
    --send-tg

# 2) Same, pessimistic execution costs.
run_step "BREAKOUT_RISK 30d top30 pessimistic costs" \
  python backtest_breakout_risk_suite.py \
    --days 30 \
    --top 30 \
    --max-open 1,2 \
    --spread-bps 3 \
    --slippage-bps 5 \
    --send-tg

# 3) Slightly broader universe, but still not broad40 rolling24 heavy.
run_step "BREAKOUT_RISK 30d top35 normal" \
  python backtest_breakout_risk_suite.py \
    --days 30 \
    --top 35 \
    --max-open 1,2 \
    --send-tg

# 4) Lite focused pass: only strongest likely modes, fast.
run_step "BREAKOUT_RISK focused modes top30" \
  python backtest_breakout_risk_suite.py \
    --days 30 \
    --top 30 \
    --max-open 1,2 \
    --confirm-modes WAIT1_CLOSE \
    --risk-modes NO_FILTER,RISK_LE3,COMBO_BALANCED,EMA_OK \
    --send-tg

echo "SKYNET BREAKOUT RISK RUN DONE UTC $(date -u)" | tee -a "$LOG_FILE"
echo "Log saved: $LOG_FILE" | tee -a "$LOG_FILE"
