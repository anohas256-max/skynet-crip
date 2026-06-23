#!/usr/bin/env python3
import os
import sys
import json
import time
import shlex
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path("/root/skynet")
os.chdir(ROOT)


def load_dotenv(path: Path):
    if not path.exists():
        return
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


load_dotenv(ROOT / ".env")


def get_cfg_attr(*names):
    try:
        import skynet_config as cfg
        for name in names:
            if hasattr(cfg, name):
                val = getattr(cfg, name)
                if val not in (None, ""):
                    return str(val)
    except Exception:
        pass
    return ""


TG_TOKEN = (
    os.getenv("TG_BOT_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("TELEGRAM_TOKEN")
    or os.getenv("BOT_TOKEN")
    or get_cfg_attr("TG_BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN", "BOT_TOKEN")
)

TG_TARGET = (
    os.getenv("TG_TARGET")
    or os.getenv("TELEGRAM_CHAT_ID")
    or os.getenv("TG_CHAT_ID")
    or os.getenv("CHAT_ID")
    or get_cfg_attr("TG_TARGET", "TELEGRAM_CHAT_ID", "TG_CHAT_ID", "CHAT_ID")
)


def run(cmd: str, timeout: int = 45) -> str:
    try:
        p = subprocess.run(
            cmd,
            shell=True,
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        out = p.stdout or ""
        return f"$ {cmd}\n{out}".rstrip()
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ""
        if isinstance(out, bytes):
            out = out.decode(errors="ignore")
        return f"$ {cmd}\nTIMEOUT after {timeout}s\n{out}".rstrip()
    except Exception as e:
        return f"$ {cmd}\nERROR: {e!r}"


def tg_send(text: str):
    if not TG_TOKEN or not TG_TARGET:
        print("TG config missing. Need TG_BOT_TOKEN/TELEGRAM_BOT_TOKEN and TG_TARGET/TELEGRAM_CHAT_ID.")
        print(text)
        sys.exit(2)

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

    # Telegram limit is 4096 chars. Keep margin.
    chunks = []
    cur = ""
    for line in text.splitlines():
        if len(cur) + len(line) + 1 > 3500:
            chunks.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        chunks.append(cur)

    for i, chunk in enumerate(chunks, 1):
        prefix = f"🧪 SKYNET smoke check {i}/{len(chunks)}\n"
        data = urllib.parse.urlencode({
            "chat_id": TG_TARGET,
            "text": prefix + chunk,
            "disable_web_page_preview": "true",
        }).encode()

        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            r.read()
        time.sleep(0.5)


def py_block(code: str) -> str:
    cmd = f"""{shlex.quote(str(ROOT / ".venv/bin/python"))} - <<'PYCODE'
{code}
PYCODE"""
    return run(cmd, timeout=60)


report = []
report.append("=== SKYNET TG SMOKE CHECK ===")
report.append(run("date -u"))
report.append(run("git status --short && git log --oneline -5", timeout=30))

report.append("\n=== 1. CODE COMPILE ===")
report.append(run("/root/skynet/.venv/bin/python -m py_compile skynet_config.py skynet_engine.py skynet_main.py skynet_context_pack.py", timeout=60))

report.append("\n=== 2. STRATEGY REGISTRATION ===")
report.append(py_block(r'''
import skynet_config as cfg

configs = cfg.build_strategy_configs()
names = [
    "COST_NEAR_MISS_FAST",
    "COST_RESCUE_CLEAN_IMPULSE",
    "DEPTH_THIN_ESCAPE_SHADOW",
    "YELLOW_SCORE3",
    "YELLOW_SCORE3_FAST",
]

for name in names:
    c = configs.get(name)
    print("=" * 72)
    print(name)
    print("exists:", c is not None)
    if c:
        for attr in [
            "family", "margin", "tp", "leverage", "max_open",
            "silent", "selector", "require_depth",
            "spread_limit_bps", "skip_track"
        ]:
            print(attr + ":", getattr(c, attr, None))
'''))

report.append("\n=== 3. ENGINE RULES ON KNOWN CASES ===")
report.append(py_block(r'''
import skynet_config as cfg
import skynet_engine as eng

configs = cfg.build_strategy_configs()

cases = {
    "RE_false_negative_should_rescue": {
        "score": 3, "price_change": 0.80, "vol_ratio": 10.1,
        "trend_15m": 4.0, "btc_5m_change": 0.10, "oi_change": 2.4,
        "current_turnover_rank": 22, "structure_risk": 2,
        "breakout_risk_score": 1, "false_breakouts_15m": 1,
        "weak_long_result": True, "initiative_buying_proxy": False,
        "depth_available": True, "depth_thin": False, "spread_bps": 2.0,
    },
    "BLESS_depth_thin_should_escape": {
        "score": 5, "price_change": 0.63, "vol_ratio": 20.7,
        "trend_15m": 0.96, "btc_5m_change": -0.02, "oi_change": 2.7,
        "current_turnover_rank": 46, "structure_risk": 2,
        "breakout_risk_score": 1, "false_breakouts_15m": 1,
        "depth_available": True, "depth_thin": True, "spread_bps": 0.93,
        "top5_bid_usdt": 383, "top5_ask_usdt": 155,
    },
    "WLD_dirty_should_not_rescue": {
        "score": 3, "price_change": 0.61, "vol_ratio": 9.0,
        "trend_15m": 0.39, "btc_5m_change": -0.04, "oi_change": 1.5,
        "current_turnover_rank": 9, "structure_risk": 3,
        "breakout_risk_score": 6, "false_breakouts_15m": 2,
        "weak_long_result": True, "initiative_buying_proxy": False,
    },
    "INJ_weak_should_fail_cost": {
        "score": 4, "price_change": 0.32, "vol_ratio": 25.9,
        "trend_15m": 0.32, "btc_5m_change": 0.36, "oi_change": -2.1,
        "current_turnover_rank": 31, "structure_risk": 1,
        "breakout_risk_score": 0, "false_breakouts_15m": 1,
    },
}

for name, c in cases.items():
    print("=" * 72)
    print(name)
    print("cost_debug:", eng.cost_gate_debug(c))
    print("cost_ok:", eng.cost_gate_long(c))
    print("near_miss:", getattr(eng, "is_cost_near_miss_fast", lambda x: None)(c))
    print("rescue:", getattr(eng, "is_cost_rescue_clean_impulse", lambda x: None)(c))
    print("depth_precheck:", getattr(eng, "is_depth_thin_escape_precheck", lambda x: None)(c))
    print("depth_escape_full:", getattr(eng, "is_depth_thin_escape_shadow", lambda x: None)(c))

    for strat in ["COST_RESCUE_CLEAN_IMPULSE", "DEPTH_THIN_ESCAPE_SHADOW"]:
        if strat in configs:
            scfg = configs[strat]
            try:
                print(strat, "should_enter:", eng.should_enter_strategy(scfg, c))
                if getattr(scfg, "require_depth", False):
                    print(strat, "depth_validate:", eng.validate_depth_for_strategy(scfg, c))
            except Exception as e:
                print(strat, "ERROR:", repr(e))
'''))

report.append("\n=== 4. SERVICE STATUS ===")
report.append(run("systemctl status skynet.service --no-pager -l | head -30", timeout=30))

report.append("\n=== 5. RECENT ERRORS ===")
report.append(run("journalctl -u skynet.service --since '10 minutes ago' --no-pager -l | grep -E 'Traceback|Ошибка|SyntaxError|TypeError' || true", timeout=30))

report.append("\n=== 6. RECENT RESCUE LANES LOGS ===")
report.append(run("grep -R 'COST_RESCUE_CLEAN_IMPULSE\\|DEPTH_THIN_ESCAPE_SHADOW\\|COST_NEAR_MISS_FAST' skynet_3h.log skynet_12h.log skynet_48h.log 2>/dev/null | tail -80 || true", timeout=30))

final = "\n\n".join(report)
print(final)
tg_send(final)
