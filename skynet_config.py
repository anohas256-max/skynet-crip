import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

BOT_VERSION = "SKYNET_PRO_V16_MICRO_LIVE_META_ONLY"

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
TG_TARGET_RAW = os.getenv("TG_TARGET", "-1002953234396")
try:
    TG_TARGET = int(TG_TARGET_RAW) if str(TG_TARGET_RAW).lstrip("-").isdigit() else TG_TARGET_RAW
except Exception:
    TG_TARGET = TG_TARGET_RAW

# ============================================================
# LIVE / DRY-LIVE
# ============================================================
# ВАЖНО: real MEXC adapter НЕ реализован. LIVE_DRY_RUN=false не использовать.
LIVE_ENABLED = os.getenv("LIVE_ENABLED", "true").lower() == "true"
LIVE_DRY_RUN = os.getenv("LIVE_DRY_RUN", "true").lower() == "true"

# Multi dry-live: несколько кандидатов параллельно с отдельным LiveNet/ShadowNet/Diff.
# Реальный live потом должен быть только один победитель.
DEFAULT_LIVE_DRY_TRACKS = "SMART_V2_STRICT_CLEAN_MO1,SMART_V2_STRICT_OI_MO1,META_V12_EXEC_SAFE_MO1"
LIVE_DRY_TRACKS = [
    x.strip()
    for x in os.getenv("LIVE_DRY_TRACKS", DEFAULT_LIVE_DRY_TRACKS).split(",")
    if x.strip()
]

# Backward compatible alias: первый dry-track.
LIVE_STRATEGY = os.getenv("LIVE_STRATEGY", LIVE_DRY_TRACKS[0] if LIVE_DRY_TRACKS else "QUALITY_TOP20_TREND040_ATR5B_WAIT1_MO1")
DRY_RUN_EXECUTION_SLIPPAGE_BPS = int(os.getenv("DRY_RUN_EXECUTION_SLIPPAGE_BPS", "5"))

# ============================================================
# BLACKLIST
# ============================================================
EXACT_BLACKLIST = [
    "USDC", "USDE", "FDUSD", "TUSD", "BUSD", "DAI", "EUR",
    "SILVER", "GOLD", "USOIL", "UKOIL", "WTI", "BRENT",
    "COINBASE", "SPX", "NDX", "DXY", "TSLA", "AAPL",
    "NVIDIA", "ROBINHOOD", "ALUMINUM", "XPD", "B", "H", "ON",
    "US", "UB", "COPPER", "RIVER", "PENGU", "FARTCOIN",
    "PLAY", "TESLA", "NAS100", "US30", "XAUT", "XAU", "BTC", "SPX500"
]
PARTIAL_BLACKLIST = ["TRUMP", "MAGA", "STOCK"]

# ============================================================
# GLOBAL / COSTS
# ============================================================
VIRTUAL_BALANCE = float(os.getenv("VIRTUAL_BALANCE", "40.0"))
LEVERAGE = int(os.getenv("LEVERAGE", "10"))
STOP_LOSS = float(os.getenv("STOP_LOSS", "0.5"))

COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.0008"))  # 0.04% per side
SPREAD_BPS = float(os.getenv("SPREAD_BPS", "3"))                 # base paper spread model
SLIPPAGE_BPS = float(os.getenv("SLIPPAGE_BPS", "5"))             # base paper slippage per side

# ============================================================
# LOCKS / RISK
# ============================================================
PROFIT_LOCK_LIMIT = float(os.getenv("PROFIT_LOCK_LIMIT", "2.0"))
LOSS_LOCK_LIMIT = float(os.getenv("LOSS_LOCK_LIMIT", "-1.2"))
GIVEBACK_ACTIVATION = float(os.getenv("GIVEBACK_ACTIVATION", "1.0"))
GIVEBACK_DROP = float(os.getenv("GIVEBACK_DROP", "0.60"))

TRADE_COOLDOWN = int(os.getenv("TRADE_COOLDOWN", "900"))
COIN_BAN_AFTER_SL = int(os.getenv("COIN_BAN_AFTER_SL", "3600"))

# ============================================================
# RADAR SETTINGS
# ============================================================
MIN_VOL_1M = float(os.getenv("MIN_VOL_1M", "30000"))
MIN_AVG_1M_VOL = float(os.getenv("MIN_AVG_1M_VOL", "4000"))
VOL_MULTIPLIER = float(os.getenv("VOL_MULTIPLIER", "8"))
PRICE_CHANGE_MIN = float(os.getenv("PRICE_CHANGE_MIN", "0.20"))
PRICE_CHANGE_MAX = float(os.getenv("PRICE_CHANGE_MAX", "0.85"))
TG_COOLDOWN = int(os.getenv("TG_COOLDOWN", "900"))

BTC_DUMP_LIMIT = float(os.getenv("BTC_DUMP_LIMIT", "-0.30"))
TREND_15M_LIMIT = float(os.getenv("TREND_15M_LIMIT", "0.0"))

EXHAUSTION_VOL_RATIO = float(os.getenv("EXHAUSTION_VOL_RATIO", "25"))
EXHAUSTION_PRICE_CHANGE = float(os.getenv("EXHAUSTION_PRICE_CHANGE", "0.50"))

# ============================================================
# DEPTH / SPREAD
# ============================================================
MIN_TOP5_BID_USDT = float(os.getenv("MIN_TOP5_BID_USDT", "3000"))
MIN_TOP5_ASK_USDT = float(os.getenv("MIN_TOP5_ASK_USDT", "3000"))
DEPTH_LIMIT = int(os.getenv("DEPTH_LIMIT", "5"))
DEPTH_TIMEOUT = float(os.getenv("DEPTH_TIMEOUT", "3"))
MAX_DEPTH_CANDIDATES_PER_SNAPSHOT = int(os.getenv("MAX_DEPTH_CANDIDATES_PER_SNAPSHOT", "4"))
DEPTH_CONCURRENCY = int(os.getenv("DEPTH_CONCURRENCY", "1"))
DEPTH_CACHE_TTL = float(os.getenv("DEPTH_CACHE_TTL", "5"))

# ============================================================
# DIAGNOSTICS / EXIT TESTS
# ============================================================
BE_CANDIDATE_MFE = float(os.getenv("BE_CANDIDATE_MFE", "0.50"))

# Old BE test proved too close. V11 uses BE_V2 only on dedicated shadow branches.
BE_V2_TRIGGER_PCT = float(os.getenv("BE_V2_TRIGGER_PCT", "0.65"))
BE_V2_STOP_PCT = float(os.getenv("BE_V2_STOP_PCT", "0.20"))

NO_FOLLOW_MINUTES = float(os.getenv("NO_FOLLOW_MINUTES", "2"))
NO_FOLLOW_MFE = float(os.getenv("NO_FOLLOW_MFE", "0.15"))

NO_REWARD_EXIT_MINUTES = float(os.getenv("NO_REWARD_EXIT_MINUTES", "4"))
NO_REWARD_EXIT_MFE = float(os.getenv("NO_REWARD_EXIT_MFE", "0.15"))

SKIP_TRACK_TTL_MINUTES = float(os.getenv("SKIP_TRACK_TTL_MINUTES", "15"))
SKIP_TRACK_COOLDOWN = int(os.getenv("SKIP_TRACK_COOLDOWN", "900"))

# ============================================================
# V11.2 MFE-RUNNER / PARTIAL EXIT TESTS
# ============================================================
# MFE is not used as future knowledge. These rules use only live-observed max_profit_pct after entry.
FAST_FAIL_AFTER_MINUTES = float(os.getenv("FAST_FAIL_AFTER_MINUTES", "0.5"))
FAST_FAIL_MFE_PCT = float(os.getenv("FAST_FAIL_MFE_PCT", "0.10"))
FAST_FAIL_LOSS_PCT = float(os.getenv("FAST_FAIL_LOSS_PCT", "-0.20"))

MICRO_LOCK_TRIGGER_PCT = float(os.getenv("MICRO_LOCK_TRIGGER_PCT", "0.30"))
MICRO_LOCK_STOP_PCT = float(os.getenv("MICRO_LOCK_STOP_PCT", "0.00"))

PARTIAL_TRIGGER_PCT = float(os.getenv("PARTIAL_TRIGGER_PCT", "0.80"))
PARTIAL_CLOSE_FRACTION = float(os.getenv("PARTIAL_CLOSE_FRACTION", "0.50"))
PARTIAL_RUNNER_TP_PCT = float(os.getenv("PARTIAL_RUNNER_TP_PCT", "2.00"))
PARTIAL_RUNNER_STOP_PCT = float(os.getenv("PARTIAL_RUNNER_STOP_PCT", "0.10"))

RUNNER_TIME_STOP_MINUTES = float(os.getenv("RUNNER_TIME_STOP_MINUTES", "35"))

GLOBAL_TOXIC_BAN_SECONDS = int(os.getenv("GLOBAL_TOXIC_BAN_SECONDS", "7200"))
GLOBAL_TOXIC_BAN_MFE_PCT = float(os.getenv("GLOBAL_TOXIC_BAN_MFE_PCT", "0.10"))

# Context gates for new runner candidates.
RUNNER_MIN_SCORE = int(os.getenv("RUNNER_MIN_SCORE", "5"))
RUNNER_MIN_TREND_15M = float(os.getenv("RUNNER_MIN_TREND_15M", "0.30"))
RUNNER_MIN_BTC_5M = float(os.getenv("RUNNER_MIN_BTC_5M", "-0.05"))
RUNNER_MAX_STRUCTURE_RISK = int(os.getenv("RUNNER_MAX_STRUCTURE_RISK", "2"))
RUNNER_MAX_PRICE_CHANGE = float(os.getenv("RUNNER_MAX_PRICE_CHANGE", "0.85"))
FOMO_RUNNER_MIN_SCORE = int(os.getenv("FOMO_RUNNER_MIN_SCORE", "6"))
FOMO_RUNNER_MIN_TREND_15M = float(os.getenv("FOMO_RUNNER_MIN_TREND_15M", "0.50"))
FOMO_RUNNER_MIN_BTC_5M = float(os.getenv("FOMO_RUNNER_MIN_BTC_5M", "0.00"))

# ============================================================
# V11.3 CONFIRMATION ENTRY
# ============================================================
# Confirmation uses only future prices AFTER signal; no lookahead.
# It waits ~1 minute and enters only if the impulse did not rug and price is still above signal.
CONFIRM_WAIT_SECONDS = float(os.getenv("CONFIRM_WAIT_SECONDS", "60"))
CONFIRM_MAX_SECONDS = float(os.getenv("CONFIRM_MAX_SECONDS", "95"))
CONFIRM_NO_RUG_PCT = float(os.getenv("CONFIRM_NO_RUG_PCT", "-0.15"))
CONFIRM_MAX_PRICE_CHANGE_DEFAULT = float(os.getenv("CONFIRM_MAX_PRICE_CHANGE_DEFAULT", "0.55"))
CONFIRM_MAX_VOL_RATIO_DEFAULT = float(os.getenv("CONFIRM_MAX_VOL_RATIO_DEFAULT", "25"))
CONFIRM_MAX_MOVE_PCT_DEFAULT = float(os.getenv("CONFIRM_MAX_MOVE_PCT_DEFAULT", "999"))

# ============================================================
# V11.4 TREND + ATR5_B + UNIVERSE
# ============================================================
# Archive / no-lookahead winners:
# - trend15 >= 0.40
# - ATR5_B dynamic exit from pre-entry 5m range
# - current rolling-24h turnover universe top20/top30
# - anti-chase cap: do not enter if confirmation move is already too extended
TREND_ATR_MIN_TREND_15M = float(os.getenv("TREND_ATR_MIN_TREND_15M", "0.40"))
TREND_ATR_MIN_SCORE = int(os.getenv("TREND_ATR_MIN_SCORE", "5"))
TREND_ATR_MAX_PRICE_CHANGE = float(os.getenv("TREND_ATR_MAX_PRICE_CHANGE", "0.55"))
TREND_ATR_MAX_VOL_RATIO = float(os.getenv("TREND_ATR_MAX_VOL_RATIO", "25"))
TREND_ATR_CONFIRM_MAX_MOVE = float(os.getenv("TREND_ATR_CONFIRM_MAX_MOVE", "0.75"))

ATR5B_SL_MULT = float(os.getenv("ATR5B_SL_MULT", "0.85"))
ATR5B_SL_MIN = float(os.getenv("ATR5B_SL_MIN", "0.40"))
ATR5B_SL_MAX = float(os.getenv("ATR5B_SL_MAX", "0.85"))
ATR5B_PARTIAL_MULT = float(os.getenv("ATR5B_PARTIAL_MULT", "1.00"))
ATR5B_PARTIAL_MIN = float(os.getenv("ATR5B_PARTIAL_MIN", "0.55"))
ATR5B_PARTIAL_MAX = float(os.getenv("ATR5B_PARTIAL_MAX", "0.90"))
ATR5B_RUNNER_TP_MULT = float(os.getenv("ATR5B_RUNNER_TP_MULT", "4.50"))
ATR5B_RUNNER_TP_MIN = float(os.getenv("ATR5B_RUNNER_TP_MIN", "2.00"))
ATR5B_RUNNER_TP_MAX = float(os.getenv("ATR5B_RUNNER_TP_MAX", "3.20"))
ATR5B_RUNNER_STOP_MULT = float(os.getenv("ATR5B_RUNNER_STOP_MULT", "0.25"))
ATR5B_RUNNER_STOP_MIN = float(os.getenv("ATR5B_RUNNER_STOP_MIN", "0.08"))
ATR5B_RUNNER_STOP_MAX = float(os.getenv("ATR5B_RUNNER_STOP_MAX", "0.20"))
ATR5B_TIME_STOP_MINUTES = float(os.getenv("ATR5B_TIME_STOP_MINUTES", "45"))
ATR5B_DEFAULT_PRE_RANGE_5M = float(os.getenv("ATR5B_DEFAULT_PRE_RANGE_5M", "0.75"))

# ============================================================
# V11.5 BREAKOUT-RISK + ATR5_B
# ============================================================
BREAKOUT_MIN_SCORE = int(os.getenv("BREAKOUT_MIN_SCORE", "4"))
BREAKOUT_MIN_TREND_15M = float(os.getenv("BREAKOUT_MIN_TREND_15M", "0.40"))
BREAKOUT_MIN_TREND_15M_LOOSE = float(os.getenv("BREAKOUT_MIN_TREND_15M_LOOSE", "0.30"))
BREAKOUT_MAX_PRICE_CHANGE = float(os.getenv("BREAKOUT_MAX_PRICE_CHANGE", "0.65"))
BREAKOUT_MAX_VOL_RATIO = float(os.getenv("BREAKOUT_MAX_VOL_RATIO", "35"))
BREAKOUT_CONFIRM_MAX_MOVE = float(os.getenv("BREAKOUT_CONFIRM_MAX_MOVE", "0.75"))
BREAKOUT_MIN_BTC_5M = float(os.getenv("BREAKOUT_MIN_BTC_5M", "-0.05"))
BREAKOUT_MAX_STRUCTURE_RISK = int(os.getenv("BREAKOUT_MAX_STRUCTURE_RISK", "2"))
BREAKOUT_SPREAD_LIMIT_BPS = float(os.getenv("BREAKOUT_SPREAD_LIMIT_BPS", "5"))

BREAKOUT_FALSE_BREAKOUT_MAX = int(os.getenv("BREAKOUT_FALSE_BREAKOUT_MAX", "1"))
BREAKOUT_COMBO_RISK_MAX = int(os.getenv("BREAKOUT_COMBO_RISK_MAX", "3"))
BREAKOUT_COMBO_RED_SHARE_MAX = float(os.getenv("BREAKOUT_COMBO_RED_SHARE_MAX", "0.68"))
BREAKOUT_COMBO_REJECTION_MAX = int(os.getenv("BREAKOUT_COMBO_REJECTION_MAX", "2"))
BREAKOUT_COMBO_WICK_PRESSURE_MAX = float(os.getenv("BREAKOUT_COMBO_WICK_PRESSURE_MAX", "0.38"))
BREAKOUT_COMBO_EMA9_SLOPE_MIN = float(os.getenv("BREAKOUT_COMBO_EMA9_SLOPE_MIN", "-0.02"))
BREAKOUT_COMBO_CLOSE_VS_EMA9_MIN = float(os.getenv("BREAKOUT_COMBO_CLOSE_VS_EMA9_MIN", "-0.10"))

# ============================================================
# V12 META EXECUTION-SAFE FRAMEWORK
# ============================================================
META_V12_MARGIN = float(os.getenv("META_V12_MARGIN", "3.0"))
META_V12_LEVERAGE = int(os.getenv("META_V12_LEVERAGE", "4"))
META_V12_MAX_OPEN = int(os.getenv("META_V12_MAX_OPEN", "1"))
META_V12_SPREAD_LIMIT_BPS = float(os.getenv("META_V12_SPREAD_LIMIT_BPS", "7"))
META_V12_MIN_SCORE = int(os.getenv("META_V12_MIN_SCORE", "4"))
META_V12_MIN_TREND_15M = float(os.getenv("META_V12_MIN_TREND_15M", "0.30"))
META_V12_STRICT_TREND_15M = float(os.getenv("META_V12_STRICT_TREND_15M", "0.40"))
META_V12_MIN_BTC_5M = float(os.getenv("META_V12_MIN_BTC_5M", "0.00"))
META_V12_MAX_PRICE_CHANGE = float(os.getenv("META_V12_MAX_PRICE_CHANGE", "0.85"))
META_V12_MAX_VOL_RATIO = float(os.getenv("META_V12_MAX_VOL_RATIO", "35"))
META_V12_MAX_STRUCTURE_RISK = int(os.getenv("META_V12_MAX_STRUCTURE_RISK", "2"))
META_V12_MAX_BRISK = int(os.getenv("META_V12_MAX_BRISK", "4"))
META_V12_MAX_FALSE_BREAKOUTS = int(os.getenv("META_V12_MAX_FALSE_BREAKOUTS", "3"))
META_V12_CONFIRM_MAX_MOVE = float(os.getenv("META_V12_CONFIRM_MAX_MOVE", "0.75"))
META_V12_OI_SOFT_MIN = float(os.getenv("META_V12_OI_SOFT_MIN", "-0.50"))
META_V12_OI_STRICT_MIN = float(os.getenv("META_V12_OI_STRICT_MIN", "0.00"))
META_V12_ROLL_TOP_N = int(os.getenv("META_V12_ROLL_TOP_N", "30"))

# ============================================================
# V13 SMART UNIVERSE V2 / FILTERED_055 + WAIT1 + ATR5B
# ============================================================
SMART_V2_MARGIN = float(os.getenv("SMART_V2_MARGIN", "3.0"))
SMART_V2_LEVERAGE = int(os.getenv("SMART_V2_LEVERAGE", "10"))
SMART_V2_MAX_OPEN = int(os.getenv("SMART_V2_MAX_OPEN", "1"))
SMART_V2_SPREAD_LIMIT_BPS = float(os.getenv("SMART_V2_SPREAD_LIMIT_BPS", "3"))

# Universe zones:
# core is always tradable after normal guards; mid is gated by rolling symbol quality;
# above mid is monitor-only for future whitelist/blacklist learning.
SMART_V2_CORE_TOP = int(os.getenv("SMART_V2_CORE_TOP", "40"))
SMART_V2_MID_TOP = int(os.getenv("SMART_V2_MID_TOP", "40"))

# V2_STRICT parameters from archive tests.
SMART_V2_MIN_OBS = int(os.getenv("SMART_V2_MIN_OBS", "2"))
SMART_V2_MIN_AVG_NET = float(os.getenv("SMART_V2_MIN_AVG_NET", "0.00"))
SMART_V2_MAX_SL_RATE = float(os.getenv("SMART_V2_MAX_SL_RATE", "0.55"))
SMART_V2_MIN_AVG_MFE = float(os.getenv("SMART_V2_MIN_AVG_MFE", "0.45"))
SMART_V2_MAX_BAD_STREAK = int(os.getenv("SMART_V2_MAX_BAD_STREAK", "1"))
SMART_V2_COOLDOWN_HOURS = float(os.getenv("SMART_V2_COOLDOWN_HOURS", "24"))

# ============================================================
# V14 ADAPTIVE PASSPORT / CORE RISK GATE
# ============================================================
# Более значимый слой: smart-universe больше не считает core/top30 безопасным автоматически.
# 1) Core risk gate режет грязные core-входы (например BRisk/false breakout).
# 2) Dynamic symbol passport живёт между рестартами и временно охлаждает токсичные символы.
SMART_V2_PERSIST_ENABLED = os.getenv("SMART_V2_PERSIST_ENABLED", "true").lower() == "true"
SMART_V2_PASSPORT_PATH = os.getenv("SMART_V2_PASSPORT_PATH", "/root/skynet/data/smart_v2_passport.json")

SMART_V2_CORE_RISK_GATE_ENABLED = os.getenv("SMART_V2_CORE_RISK_GATE_ENABLED", "false").lower() == "true"
SMART_V2_CORE_MIN_SCORE = int(os.getenv("SMART_V2_CORE_MIN_SCORE", "5"))
SMART_V2_CORE_MAX_BRISK = int(os.getenv("SMART_V2_CORE_MAX_BRISK", "3"))
SMART_V2_CORE_MAX_FALSE_BREAKOUTS = int(os.getenv("SMART_V2_CORE_MAX_FALSE_BREAKOUTS", "2"))
SMART_V2_CORE_MAX_STRUCTURE_RISK = int(os.getenv("SMART_V2_CORE_MAX_STRUCTURE_RISK", "2"))
SMART_V2_CORE_MIN_TREND_15M = float(os.getenv("SMART_V2_CORE_MIN_TREND_15M", "0.30"))
SMART_V2_CORE_MIN_BTC_5M = float(os.getenv("SMART_V2_CORE_MIN_BTC_5M", "-0.05"))
SMART_V2_CORE_MIN_OI = float(os.getenv("SMART_V2_CORE_MIN_OI", "-0.50"))

SMART_V2_TOXIC_WINDOW = int(os.getenv("SMART_V2_TOXIC_WINDOW", "4"))
SMART_V2_TOXIC_COOLDOWN_HOURS = float(os.getenv("SMART_V2_TOXIC_COOLDOWN_HOURS", "12"))
SMART_V2_TOXIC_MAX_SL_RATE = float(os.getenv("SMART_V2_TOXIC_MAX_SL_RATE", "0.50"))
SMART_V2_TOXIC_SL_AVG_NET_MAX = float(os.getenv("SMART_V2_TOXIC_SL_AVG_NET_MAX", "0.02"))
SMART_V2_TOXIC_MIN_AVG_NET = float(os.getenv("SMART_V2_TOXIC_MIN_AVG_NET", "-0.05"))
SMART_V2_TOXIC_MIN_AVG_MFE = float(os.getenv("SMART_V2_TOXIC_MIN_AVG_MFE", "0.60"))
SMART_V2_GOOD_MFE = float(os.getenv("SMART_V2_GOOD_MFE", "0.80"))

# ============================================================
# V15 SPREAD SCOUT / SKIP LEARNING
# ============================================================
# V15 не трогает DEPTH_THIN. Он проверяет гипотезу:
# часть SPREAD_WIDE 5-12bps может быть прибыльной, если сигнал очень чистый.
# Ветка dry-only; real НЕ включать.
V15_SCOUT_MARGIN = float(os.getenv("V15_SCOUT_MARGIN", "3.0"))
V15_SCOUT_LEVERAGE = int(os.getenv("V15_SCOUT_LEVERAGE", "4"))
V15_SCOUT_MAX_OPEN = int(os.getenv("V15_SCOUT_MAX_OPEN", "1"))

V15_SCOUT_MIN_SPREAD_BPS = float(os.getenv("V15_SCOUT_MIN_SPREAD_BPS", "5.0"))
V15_SCOUT_MAX_SPREAD_BPS = float(os.getenv("V15_SCOUT_MAX_SPREAD_BPS", "12.0"))

V15_SCOUT_MIN_SCORE = int(os.getenv("V15_SCOUT_MIN_SCORE", "6"))
V15_SCOUT_MIN_TREND_15M = float(os.getenv("V15_SCOUT_MIN_TREND_15M", "0.40"))
V15_SCOUT_MIN_BTC_5M = float(os.getenv("V15_SCOUT_MIN_BTC_5M", "0.00"))
V15_SCOUT_MIN_OI = float(os.getenv("V15_SCOUT_MIN_OI", "-0.50"))
V15_SCOUT_MAX_PRICE_CHANGE = float(os.getenv("V15_SCOUT_MAX_PRICE_CHANGE", "0.65"))
V15_SCOUT_MAX_VOL_RATIO = float(os.getenv("V15_SCOUT_MAX_VOL_RATIO", "35"))
V15_SCOUT_MAX_BRISK = int(os.getenv("V15_SCOUT_MAX_BRISK", "3"))
V15_SCOUT_MAX_FALSE_BREAKOUTS = int(os.getenv("V15_SCOUT_MAX_FALSE_BREAKOUTS", "1"))
V15_SCOUT_MAX_STRUCTURE_RISK = int(os.getenv("V15_SCOUT_MAX_STRUCTURE_RISK", "1"))

V15_SCOUT_PROFIT_LOCK = float(os.getenv("V15_SCOUT_PROFIT_LOCK", "0.70"))
V15_SCOUT_LOSS_LOCK = float(os.getenv("V15_SCOUT_LOSS_LOCK", "-0.35"))
V15_SCOUT_GIVEBACK_ACTIVATION = float(os.getenv("V15_SCOUT_GIVEBACK_ACTIVATION", "0.45"))
V15_SCOUT_GIVEBACK_DROP = float(os.getenv("V15_SCOUT_GIVEBACK_DROP", "0.25"))

V15_SKIP_LEARNING_ENABLED = os.getenv("V15_SKIP_LEARNING_ENABLED", "true").lower() == "true"
V15_SKIP_LEARN_COOLDOWN = int(os.getenv("V15_SKIP_LEARN_COOLDOWN", "900"))
V15_SKIP_LEARN_DEPTH_THIN = os.getenv("V15_SKIP_LEARN_DEPTH_THIN", "true").lower() == "true"
V15_SKIP_LEARN_SPREAD_WIDE = os.getenv("V15_SKIP_LEARN_SPREAD_WIDE", "true").lower() == "true"
V15_SKIP_LEARN_TIME_AS_NEUTRAL = os.getenv("V15_SKIP_LEARN_TIME_AS_NEUTRAL", "true").lower() == "true" 

# Current signal overrides used by winning V2_STRICT.
SMART_V2_ALLOW_STRONG_OVERRIDE = os.getenv("SMART_V2_ALLOW_STRONG_OVERRIDE", "true").lower() == "true"
SMART_V2_ALLOW_ULTRA_OVERRIDE = os.getenv("SMART_V2_ALLOW_ULTRA_OVERRIDE", "true").lower() == "true"

# Daily dry-live locks for x10 micro profile.
SMART_V2_PROFIT_LOCK = float(os.getenv("SMART_V2_PROFIT_LOCK", "2.0"))
SMART_V2_LOSS_LOCK = float(os.getenv("SMART_V2_LOSS_LOCK", "-1.2"))
SMART_V2_GIVEBACK_ACTIVATION = float(os.getenv("SMART_V2_GIVEBACK_ACTIVATION", "1.0"))
SMART_V2_GIVEBACK_DROP = float(os.getenv("SMART_V2_GIVEBACK_DROP", "0.60"))






# ============================================================
# V16 MICRO-LIVE REAL EXECUTION GATE
# ============================================================
# Real trading is disabled unless ALL are true:
# REAL_TRADING_ENABLED=true, REAL_TRADING_ARMED=true, LIVE_DRY_RUN=false.
# Keep LIVE_DRY_TRACKS=META_V12_EXEC_SAFE_MO1 for first micro-live stage.
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET", "")
MEXC_FUTURES_BASE_URL = os.getenv("MEXC_FUTURES_BASE_URL", "https://api.mexc.com")
MEXC_RECV_WINDOW = int(os.getenv("MEXC_RECV_WINDOW", "10000"))

REAL_TRADING_ENABLED = os.getenv("REAL_TRADING_ENABLED", "false").lower() == "true"
REAL_TRADING_ARMED = os.getenv("REAL_TRADING_ARMED", "false").lower() == "true"
REAL_STRATEGY = os.getenv("REAL_STRATEGY", "META_V12_EXEC_SAFE_MO1")
REAL_MARGIN_USDT = float(os.getenv("REAL_MARGIN_USDT", "3.0"))
REAL_MAX_MARGIN_USDT = float(os.getenv("REAL_MAX_MARGIN_USDT", "3.0"))
REAL_MAX_ACTUAL_MARGIN_USDT = float(os.getenv("REAL_MAX_ACTUAL_MARGIN_USDT", "4.25"))
REAL_LEVERAGE = int(os.getenv("REAL_LEVERAGE", "4"))
REAL_MAX_TRADES_PER_DAY = int(os.getenv("REAL_MAX_TRADES_PER_DAY", "1"))
REAL_DAILY_MAX_LOSS_USDT = float(os.getenv("REAL_DAILY_MAX_LOSS_USDT", "0.35"))
REAL_MAX_SPREAD_BPS = float(os.getenv("REAL_MAX_SPREAD_BPS", "3.0"))
REAL_POSITION_MODE = int(os.getenv("REAL_POSITION_MODE", "1"))  # 1 dual-side, 2 one-way


# ============================================================
# STRATEGY CONFIGS
# ============================================================
@dataclass
class StrategyConfig:
    name: str
    family: str
    margin: float
    tp: float
    leverage: int = LEVERAGE
    max_open: int = 2
    p_lock: float = PROFIT_LOCK_LIMIT
    l_lock: float = LOSS_LOCK_LIMIT
    give_act: float = GIVEBACK_ACTIVATION
    give_drop: float = GIVEBACK_DROP
    silent: bool = True
    selector: bool = False
    require_depth: bool = False
    spread_limit_bps: float = 999.0
    coin_ban_after_sl: bool = False
    be_v2_test: bool = False
    no_reward_exit_test: bool = False
    skip_track: bool = False

    # V11.2 live-compatible MFE-based exit tests.
    time_stop_min: float = 15.0
    fast_fail_test: bool = False
    micro_lock_test: bool = False
    partial_take_test: bool = False
    global_toxic_ban: bool = False

    # V11.3 confirmation entry: selector does not open immediately.
    # It stores signal into pending-watch and opens only after follow-through.
    confirm_entry: bool = False
    confirm_mode: str = "NONE"
    confirm_no_rug_pct: float = CONFIRM_NO_RUG_PCT
    confirm_wait_seconds: float = CONFIRM_WAIT_SECONDS
    confirm_max_seconds: float = CONFIRM_MAX_SECONDS
    confirm_max_price_change: float = CONFIRM_MAX_PRICE_CHANGE_DEFAULT
    confirm_max_vol_ratio: float = CONFIRM_MAX_VOL_RATIO_DEFAULT
    confirm_max_move_pct: float = CONFIRM_MAX_MOVE_PCT_DEFAULT
    confirm_keep_until_max: bool = False

    # V11.4 dynamic exit/universe gates.
    atr5b_exit: bool = False
    universe_top_n: int = 0        # 0 = no current-turnover universe filter
    min_trend_15m_override: float = -999.0
    # V11.5 breakout-risk gates.
    breakout_risk_mode: str = "NONE"  # NONE / NO_FALSE_BREAKOUT / COMBO_BALANCED
    # V12 meta-selector gates.
    meta_oi_min: float = -999.0
    meta_trend_min: float = -999.0
    meta_risk_max: int = 999
    meta_false_bo_max: int = 999
    # V13 smart-universe gates.
    smart_guard: str = "NONE"      # CLEAN_EXEC / OI0_CLEAN / BTC0_CLEAN
    smart_mode: str = "NONE"       # V2_STRICT
    smart_core_top: int = 0
    smart_mid_top: int = 0
    # V15 scout gates.
    min_spread_bps: float = 0.0




def _exec_main(name: str, spread: float, silent: bool = True, nf: bool = False, be: bool = False) -> StrategyConfig:
    return StrategyConfig(
        name=name,
        family="main_tp08_exec",
        margin=3.0,
        tp=0.8,
        leverage=4,
        max_open=1,
        p_lock=0.60,
        l_lock=-0.35,
        give_act=0.40,
        give_drop=0.22,
        silent=silent,
        selector=True,
        require_depth=True,
        spread_limit_bps=spread,
        coin_ban_after_sl=True,
        be_v2_test=be,
        no_reward_exit_test=nf,
        skip_track=True,
    )


def _exec_fomo(name: str, spread: float, silent: bool = True, nf: bool = False, be: bool = False) -> StrategyConfig:
    return StrategyConfig(
        name=name,
        family="hybrid_full_main_fomo_exec",
        margin=3.0,
        tp=0.8,
        leverage=4,
        max_open=1,
        p_lock=0.70,
        l_lock=-0.40,
        give_act=0.45,
        give_drop=0.25,
        silent=silent,
        selector=True,
        require_depth=True,
        spread_limit_bps=spread,
        coin_ban_after_sl=True,
        be_v2_test=be,
        no_reward_exit_test=nf,
        skip_track=True,
    )



def _runner_strategy(
    name: str,
    family: str,
    spread: float,
    silent: bool = False,
    partial: bool = False,
    micro: bool = False,
    fast: bool = True,
    confirm: bool = False,
    confirm_mode: str = "NO_RUG_CLOSE",
    confirm_no_rug: float = CONFIRM_NO_RUG_PCT,
    confirm_max_price: float = CONFIRM_MAX_PRICE_CHANGE_DEFAULT,
    confirm_max_vol: float = CONFIRM_MAX_VOL_RATIO_DEFAULT,
    confirm_max_move: float = CONFIRM_MAX_MOVE_PCT_DEFAULT,
    confirm_keep_until_max: bool = False,
    atr5b_exit: bool = False,
    universe_top_n: int = 0,
    min_trend_15m_override: float = -999.0,
    max_open: int = 1,
) -> StrategyConfig:
    return StrategyConfig(
        name=name,
        family=family,
        margin=3.0,
        tp=PARTIAL_RUNNER_TP_PCT,
        leverage=4,
        max_open=max_open,
        p_lock=0.80,
        l_lock=-0.35,
        give_act=0.55,
        give_drop=0.25,
        silent=silent,
        selector=True,
        require_depth=True,
        spread_limit_bps=spread,
        coin_ban_after_sl=True,
        be_v2_test=False,
        no_reward_exit_test=False,
        skip_track=True,
        time_stop_min=RUNNER_TIME_STOP_MINUTES,
        fast_fail_test=fast,
        micro_lock_test=micro,
        partial_take_test=partial,
        global_toxic_ban=True,
        confirm_entry=confirm,
        confirm_mode=confirm_mode,
        confirm_no_rug_pct=confirm_no_rug,
        confirm_wait_seconds=CONFIRM_WAIT_SECONDS,
        confirm_max_seconds=CONFIRM_MAX_SECONDS,
        confirm_max_price_change=confirm_max_price,
        confirm_max_vol_ratio=confirm_max_vol,
        confirm_max_move_pct=confirm_max_move,
        confirm_keep_until_max=confirm_keep_until_max,
        atr5b_exit=atr5b_exit,
        universe_top_n=universe_top_n,
        min_trend_15m_override=min_trend_15m_override,
    )


def _trend_atr_confirm_strategy(
    name: str,
    universe_top_n: int,
    max_open: int,
    wait_seconds: float,
    max_seconds: float,
    keep_until_max: bool,
    spread: float = 5,
    silent: bool = False,
) -> StrategyConfig:
    s = _runner_strategy(
        name=name,
        family="initiative_confirm_trend_atr",
        spread=spread,
        silent=silent,
        partial=True,
        micro=False,
        fast=False,
        confirm=True,
        confirm_mode="NO_RUG_CLOSE",
        confirm_no_rug=-0.15,
        confirm_max_price=TREND_ATR_MAX_PRICE_CHANGE,
        confirm_max_vol=TREND_ATR_MAX_VOL_RATIO,
        confirm_max_move=TREND_ATR_CONFIRM_MAX_MOVE,
        confirm_keep_until_max=keep_until_max,
        atr5b_exit=True,
        universe_top_n=universe_top_n,
        min_trend_15m_override=TREND_ATR_MIN_TREND_15M,
        max_open=max_open,
    )
    s.confirm_wait_seconds = wait_seconds
    s.confirm_max_seconds = max_seconds
    s.time_stop_min = ATR5B_TIME_STOP_MINUTES
    return s


# === V11.5 PATCH START: breakout confirm strategy ===
def _breakout_confirm_strategy(
    name: str,
    risk_mode: str,
    trend_min: float,
    max_open: int,
    spread: float = BREAKOUT_SPREAD_LIMIT_BPS,
    silent: bool = False,
) -> StrategyConfig:
    s = _runner_strategy(
        name=name,
        family="breakout_confirm_atr",
        spread=spread,
        silent=silent,
        partial=True,
        micro=False,
        fast=False,
        confirm=True,
        confirm_mode="NO_RUG_CLOSE",
        confirm_no_rug=-0.15,
        confirm_max_price=BREAKOUT_MAX_PRICE_CHANGE,
        confirm_max_vol=BREAKOUT_MAX_VOL_RATIO,
        confirm_max_move=BREAKOUT_CONFIRM_MAX_MOVE,
        confirm_keep_until_max=False,
        atr5b_exit=True,
        universe_top_n=0,
        min_trend_15m_override=trend_min,
        max_open=max_open,
    )
    s.confirm_wait_seconds = 60
    s.confirm_max_seconds = 95
    s.time_stop_min = ATR5B_TIME_STOP_MINUTES
    s.breakout_risk_mode = risk_mode
    return s
# === V11.5 PATCH END: breakout confirm strategy ===



# === V12 PATCH START: meta exec-safe strategy ===
def _meta_v12_strategy(
    name: str,
    family: str,
    oi_min: float,
    trend_min: float,
    risk_max: int = META_V12_MAX_BRISK,
    false_bo_max: int = META_V12_MAX_FALSE_BREAKOUTS,
    silent: bool = False,
) -> StrategyConfig:
    s = _runner_strategy(
        name=name,
        family=family,
        spread=META_V12_SPREAD_LIMIT_BPS,
        silent=silent,
        partial=True,
        micro=False,
        fast=False,
        confirm=True,
        confirm_mode="NO_RUG_CLOSE",
        confirm_no_rug=-0.15,
        confirm_max_price=META_V12_MAX_PRICE_CHANGE,
        confirm_max_vol=META_V12_MAX_VOL_RATIO,
        confirm_max_move=META_V12_CONFIRM_MAX_MOVE,
        confirm_keep_until_max=False,
        atr5b_exit=True,
        universe_top_n=0,
        min_trend_15m_override=trend_min,
        max_open=META_V12_MAX_OPEN,
    )
    s.margin = META_V12_MARGIN
    s.leverage = META_V12_LEVERAGE
    s.tp = PARTIAL_RUNNER_TP_PCT
    s.time_stop_min = ATR5B_TIME_STOP_MINUTES
    s.meta_oi_min = oi_min
    s.meta_trend_min = trend_min
    s.meta_risk_max = risk_max
    s.meta_false_bo_max = false_bo_max
    return s
# === V12 PATCH END: meta exec-safe strategy ===


# === V13 PATCH START: smart-universe V2 strategy ===
def _smart_v2_strategy(
    name: str,
    guard: str,
    silent: bool = False,
) -> StrategyConfig:
    s = _runner_strategy(
        name=name,
        family="smart_v2_strict",
        spread=SMART_V2_SPREAD_LIMIT_BPS,
        silent=silent,
        partial=True,
        micro=False,
        fast=False,
        confirm=True,
        confirm_mode="NO_RUG_CLOSE",
        confirm_no_rug=-0.15,
        confirm_max_price=0.55,
        confirm_max_vol=35,
        confirm_max_move=0.75,
        confirm_keep_until_max=False,
        atr5b_exit=True,
        universe_top_n=0,
        min_trend_15m_override=0.30,
        max_open=SMART_V2_MAX_OPEN,
    )
    s.margin = SMART_V2_MARGIN
    s.leverage = SMART_V2_LEVERAGE
    s.tp = PARTIAL_RUNNER_TP_PCT
    s.time_stop_min = ATR5B_TIME_STOP_MINUTES
    s.smart_guard = guard
    s.smart_mode = "V2_STRICT"
    s.smart_core_top = SMART_V2_CORE_TOP
    s.smart_mid_top = SMART_V2_MID_TOP
    s.p_lock = SMART_V2_PROFIT_LOCK
    s.l_lock = SMART_V2_LOSS_LOCK
    s.give_act = SMART_V2_GIVEBACK_ACTIVATION
    s.give_drop = SMART_V2_GIVEBACK_DROP
    return s
# === V13 PATCH END: smart-universe V2 strategy ===

# === V15 PATCH START: spread scout dry-only ===
def _v15_spread_scout_strategy(name: str = "V15_SPREAD_SCOUT_MO1", silent: bool = False) -> StrategyConfig:
    s = _runner_strategy(
        name=name,
        family="v15_spread_scout",
        spread=V15_SCOUT_MAX_SPREAD_BPS,
        silent=silent,
        partial=True,
        micro=False,
        fast=False,
        confirm=True,
        confirm_mode="NO_RUG_CLOSE",
        confirm_no_rug=-0.15,
        confirm_max_price=V15_SCOUT_MAX_PRICE_CHANGE,
        confirm_max_vol=V15_SCOUT_MAX_VOL_RATIO,
        confirm_max_move=0.75,
        confirm_keep_until_max=False,
        atr5b_exit=True,
        universe_top_n=0,
        min_trend_15m_override=V15_SCOUT_MIN_TREND_15M,
        max_open=V15_SCOUT_MAX_OPEN,
    )
    s.margin = V15_SCOUT_MARGIN
    s.leverage = V15_SCOUT_LEVERAGE
    s.tp = PARTIAL_RUNNER_TP_PCT
    s.time_stop_min = ATR5B_TIME_STOP_MINUTES
    s.min_spread_bps = V15_SCOUT_MIN_SPREAD_BPS
    s.p_lock = V15_SCOUT_PROFIT_LOCK
    s.l_lock = V15_SCOUT_LOSS_LOCK
    s.give_act = V15_SCOUT_GIVEBACK_ACTIVATION
    s.give_drop = V15_SCOUT_GIVEBACK_DROP
    return s
# === V15 PATCH END: spread scout dry-only ===




def build_strategy_configs():
    configs = []

    # V13 SMART UNIVERSE V2 DRY CANDIDATES.
    # Archive winner family:
    # FILTERED_055 + CLEAN/OI/BTC guards + WAIT1_CLOSE + ATR5B_ORIGINAL,
    # with smart universe: core<=30, mid<=70 gated by symbol-quality, >mid monitor-only.
    configs += [
        _smart_v2_strategy("SMART_V2_STRICT_CLEAN_MO1", guard="CLEAN_EXEC", silent=False),
        _smart_v2_strategy("SMART_V2_STRICT_OI_MO1", guard="OI0_CLEAN", silent=False),
        _smart_v2_strategy("SMART_V2_STRICT_BTC_MO1", guard="BTC0_CLEAN", silent=True),
    ]



    # V15 SPREAD SCOUT DRY-ONLY.
    # Берёт только depth-ok, spread 5-12bps, очень чистые сигналы.
    configs += [
        _v15_spread_scout_strategy("V15_SPREAD_SCOUT_MO1", silent=False),
    ]


    # V12 META EXEC-SAFE DRY CANDIDATES.
    # Old/new signal families become sources only; they no longer open as raw 10x shadow tracks.
    configs += [
        _meta_v12_strategy(
            "META_V12_EXEC_SAFE_MO1",
            family="meta_v12_exec_safe",
            oi_min=META_V12_OI_SOFT_MIN,
            trend_min=META_V12_MIN_TREND_15M,
            silent=False,
        ),
        _meta_v12_strategy(
            "META_V12_OI_SAFE_MO1",
            family="meta_v12_oi_safe",
            oi_min=META_V12_OI_STRICT_MIN,
            trend_min=META_V12_MIN_TREND_15M,
            silent=False,
        ),
    ]



    # V11.5 BREAKOUT-RISK + ATR5_B DRY CANDIDATES.
    configs += [
        _breakout_confirm_strategy(
            "BREAKOUT_TREND040_PC065_VOL35_NO_FALSE_ATR5B_WAIT1_MO1",
            risk_mode="NO_FALSE_BREAKOUT",
            trend_min=BREAKOUT_MIN_TREND_15M,
            max_open=1,
            silent=False,
        ),
        _breakout_confirm_strategy(
            "BREAKOUT_TREND040_PC065_VOL35_NO_FALSE_ATR5B_WAIT1_MO2",
            risk_mode="NO_FALSE_BREAKOUT",
            trend_min=BREAKOUT_MIN_TREND_15M,
            max_open=2,
            silent=False,
        ),
        _breakout_confirm_strategy(
            "BREAKOUT_TREND040_PC065_VOL35_COMBO_BALANCED_ATR5B_WAIT1_MO1",
            risk_mode="COMBO_BALANCED",
            trend_min=BREAKOUT_MIN_TREND_15M,
            max_open=1,
            silent=False,
        ),
        _breakout_confirm_strategy(
            "BREAKOUT_TREND040_PC065_VOL35_COMBO_BALANCED_ATR5B_WAIT1_MO2",
            risk_mode="COMBO_BALANCED",
            trend_min=BREAKOUT_MIN_TREND_15M,
            max_open=2,
            silent=False,
        ),
        _breakout_confirm_strategy(
            "BREAKOUT_TREND030_PC065_VOL35_NO_FALSE_ATR5B_WAIT1_MO2",
            risk_mode="NO_FALSE_BREAKOUT",
            trend_min=BREAKOUT_MIN_TREND_15M_LOOSE,
            max_open=2,
            silent=True,
        ),
    ]


    # V11.4 TREND + ATR5_B + UNIVERSE DRY CANDIDATES.
    # QUALITY_TOP20: highest AvgNet in no-lookahead/static-top tests.
    # ROLL24_TOP30: more trades using current rolling 24h turnover rank from ticker amount24.
    # MO2 tracks are shadow-only by default because DryLiveManager currently tracks one live position per track.
    configs += [
        _trend_atr_confirm_strategy(
            "QUALITY_TOP20_TREND040_ATR5B_WAIT1_MO1",
            universe_top_n=20,
            max_open=1,
            wait_seconds=60,
            max_seconds=95,
            keep_until_max=False,
            silent=False,
        ),
        _trend_atr_confirm_strategy(
            "QUALITY_TOP20_TREND040_ATR5B_WAIT1_MO2",
            universe_top_n=20,
            max_open=2,
            wait_seconds=60,
            max_seconds=95,
            keep_until_max=False,
            silent=False,
        ),
        _trend_atr_confirm_strategy(
            "ROLL24_TOP30_TREND040_ATR5B_WAIT3_MO1",
            universe_top_n=30,
            max_open=1,
            wait_seconds=60,
            max_seconds=205,
            keep_until_max=True,
            silent=False,
        ),
        _trend_atr_confirm_strategy(
            "ROLL24_TOP30_TREND040_ATR5B_WAIT3_MO2",
            universe_top_n=30,
            max_open=2,
            wait_seconds=60,
            max_seconds=205,
            keep_until_max=True,
            silent=False,
        ),
    ]

    # V11.3 CONFIRMATION RUNNER CANDIDATES.
    # Archive winner family:
    # - wait for follow-through after anomaly
    # - next/live price must stay above signal and no-rug threshold must hold
    # - partial 50% at +0.80, runner TP +2.00, runner stop +0.10
    configs += [
        _runner_strategy(
            "INITIATIVE_CONFIRM_RUG015_PC055_VOL25_DYN08_5",
            "initiative_confirm_runner",
            5,
            silent=False,
            partial=True,
            micro=False,
            fast=True,
            confirm=True,
            confirm_mode="NO_RUG_CLOSE",
            confirm_no_rug=-0.15,
            confirm_max_price=0.55,
            confirm_max_vol=25,
        ),
        _runner_strategy(
            "INITIATIVE_CONFIRM_RUG015_PC065_VOL25_DYN08_5",
            "initiative_confirm_runner",
            5,
            silent=False,
            partial=True,
            micro=False,
            fast=True,
            confirm=True,
            confirm_mode="NO_RUG_CLOSE",
            confirm_no_rug=-0.15,
            confirm_max_price=0.65,
            confirm_max_vol=25,
        ),
        _runner_strategy(
            "INITIATIVE_CONFIRM_RUG020_PC055_VOL25_DYN08_5",
            "initiative_confirm_runner",
            5,
            silent=False,
            partial=True,
            micro=False,
            fast=True,
            confirm=True,
            confirm_mode="NO_RUG_CLOSE",
            confirm_no_rug=-0.20,
            confirm_max_price=0.55,
            confirm_max_vol=25,
        ),

        # Kept as shadow controls, not default dry-live.
        _runner_strategy("INITIATIVE_RUNNER_TP20_FF_PARTIAL_5", "initiative_runner", 5, silent=True, partial=True, micro=True, fast=True),
        _runner_strategy("MAIN_CONTEXT_STRICT_TP20_FF_PARTIAL_5", "main_context_strict_runner", 5, silent=True, partial=True, micro=True, fast=True),
    ]

    # V11 EXEC-SAFE CONTROL CANDIDATES.
    # Kept for comparison with previous version.
    configs += [
        _exec_main("MAIN_V92_TP08_EXEC_5", 5, silent=True),
        _exec_main("MAIN_V92_TP08_EXEC_7", 7, silent=False),
        _exec_main("MAIN_V92_TP08_EXEC_10", 10, silent=False),

        _exec_fomo("HYBRID_FULL_MAIN_FOMO_EXEC_5", 5, silent=True),
        _exec_fomo("HYBRID_FULL_MAIN_FOMO_EXEC_7", 7, silent=False),
        _exec_fomo("HYBRID_FULL_MAIN_FOMO_EXEC_10", 10, silent=True),

        _exec_main("MAIN_V92_TP08_EXEC_7_NF_TEST", 7, silent=True, nf=True),
        _exec_fomo("HYBRID_FULL_MAIN_FOMO_EXEC_7_NF_TEST", 7, silent=True, nf=True),
        _exec_main("MAIN_V92_TP08_EXEC_7_BE_V2", 7, silent=True, be=True),
        _exec_fomo("HYBRID_FULL_MAIN_FOMO_EXEC_7_BE_V2", 7, silent=True, be=True),
    ]

    # OLD SAFE CONTROL SET from v10.5a. Not live-candidate anymore, just baseline.
    configs += [
        StrategyConfig("FILTERED_045_SAFE", "safe_045", 3.0, 0.8, 4, 1, 0.50, -0.30, 0.30, 0.18, True, True, True, 5, True),
        StrategyConfig("FILTERED_045_SAFE_2X", "safe_045", 3.0, 0.8, 4, 2, 0.70, -0.50, 0.40, 0.25, True, True, True, 5, True),
        StrategyConfig("FILTERED_045_SAFE_STRICT", "safe_045_strict", 3.0, 0.8, 4, 1, 0.50, -0.30, 0.30, 0.18, True, True, True, 5, True),
    ]

    # FULL SHADOW RESEARCH SET.
    configs += [
        StrategyConfig("HYBRID_CORE", "hybrid_core", 4.5, 0.8, silent=True),
        StrategyConfig("HYBRID_SCALP", "hybrid_scalp", 4.5, 0.8, silent=True),
        StrategyConfig("HYBRID_FULL_MAIN_FOMO", "hybrid_full_main_fomo", 4.5, 0.8, silent=True),
        StrategyConfig("HYBRID_FULL_ALL", "hybrid_full_all", 4.5, 0.8, silent=True),
        StrategyConfig("HYBRID_FULL_ALL_SAFE_SHADOW", "hybrid_full_all_safe_shadow", 4.5, 0.8, silent=True),

        StrategyConfig("MAIN_V92_TP10", "main_v92_tp10", 4.5, 1.0, silent=True),
        StrategyConfig("MAIN_V92_TP08", "main_v92_tp08", 4.5, 0.8, silent=True),
        StrategyConfig("FILTERED_055_TP08", "filtered_055", 4.5, 0.8, silent=True),
        StrategyConfig("FILTERED_045", "filtered_045", 4.5, 0.8, silent=True),
        StrategyConfig("FOMO_TEST", "fomo_test", 3.0, 0.8, silent=True),
        StrategyConfig("YELLOW_SCORE3", "yellow_score3", 3.0, 0.8, silent=True),
        StrategyConfig("YELLOW_SCORE3_FAST", "yellow_score3_fast", 3.0, 0.8, silent=True),
        StrategyConfig(
            "COST_NEAR_MISS_FAST", "cost_near_miss_fast",
            margin=3.0, tp=0.8, leverage=4, max_open=1,
            silent=True, selector=True, require_depth=True,
            spread_limit_bps=5.0, skip_track=True,
        ),
        StrategyConfig(
            "COST_RESCUE_CLEAN_IMPULSE", "cost_rescue_clean_impulse",
            margin=3.0, tp=0.8, leverage=4, max_open=1,
            silent=True, selector=True, require_depth=True,
            spread_limit_bps=5.0, skip_track=True,
        ),
        StrategyConfig(
            "DEPTH_THIN_ESCAPE_SHADOW", "depth_thin_escape_shadow",
            margin=3.0, tp=0.8, leverage=4, max_open=1,
            silent=True, selector=True, require_depth=True,
            spread_limit_bps=5.0, skip_track=True,
        ),
        StrategyConfig("YELLOW_SCORE2", "yellow_score2", 3.0, 0.8, silent=True),
        StrategyConfig("YELLOW_SCORE2_TIGHT", "yellow_score2_tight", 3.0, 0.8, silent=True),
    ]

    return {c.name: c for c in configs}


# ============================================================
# RESEARCH FADE V1 SHADOW ONLY
# ============================================================
# Based on v17 train/test weak robust rule:
# SHORT ABS030|SP3|R150|V5|IMB_ASK
# This is research-only. It never sends real orders and does not affect dry-live.
RESEARCH_FADE_V1_ENABLED = os.getenv("RESEARCH_FADE_V1_ENABLED", "true").lower() == "true"
RESEARCH_FADE_V1_SIDE = os.getenv("RESEARCH_FADE_V1_SIDE", "SHORT")
RESEARCH_FADE_V1_TTL_SECONDS = float(os.getenv("RESEARCH_FADE_V1_TTL_SECONDS", "300"))
RESEARCH_FADE_V1_MARGIN = float(os.getenv("RESEARCH_FADE_V1_MARGIN", "3.0"))
RESEARCH_FADE_V1_LEVERAGE = int(os.getenv("RESEARCH_FADE_V1_LEVERAGE", "4"))
RESEARCH_FADE_V1_MAX_OPEN = int(os.getenv("RESEARCH_FADE_V1_MAX_OPEN", "3"))
RESEARCH_FADE_V1_COOLDOWN_SECONDS = float(os.getenv("RESEARCH_FADE_V1_COOLDOWN_SECONDS", "600"))

RESEARCH_FADE_V1_MIN_ABS_PC = float(os.getenv("RESEARCH_FADE_V1_MIN_ABS_PC", "0.30"))
RESEARCH_FADE_V1_MAX_SPREAD_BPS = float(os.getenv("RESEARCH_FADE_V1_MAX_SPREAD_BPS", "3.0"))
RESEARCH_FADE_V1_MAX_RANK = int(os.getenv("RESEARCH_FADE_V1_MAX_RANK", "150"))
RESEARCH_FADE_V1_MIN_VOL_RATIO = float(os.getenv("RESEARCH_FADE_V1_MIN_VOL_RATIO", "5.0"))
RESEARCH_FADE_V1_IMB5_MAX = float(os.getenv("RESEARCH_FADE_V1_IMB5_MAX", "-0.20"))
# Aggressive fade matrix runtime controls.
RESEARCH_FADE_V1_MAX_OPEN_TOTAL = int(os.getenv("RESEARCH_FADE_V1_MAX_OPEN_TOTAL", "9"))
RESEARCH_FADE_V1_MAX_OPEN_PER_PROFILE = int(os.getenv("RESEARCH_FADE_V1_MAX_OPEN_PER_PROFILE", "3"))
RESEARCH_FADE_V1_POLL_SECONDS = float(os.getenv("RESEARCH_FADE_V1_POLL_SECONDS", "20"))


# ============================================================
# REJECT OBSERVER V1
# Tracks virtual trades that were rejected by filters/rules.
# This does NOT affect real/dry execution; it only answers:
# "what would have happened if this filter did not reject?"
# ============================================================
REJECT_OBSERVER_ENABLED = True
REJECT_OBSERVER_TRACK_RULES_NOT_MET = True
REJECT_OBSERVER_TRACK_CAN_OPEN = True

# Do not observe every tiny trash signal. Keep volume useful but controlled.
REJECT_OBSERVER_MIN_SCORE = 3
REJECT_OBSERVER_MIN_VOL_RATIO = 8.0
REJECT_OBSERVER_MIN_ABS_PRICE_CHANGE = 0.20

# Avoid infinite duplicated reject watches from many similar strategies.
REJECT_OBSERVER_REASON_PREFIX = "REJECT_"



# ============================================================
# COST AWARE V1 / YELLOW FAST / DEPTH THIN ESCAPE
# ============================================================
COST_AWARE_ENABLED = True

# Current heavy taker model ~= 29bps breakeven.
# We demand at least some expected move buffer.
COST_GATE_MIN_PC_LONG = 0.30
COST_GATE_MIN_VOL_LONG = 8.0
COST_GATE_MIN_SCORE_LONG = 3
COST_GATE_MAX_SPREAD_LONG_BPS = 5.0

YELLOW_SCORE3_FAST_ENABLED = True
YELLOW_SCORE3_FAST_MIN_PC = 0.30
YELLOW_SCORE3_FAST_MAX_PC = 0.50
YELLOW_SCORE3_FAST_MIN_VOL = 8.0
YELLOW_SCORE3_FAST_MIN_TREND = 0.20
YELLOW_SCORE3_FAST_MIN_BTC = -0.05
YELLOW_SCORE3_FAST_MIN_OI = -1.0
YELLOW_SCORE3_FAST_MAX_STRUCT = 3
YELLOW_SCORE3_FAST_MAX_BRISK = 4
YELLOW_SCORE3_FAST_MAX_FB = 2

# Do not disable DEPTH_THIN globally.
# Only observe an escape lane when the rejected signal is unusually strong.
DEPTH_THIN_ESCAPE_ENABLED = True
DEPTH_THIN_ESCAPE_MIN_SCORE = 5
DEPTH_THIN_ESCAPE_MIN_VOL = 15.0
DEPTH_THIN_ESCAPE_MIN_PC = 0.30
DEPTH_THIN_ESCAPE_MAX_RANK = 80



# ============================================================
# EXECUTION COST MODEL V2
# ============================================================
# Core idea:
# Do not let strategies spend taker-like costs on moves that cannot
# realistically survive fees + spread + slippage.
#
# Units: bps. 1 bps = 0.01%.
#
# Current conservative model:
#   taker 8 bps per side + spread + slippage.
# If actual account fee is lower, change these constants after verification,
# not by hope.
EXEC_COST_MODEL_ENABLED = True

EXEC_FEE_TAKER_BPS_PER_SIDE = 8.0
EXEC_FEE_MAKER_BPS_PER_SIDE = 0.0

EXEC_DEFAULT_SLIPPAGE_BPS_PER_SIDE = 5.0
EXEC_MIN_SPREAD_BPS_FLOOR = 1.0

# Cost buffer:
# 1.0 = expected move only equals breakeven
# 1.5 = expected move must be 50% bigger than breakeven
# 2.0 = aggressive safety
EXEC_COST_BUFFER_NORMAL = 1.60
EXEC_COST_BUFFER_FAST = 1.30
EXEC_COST_BUFFER_ESCAPE = 1.20

# Absolute minimums for taker-like scalping.
# Even if formula says lower, do not trade tiny moves.
EXEC_MIN_EXPECTED_MOVE_BPS_NORMAL = 35.0
EXEC_MIN_EXPECTED_MOVE_BPS_FAST = 30.0
EXEC_MIN_EXPECTED_MOVE_BPS_ESCAPE = 30.0

# How we estimate expected move from current signal.
# Current signal price_change is in percent, so 0.35% = 35 bps.
# We do NOT assume full current impulse will continue.
EXEC_EXPECTED_MOVE_MULTIPLIER_NORMAL = 0.85
EXEC_EXPECTED_MOVE_MULTIPLIER_FAST = 0.90
EXEC_EXPECTED_MOVE_MULTIPLIER_ESCAPE = 0.80

# Gross-positive but cost-killed trades should go to observer/shadow,
# not into real.
EXEC_COST_GATE_LOG_PREFIX = "COST_GATE"



# ============================================================
# REJECT OBSERVER V2 NO-SPAM
# ============================================================
# Do not create reject watches for every experimental strategy.
# We only need representative lanes to measure what filters reject.
REJECT_OBSERVER_STRATEGY_ALLOWLIST = (
    "SMART_V2_STRICT_CLEAN_MO1,"
    "SMART_V2_STRICT_OI_MO1,"
    "META_V12_EXEC_SAFE_MO1,"
    "MAIN_V92_TP08_EXEC_7,"
    "YELLOW_SCORE3,"
    "YELLOW_SCORE3_FAST,"
    ""
)

REJECT_OBSERVER_COMPACT_REASONS = True



# ============================================================
# COST NEAR MISS FAST SHADOW
# ============================================================
# Cost gate stays strict globally.
# This lane studies cases that barely fail cost gate but have clean structure.
# Shadow only. Real remains OFF.
COST_NEAR_MISS_FAST_ENABLED = True
COST_NEAR_MISS_MIN_EXPECTED_TO_REQUIRED = 0.80
COST_NEAR_MISS_MIN_SCORE = 4
COST_NEAR_MISS_MIN_VOL = 8.0
COST_NEAR_MISS_MIN_PC = 0.40
COST_NEAR_MISS_MAX_PC = 0.55
COST_NEAR_MISS_MIN_TREND = 1.0
COST_NEAR_MISS_MIN_BTC = -0.08
COST_NEAR_MISS_MIN_OI = -2.0
COST_NEAR_MISS_MAX_RANK = 50
COST_NEAR_MISS_MAX_STRUCT = 2
COST_NEAR_MISS_MAX_BRISK = 2
COST_NEAR_MISS_MAX_FB = 1



# ============================================================
# RISK ADJUSTED COST GATE V1
# ============================================================
# Cost gate should not only ask "is price_change big enough?"
# It must ask "is CLEAN expected move big enough after risks?"
EXEC_RISK_ADJUSTED_EXPECTED_MOVE_ENABLED = True

# Multipliers applied to expected move for long continuation.
# Example: pc=0.66% can pass raw cost gate, but if OI is negative
# and there is no initiative, expected capturable move should be reduced.
EXEC_RISK_PENALTY_OI_NEG = 0.78
EXEC_RISK_PENALTY_BTC_WEAK = 0.85
EXEC_RISK_PENALTY_BRISK_HIGH = 0.78
EXEC_RISK_PENALTY_FB_HIGH = 0.78
EXEC_RISK_PENALTY_NO_INITIATIVE = 0.82
EXEC_RISK_PENALTY_HIGH_EFFORT = 0.70
EXEC_RISK_PENALTY_WEAK_RESULT = 0.70
EXEC_RISK_PENALTY_STRUCT_HIGH = 0.85
EXEC_RISK_MIN_QUALITY_FACTOR = 0.35

EXEC_RISK_OI_NEG_LEVEL = 0.0
EXEC_RISK_BTC_WEAK_LEVEL = -0.05
EXEC_RISK_BRISK_HIGH_LEVEL = 4
EXEC_RISK_FB_HIGH_LEVEL = 2
EXEC_RISK_STRUCT_HIGH_LEVEL = 4



# ============================================================
# COST RESCUE CLEAN IMPULSE SHADOW
# ============================================================
# Global cost gate stays strict.
# This lane studies rare RE-like false negatives:
# strong raw impulse, strong trend, clean risk, but risk-adjusted cost gate failed.
COST_RESCUE_CLEAN_IMPULSE_ENABLED = True
COST_RESCUE_MIN_EXPECTED_TO_REQUIRED = 0.75
COST_RESCUE_MIN_SCORE = 3
COST_RESCUE_MIN_VOL = 8.0
COST_RESCUE_MIN_PC = 0.70
COST_RESCUE_MAX_PC = 1.05
COST_RESCUE_MIN_TREND = 2.0
COST_RESCUE_MIN_BTC = 0.00
COST_RESCUE_MIN_OI = 0.50
COST_RESCUE_MAX_RANK = 35
COST_RESCUE_MAX_STRUCT = 2
COST_RESCUE_MAX_BRISK = 2
COST_RESCUE_MAX_FB = 1

# ============================================================
# DEPTH THIN ESCAPE SHADOW V2
# ============================================================
# Do not disable DEPTH_THIN globally.
# Only study narrow BLESS/SYN-like escape cases.
DEPTH_THIN_ESCAPE_V2_ENABLED = True
DEPTH_THIN_ESCAPE_V2_MIN_SCORE = 5
DEPTH_THIN_ESCAPE_V2_MIN_VOL = 12.0
DEPTH_THIN_ESCAPE_V2_MIN_PC = 0.60
DEPTH_THIN_ESCAPE_V2_MIN_TREND = 0.40
DEPTH_THIN_ESCAPE_V2_MIN_BTC = -0.10
DEPTH_THIN_ESCAPE_V2_MIN_OI = 0.00
DEPTH_THIN_ESCAPE_V2_MAX_SPREAD_BPS = 5.0
DEPTH_THIN_ESCAPE_V2_MIN_BID5_USD = 300.0
DEPTH_THIN_ESCAPE_V2_MIN_ASK5_USD = 150.0
DEPTH_THIN_ESCAPE_V2_MAX_BRISK = 3
DEPTH_THIN_ESCAPE_V2_MAX_FB = 1
DEPTH_THIN_ESCAPE_V2_MAX_STRUCT = 2
DEPTH_THIN_ESCAPE_V2_MAX_RANK = 50


# ============================================================
# MAKER SHORT TP3 SL03 SHADOW — V18 maker-offset edge test
# ============================================================
# Research-only. Never sends real orders.
# Best V18 lab profile:
#   SHORT after positive impulse >=1%, vol>=8, spread<=8bps, rank<=80,
#   maker limit above signal by 0.15%, TP=3.0%, SL=0.3%.
MAKER_SHORT_V1_ENABLED = os.getenv("MAKER_SHORT_V1_ENABLED", "true").lower() == "true"
MAKER_SHORT_V1_MIN_PC = float(os.getenv("MAKER_SHORT_V1_MIN_PC", "1.0"))
MAKER_SHORT_V1_SCAN_MAX_PC = float(os.getenv("MAKER_SHORT_V1_SCAN_MAX_PC", "3.0"))
MAKER_SHORT_V1_MIN_VOL = float(os.getenv("MAKER_SHORT_V1_MIN_VOL", "8.0"))
MAKER_SHORT_V1_MAX_SPREAD_BPS = float(os.getenv("MAKER_SHORT_V1_MAX_SPREAD_BPS", "8.0"))
MAKER_SHORT_V1_MAX_RANK = int(os.getenv("MAKER_SHORT_V1_MAX_RANK", "80"))

MAKER_SHORT_V1_OFFSET_PCT = float(os.getenv("MAKER_SHORT_V1_OFFSET_PCT", "0.15"))
MAKER_SHORT_V1_TP_PCT = float(os.getenv("MAKER_SHORT_V1_TP_PCT", "3.0"))
MAKER_SHORT_V1_SL_PCT = float(os.getenv("MAKER_SHORT_V1_SL_PCT", "0.3"))
MAKER_SHORT_V1_COST_PCT = float(os.getenv("MAKER_SHORT_V1_COST_PCT", "0.03"))

MAKER_SHORT_V1_WAIT_SECONDS = float(os.getenv("MAKER_SHORT_V1_WAIT_SECONDS", "300"))
MAKER_SHORT_V1_TTL_SECONDS = float(os.getenv("MAKER_SHORT_V1_TTL_SECONDS", "300"))
MAKER_SHORT_V1_MARGIN = float(os.getenv("MAKER_SHORT_V1_MARGIN", "3.0"))
MAKER_SHORT_V1_LEVERAGE = int(os.getenv("MAKER_SHORT_V1_LEVERAGE", "4"))
MAKER_SHORT_V1_MAX_PENDING = int(os.getenv("MAKER_SHORT_V1_MAX_PENDING", "4"))
MAKER_SHORT_V1_MAX_ACTIVE = int(os.getenv("MAKER_SHORT_V1_MAX_ACTIVE", "3"))
MAKER_SHORT_V1_COOLDOWN_SECONDS = float(os.getenv("MAKER_SHORT_V1_COOLDOWN_SECONDS", "900"))
MAKER_SHORT_V1_POLL_SECONDS = float(os.getenv("MAKER_SHORT_V1_POLL_SECONDS", "5"))
