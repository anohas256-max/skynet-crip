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
    backup = ROOT / f"backup_v14_adaptive_passport_{stamp}"
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
        'BOT_VERSION = "SKYNET_PRO_V14_ADAPTIVE_PASSPORT_DRY"',
        text,
        count=1,
    )

    text = text.replace(
        '"SMART_V2_STRICT_OI_MO1,"\n    # Keep one V12 control for comparison.\n    "META_V12_EXEC_SAFE_MO1"',
        '"SMART_V2_STRICT_BTC_MO1,"\n    # Keep one V12 control for comparison.\n    "META_V12_EXEC_SAFE_MO1"',
    )

    if "# V14 ADAPTIVE PASSPORT / CORE RISK GATE" not in text:
        marker = 'SMART_V2_COOLDOWN_HOURS = float(os.getenv("SMART_V2_COOLDOWN_HOURS", "24"))'
        insert = marker + """

# ============================================================
# V14 ADAPTIVE PASSPORT / CORE RISK GATE
# ============================================================
# Более значимый слой: smart-universe больше не считает core/top30 безопасным автоматически.
# 1) Core risk gate режет грязные core-входы (например BRisk/false breakout).
# 2) Dynamic symbol passport живёт между рестартами и временно охлаждает токсичные символы.
SMART_V2_PERSIST_ENABLED = os.getenv("SMART_V2_PERSIST_ENABLED", "true").lower() == "true"
SMART_V2_PASSPORT_PATH = os.getenv("SMART_V2_PASSPORT_PATH", "/root/skynet/data/smart_v2_passport.json")

SMART_V2_CORE_RISK_GATE_ENABLED = os.getenv("SMART_V2_CORE_RISK_GATE_ENABLED", "true").lower() == "true"
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
SMART_V2_GOOD_MFE = float(os.getenv("SMART_V2_GOOD_MFE", "0.80"))"""
        text = replace_once(text, marker, insert, "SMART_V2_COOLDOWN_HOURS")
    return text


def patch_engine(text: str) -> str:
    if "import json\nimport os\n" not in text:
        text = replace_once(text, "import asyncio\nimport time\n", "import asyncio\nimport time\nimport json\nimport os\n", "engine imports")

    start = text.index("class SmartV2SymbolQuality:")
    end = text.index("_SMART_V2_QUALITY = {}", start)
    new_class = """class SmartV2SymbolQuality:
    def __init__(self, maxlen: int = None):
        self.items = []
        self.maxlen = int(maxlen or getattr(cfg, "SMART_V2_TOXIC_WINDOW", 4))
        self.bad_streak = 0
        self.cooldown_until = 0.0
        self.last_toxic_reason = ""

    def update(self, net: float, mfe: float, reason: str, exit_time: float):
        # V14: не вечный blacklist, а временный toxic-score.
        # Символ может восстановиться: хорошие outcomes уменьшают bad_streak.
        sl = reason == "SL"
        bad = (
            sl
            or net < -0.05
            or (net < 0 and mfe < getattr(cfg, "SMART_V2_TOXIC_MIN_AVG_MFE", 0.60))
        )
        good = net > 0 and mfe >= getattr(cfg, "SMART_V2_GOOD_MFE", 0.80)

        if bad:
            self.bad_streak += 1
        elif good:
            self.bad_streak = max(0, self.bad_streak - 1)

        self.items.append({"net": float(net), "mfe": float(mfe), "reason": reason, "bad": bool(bad), "good": bool(good)})
        if len(self.items) > self.maxlen:
            self.items = self.items[-self.maxlen:]

        if self._is_toxic_now():
            self.cooldown_until = exit_time + getattr(cfg, "SMART_V2_TOXIC_COOLDOWN_HOURS", cfg.SMART_V2_COOLDOWN_HOURS) * 3600.0

    def _is_toxic_now(self) -> bool:
        if len(self.items) < 2:
            return False

        n = len(self.items)
        avg_net = sum(x["net"] for x in self.items) / n
        avg_mfe = sum(x["mfe"] for x in self.items) / n
        sl_rate = sum(1 for x in self.items if x["reason"] == "SL") / n

        if self.bad_streak >= cfg.SMART_V2_MAX_BAD_STREAK and avg_net <= getattr(cfg, "SMART_V2_TOXIC_SL_AVG_NET_MAX", 0.02):
            self.last_toxic_reason = "BAD_STREAK"
            return True

        if sl_rate >= getattr(cfg, "SMART_V2_TOXIC_MAX_SL_RATE", 0.50) and avg_net < getattr(cfg, "SMART_V2_TOXIC_SL_AVG_NET_MAX", 0.02):
            self.last_toxic_reason = "SL_RATE"
            return True

        if avg_net < getattr(cfg, "SMART_V2_TOXIC_MIN_AVG_NET", -0.05):
            self.last_toxic_reason = "AVG_NET"
            return True

        if avg_mfe < getattr(cfg, "SMART_V2_TOXIC_MIN_AVG_MFE", 0.60) and avg_net <= 0:
            self.last_toxic_reason = "LOW_MFE"
            return True

        self.last_toxic_reason = ""
        return False

    def features(self):
        n = len(self.items)
        if n <= 0:
            return {
                "obs": 0,
                "avg_net": 0.0,
                "avg_mfe": 0.0,
                "sl_rate": 0.0,
                "good_rate": 0.0,
                "bad_streak": self.bad_streak,
                "cooldown_until": self.cooldown_until,
                "toxic_reason": self.last_toxic_reason,
            }

        return {
            "obs": n,
            "avg_net": sum(x["net"] for x in self.items) / n,
            "avg_mfe": sum(x["mfe"] for x in self.items) / n,
            "sl_rate": sum(1 for x in self.items if x["reason"] == "SL") / n,
            "good_rate": sum(1 for x in self.items if x.get("good")) / n,
            "bad_streak": self.bad_streak,
            "cooldown_until": self.cooldown_until,
            "toxic_reason": self.last_toxic_reason,
        }

    def to_dict(self):
        return {
            "items": self.items,
            "maxlen": self.maxlen,
            "bad_streak": self.bad_streak,
            "cooldown_until": self.cooldown_until,
            "last_toxic_reason": self.last_toxic_reason,
        }

    @classmethod
    def from_dict(cls, data):
        q = cls(maxlen=int(data.get("maxlen", getattr(cfg, "SMART_V2_TOXIC_WINDOW", 4))))
        q.items = list(data.get("items", []))[-q.maxlen:]
        q.bad_streak = int(data.get("bad_streak", 0))
        q.cooldown_until = float(data.get("cooldown_until", 0.0))
        q.last_toxic_reason = str(data.get("last_toxic_reason", ""))
        return q


"""
    text = text[:start] + new_class + text[end:]

    if "def _smart_v2_load_passports()" not in text:
        marker = "\n\ndef _smart_v2_quality(symbol: str) -> SmartV2SymbolQuality:"
        helpers = """

def _smart_v2_load_passports():
    if not getattr(cfg, "SMART_V2_PERSIST_ENABLED", True):
        return
    path = getattr(cfg, "SMART_V2_PASSPORT_PATH", "/root/skynet/data/smart_v2_passport.json")
    try:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        now = time.time()
        loaded = 0
        for symbol, data in raw.get("symbols", {}).items():
            q = SmartV2SymbolQuality.from_dict(data)
            # Не тащим древние cooldown навсегда.
            if q.cooldown_until and q.cooldown_until < now - 86400:
                q.cooldown_until = 0.0
            _SMART_V2_QUALITY[symbol] = q
            loaded += 1
        if loaded:
            log(f"🧠 SMART_V2_PASSPORT_LOADED symbols={loaded} path={path}\\n")
    except Exception as e:
        log(f"⚠️ SMART_V2_PASSPORT_LOAD_ERROR | {type(e).__name__}: {e}\\n")


def _smart_v2_save_passports():
    if not getattr(cfg, "SMART_V2_PERSIST_ENABLED", True):
        return
    path = getattr(cfg, "SMART_V2_PASSPORT_PATH", "/root/skynet/data/smart_v2_passport.json")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
            "version": "v14",
            "updated": time.time(),
            "symbols": {symbol: q.to_dict() for symbol, q in _SMART_V2_QUALITY.items()},
        }
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as e:
        log(f"⚠️ SMART_V2_PASSPORT_SAVE_ERROR | {type(e).__name__}: {e}\\n")


_smart_v2_load_passports()
"""
        text = replace_once(text, marker, helpers + marker, "_smart_v2_quality marker")

    old = """    q.update(net, w["max_profit_pct"], reason, current_time)
    _SMART_V2_STATS["closed"] += 1
"""
    new = """    q.update(net, w["max_profit_pct"], reason, current_time)
    _smart_v2_save_passports()
    _SMART_V2_STATS["closed"] += 1
"""
    if old in text and "_smart_v2_save_passports()\n    _SMART_V2_STATS" not in text:
        text = text.replace(old, new, 1)

    if "def _smart_v2_core_candidate" not in text:
        marker = "\n\ndef smart_v2_pass_guard(c: dict, guard: str) -> bool:"
        core_func = """

def _smart_v2_core_candidate(c: dict) -> bool:
    # V14: core/top30 больше не автопроход.
    # Вырезает ситуации типа score=7, rank=14, но BRisk=4 / FB=3.
    if not getattr(cfg, "SMART_V2_CORE_RISK_GATE_ENABLED", True):
        return True

    return (
        c.get("score", 0) >= getattr(cfg, "SMART_V2_CORE_MIN_SCORE", 5)
        and c.get("breakout_risk_score", 999) <= getattr(cfg, "SMART_V2_CORE_MAX_BRISK", 3)
        and c.get("false_breakouts_15m", 999) <= getattr(cfg, "SMART_V2_CORE_MAX_FALSE_BREAKOUTS", 2)
        and c.get("structure_risk", 999) <= getattr(cfg, "SMART_V2_CORE_MAX_STRUCTURE_RISK", 2)
        and c.get("trend_15m", -999.0) >= getattr(cfg, "SMART_V2_CORE_MIN_TREND_15M", 0.30)
        and c.get("btc_5m_change", -999.0) >= getattr(cfg, "SMART_V2_CORE_MIN_BTC_5M", -0.05)
        and c.get("oi_change", -999.0) >= getattr(cfg, "SMART_V2_CORE_MIN_OI", -0.50)
        and c.get("initiative_buying_proxy", False)
    )
"""
        text = replace_once(text, marker, core_func + marker, "smart_v2_pass_guard marker")

    start = text.index("def smart_v2_decision(c: dict, scfg) -> Tuple[bool, str]:")
    end = text.index("\n\ndef smart_v2_should_enter", start)
    new_decision = """def smart_v2_decision(c: dict, scfg) -> Tuple[bool, str]:
    rank = int(c.get("current_turnover_rank", 999999))
    core_top = int(getattr(scfg, "smart_core_top", cfg.SMART_V2_CORE_TOP) or cfg.SMART_V2_CORE_TOP)
    mid_top = int(getattr(scfg, "smart_mid_top", cfg.SMART_V2_MID_TOP) or cfg.SMART_V2_MID_TOP)

    q = _smart_v2_quality(c.get("symbol", "")).features()
    current_time = safe_float(c.get("_current_time"), time.time())

    # V14: временный toxic cooldown работает даже для core/top30.
    if q["cooldown_until"] and current_time < q["cooldown_until"]:
        if cfg.SMART_V2_ALLOW_ULTRA_OVERRIDE and _smart_v2_ultra_candidate(c):
            return True, "COOLDOWN_ULTRA_OVERRIDE"
        return False, "COOLDOWN"

    if q["bad_streak"] >= cfg.SMART_V2_MAX_BAD_STREAK and q["obs"] >= 2:
        if cfg.SMART_V2_ALLOW_ULTRA_OVERRIDE and _smart_v2_ultra_candidate(c):
            return True, "BAD_STREAK_ULTRA_OVERRIDE"
        return False, "BAD_STREAK"

    if rank <= core_top:
        if not _smart_v2_core_candidate(c):
            return False, "CORE_RISK_REJECT"
        return True, "CORE_CLEAN"

    if rank > mid_top:
        return False, "EXPLORE_MONITOR_ONLY"

    if q["obs"] < cfg.SMART_V2_MIN_OBS:
        # V2_STRICT cold policy: only ultra current signal may spend money in MID.
        if _smart_v2_ultra_candidate(c):
            return True, "MID_COLD_ULTRA"
        return False, "MID_COLD_REJECT"

    quality_ok = (
        q["avg_net"] >= cfg.SMART_V2_MIN_AVG_NET
        and q["sl_rate"] <= cfg.SMART_V2_MAX_SL_RATE
        and q["avg_mfe"] >= cfg.SMART_V2_MIN_AVG_MFE
        and _smart_v2_clean_candidate(c)
    )
    if quality_ok:
        return True, "MID_QUALITY_OK"

    if cfg.SMART_V2_ALLOW_STRONG_OVERRIDE and _smart_v2_strong_candidate(c) and q["sl_rate"] <= min(0.75, cfg.SMART_V2_MAX_SL_RATE + 0.15):
        return True, "MID_STRONG_OVERRIDE"

    if cfg.SMART_V2_ALLOW_ULTRA_OVERRIDE and _smart_v2_ultra_candidate(c) and q["sl_rate"] <= 0.75:
        return True, "MID_ULTRA_OVERRIDE"

    return False, "MID_QUALITY_REJECT\""""
    # fix escaped quote typo if present
    new_decision = new_decision.replace('return False, "MID_QUALITY_REJECT\\"', 'return False, "MID_QUALITY_REJECT"')
    text = text[:start] + new_decision + text[end:]

    old_report = """f"avgMFE={f['avg_mfe']:.2f}% slRate={f['sl_rate']:.2f} bad={f['bad_streak']}" """
    # report line has no trailing space in real file, use replace with exact substring fallback
    text = text.replace(
        """f"avgMFE={f['avg_mfe']:.2f}% slRate={f['sl_rate']:.2f} bad={f['bad_streak']}" """.strip(),
        """f"avgMFE={f['avg_mfe']:.2f}% slRate={f['sl_rate']:.2f} bad={f['bad_streak']} tox={f.get('toxic_reason','')}" """.strip(),
    )

    return text


def main():
    if not CFG.exists() or not ENG.exists() or not MAIN.exists():
        raise SystemExit("Run from /root/skynet with skynet_config.py, skynet_engine.py, skynet_main.py present.")

    backup = backup_files()
    print(f"📦 Backup created: {backup}")

    cfg_text = CFG.read_text(encoding="utf-8")
    eng_text = ENG.read_text(encoding="utf-8")

    CFG.write_text(patch_config(cfg_text), encoding="utf-8")
    ENG.write_text(patch_engine(eng_text), encoding="utf-8")

    code = os.system(f"{ROOT}/.venv/bin/python -m py_compile {CFG} {ENG} {MAIN}")
    if code != 0:
        print("❌ py_compile failed. Restore from backup:", backup)
        raise SystemExit(1)

    print("✅ V14 adaptive passport patch applied.")
    print("Next: update .env if needed, then systemctl restart skynet")


if __name__ == "__main__":
    main()
