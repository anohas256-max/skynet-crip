#!/usr/bin/env bash
set -euo pipefail

cd /root/skynet

cmd="${1:-help}"

safe_flags() {
  grep -E '^(REAL_TRADING_ENABLED|REAL_TRADING_ARMED|LIVE_DRY_RUN|CLEAN_CORE_ONLY|RESEARCH_FADE_V1_ENABLED|V18_FADE_DB_PC_MIN|V18_FADE_DB_PC_MAX|V18_FADE_DB_VOL_MIN|V18_FADE_DB_SPREAD_MAX|V18_FADE_DB_RANK_MAX|V18_FADE_DB_MAX_OPEN_TOTAL|V18_FADE_DB_BLACKLIST)=' .env || true
}

case "$cmd" in
  status)
    echo "=== SERVICES ==="
    systemctl status skynet.service --no-pager -l | sed -n '1,80p' || true
    echo
    systemctl status skynet-v18-fade-db-shadow.service --no-pager -l | sed -n '1,100p' || true
    echo
    systemctl status skynet-phase2d-monitor.timer --no-pager -l | sed -n '1,80p' || true
    echo
    echo "=== TIMERS ==="
    systemctl list-timers --all | grep -E 'skynet-phase2d|NEXT' || true
    echo
    echo "=== SAFETY FLAGS ==="
    safe_flags
    ;;

  report)
    source .venv/bin/activate
    python v18_fade_db_shadow_report.py || true
    python v18_fade_db_shadow_analyze.py || true
    echo
    echo "=== REPORT ==="
    cat v18_fade_db_shadow_report_latest.txt || true
    echo
    echo "=== ANALYSIS ==="
    cat v18_fade_db_shadow_analysis_latest.txt || true
    ;;

  send)
    source .venv/bin/activate
    python v18_fade_db_shadow_report.py || true
    python v18_fade_db_shadow_analyze.py || true
    python tg_send_any.py v18_fade_db_shadow_report_latest.txt "SKYNET current fade report" || true
    python tg_send_any.py v18_fade_db_shadow_analysis_latest.txt "SKYNET current fade analysis" || true
    python skynet_context_pack.py --send || true
    ;;

  safe)
    set_env () {
      KEY="$1"
      VAL="$2"
      grep -q "^${KEY}=" /root/skynet/.env && sed -i "s/^${KEY}=.*/${KEY}=${VAL}/" /root/skynet/.env || echo "${KEY}=${VAL}" >> /root/skynet/.env
    }

    set_env REAL_TRADING_ENABLED false
    set_env REAL_TRADING_ARMED false
    set_env LIVE_DRY_RUN true
    set_env CLEAN_CORE_ONLY true
    set_env RESEARCH_FADE_V1_ENABLED false

    set_env V18_FADE_DB_PC_MIN 0.30
    set_env V18_FADE_DB_PC_MAX 0.50
    set_env V18_FADE_DB_VOL_MIN 12.0
    set_env V18_FADE_DB_SPREAD_MAX 2.0
    set_env V18_FADE_DB_RANK_MAX 50
    set_env V18_FADE_DB_MAX_OPEN_TOTAL 1
    set_env V18_FADE_DB_BLACKLIST ALLO,XPL,TAC,SOXL
    set_env V18_FADE_DB_AUTO_BAN_AFTER_SL 1

    chmod 600 .env
    systemctl restart skynet-v18-fade-db-shadow.service || true

    echo "=== SAFE MODE ENABLED ==="
    safe_flags
    ;;

  stop-real-risk)
    set_env () {
      KEY="$1"
      VAL="$2"
      grep -q "^${KEY}=" /root/skynet/.env && sed -i "s/^${KEY}=.*/${KEY}=${VAL}/" /root/skynet/.env || echo "${KEY}=${VAL}" >> /root/skynet/.env
    }

    set_env REAL_TRADING_ENABLED false
    set_env REAL_TRADING_ARMED false
    set_env LIVE_DRY_RUN true
    chmod 600 .env

    systemctl restart skynet.service || true
    systemctl restart skynet-v18-fade-db-shadow.service || true

    echo "REAL HARD-OFF DONE"
    safe_flags
    ;;

  pack)
    source .venv/bin/activate
    python skynet_context_pack.py --send || true
    ;;

  last)
    echo "=== LAST JOURNAL FADE ==="
    journalctl -u skynet-v18-fade-db-shadow -n 160 --no-pager -l \
      | grep -E 'START|V18_FADE_DB_OPEN|V18_FADE_DB_CLOSE|ERROR|TRACEBACK|TimeoutError|DNSError' \
      | tail -160 || true
    echo
    echo "=== LAST MAIN BOT ERRORS ==="
    journalctl -u skynet -n 160 --no-pager -l \
      | grep -E 'ERROR|TRACEBACK|TimeoutError|DNSError|LOOP_EXCEPTION' \
      | tail -160 || true
    ;;

  help|*)
    cat <<'EOF'
SKYNET CONTROL

Commands:
  ./skynet_control.sh status          service/timer/safety status
  ./skynet_control.sh report          generate and print fade report/analysis
  ./skynet_control.sh send            send report + context pack to Telegram
  ./skynet_control.sh safe            force safe dry narrow research mode
  ./skynet_control.sh stop-real-risk  hard-disable real trading flags
  ./skynet_control.sh pack            send context pack to Telegram
  ./skynet_control.sh last            show recent important logs

Real trading rule:
  Do NOT enable real unless fresh shadow stats pass:
    closes >= 50
    net > 0
    PF > 1.25
    avg > $0.01
    no single-symbol concentration
    no network instability
EOF
    ;;
esac
