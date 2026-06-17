#!/bin/bash
cd /root/skynet || exit 1
source .venv/bin/activate

LOG_DIR="/root/skynet/data/backtest/smart_universe_v3_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/smart_universe_v3_${STAMP}.log"

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

echo "SMART UNIVERSE V3 GRID START UTC $(date -u)" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"
df -h / | tee -a "$LOG_FILE"

python -m py_compile backtest_smart_universe_v3_grid.py 2>&1 | tee -a "$LOG_FILE"

for TOP in 100 150 200; do
  run_step "smart universe v3 top${TOP} normal M3x10" \
    python backtest_smart_universe_v3_grid.py \
      --days 30 \
      --top "$TOP" \
      --core-top 30 \
      --mid-top 70 \
      --max-open 1,2 \
      --margin 3 \
      --leverage 10 \
      --families FILTERED_055 \
      --guards CLEAN_EXEC,OI0_CLEAN,BTC0_CLEAN \
      --confirms WAIT1_CLOSE \
      --send-tg

  run_step "smart universe v3 top${TOP} pessimistic M3x10" \
    python backtest_smart_universe_v3_grid.py \
      --days 30 \
      --top "$TOP" \
      --core-top 30 \
      --mid-top 70 \
      --max-open 1,2 \
      --margin 3 \
      --leverage 10 \
      --families FILTERED_055 \
      --guards CLEAN_EXEC,OI0_CLEAN,BTC0_CLEAN \
      --confirms WAIT1_CLOSE \
      --spread-bps 3 \
      --slippage-bps 5 \
      --send-tg
done

echo "SMART UNIVERSE V3 GRID DONE UTC $(date -u)" | tee -a "$LOG_FILE"
echo "LOG: $LOG_FILE" | tee -a "$LOG_FILE"
