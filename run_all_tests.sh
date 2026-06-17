#!/bin/bash
# SKYNET sequential research runner.
# Runs backtests one by one and sends each ZIP to Telegram.
# Does NOT trade. Does NOT touch skynet service.

cd /root/skynet || exit 1
source .venv/bin/activate

LOG_DIR="/root/skynet/data/backtest/run_all_logs"
mkdir -p "$LOG_DIR"

STAMP="$(date -u +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/run_all_${STAMP}.log"

echo "==================================================" | tee -a "$LOG_FILE"
echo "SKYNET RUN ALL TESTS START UTC $(date -u)" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"

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

  echo "==================================================" | tee -a "$LOG_FILE"
  echo "END: $NAME | code=$CODE | UTC $(date -u)" | tee -a "$LOG_FILE"
  echo "==================================================" | tee -a "$LOG_FILE"

  if [ "$CODE" -ne 0 ]; then
    echo "WARNING: step failed, continuing to next step." | tee -a "$LOG_FILE"
  fi

  sleep 10
}

# Safety checks.
echo "Python:" "$(which python)" | tee -a "$LOG_FILE"
python -V 2>&1 | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"
df -h / | tee -a "$LOG_FILE"

# Compile before long run.
echo "Compiling scripts..." | tee -a "$LOG_FILE"
python -m py_compile backtest_1m.py 2>&1 | tee -a "$LOG_FILE"

if [ -f backtest_maxopen_suite.py ]; then
  python -m py_compile backtest_maxopen_suite.py 2>&1 | tee -a "$LOG_FILE"
else
  echo "MISSING: backtest_maxopen_suite.py" | tee -a "$LOG_FILE"
fi

if [ -f backtest_mfe_suite.py ]; then
  python -m py_compile backtest_mfe_suite.py 2>&1 | tee -a "$LOG_FILE"
else
  echo "MISSING: backtest_mfe_suite.py" | tee -a "$LOG_FILE"
fi

# ==================================================
# SAFE DEFAULT PACK
# Avoid top50 because it previously froze the server.
# ==================================================

# 1) Max-open baseline on current best family.
run_step "MAXOPEN 30d top30 core" \
  python backtest_maxopen_suite.py --days 30 --top 30 --max-open 1,2,3 --suite core --send-tg

# 2) Max-open pessimistic costs.
run_step "MAXOPEN 30d top30 core pessimistic costs" \
  python backtest_maxopen_suite.py --days 30 --top 30 --max-open 1,2,3 --suite core --spread-bps 3 --slippage-bps 5 --send-tg

# 3) MFE core: tests strict/looser entries + MFE guard/lock.
run_step "MFE 30d top30 core" \
  python backtest_mfe_suite.py --days 30 --top 30 --max-open 1,2,3 --suite core --send-tg

# 4) MFE pessimistic costs.
run_step "MFE 30d top30 core pessimistic costs" \
  python backtest_mfe_suite.py --days 30 --top 30 --max-open 1,2,3 --suite core --spread-bps 3 --slippage-bps 5 --send-tg

# 5) MFE top35: checks universe fragility without going top50.
run_step "MFE 30d top35 core" \
  python backtest_mfe_suite.py --days 30 --top 35 --max-open 1,2,3 --suite core --send-tg

# 6) MFE wide: larger parameter sweep, still top30.
run_step "MFE 30d top30 wide" \
  python backtest_mfe_suite.py --days 30 --top 30 --max-open 1,2,3 --suite wide --send-tg

echo "" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"
echo "SKYNET RUN ALL TESTS DONE UTC $(date -u)" | tee -a "$LOG_FILE"
echo "Log saved: $LOG_FILE" | tee -a "$LOG_FILE"
echo "You should have several ZIP files in Telegram." | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"
