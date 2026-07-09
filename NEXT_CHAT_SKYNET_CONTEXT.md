# SKYNET next chat context

Project path: /root/skynet
Repo: https://github.com/anohas256-max/skynet-crip

Hard rule:
REAL_TRADING_ENABLED=false
REAL_TRADING_ARMED=false
LIVE_DRY_RUN=true
Do NOT enable real unless a fresh dry/shadow profile passes strict gates.

Current conclusion:
- Wide phase2D pc>=0.3 pc<=999 vol>=12 spread<=2 rank<=50 failed after 24h:
  opens=8 closes=8 SL=6 TIME=2 WR=25% net=-$0.3689 avg=-$0.04611 PF=0.18.
- Toxic area: pc>=1.2. It caused most of the loss.
- pc_030_050 was still mildly positive in latest sample but small n.
- Real trading is NOT justified.

Current final safe mode:
- V18_FADE_DB_PC_MIN=0.30
- V18_FADE_DB_PC_MAX=0.50
- V18_FADE_DB_VOL_MIN=12.0
- V18_FADE_DB_SPREAD_MAX=2.0
- V18_FADE_DB_RANK_MAX=50
- V18_FADE_DB_MAX_OPEN_TOTAL=1
- V18_FADE_DB_BLACKLIST=ALLO,XPL,TAC,SOXL
- real OFF

Services:
- skynet.service
- skynet-v18-fade-db-shadow.service
- skynet-phase2d-monitor.timer

Check commands:
cd /root/skynet
source .venv/bin/activate
python v18_fade_db_shadow_report.py
python v18_fade_db_shadow_analyze.py
cat v18_fade_db_shadow_report_latest.txt
cat v18_fade_db_shadow_analysis_latest.txt
systemctl status skynet-v18-fade-db-shadow.service --no-pager -l
systemctl list-timers --all | grep skynet-phase2d
