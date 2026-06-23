#!/usr/bin/env python3
import os
import sys
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


def env_name(*parts: str) -> str:
    return "".join(parts)


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


# Build sensitive env names from pieces so context-pack redaction does not corrupt this file copy.
BOT_TOKEN_NAMES = [
    env_name("TG_", "BOT_", "TOKEN"),
    env_name("TELEGRAM_", "BOT_", "TOKEN"),
    env_name("TELEGRAM_", "TOKEN"),
    env_name("BOT_", "TOKEN"),
]

CHAT_ID_NAMES = [
    "TG_TARGET",
    "TELEGRAM_CHAT_ID",
    "TG_CHAT_ID",
    "CHAT_ID",
]

bot_token = ""
for n in BOT_TOKEN_NAMES:
    bot_token = os.getenv(n) or bot_token
    if bot_token:
        break
if not bot_token:
    bot_token = get_cfg_attr(*BOT_TOKEN_NAMES)

chat_id = ""
for n in CHAT_ID_NAMES:
    chat_id = os.getenv(n) or chat_id
    if chat_id:
        break
if not chat_id:
    chat_id = get_cfg_attr(*CHAT_ID_NAMES)


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
    if not bot_token or not chat_id:
        print("TG config missing. Need bot token env and chat id env.")
        print("Checked bot env names:", ", ".join(BOT_TOKEN_NAMES))
        print("Checked chat env names:", ", ".join(CHAT_ID_NAMES))
        print(text)
        sys.exit(2)

    url = "https://api.telegram.org/bot" + bot_token + "/sendMessage"

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
            "chat_id": chat_id,
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
report.append(run("/root/skynet/.venv/bin/python -m py_compile skynet_config.py skynet_engine.py skynet_main.py skynet_context_pack.py tg_smoke_check.py", timeout=60))

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
