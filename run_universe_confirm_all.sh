#!/bin/bash
# Sequential universe/confirm tests.
# Does NOT trade.

cd /root/skynet || exit 1
source .venv/bin/activate

LOG_DIR="/root/skynet/data/backtest/run_universe_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/run_universe_${STAMP}.log"

run_step () {
  NAME="$1"
  shift
  echo "" | tee -a "$LOG_FILE"
  echo "==================================================" | tee -a "$LOG_FILE"
  echo "START: $NAME | UTC $(date -u)" | tee -a "$LOG_FILE"
  echo "CMD: $*" | tee -a "$LOG_FILE"
  echo "==================================================" | tee -a "$LOG_FILE"
  nice -n 10 "$@" 2>&1 | tee -a "$LOG_FILE"
  CODE=${PIPESTATUS[0]}
  echo "END: $NAME | code=$CODE | UTC $(date -u)" | tee -a "$LOG_FILE"
  if [ "$CODE" -ne 0 ]; then
    echo "WARNING: step failed, continuing." | tee -a "$LOG_FILE"
  fi
  sleep 10
}

echo "SKYNET UNIVERSE RUN START UTC $(date -u)" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"
df -h / | tee -a "$LOG_FILE"

python -m py_compile backtest_universe_confirm_suite.py 2>&1 | tee -a "$LOG_FILE"

run_step "UNIVERSE 30d broad40" \
  python backtest_universe_confirm_suite.py --days 30 --broad-top 40 --max-open 1,2,3 --send-tg

run_step "UNIVERSE 30d broad40 pessimistic costs" \
  python backtest_universe_confirm_suite.py --days 30 --broad-top 40 --max-open 1,2,3 --spread-bps 3 --slippage-bps 5 --send-tg

echo "SKYNET UNIVERSE RUN DONE UTC $(date -u)" | tee -a "$LOG_FILE"
echo "Log saved: $LOG_FILE" | tee -a "$LOG_FILE"
