#!/bin/bash
cd /root/skynet || exit 1
source .venv/bin/activate
LOG_DIR="/root/skynet/data/backtest/run_universe_nolookahead_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/run_universe_nolookahead_${STAMP}.log"

run_step () {
  NAME="$1"; shift
  echo "" | tee -a "$LOG_FILE"
  echo "==================================================" | tee -a "$LOG_FILE"
  echo "START: $NAME | UTC $(date -u)" | tee -a "$LOG_FILE"
  echo "CMD: $*" | tee -a "$LOG_FILE"
  echo "==================================================" | tee -a "$LOG_FILE"
  nice -n 10 "$@" 2>&1 | tee -a "$LOG_FILE"
  CODE=${PIPESTATUS[0]}
  echo "END: $NAME | code=$CODE | UTC $(date -u)" | tee -a "$LOG_FILE"
  [ "$CODE" -ne 0 ] && echo "WARNING: step failed, continuing." | tee -a "$LOG_FILE"
  sleep 10
}

echo "SKYNET UNIVERSE NO-LOOKAHEAD RUN START UTC $(date -u)" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"
df -h / | tee -a "$LOG_FILE"
python -m py_compile backtest_universe_nolookahead_suite.py 2>&1 | tee -a "$LOG_FILE"

run_step "NOLOOKAHEAD 30d broad40 normal" \
  python backtest_universe_nolookahead_suite.py --days 30 --broad-top 40 --max-open 1,2,3 --send-tg

run_step "NOLOOKAHEAD 30d broad40 pessimistic costs" \
  python backtest_universe_nolookahead_suite.py --days 30 --broad-top 40 --max-open 1,2,3 --spread-bps 3 --slippage-bps 5 --send-tg

echo "SKYNET UNIVERSE NO-LOOKAHEAD RUN DONE UTC $(date -u)" | tee -a "$LOG_FILE"
echo "Log saved: $LOG_FILE" | tee -a "$LOG_FILE"
