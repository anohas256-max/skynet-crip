#!/usr/bin/env python3
import os
import re
import shutil
import time
from pathlib import Path

ROOT = Path("/root/skynet")
CFG = ROOT / "skynet_config.py"
ENG = ROOT / "skynet_engine.py"
MAIN = ROOT / "skynet_main.py"


def backup_files():
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup = ROOT / f"backup_v15_spread_scout_{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    for p in [CFG, ENG, MAIN]:
        if p.exists():
            shutil.copy2(p, backup / p.name)
    return backup


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Marker not found: {label}")
    return text.replace(old, new, 1)


def patch_config(text: str) -> str:
    text = re.sub(
        r'BOT_VERSION\s*=\s*"[^"]+"',
        'BOT_VERSION = "SKYNET_PRO_V15_SPREAD_SCOUT_DRY"',
        text,
        count=1,
    )

    if '"V15_SPREAD_SCOUT_MO1,"' not in text:
        text = text.replace(
            '"SMART_V2_STRICT_BTC_MO1,"\n    # Keep one V12 control for comparison.\n    "META_V12_EXEC_SAFE_MO1"',
            '"SMART_V2_STRICT_BTC_MO1,"\n    "V15_SPREAD_SCOUT_MO1,"\n    # Keep one V12 control for comparison.\n    "META_V12_EXEC_SAFE_MO1"',
        )

    if "# V15 SPREAD SCOUT / SKIP LEARNING" not in text:
        marker = 'SMART_V2_GOOD_MFE = float(os.getenv("SMART_V2_GOOD_MFE", "0.80"))'
        insert = marker + """

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
V15_SKIP_LEARN_TIME_AS_NEUTRAL = os.getenv("V15_SKIP_LEARN_TIME_AS_NEUTRAL", "true").lower() == "true" """
        text = replace_once(text, marker, insert, "SMART_V2_GOOD_MFE")

    if "min_spread_bps: float = 0.0" not in text:
        marker = '    smart_mid_top: int = 0\n'
        text = replace_once(text, marker, marker + '    # V15 scout gates.\n    min_spread_bps: float = 0.0\n', "StrategyConfig smart_mid_top")

    if "def _v15_spread_scout_strategy(" not in text:
        marker = "# === V13 PATCH END: smart-universe V2 strategy ==="
        func = """

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
"""
        text = replace_once(text, marker, marker + func, "V13 patch end")

    build_part = text.split("def build_strategy_configs():", 1)[1] if "def build_strategy_configs():" in text else ""
    if '"V15_SPREAD_SCOUT_MO1"' not in build_part:
        marker = """    # V12 META EXEC-SAFE DRY CANDIDATES."""
        insert = """    # V15 SPREAD SCOUT DRY-ONLY.
    # Берёт только depth-ok, spread 5-12bps, очень чистые сигналы.
    configs += [
        _v15_spread_scout_strategy("V15_SPREAD_SCOUT_MO1", silent=False),
    ]


"""
        text = replace_once(text, marker, insert + marker, "V12 candidates marker")

    return text


def patch_engine(text: str) -> str:
    if '"V15_SKIP_LEARN": 0' not in text:
        marker = '    "BAD_STREAK": 0,\n'
        text = replace_once(
            text,
            marker,
            marker + '    "V15_SKIP_LEARN": 0,\n    "V15_SKIP_LEARN_DEPTH_THIN": 0,\n    "V15_SKIP_LEARN_SPREAD_WIDE": 0,\n',
            "_SMART_V2_STATS BAD_STREAK",
        )

    if "self.last_learn = {}" not in text:
        marker = "        self.last_open = {}\n"
        text = replace_once(text, marker, marker + "        self.last_learn = {}\n", "SkipTracker last_open")

    if "def _learn_skip_outcome" not in text:
        marker = "    def update_symbol(self, symbol, clean_symbol, price, current_time, time_str):\n"
        method = """    def _learn_skip_outcome(self, w, net, reason, current_time, time_str):
        if not getattr(cfg, "V15_SKIP_LEARNING_ENABLED", False):
            return

        original_skip = str(w.get("reason", ""))
        skip_kind = None

        if original_skip == "DEPTH_THIN":
            if not getattr(cfg, "V15_SKIP_LEARN_DEPTH_THIN", True):
                return
            skip_kind = "DEPTH_THIN"
        elif original_skip.startswith("SPREAD_WIDE"):
            if not getattr(cfg, "V15_SKIP_LEARN_SPREAD_WIDE", True):
                return
            skip_kind = "SPREAD_WIDE"
        else:
            return

        # Убираем дубли: skip tracker открывается многими стратегиями на один и тот же сигнал.
        # Для паспорта нужен один outcome на symbol/skip_kind/15m bucket.
        symbol = w.get("symbol", "")
        clean_symbol = w.get("clean_symbol", symbol)
        bucket = int(current_time // max(60, getattr(cfg, "V15_SKIP_LEARN_COOLDOWN", 900)))
        key = (symbol, skip_kind, bucket)
        if self.last_learn.get(key):
            return
        self.last_learn[key] = True

        learn_reason = reason
        if reason == "WOULD_TP":
            learn_reason = "RUNNER_TP"
        elif reason == "WOULD_SL":
            learn_reason = "SL"
        elif reason == "WOULD_TIME":
            learn_reason = "TIME"

        if getattr(cfg, "V15_SKIP_LEARN_TIME_AS_NEUTRAL", True) and learn_reason == "TIME":
            # TIME часто около нуля, не хотим забивать паспорт шумом.
            if abs(float(net)) < 0.05:
                return

        try:
            q = _smart_v2_quality(symbol)
            q.update(float(net), float(w.get("max_profit_pct", 0.0)), learn_reason, current_time)
            _smart_v2_save_passports()

            _SMART_V2_STATS["V15_SKIP_LEARN"] = _SMART_V2_STATS.get("V15_SKIP_LEARN", 0) + 1
            if skip_kind == "DEPTH_THIN":
                _SMART_V2_STATS["V15_SKIP_LEARN_DEPTH_THIN"] = _SMART_V2_STATS.get("V15_SKIP_LEARN_DEPTH_THIN", 0) + 1
            if skip_kind == "SPREAD_WIDE":
                _SMART_V2_STATS["V15_SKIP_LEARN_SPREAD_WIDE"] = _SMART_V2_STATS.get("V15_SKIP_LEARN_SPREAD_WIDE", 0) + 1

            f = q.features()
            log(
                f"[{time_str}] V15_SKIP_LEARN | {clean_symbol} | {skip_kind} -> {learn_reason} | "
                f"net={net:+.2f}$ MFE=+{w.get('max_profit_pct',0.0):.2f}% "
                f"Qobs={f['obs']} Qavg={f['avg_net']:+.2f}$ Qsl={f['sl_rate']:.2f} "
                f"bad={f['bad_streak']} tox={f.get('toxic_reason','')}\\n"
            )
        except Exception as e:
            log(f"[{time_str}] V15_SKIP_LEARN_ERROR | {clean_symbol} | {type(e).__name__}: {e}\\n")

"""
        text = replace_once(text, marker, method + marker, "SkipTracker update_symbol")

    if "self._learn_skip_outcome(w, net, reason, current_time, time_str)" not in text:
        old = """                log(
                    f"[{time_str}] SKIP_TRACK_CLOSE | {w['strategy']} | {clean_symbol} | {reason} | "
                    f"original_skip={w['reason']} | HypoNet:{net:+.2f}$ | "
                    f"MFE:+{w['max_profit_pct']:.2f}% MAE:{w['max_loss_pct']:.2f}%\\n"
                )
"""
        new = old + "                self._learn_skip_outcome(w, net, reason, current_time, time_str)\n"
        text = replace_once(text, old, new, "SKIP_TRACK_CLOSE log")

    if "V15_SCOUT_SPREAD_TOO_TIGHT" not in text:
        old = """    if safe_float(cand.get("spread_bps"), 999.0) > scfg.spread_limit_bps:
        return False, f"SPREAD_WIDE_{safe_float(cand.get('spread_bps'), 999.0):.2f}bps_GT_{scfg.spread_limit_bps:.0f}"
    return True, "DEPTH_OK"
"""
        new = """    spread_bps = safe_float(cand.get("spread_bps"), 999.0)
    if spread_bps > scfg.spread_limit_bps:
        return False, f"SPREAD_WIDE_{spread_bps:.2f}bps_GT_{scfg.spread_limit_bps:.0f}"

    min_spread = safe_float(getattr(scfg, "min_spread_bps", 0.0), 0.0)
    if min_spread > 0 and spread_bps < min_spread:
        return False, f"V15_SCOUT_SPREAD_TOO_TIGHT_{spread_bps:.2f}bps_LT_{min_spread:.0f}"

    return True, "DEPTH_OK"
"""
        text = replace_once(text, old, new, "validate_depth spread block")

    if 'if f == "v15_spread_scout":' not in text:
        marker = '    if f == "smart_v2_strict":\n'
        branch = """    if f == "v15_spread_scout":
        # Dry-only scout: проверяем прибыльную часть SPREAD_WIDE, но не лезем в DEPTH_THIN.
        # Spread-границы проверятся позже после depth enrich через validate_depth_for_strategy().
        q = _smart_v2_quality(c.get("symbol", "")).features()
        now = safe_float(c.get("_current_time"), time.time())

        if q.get("cooldown_until") and now < q.get("cooldown_until"):
            return False
        if q.get("bad_streak", 0) >= cfg.SMART_V2_MAX_BAD_STREAK and q.get("obs", 0) >= 2:
            if not _smart_v2_ultra_candidate(c):
                return False

        return (
            c.get("score", -999) >= cfg.V15_SCOUT_MIN_SCORE
            and cfg.PRICE_CHANGE_MIN <= c.get("price_change", 999.0) <= cfg.V15_SCOUT_MAX_PRICE_CHANGE
            and c.get("vol_ratio", 999.0) <= cfg.V15_SCOUT_MAX_VOL_RATIO
            and c.get("trend_15m", -999.0) >= cfg.V15_SCOUT_MIN_TREND_15M
            and c.get("btc_5m_change", -999.0) >= cfg.V15_SCOUT_MIN_BTC_5M
            and c.get("oi_change", -999.0) >= cfg.V15_SCOUT_MIN_OI
            and c.get("breakout_risk_score", 999) <= cfg.V15_SCOUT_MAX_BRISK
            and c.get("false_breakouts_15m", 999) <= cfg.V15_SCOUT_MAX_FALSE_BREAKOUTS
            and c.get("structure_risk", 999) <= cfg.V15_SCOUT_MAX_STRUCTURE_RISK
            and c.get("initiative_buying_proxy", False)
            and not c.get("absorption_risk_long")
            and not c.get("high_effort_low_result")
            and not c.get("weak_long_result")
        )

"""
        text = replace_once(text, marker, branch + marker, "should_enter smart_v2 marker")

    if 'if fam == "v15_spread_scout":' not in text:
        marker = '    if fam in ("meta_v12_exec_safe", "meta_v12_oi_safe"):\n'
        branch = """    if fam == "v15_spread_scout":
        score = safe_float(c.get("score"), 0)
        pc = safe_float(c.get("price_change"), 0)
        trend = safe_float(c.get("trend_15m"), 0)
        btc5 = safe_float(c.get("btc_5m_change"), 0)
        oi = safe_float(c.get("oi_change"), 0)
        spread = safe_float(c.get("spread_bps"), 8.0)
        brisk = safe_float(c.get("breakout_risk_score"), 5)
        fb = safe_float(c.get("false_breakouts_15m"), 2)
        struct = safe_float(c.get("structure_risk"), 3)
        depth = min((safe_float(c.get("top5_bid_usdt"), 0) + safe_float(c.get("top5_ask_usdt"), 0)) / 10000.0, 8.0)
        rank = safe_float(c.get("current_turnover_rank"), 999)

        # Scout предпочитает spread около 6-8bps, не погоню за 12bps.
        return (
            score * 100.0
            + min(trend, 2.5) * 12.0
            + btc5 * 10.0
            + max(min(oi, 8.0), -2.0) * 3.0
            + depth * 4.0
            + (12.0 if rank <= 50 else 0.0)
            - abs(pc - 0.45) * 18.0
            - abs(spread - 7.0) * 8.0
            - brisk * 28.0
            - fb * 45.0
            - struct * 22.0
        )

"""
        text = replace_once(text, marker, branch + marker, "candidate_priority meta marker")

    if '"V15 SPREAD SCOUT"' not in text:
        old = """    groups = [
        ("EXEC_SAFE STRATEGIES", lambda n, b: "_EXEC_" in n),
        ("OLD SAFE CONTROL", lambda n, b: n.startswith("FILTERED_045_SAFE")),
        ("BASE SHADOW STRATEGIES", lambda n, b: "_EXEC_" not in n and not n.startswith("FILTERED_045_SAFE")),
    ]
"""
        new = """    groups = [
        ("V15 SPREAD SCOUT", lambda n, b: n.startswith("V15_SPREAD_SCOUT")),
        ("SMART/META SAFE DRY", lambda n, b: n.startswith("SMART_V2_") or n.startswith("META_V12_")),
        ("EXEC_SAFE STRATEGIES", lambda n, b: "_EXEC_" in n),
        ("OLD SAFE CONTROL", lambda n, b: n.startswith("FILTERED_045_SAFE")),
        ("BASE SHADOW STRATEGIES", lambda n, b: "_EXEC_" not in n and not n.startswith("FILTERED_045_SAFE") and not n.startswith("V15_SPREAD_SCOUT") and not n.startswith("SMART_V2_") and not n.startswith("META_V12_")),
    ]
"""
        text = replace_once(text, old, new, "format_strategy_report groups")

    return text


def patch_main(text: str) -> str:
    text = text.replace("SMART UNIVERSE V2", "V15 SPREAD SCOUT")
    text = text.replace("v13 SmartUniverseV2", "v15 SpreadScout")
    text = text.replace("🤖 **V12 META EXEC SAFE ЖИВ** 🤖", "🤖 **SKYNET V15 DRY ЖИВ** 🤖")
    return text


def main():
    if not CFG.exists() or not ENG.exists() or not MAIN.exists():
        raise SystemExit("Run from /root/skynet with skynet_config.py, skynet_engine.py, skynet_main.py present.")

    backup = backup_files()
    print(f"📦 Backup created: {backup}")

    CFG.write_text(patch_config(CFG.read_text(encoding="utf-8")), encoding="utf-8")
    ENG.write_text(patch_engine(ENG.read_text(encoding="utf-8")), encoding="utf-8")
    MAIN.write_text(patch_main(MAIN.read_text(encoding="utf-8")), encoding="utf-8")

    code = os.system(f"{ROOT}/.venv/bin/python -m py_compile {CFG} {ENG} {MAIN}")
    if code != 0:
        print("❌ py_compile failed. Restore from backup:", backup)
        raise SystemExit(1)

    print("✅ V15 spread scout patch applied.")
    print("Next: update .env and restart skynet.")


if __name__ == "__main__":
    main()
