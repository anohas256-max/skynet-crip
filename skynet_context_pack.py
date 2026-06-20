#!/usr/bin/env python3
import argparse
import os
import re
import sys
import tarfile
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
OUT_ROOT = ROOT / "safe_exports"
DATA_DIR = ROOT / "data"

SECRET_KEYWORDS = [
    "API_HASH",
    "API_ID",
    "MEXC_API_KEY",
    "MEXC_API_SECRET",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "PRIVATE_KEY",
    "SECRET_KEY",
    "PASSWORD",
    "TOKEN",
]

BAD_PATH_PARTS = [
    "/.git/",
    "/.venv/",
    "/venv/",
    "/env/",
    "/data/",
    "/archive/",
    "/safe_exports/",
    "__pycache__",
]

BAD_SUFFIXES = [
    ".pyc",
    ".log",
    ".session",
    ".session-journal",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".zip",
    ".tar",
    ".gz",
    ".bak",
]

def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")

def run(cmd: str, timeout: int = 20) -> str:
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
        return redact(p.stdout)
    except Exception as e:
        return f"[RUN_ERROR] {cmd}\n{type(e).__name__}: {e}\n"

def redact(text: str) -> str:
    if not text:
        return text

    # hide KEY=value style
    for key in SECRET_KEYWORDS:
        text = re.sub(rf"({re.escape(key)}\s*=\s*)([^\s'\"]+)", rf"\1<hidden>", text, flags=re.I)
        text = re.sub(rf"({re.escape(key)}['\"]?\s*:\s*['\"])([^'\"]+)(['\"])", rf"\1<hidden>\3", text, flags=re.I)

    # hide common long token-like strings after dangerous words
    text = re.sub(r"(secret[_-]?key|api[_-]?secret|api[_-]?key|token)(.{0,8})([A-Za-z0-9_\-:]{16,})", r"\1\2<hidden>", text, flags=re.I)
    return text

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redact(content), encoding="utf-8", errors="ignore")

def env_keys_report() -> str:
    p = ROOT / ".env"
    if not p.exists():
        return ".env not found\n"

    lines = []
    lines.append(f".env exists = true")
    lines.append(f".env mode = {oct(p.stat().st_mode)[-3:]}")
    lines.append("")
    for i, raw in enumerate(p.read_text(errors="ignore").splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if "=" in s:
            k = s.split("=", 1)[0].strip()
            lines.append(f"{i}: {k}=<hidden>")
    return "\n".join(lines) + "\n"

def config_snapshot() -> str:
    code = r'''
import skynet_config as cfg

secret = {"API_ID", "API_HASH", "MEXC_API_KEY", "MEXC_API_SECRET", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"}

names = [n for n in dir(cfg) if n.isupper()]
for n in sorted(names):
    try:
        v = getattr(cfg, n)
    except Exception as e:
        print(f"{n}=<ERROR {e}>")
        continue
    if n in secret or any(x in n for x in ["SECRET", "TOKEN", "HASH", "API_KEY"]):
        print(f"{n}=<hidden> exists={bool(v)}")
    else:
        print(f"{n}={repr(v)}")
'''
    return run(f'{ROOT}/.venv/bin/python - <<\'PY\'\n{code}\nPY', timeout=30)

def sqlite_summary_one(db: Path) -> str:
    out = []
    out.append(f"DB: {db}")
    out.append(f"size_mb={db.stat().st_size / 1024 / 1024:.2f}")

    try:
        con = sqlite3.connect(str(db))
        con.row_factory = sqlite3.Row
    except Exception as e:
        out.append(f"connect_error={type(e).__name__}: {e}")
        return "\n".join(out) + "\n"

    try:
        tables = [
            r["name"]
            for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
    except Exception as e:
        out.append(f"tables_error={type(e).__name__}: {e}")
        return "\n".join(out) + "\n"

    out.append("tables=" + ", ".join(tables))

    for t in tables:
        try:
            n = con.execute(f'SELECT COUNT(*) AS n FROM "{t}"').fetchone()["n"]
            out.append(f"table {t}: rows={n}")

            cols = [r["name"] for r in con.execute(f'PRAGMA table_info("{t}")').fetchall()]
            out.append(f"  cols={', '.join(cols[:40])}")

            # known-ish useful numeric stats
            interesting = [
                "long_net_5m", "short_net_5m", "max_up_5m", "max_down_5m", "close_5m",
                "mfe", "mae", "pnl", "net", "spread_bps", "price_change", "vol_ratio",
                "oi_change", "current_turnover_rank",
            ]
            for c in interesting:
                if c in cols:
                    row = con.execute(
                        f'SELECT COUNT("{c}") n, AVG("{c}") avg, MIN("{c}") minv, MAX("{c}") maxv FROM "{t}"'
                    ).fetchone()
                    out.append(
                        f"  stat {c}: n={row['n']} avg={row['avg']} min={row['minv']} max={row['maxv']}"
                    )

            # sample recent rows without huge dump
            time_col = None
            for c in ["time_iso", "created_at", "ts", "timestamp", "opened_at", "closed_at"]:
                if c in cols:
                    time_col = c
                    break
            if time_col:
                sample_cols = [c for c in cols if c in [
                    "clean_symbol", "symbol", "strategy", "side", "time_iso",
                    "price_change", "vol_ratio", "oi_change", "spread_bps",
                    "max_up_5m", "max_down_5m", "close_5m", "long_net_5m", "short_net_5m",
                    "exit_reason", "pnl", "net"
                ]]
                if sample_cols:
                    sel = ", ".join(f'"{c}"' for c in sample_cols[:12])
                    rows = con.execute(
                        f'SELECT {sel} FROM "{t}" ORDER BY "{time_col}" DESC LIMIT 10'
                    ).fetchall()
                    out.append("  recent_sample:")
                    for r in rows:
                        out.append("    " + str(dict(r)))

        except Exception as e:
            out.append(f"table {t}: error={type(e).__name__}: {e}")

    try:
        con.close()
    except Exception:
        pass

    return "\n".join(out) + "\n"

def sqlite_summary() -> str:
    out = []
    if not DATA_DIR.exists():
        return "data dir not found\n"

    dbs = sorted(DATA_DIR.glob("*.sqlite3")) + sorted(DATA_DIR.glob("*.db")) + sorted(DATA_DIR.glob("*.sqlite"))
    if not dbs:
        return "no sqlite dbs found in data/\n"

    for db in dbs:
        out.append(sqlite_summary_one(db))
        out.append("-" * 80)

    return "\n".join(out)

def tracked_code_scan() -> str:
    out = []
    out.append("BAD TRACKED FILES:")
    out.append(run(r'''git ls-files | grep -E '(^|/)(\.env$|data/|archive/|safe_exports/|.*\.session.*|.*\.log|.*\.txt|.*\.zip|.*\.db|.*\.sqlite|.*\.sqlite3|.*\.bak|real_smoke_open_close\.py)' || true'''))

    out.append("\nSECRET-LIKE CHECK:")
    cmd = r'''
git ls-files | grep -v "^skynet_context_pack.py$" | while read f; do
  [ -f "$f" ] || continue
  grep -nE "MEXC_API_KEY=.+|MEXC_API_SECRET=.+|TELEGRAM_BOT_TOKEN=.+|TELEGRAM_CHAT_ID=.+|API_HASH=.+|PRIVATE_KEY=.+|SECRET_KEY=.+" "$f" && echo "FOUND_IN: $f"
done || true
'''
    out.append(run(cmd))
    return "\n".join(out)

def should_add_code_file(path: Path) -> bool:
    s = "/" + str(path.relative_to(ROOT))
    if any(part in s for part in BAD_PATH_PARTS):
        return False
    if path.name == ".env" or path.name.startswith(".env."):
        return False
    if any(path.name.endswith(x) for x in BAD_SUFFIXES):
        return False
    return True

def build_pack(send: bool = False, target: str | None = None) -> Path:
    ts = now_stamp()
    pack_dir = OUT_ROOT / f"skynet_context_{ts}"
    report_dir = pack_dir / "reports"
    code_dir = pack_dir / "code"
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    pack_dir.mkdir(parents=True, exist_ok=True)

    write(report_dir / "00_PROJECT_STATE.md", f"""# SKYNET context pack

Generated UTC: {ts}

Current intent:
- personal MEXC futures scalping bot;
- real trading is still disabled;
- current mode: dry-live / shadow / research;
- goal for next 2-3 weeks: find robust positive edge before vacation;
- do not rely on old ChatGPT context, use this pack.

Current architecture:
- skynet_config.py: config and strategy params
- skynet_engine.py: dry-live/shadow engine, entries/exits, guards, passport
- skynet_main.py: runtime loop, MEXC scan, Telegram reports
- skynet_live_mexc.py: experimental MEXC real adapter
- analyze_*.py: analysis scripts
- replay_*.py: replay recorded signals with new filters
- backtest_*.py: archive/grid/historical tests
- recorder.py, v17_micro_recorder.py, v18_path_recorder.py: data collection
""")

    write(report_dir / "01_git.txt", "\n".join([
        "=== git log ===",
        run("git log --oneline --decorate --max-count=20"),
        "=== git status ===",
        run("git status --short"),
        "=== git remote ===",
        run("git remote -v"),
        "=== tracked files ===",
        run("git ls-files"),
        "=== tracked code scan ===",
        tracked_code_scan(),
    ]))

    write(report_dir / "02_service_and_journal.txt", "\n".join([
        "=== systemctl status ===",
        run("systemctl status skynet.service --no-pager -l", timeout=10),
        "=== journal last 350 ===",
        run("journalctl -u skynet.service -n 350 --no-pager -l", timeout=20),
    ]))

    write(report_dir / "03_env_keys_only.txt", env_keys_report())
    write(report_dir / "04_config_snapshot.txt", config_snapshot())

    write(report_dir / "05_data_inventory.txt", "\n".join([
        "=== df -h ===",
        run("df -h"),
        "=== du root ===",
        run("du -h --max-depth=2 /root/skynet | sort -hr | head -150"),
        "=== biggest data files ===",
        run("find /root/skynet/data -type f -printf '%s %p\\n' 2>/dev/null | sort -nr | head -100 | awk '{printf \"%.2f MB  %s\\n\", $1/1024/1024, $2}'"),
        "=== safe exports ===",
        run("find /root/skynet/safe_exports -maxdepth 2 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\\n' 2>/dev/null | sort -r | head -100"),
    ]))

    write(report_dir / "06_sqlite_summary.txt", sqlite_summary())

    write(report_dir / "07_recent_analysis_outputs.txt", "\n".join([
        "=== root txt ignored reports ===",
        run("find /root/skynet -maxdepth 1 -type f -name '*.txt' -printf '%TY-%Tm-%Td %TH:%TM %s %p\\n' | sort -r | head -80"),
        "=== recent report previews ===",
        run("for f in $(find /root/skynet -maxdepth 1 -type f -name '*.txt' | sort | tail -10); do echo '---' $f; tail -80 \"$f\"; done", timeout=20),
    ]))

    write(report_dir / "08_code_compile_check.txt", run(f"{ROOT}/.venv/bin/python -m py_compile skynet_config.py skynet_engine.py skynet_main.py skynet_live_mexc.py skynet_lab_report.py research_fade_lab.py research_fade_shadow.py research_fade_live_report.py offline_edge_hunter.py high_freq_opportunity_lab.py false_negative_filter_lab.py dynamic_filter_intelligence_lab.py fee_intelligence_lab.py depth_thin_escape_lab.py", timeout=30))

    write(report_dir / "09_lab_report.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/skynet_lab_report.py --stdout", timeout=40))

    write(report_dir / "10_research_fade_lab.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/research_fade_lab.py --stdout", timeout=60))

    write(report_dir / "11_research_fade_live_report.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/research_fade_live_report.py --stdout", timeout=20))

    write(report_dir / "12_offline_edge_hunter.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/offline_edge_hunter.py --stdout", timeout=180))

    write(report_dir / "13_false_negative_filter_lab.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/false_negative_filter_lab.py", timeout=60))

    write(report_dir / "14_high_freq_opportunity_lab.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/high_freq_opportunity_lab.py", timeout=60))

    write(report_dir / "15_dynamic_filter_intelligence_lab.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/dynamic_filter_intelligence_lab.py fee_intelligence_lab.py", timeout=60))

    write(report_dir / "15_depth_thin_escape_lab.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/depth_thin_escape_lab.py", timeout=60))

    write(report_dir / "16_fee_intelligence_lab.txt", run(f"{ROOT}/.venv/bin/python {ROOT}/fee_intelligence_lab.py", timeout=60))

    # copy tracked code files
    tracked = run("git ls-files").splitlines()
    for rel in tracked:
        src = ROOT / rel
        if src.exists() and src.is_file() and should_add_code_file(src):
            dst = code_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            content = src.read_text(errors="ignore")
            dst.write_text(redact(content), encoding="utf-8", errors="ignore")

    archive_path = OUT_ROOT / f"skynet_context_{ts}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(pack_dir, arcname=pack_dir.name)

    # cleanup folder, keep tar only
    subprocess.run(f"rm -rf {pack_dir}", shell=True)

    print(f"CONTEXT_PACK={archive_path}")
    print(f"SIZE={archive_path.stat().st_size / 1024:.1f} KB")

    if send:
        send_to_telegram(archive_path, target)

    return archive_path

def send_to_telegram(path: Path, target: str | None):
    # Uses existing Telethon credentials/session.
    sys.path.insert(0, str(ROOT))
    import skynet_config as cfg
    from telethon.sync import TelegramClient

    api_id = int(getattr(cfg, "API_ID", 0) or 0)
    api_hash = getattr(cfg, "API_HASH", "") or ""
    if not api_id or not api_hash:
        raise RuntimeError("API_ID/API_HASH missing; cannot send via Telethon")

    target = target or os.getenv("TG_TARGET") or getattr(cfg, "TG_TARGET", None) or "me"
    
    # Separate Telethon session for context exports.
    # Do not use the runtime volume_session, otherwise sqlite session may lock
    # when skynet.service is running.
    session = str(ROOT / "context_pack_session")

    caption = f"SKYNET context pack {path.name}"
    print(f"SENDING_TO={target}")
    with TelegramClient(session, api_id, api_hash) as client:
        client.send_file(target, str(path), caption=caption)
    print("TELEGRAM_SEND=OK")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true", help="send archive to Telegram via Telethon")
    ap.add_argument("--target", default=None, help="Telegram target: me, @channel, or chat id")
    args = ap.parse_args()
    build_pack(send=args.send, target=args.target)

if __name__ == "__main__":
    main()
