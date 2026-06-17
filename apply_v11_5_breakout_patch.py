#!/usr/bin/env python3
import re
import shutil
import py_compile
from pathlib import Path
from datetime import datetime

ROOT = Path("/root/skynet")
FILES = {
    "config": ROOT / "skynet_config.py",
    "engine": ROOT / "skynet_engine.py",
    "main": ROOT / "skynet_main.py",
}

STAMP = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / f"backup_v11_5_{STAMP}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def backup_files():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for path in FILES.values():
        shutil.copy2(path, BACKUP_DIR / path.name)
    print(f"✅ Backup saved: {BACKUP_DIR}")


def restore_files():
    if not BACKUP_DIR.exists():
        return
    for path in FILES.values():
        src = BACKUP_DIR / path.name
        if src.exists():
            shutil.copy2(src, path)
    print("↩️ Restored files from backup.")


def must_contain(text, needle, file_name):
    if needle not in text:
        raise RuntimeError(f"Cannot find expected block in {file_name}: {needle[:120]!r}")


def replace_regex(text, pattern, repl, file_name, flags=re.S, count=1):
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n != count:
        raise RuntimeError(f"Regex replace failed in {file_name}. Pattern: {pattern[:160]!r}, replacements={n}")
    return new


def insert_before(text, needle, insertion, file_name, marker):
    if marker in text:
        return text
    must_contain(text, needle, file_name)
    return text.replace(needle, insertion + "\n\n" + needle, 1)


def insert_after(text, needle, insertion, file_name, marker):
    if marker in text:
        return text
    must_contain(text, needle, file_name)
    return text.replace(needle, needle + "\n" + insertion, 1)


def patch_config(text: str) -> str:
    text = re.sub(
        r'BOT_VERSION\s*=\s*"[^"]+"',
        'BOT_VERSION = "SKYNET_PRO_V11_5_BREAKOUT_RISK_ATR_DRY"',
        text,
        count=1,
    )

    default_tracks = '''DEFAULT_LIVE_DRY_TRACKS = (
    # CONTROL: current v11.3/v11.4 confirm branch.
    "INITIATIVE_CONFIRM_RUG015_PC055_VOL25_DYN08_5,"
    # V11.5 main archive winners: wider PC/VOL + breakout-risk + ATR5_B.
    "BREAKOUT_TREND040_PC065_VOL35_NO_FALSE_ATR5B_WAIT1_MO1,"
    "BREAKOUT_TREND040_PC065_VOL35_COMBO_BALANCED_ATR5B_WAIT1_MO1"
)'''
    text = replace_regex(
        text,
        r'DEFAULT_LIVE_DRY_TRACKS\s*=\s*\([\s\S]*?\)\nLIVE_DRY_TRACKS',
        default_tracks + "\nLIVE_DRY_TRACKS",
        "skynet_config.py",
        flags=0,
        count=1,
    )

    v115_settings = '''
# ============================================================
# V11.5 BREAKOUT-RISK + ATR5_B
# ============================================================
BREAKOUT_MIN_SCORE = int(os.getenv("BREAKOUT_MIN_SCORE", "5"))
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
'''
    text = insert_after(
        text,
        'ATR5B_DEFAULT_PRE_RANGE_5M = float(os.getenv("ATR5B_DEFAULT_PRE_RANGE_5M", "0.75"))',
        v115_settings,
        "skynet_config.py",
        "V11.5 BREAKOUT-RISK + ATR5_B",
    )

    dataclass_add = '''    # V11.5 breakout-risk gates.
    breakout_risk_mode: str = "NONE"  # NONE / NO_FALSE_BREAKOUT / COMBO_BALANCED
'''
    text = insert_after(
        text,
        "    min_trend_15m_override: float = -999.0",
        dataclass_add,
        "skynet_config.py",
        "breakout_risk_mode",
    )

    helper = '''
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
'''
    text = insert_before(
        text,
        "def build_strategy_configs():",
        helper,
        "skynet_config.py",
        "V11.5 PATCH START: breakout confirm strategy",
    )

    configs_block = '''
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

'''
    text = insert_after(
        text,
        "    configs = []\n",
        configs_block,
        "skynet_config.py",
        "V11.5 BREAKOUT-RISK + ATR5_B DRY CANDIDATES",
    )

    return text


def patch_engine(text: str) -> str:
    risk_func = '''
# === V11.5 PATCH START: breakout-risk filters ===
def passes_breakout_risk_mode(c: dict, mode: str) -> bool:
    mode = (mode or "NONE").upper()
    if mode in ("NONE", "NO_FILTER"):
        return True

    risk = safe_float(c.get("breakout_risk_score"), 999.0)
    red_share = safe_float(c.get("red_volume_share_10m"), 1.0)
    reject = safe_float(c.get("rejection_count_10m"), 99.0)
    false_bo = safe_float(c.get("false_breakouts_15m"), 99.0)
    flush = int(safe_float(c.get("recent_flush_15m"), 1.0))
    wick_pressure = safe_float(c.get("upper_wick_pressure_10m"), 999.0)
    ema_slope = safe_float(c.get("ema9_slope_3m_pct"), -999.0)
    close_vs_ema = safe_float(c.get("close_vs_ema9_pct"), -999.0)

    if mode == "NO_FALSE_BREAKOUT":
        return false_bo <= cfg.BREAKOUT_FALSE_BREAKOUT_MAX

    if mode == "COMBO_BALANCED":
        return (
            risk <= cfg.BREAKOUT_COMBO_RISK_MAX
            and red_share < cfg.BREAKOUT_COMBO_RED_SHARE_MAX
            and reject <= cfg.BREAKOUT_COMBO_REJECTION_MAX
            and false_bo <= cfg.BREAKOUT_FALSE_BREAKOUT_MAX
            and flush == 0
            and wick_pressure < cfg.BREAKOUT_COMBO_WICK_PRESSURE_MAX
            and ema_slope >= cfg.BREAKOUT_COMBO_EMA9_SLOPE_MIN
            and close_vs_ema >= cfg.BREAKOUT_COMBO_CLOSE_VS_EMA9_MIN
        )

    return True
# === V11.5 PATCH END: breakout-risk filters ===
'''
    text = insert_before(
        text,
        "# ============================================================\n# STRATEGY RULES",
        risk_func,
        "skynet_engine.py",
        "V11.5 PATCH START: breakout-risk filters",
    )

    breakout_rule = '''
    if f == "breakout_confirm_atr":
        if c.get("score", -999) < cfg.BREAKOUT_MIN_SCORE:
            return False
        if not c.get("initiative_buying_proxy"):
            return False
        if not (0.25 <= c.get("price_change", 999.0) <= getattr(scfg, "confirm_max_price_change", cfg.BREAKOUT_MAX_PRICE_CHANGE)):
            return False
        if c.get("vol_ratio", 999.0) > getattr(scfg, "confirm_max_vol_ratio", cfg.BREAKOUT_MAX_VOL_RATIO):
            return False
        if c.get("trend_15m", -999.0) < getattr(scfg, "min_trend_15m_override", cfg.BREAKOUT_MIN_TREND_15M):
            return False
        if c.get("btc_5m_change", 0.0) < cfg.BREAKOUT_MIN_BTC_5M:
            return False
        if c.get("structure_risk", 0) > cfg.BREAKOUT_MAX_STRUCTURE_RISK:
            return False
        if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
            return False
        if not passes_breakout_risk_mode(c, getattr(scfg, "breakout_risk_mode", "NONE")):
            return False
        return True

'''
    text = insert_before(
        text,
        '    if f == "initiative_confirm_trend_atr":',
        breakout_rule,
        "skynet_engine.py",
        'if f == "breakout_confirm_atr":',
    )

    text = text.replace(
        'if fam in ("initiative_runner", "main_context_strict_runner", "initiative_confirm_trend_atr", "initiative_confirm_runner"):',
        'if fam in ("initiative_runner", "main_context_strict_runner", "initiative_confirm_trend_atr", "initiative_confirm_runner", "breakout_confirm_atr"):',
        1,
    )

    context_old = '''            "confirm_move_pct": candidate.get("confirm_move_pct", 0.0),'''
    context_new = '''            "confirm_move_pct": candidate.get("confirm_move_pct", 0.0),
            "breakout_risk_score": candidate.get("breakout_risk_score", 0),
            "false_breakouts_15m": candidate.get("false_breakouts_15m", 0),
            "red_volume_share_10m": candidate.get("red_volume_share_10m", 0.0),
            "ema9_slope_3m_pct": candidate.get("ema9_slope_3m_pct", 0.0),'''
    if '"breakout_risk_score": candidate.get("breakout_risk_score"' not in text:
        text = text.replace(context_old, context_new, 1)

    return text


NEW_KLINE_FUNC = '''async def get_kline_1m_metrics(session, symbol):
    try:
        # limit=30 gives latest candle shape, ATR5_B pre-range and breakout-risk context.
        url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval=Min1&limit=30"
        async with session.get(url, timeout=5) as res:
            if res.status != 200:
                return None
            data = await res.json()
            d = data.get("data")
            if not d or not d.get("open") or not d.get("close"):
                return None

            opens = d.get("open") or []
            closes = d.get("close") or []
            highs = d.get("high") or []
            lows = d.get("low") or []
            vols = d.get("vol") or d.get("volume") or d.get("amount") or []

            n = min(len(opens), len(closes), len(highs), len(lows))
            if n <= 0:
                return None

            def sf(x, default=0.0):
                return eng.safe_float(x, default)

            opens = [sf(x) for x in opens[-n:]]
            closes = [sf(x) for x in closes[-n:]]
            highs = [sf(x) for x in highs[-n:]]
            lows = [sf(x) for x in lows[-n:]]
            if vols:
                vols = [sf(x) for x in vols[-n:]]
                if len(vols) < n:
                    vols = [0.0] * (n - len(vols)) + vols
            else:
                vols = [0.0] * n

            open_p = opens[-1]
            close_p = closes[-1]
            high_p = highs[-1]
            low_p = lows[-1]

            pre_range_5m_pct = 0.0
            if n >= 2 and close_p > 0:
                pre_highs = highs[max(0, n - 6): n - 1] or [high_p]
                pre_lows = lows[max(0, n - 6): n - 1] or [low_p]
                pre_hi = max([x for x in pre_highs if x > 0] or [high_p])
                pre_lo = min([x for x in pre_lows if x > 0] or [low_p])
                if pre_hi > 0 and pre_lo > 0 and pre_hi >= pre_lo:
                    pre_range_5m_pct = ((pre_hi - pre_lo) / close_p) * 100.0

            if min(open_p, close_p, high_p, low_p) <= 0:
                return None

            def candle_features(i):
                o = opens[i]
                c = closes[i]
                h = highs[i]
                l = lows[i]
                v = vols[i] if i < len(vols) else 0.0
                full = h - l
                if min(o, c, h, l) <= 0 or full <= 0:
                    return {
                        "is_red": 0, "close_position": 0.5, "body_ratio": 0.0,
                        "upper_wick_ratio": 0.0, "lower_wick_ratio": 0.0,
                        "range_pct": 0.0, "vol": v,
                    }
                upper = h - max(o, c)
                lower = min(o, c) - l
                body = abs(c - o)
                return {
                    "is_red": 1 if c < o else 0,
                    "close_position": (c - l) / full,
                    "body_ratio": body / full,
                    "upper_wick_ratio": max(0.0, upper / full),
                    "lower_wick_ratio": max(0.0, lower / full),
                    "range_pct": (full / c) * 100.0,
                    "vol": v,
                }

            latest = candle_features(n - 1)
            is_red = bool(latest["is_red"])
            close_position = latest["close_position"]
            body_ratio = latest["body_ratio"]
            upper_wick_ratio = latest["upper_wick_ratio"]
            lower_wick_ratio = latest["lower_wick_ratio"]
            has_tail = upper_wick_ratio > 0.4

            start10 = max(0, n - 10)
            start15 = max(0, n - 15)
            start30 = max(0, n - 30)
            stats10 = [candle_features(i) for i in range(start10, n)]

            total_vol10 = sum(s["vol"] for s in stats10)
            red_vol10 = sum(s["vol"] for s in stats10 if s["is_red"])
            red_volume_share_10m = red_vol10 / total_vol10 if total_vol10 > 0 else 0.0

            rejection_count_10m = sum(
                1 for s in stats10
                if s["upper_wick_ratio"] >= 0.45 and s["close_position"] <= 0.65
            )
            weak_close_count_10m = sum(1 for s in stats10 if s["close_position"] <= 0.45)
            upper_wick_pressure_10m = sum(s["upper_wick_ratio"] for s in stats10) / max(1, len(stats10))

            false_breakouts_15m = 0
            for i in range(max(5, start15), n):
                prev_high = max(highs[max(0, i - 5):i] or [highs[i]])
                s = candle_features(i)
                if highs[i] > prev_high and s["close_position"] < 0.60:
                    false_breakouts_15m += 1

            recent_flush_15m = 0
            for i in range(start15, n):
                if opens[i] > 0 and ((lows[i] - opens[i]) / opens[i]) * 100.0 <= -0.60:
                    recent_flush_15m = 1
                    break

            closes30 = closes[start30:n]
            ema9_vals = []
            if closes30:
                k = 2.0 / 10.0
                ema9_vals = [closes30[0]]
                for x in closes30[1:]:
                    ema9_vals.append(x * k + ema9_vals[-1] * (1.0 - k))

            if len(ema9_vals) >= 4 and ema9_vals[-1] > 0 and ema9_vals[-4] > 0:
                close_vs_ema9_pct = ((closes30[-1] - ema9_vals[-1]) / ema9_vals[-1]) * 100.0
                ema9_slope_3m_pct = ((ema9_vals[-1] - ema9_vals[-4]) / ema9_vals[-4]) * 100.0
            else:
                close_vs_ema9_pct = 0.0
                ema9_slope_3m_pct = 0.0

            breakout_risk_score = 0
            if red_volume_share_10m >= 0.60:
                breakout_risk_score += 2
            if rejection_count_10m >= 2:
                breakout_risk_score += 2
            if false_breakouts_15m >= 2:
                breakout_risk_score += 2
            if recent_flush_15m:
                breakout_risk_score += 1
            if upper_wick_pressure_10m >= 0.30:
                breakout_risk_score += 1
            if weak_close_count_10m >= 4:
                breakout_risk_score += 1
            if ema9_slope_3m_pct < 0:
                breakout_risk_score += 1
            if close_vs_ema9_pct < -0.05:
                breakout_risk_score += 1

            return {
                "open": open_p,
                "close": close_p,
                "high": high_p,
                "low": low_p,
                "is_red": is_red,
                "has_tail": has_tail,
                "close_position": close_position,
                "body_ratio": body_ratio,
                "upper_wick_ratio": upper_wick_ratio,
                "lower_wick_ratio": lower_wick_ratio,
                "pre_range_5m_pct": pre_range_5m_pct,

                "red_volume_share_10m": red_volume_share_10m,
                "rejection_count_10m": rejection_count_10m,
                "weak_close_count_10m": weak_close_count_10m,
                "upper_wick_pressure_10m": upper_wick_pressure_10m,
                "false_breakouts_15m": false_breakouts_15m,
                "recent_flush_15m": recent_flush_15m,
                "close_vs_ema9_pct": close_vs_ema9_pct,
                "ema9_slope_3m_pct": ema9_slope_3m_pct,
                "breakout_risk_score": breakout_risk_score,
            }
    except Exception:
        return None

'''


def patch_main(text: str) -> str:
    text = replace_regex(
        text,
        r'async def get_kline_1m_metrics\(session, symbol\):[\s\S]*?\n\nasync def get_15m_metrics',
        NEW_KLINE_FUNC + "\nasync def get_15m_metrics",
        "skynet_main.py",
        flags=re.S,
        count=1,
    )

    text = text.replace(
        "=== START {cfg.BOT_VERSION} | TREND ATR5B UNIVERSE ===",
        "=== START {cfg.BOT_VERSION} | BREAKOUT RISK ATR5B ===",
    )
    text = text.replace(
        'caption=f"📁 v11.4 TrendATR лог за {log_interval} ({date_postfix})"',
        'caption=f"📁 v11.5 BreakoutRisk лог за {log_interval} ({date_postfix})"',
    )
    text = text.replace(
        'f"🤖 **V11.3 CONFIRM RUNNER ЖИВ** 🤖\\n"',
        'f"🤖 **V11.5 BREAKOUT RISK ATR ЖИВ** 🤖\\n"',
    )

    old_log = '''                            f"Score:{candidate['score']} | Struct:{candidate.get('structure_risk',0)} | "
                            f"CP:{candidate.get('close_position',0.5):.2f} | Body:{candidate.get('body_ratio',0):.2f} | "'''
    new_log = '''                            f"Score:{candidate['score']} | Struct:{candidate.get('structure_risk',0)} | "
                            f"BRisk:{candidate.get('breakout_risk_score',0)} FB:{candidate.get('false_breakouts_15m',0)} | "
                            f"CP:{candidate.get('close_position',0.5):.2f} | Body:{candidate.get('body_ratio',0):.2f} | "'''
    if old_log in text and "BRisk:" not in text:
        text = text.replace(old_log, new_log, 1)

    old_alert = '''                                f"🧩 StructureRisk: **{candidate.get('structure_risk',0)}** | "
                                f"ClosePos: {candidate.get('close_position',0.5):.2f} | Body: {candidate.get('body_ratio',0):.2f}\\n\\n"'''
    new_alert = '''                                f"🧩 StructureRisk: **{candidate.get('structure_risk',0)}** | "
                                f"ClosePos: {candidate.get('close_position',0.5):.2f} | Body: {candidate.get('body_ratio',0):.2f}\\n"
                                f"🧪 BRisk: **{candidate.get('breakout_risk_score',0)}** | "
                                f"FalseBO: {candidate.get('false_breakouts_15m',0)} | "
                                f"EMA9Slope: {candidate.get('ema9_slope_3m_pct',0):+.3f}% | "
                                f"RedVol10m: {candidate.get('red_volume_share_10m',0):.2f}\\n\\n"'''
    if old_alert in text and "FalseBO:" not in text:
        text = text.replace(old_alert, new_alert, 1)

    old_pending = '''            f"vol=x{int(cand.get('vol_ratio',0))} trend={cand['trend_15m']:.2f}% btc={cand['btc_5m_change']:.2f}% "
            f"spread={cand.get('spread_bps',999):.2f}bps/{scfg.spread_limit_bps:.0f}\\n"'''
    new_pending = '''            f"vol=x{int(cand.get('vol_ratio',0))} trend={cand['trend_15m']:.2f}% btc={cand['btc_5m_change']:.2f}% "
            f"spread={cand.get('spread_bps',999):.2f}bps/{scfg.spread_limit_bps:.0f} "
            f"br={cand.get('breakout_risk_score',0)} fb={cand.get('false_breakouts_15m',0)}\\n"'''
    if old_pending in text and "br={cand.get('breakout_risk_score'" not in text:
        text = text.replace(old_pending, new_pending, 1)

    return text


def main():
    if not ROOT.exists():
        raise SystemExit("/root/skynet not found")

    for path in FILES.values():
        if not path.exists():
            raise SystemExit(f"Missing {path}")

    backup_files()

    try:
        cfg_text = patch_config(read(FILES["config"]))
        eng_text = patch_engine(read(FILES["engine"]))
        main_text = patch_main(read(FILES["main"]))

        write(FILES["config"], cfg_text)
        write(FILES["engine"], eng_text)
        write(FILES["main"], main_text)

        for path in FILES.values():
            py_compile.compile(str(path), doraise=True)

        print("✅ V11.5 patch applied and py_compile OK.")
        print("Next:")
        print("  systemctl restart skynet")
        print("  systemctl status skynet --no-pager")
        print("  journalctl -u skynet -n 80 --no-pager -l")

    except Exception as e:
        print(f"❌ Patch failed: {type(e).__name__}: {e}")
        restore_files()
        print("Files restored. Nothing changed.")
        raise


if __name__ == "__main__":
    main()
