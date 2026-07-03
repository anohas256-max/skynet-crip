#!/usr/bin/env bash
set -u

cd /root/skynet || exit 1
source .venv/bin/activate || exit 1

echo "===================================================================================================="
echo "SKYNET OPS STATUS UTC=$(date -u '+%Y%m%d_%H%M%S_UTC')"
echo "===================================================================================================="

echo
echo "=== GIT ==="
git remote -v || true
git status --short || true
git log --oneline -12 || true

echo
echo "=== SYSTEMD SERVICES ==="
for svc in \
  skynet.service \
  skynet-v18-fade-db-shadow.service \
  skynet-recorder.service \
  skynet-v17-recorder.service \
  skynet-v18-path-recorder.service
do
  echo
  echo "--- $svc ---"
  systemctl status "$svc" --no-pager -l 2>/dev/null | sed -n '1,70p' || echo "service_missing_or_inactive=$svc"
done

echo
echo "=== RECENT JOURNAL: MAIN BOT ==="
journalctl -u skynet.service -n 80 --no-pager -l 2>/dev/null \
  | grep -E 'LOOP_EXCEPTION|MULTI DRY-LIVE|REAL_ENABLED|TRACEBACK|ERROR|✅' \
  | tail -80 || true

echo
echo "=== RECENT JOURNAL: DB FADE ==="
journalctl -u skynet-v18-fade-db-shadow -n 160 --no-pager -l 2>/dev/null \
  | grep -E 'START|V18_FADE_DB_OPEN|V18_FADE_DB_CLOSE|LOOP_EXCEPTION|TRACEBACK|ERROR' \
  | tail -160 || true

echo
echo "=== COMPILE CORE + RECORDERS + RESEARCH ==="
python -m py_compile \
  skynet_config.py \
  skynet_engine.py \
  skynet_main.py \
  skynet_live_mexc.py \
  recorder.py \
  v17_micro_recorder.py \
  v18_path_recorder.py \
  v18_fade_db_shadow.py \
  v18_fade_db_shadow_report.py \
  v18_fade_db_shadow_analyze.py \
  targeted_fade_v18_readiness.py \
  skynet_context_pack.py \
  tg_send_any.py

echo "compile_ok=1"

echo
echo "=== SAFETY CONFIG SNAPSHOT ==="
python3 - <<'PY'
import skynet_config as c
print("REAL_TRADING_ENABLED=", getattr(c, "REAL_TRADING_ENABLED", None))
print("REAL_TRADING_ARMED=", getattr(c, "REAL_TRADING_ARMED", None))
print("LIVE_DRY_RUN=", getattr(c, "LIVE_DRY_RUN", None))
print("CLEAN_CORE_ONLY=", getattr(c, "CLEAN_CORE_ONLY", None))
print("RESEARCH_FADE_V1_ENABLED=", getattr(c, "RESEARCH_FADE_V1_ENABLED", None))
print("STRATEGIES=", sorted(getattr(c, "STRATEGIES", {}).keys()))
assert getattr(c, "REAL_TRADING_ENABLED", True) is False
assert getattr(c, "REAL_TRADING_ARMED", True) is False
assert getattr(c, "LIVE_DRY_RUN", False) is True
PY

echo
echo "=== ENV KEYS ONLY ==="
grep -E '^(REAL_TRADING|LIVE_DRY_RUN|CLEAN_CORE_ONLY|RESEARCH_FADE|V18_FADE_DB|TELEGRAM|TG_|MEXC)' .env 2>/dev/null \
  | sed -E 's/(API|KEY|SECRET|TOKEN|HASH|CHAT|ID)=.*/\1=***MASKED***/g' || true

echo
echo "=== DB FADE REPORT ==="
python v18_fade_db_shadow_report.py || true
cat v18_fade_db_shadow_report_latest.txt 2>/dev/null || true

echo
echo "=== DB FADE ANALYSIS ==="
python v18_fade_db_shadow_analyze.py || true
cat v18_fade_db_shadow_analysis_latest.txt 2>/dev/null || true

echo
echo "=== SQLITE: RECORDER HEARTBEAT + V18 PATHS ==="
python3 - <<'PY'
import sqlite3
from pathlib import Path

def q(db, sql):
    p = Path(db)
    print()
    print(f"--- {db} exists={p.exists()} size_mb={(p.stat().st_size/1024/1024 if p.exists() else 0):.2f} ---")
    if not p.exists():
        return
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    try:
        for row in con.execute(sql):
            print(dict(row))
    except Exception as e:
        print("SQL_ERROR", repr(e))
    finally:
        con.close()

q("/root/skynet/data/skynet_recorder.sqlite3", """
SELECT 'candidate_events' AS table_name, COUNT(*) AS rows FROM candidate_events
UNION ALL
SELECT 'recorder_heartbeat', COUNT(*) FROM recorder_heartbeat;
""")

q("/root/skynet/data/skynet_recorder.sqlite3", """
SELECT time_iso, loop_count, market_count, candidate_count, depth_checked_count, error_count, note
FROM recorder_heartbeat
ORDER BY id DESC
LIMIT 5;
""")

q("/root/skynet/data/v18_micro_paths.sqlite3", """
SELECT COUNT(*) AS rows, MAX(id) AS max_id, MAX(time_iso) AS max_time
FROM signals;
""")

q("/root/skynet/data/v18_micro_paths.sqlite3", """
SELECT id, time_iso, clean_symbol,
       ROUND(price_change,3) AS pc,
       ROUND(vol_ratio,1) AS vol,
       ROUND(spread_bps,2) AS spread,
       rank
FROM signals
ORDER BY id DESC
LIMIT 10;
""")
PY

echo
echo "=== DISK ==="
df -h /
du -sh /root/skynet /root/skynet/data /root/skynet/safe_exports 2>/dev/null || true

echo
echo "=== DONE ==="
