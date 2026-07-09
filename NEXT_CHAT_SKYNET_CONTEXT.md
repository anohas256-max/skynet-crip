# SKYNET final context

Path: /root/skynet
Repo: https://github.com/anohas256-max/skynet-crip

IMPORTANT:
Real trading is NOT ready.
Keep:
REAL_TRADING_ENABLED=false
REAL_TRADING_ARMED=false
LIVE_DRY_RUN=true

Main conclusion:
The bot does not currently have a proven live edge.

Latest important result:
Wide phase2D failed after 24h:
opens=8
closes=8
SL=6
TIME=2
WR=25%
net=-$0.3689
avg=-$0.04611
PF=0.18

Do not enable real from this.

Toxic area:
pc >= 1.2 was very bad.

Only mildly interesting area:
pc 0.30–0.50, but sample is small.
Current safe research mode:
V18_FADE_DB_PC_MIN=0.30
V18_FADE_DB_PC_MAX=0.50
V18_FADE_DB_VOL_MIN=12.0
V18_FADE_DB_SPREAD_MAX=2.0
V18_FADE_DB_RANK_MAX=50
V18_FADE_DB_MAX_OPEN_TOTAL=1
V18_FADE_DB_BLACKLIST=ALLO,XPL,TAC,SOXL

Next real work:
Do not tune live blindly.
Run offline DB research and find a profile with:
n >= 100 historical simulated trades,
PF > 1.5,
avg positive after costs,
recent window also positive,
no single-symbol concentration.
Only then shadow it live again.
