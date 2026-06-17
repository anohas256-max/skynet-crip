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
BACKUP_DIR = ROOT / f"backup_v12_meta_{STAMP}"


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
        raise RuntimeError(f"Cannot find expected block in {file_name}: {needle[:160]!r}")


def replace_regex(text, pattern, repl, file_name, flags=re.S, count=1):
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n != count:
        raise RuntimeError(f"Regex replace failed in {file_name}. Pattern: {pattern[:180]!r}, replacements={n}")
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
        'BOT_VERSION = "SKYNET_PRO_V12_META_EXEC_SAFE_DRY"',
        text,
        count=1,
    )

    default_tracks = '''DEFAULT_LIVE_DRY_TRACKS = (
    # V12 meta-selector candidates: one unified execution layer, not raw shadow branches.
    "META_V12_EXEC_SAFE_MO1,"
    "META_V12_OI_SAFE_MO1,"
    # Keep one v11.5 control branch for comparison.
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

    v12_settings = '''
# ============================================================
# V12 META EXECUTION-SAFE FRAMEWORK
# ============================================================
META_V12_MARGIN = float(os.getenv("META_V12_MARGIN", "3.0"))
META_V12_LEVERAGE = int(os.getenv("META_V12_LEVERAGE", "4"))
META_V12_MAX_OPEN = int(os.getenv("META_V12_MAX_OPEN", "1"))
META_V12_SPREAD_LIMIT_BPS = float(os.getenv("META_V12_SPREAD_LIMIT_BPS", "5"))
META_V12_MIN_SCORE = int(os.getenv("META_V12_MIN_SCORE", "4"))
META_V12_MIN_TREND_15M = float(os.getenv("META_V12_MIN_TREND_15M", "0.30"))
META_V12_STRICT_TREND_15M = float(os.getenv("META_V12_STRICT_TREND_15M", "0.40"))
META_V12_MIN_BTC_5M = float(os.getenv("META_V12_MIN_BTC_5M", "-0.10"))
META_V12_MAX_PRICE_CHANGE = float(os.getenv("META_V12_MAX_PRICE_CHANGE", "0.65"))
META_V12_MAX_VOL_RATIO = float(os.getenv("META_V12_MAX_VOL_RATIO", "35"))
META_V12_MAX_STRUCTURE_RISK = int(os.getenv("META_V12_MAX_STRUCTURE_RISK", "2"))
META_V12_MAX_BRISK = int(os.getenv("META_V12_MAX_BRISK", "3"))
META_V12_MAX_FALSE_BREAKOUTS = int(os.getenv("META_V12_MAX_FALSE_BREAKOUTS", "1"))
META_V12_CONFIRM_MAX_MOVE = float(os.getenv("META_V12_CONFIRM_MAX_MOVE", "0.75"))
META_V12_OI_SOFT_MIN = float(os.getenv("META_V12_OI_SOFT_MIN", "-0.50"))
META_V12_OI_STRICT_MIN = float(os.getenv("META_V12_OI_STRICT_MIN", "0.00"))
META_V12_ROLL_TOP_N = int(os.getenv("META_V12_ROLL_TOP_N", "30"))
'''
    anchor = 'BREAKOUT_COMBO_CLOSE_VS_EMA9_MIN = float(os.getenv("BREAKOUT_COMBO_CLOSE_VS_EMA9_MIN", "-0.10"))'
    if anchor in text:
        text = insert_after(text, anchor, v12_settings, "skynet_config.py", "V12 META EXECUTION-SAFE FRAMEWORK")
    else:
        text = insert_after(
            text,
            'ATR5B_DEFAULT_PRE_RANGE_5M = float(os.getenv("ATR5B_DEFAULT_PRE_RANGE_5M", "0.75"))',
            v12_settings,
            "skynet_config.py",
            "V12 META EXECUTION-SAFE FRAMEWORK",
        )

    dataclass_add = '''    # V12 meta-selector gates.
    meta_oi_min: float = -999.0
    meta_trend_min: float = -999.0
    meta_risk_max: int = 999
    meta_false_bo_max: int = 999
'''
    text = insert_after(
        text,
        '    breakout_risk_mode: str = "NONE"  # NONE / NO_FALSE_BREAKOUT / COMBO_BALANCED',
        dataclass_add,
        "skynet_config.py",
        "meta_oi_min",
    )

    helper = '''
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
'''
    text = insert_before(
        text,
        "def build_strategy_configs():",
        helper,
        "skynet_config.py",
        "V12 PATCH START: meta exec-safe strategy",
    )

    configs_block = '''
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

'''
    text = insert_after(
        text,
        "    configs = []\n",
        configs_block,
        "skynet_config.py",
        "V12 META EXEC-SAFE DRY CANDIDATES",
    )

    return text


def patch_engine(text: str) -> str:
    meta_func = '''
# === V12 PATCH START: meta selector rules ===
def meta_v12_sources(c: dict, scfg: cfg.StrategyConfig) -> list:
    # Return live-compatible source labels.
    # Raw old strategies are not opened directly here.
    sources = []

    score = int(safe_float(c.get("score"), -999))
    pc = safe_float(c.get("price_change"), 999.0)
    vol = safe_float(c.get("vol_ratio"), 999.0)
    trend = safe_float(c.get("trend_15m"), -999.0)
    btc5 = safe_float(c.get("btc_5m_change"), -999.0)
    oi = safe_float(c.get("oi_change"), -999.0)
    struct = int(safe_float(c.get("structure_risk"), 999))
    brisk = int(safe_float(c.get("breakout_risk_score"), 999))
    fb = int(safe_float(c.get("false_breakouts_15m"), 999))
    rank = int(safe_float(c.get("current_turnover_rank"), 999999))

    if score < cfg.META_V12_MIN_SCORE:
        return sources
    if not (cfg.PRICE_CHANGE_MIN <= pc <= cfg.META_V12_MAX_PRICE_CHANGE):
        return sources
    if vol > cfg.META_V12_MAX_VOL_RATIO:
        return sources
    if trend < getattr(scfg, "meta_trend_min", cfg.META_V12_MIN_TREND_15M):
        return sources
    if btc5 < cfg.META_V12_MIN_BTC_5M:
        return sources
    if oi < getattr(scfg, "meta_oi_min", cfg.META_V12_OI_SOFT_MIN):
        return sources
    if struct > cfg.META_V12_MAX_STRUCTURE_RISK:
        return sources
    if brisk > getattr(scfg, "meta_risk_max", cfg.META_V12_MAX_BRISK):
        return sources
    if fb > getattr(scfg, "meta_false_bo_max", cfg.META_V12_MAX_FALSE_BREAKOUTS):
        return sources
    if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
        return sources
    if not c.get("initiative_buying_proxy"):
        return sources

    if "passes_breakout_risk_mode" in globals() and passes_breakout_risk_mode(c, "COMBO_BALANCED"):
        sources.append("BREAKOUT_COMBO")

    if score >= 4 and 0.25 <= pc <= 0.55 and trend >= cfg.META_V12_MIN_TREND_15M and not is_exhaustion(vol, pc):
        sources.append("FILTERED_055_EXEC_SAFE")

    if (
        (score >= 4 and 0.25 <= pc <= 0.45)
        or (score >= 6 and 0.45 < pc <= cfg.META_V12_MAX_PRICE_CHANGE and trend >= cfg.META_V12_STRICT_TREND_15M)
    ):
        sources.append("HYBRID_SCALP_EXEC_SAFE")

    if rank <= cfg.META_V12_ROLL_TOP_N and trend >= cfg.META_V12_STRICT_TREND_15M:
        sources.append(f"ROLL24_TOP{cfg.META_V12_ROLL_TOP_N}")

    if oi >= cfg.META_V12_OI_STRICT_MIN:
        sources.append("OI_FRESH")

    return sources
# === V12 PATCH END: meta selector rules ===
'''
    text = insert_before(
        text,
        "# ============================================================\n# STRATEGY RULES",
        meta_func,
        "skynet_engine.py",
        "V12 PATCH START: meta selector rules",
    )

    meta_rule = '''
    if f in ("meta_v12_exec_safe", "meta_v12_oi_safe"):
        sources = meta_v12_sources(c, scfg)
        if not sources:
            return False
        c["meta_sources_v12"] = ",".join(sources)
        c["meta_source_count_v12"] = len(sources)
        return True

'''
    if '    if f == "breakout_confirm_atr":' in text:
        text = insert_before(
            text,
            '    if f == "breakout_confirm_atr":',
            meta_rule,
            "skynet_engine.py",
            'if f in ("meta_v12_exec_safe", "meta_v12_oi_safe"):',
        )
    else:
        text = insert_before(
            text,
            '    if f == "initiative_confirm_trend_atr":',
            meta_rule,
            "skynet_engine.py",
            'if f in ("meta_v12_exec_safe", "meta_v12_oi_safe"):',
        )

    text = text.replace(
        'if fam in ("initiative_runner", "main_context_strict_runner", "initiative_confirm_trend_atr", "initiative_confirm_runner", "breakout_confirm_atr"):',
        'if fam in ("initiative_runner", "main_context_strict_runner", "initiative_confirm_trend_atr", "initiative_confirm_runner", "breakout_confirm_atr", "meta_v12_exec_safe", "meta_v12_oi_safe"):',
        1,
    )
    text = text.replace(
        'if fam in ("initiative_runner", "main_context_strict_runner", "initiative_confirm_trend_atr", "initiative_confirm_runner"):',
        'if fam in ("initiative_runner", "main_context_strict_runner", "initiative_confirm_trend_atr", "initiative_confirm_runner", "breakout_confirm_atr", "meta_v12_exec_safe", "meta_v12_oi_safe"):',
        1,
    )

    priority_insert = '''
    if fam in ("meta_v12_exec_safe", "meta_v12_oi_safe"):
        score = safe_float(c.get("score"), 0)
        pc = safe_float(c.get("price_change"), 0)
        trend = safe_float(c.get("trend_15m"), 0)
        btc5 = safe_float(c.get("btc_5m_change"), 0)
        oi = safe_float(c.get("oi_change"), 0)
        spread = safe_float(c.get("spread_bps"), 7.0)
        brisk = safe_float(c.get("breakout_risk_score"), 5)
        fb = safe_float(c.get("false_breakouts_15m"), 2)
        struct = safe_float(c.get("structure_risk"), 3)
        src_count = safe_float(c.get("meta_source_count_v12"), 0)
        rank = safe_float(c.get("current_turnover_rank"), 999)

        return (
            score * 100.0
            + min(trend, 2.0) * 10.0
            + btc5 * 6.0
            + max(min(oi, 10.0), -3.0) * 4.0
            + src_count * 18.0
            - abs(pc - 0.42) * 20.0
            - spread * 3.0
            - brisk * 18.0
            - fb * 35.0
            - struct * 10.0
            + (10.0 if rank <= cfg.META_V12_ROLL_TOP_N else 0.0)
        )
'''
    text = insert_after(
        text,
        '    fam = scfg.family if scfg else ""',
        priority_insert,
        "skynet_engine.py",
        'fam in ("meta_v12_exec_safe", "meta_v12_oi_safe")',
    )

    context_old = '''            "confirm_move_pct": candidate.get("confirm_move_pct", 0.0),'''
    context_new = '''            "confirm_move_pct": candidate.get("confirm_move_pct", 0.0),
            "meta_sources_v12": candidate.get("meta_sources_v12", ""),
            "meta_source_count_v12": candidate.get("meta_source_count_v12", 0),'''
    if '"meta_sources_v12": candidate.get("meta_sources_v12"' not in text:
        text = text.replace(context_old, context_new, 1)

    return text


def patch_main(text: str) -> str:
    if "import csv\n" not in text:
        text = text.replace("import os\n", "import os\nimport csv\n", 1)

    text = text.replace(
        "=== START {cfg.BOT_VERSION} | BREAKOUT RISK ATR5B ===",
        "=== START {cfg.BOT_VERSION} | META EXEC SAFE ===",
    )
    text = text.replace(
        "=== START {cfg.BOT_VERSION} | TREND ATR5B UNIVERSE ===",
        "=== START {cfg.BOT_VERSION} | META EXEC SAFE ===",
    )
    text = text.replace(
        'caption=f"📁 v11.5 BreakoutRisk лог за {log_interval} ({date_postfix})"',
        'caption=f"📁 v12 MetaExecSafe лог за {log_interval} ({date_postfix})"',
    )
    text = text.replace(
        'caption=f"📁 v11.4 TrendATR лог за {log_interval} ({date_postfix})"',
        'caption=f"📁 v12 MetaExecSafe лог за {log_interval} ({date_postfix})"',
    )
    text = text.replace(
        'f"🤖 **V11.5 BREAKOUT RISK ATR ЖИВ** 🤖\\n"',
        'f"🤖 **V12 META EXEC SAFE ЖИВ** 🤖\\n"',
    )
    text = text.replace(
        'f"🤖 **V11.3 CONFIRM RUNNER ЖИВ** 🤖\\n"',
        'f"🤖 **V12 META EXEC SAFE ЖИВ** 🤖\\n"',
    )

    logger = '''
# === V12 PATCH START: market event logger ===
V12_EVENT_CSV = "/root/skynet/data/v12_market_events.csv"

def write_v12_event(candidate: dict, stage: str, note: str = ""):
    try:
        os.makedirs(os.path.dirname(V12_EVENT_CSV), exist_ok=True)
        exists = os.path.exists(V12_EVENT_CSV)
        fields = [
            "ts", "stage", "note", "symbol", "score", "price_change", "vol_ratio",
            "trend_15m", "btc_5m_change", "oi_change", "spread_bps", "structure_risk",
            "breakout_risk_score", "false_breakouts_15m", "current_turnover_rank",
            "initiative", "meta_sources_v12"
        ]
        row = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stage": stage,
            "note": note,
            "symbol": candidate.get("clean_symbol", candidate.get("symbol", "")),
            "score": candidate.get("score", ""),
            "price_change": candidate.get("price_change", ""),
            "vol_ratio": candidate.get("vol_ratio", ""),
            "trend_15m": candidate.get("trend_15m", ""),
            "btc_5m_change": candidate.get("btc_5m_change", ""),
            "oi_change": candidate.get("oi_change", ""),
            "spread_bps": candidate.get("spread_bps", ""),
            "structure_risk": candidate.get("structure_risk", ""),
            "breakout_risk_score": candidate.get("breakout_risk_score", ""),
            "false_breakouts_15m": candidate.get("false_breakouts_15m", ""),
            "current_turnover_rank": candidate.get("current_turnover_rank", ""),
            "initiative": int(bool(candidate.get("initiative_buying_proxy", False))),
            "meta_sources_v12": candidate.get("meta_sources_v12", ""),
        }
        with open(V12_EVENT_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            if not exists:
                w.writeheader()
            w.writerow(row)
    except Exception as e:
        write_to_logs(f"[{time.strftime('%H:%M:%S')}] V12_EVENT_LOG_ERROR | {type(e).__name__}: {e}\\n")
# === V12 PATCH END: market event logger ===
'''
    text = insert_after(
        text,
        "eng.set_log_writer(write_to_logs)",
        logger,
        "skynet_main.py",
        "V12 PATCH START: market event logger",
    )

    old_log = '''                            f"BRisk:{candidate.get('breakout_risk_score',0)} FB:{candidate.get('false_breakouts_15m',0)} | "
                            f"CP:{candidate.get('close_position',0.5):.2f} | Body:{candidate.get('body_ratio',0):.2f} | "'''
    new_log = '''                            f"BRisk:{candidate.get('breakout_risk_score',0)} FB:{candidate.get('false_breakouts_15m',0)} | "
                            f"Meta:{candidate.get('meta_sources_v12','-')} | "
                            f"CP:{candidate.get('close_position',0.5):.2f} | Body:{candidate.get('body_ratio',0):.2f} | "'''
    if old_log in text and "Meta:{candidate.get('meta_sources_v12'" not in text:
        text = text.replace(old_log, new_log, 1)

    anchor = '''                        if (candidate["score"] > 0 or visible_entered) and is_tg_cooldown_ok:'''
    insertion = '''                        # V12: write every anomaly to CSV, even if no selector opens it.
                        write_v12_event(candidate, "ANOMALY", verdict)
'''
    if "write_v12_event(candidate, \"ANOMALY\"" not in text:
        text = text.replace(anchor, insertion + "\n" + anchor, 1)

    old_pending = '''            f"spread={cand.get('spread_bps',999):.2f}bps/{scfg.spread_limit_bps:.0f} "
            f"br={cand.get('breakout_risk_score',0)} fb={cand.get('false_breakouts_15m',0)}\\n"'''
    new_pending = '''            f"spread={cand.get('spread_bps',999):.2f}bps/{scfg.spread_limit_bps:.0f} "
            f"br={cand.get('breakout_risk_score',0)} fb={cand.get('false_breakouts_15m',0)} "
            f"meta={cand.get('meta_sources_v12','-')}\\n"'''
    if old_pending in text and "meta={cand.get('meta_sources_v12'" not in text:
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

        print("✅ V12 meta patch applied and py_compile OK.")
        print("Next:")
        print("  update .env LIVE_DRY_TRACKS to META_V12_EXEC_SAFE_MO1,META_V12_OI_SAFE_MO1,BREAKOUT_TREND040_PC065_VOL35_COMBO_BALANCED_ATR5B_WAIT1_MO1")
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
