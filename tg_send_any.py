#!/usr/bin/env python3
import os
import sys
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
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv(ROOT / ".env")

sys.path.insert(0, str(ROOT))

import skynet_config as cfg
from telethon.sync import TelegramClient


def get_value(*names, default=None):
    for name in names:
        val = os.getenv(name)
        if val not in (None, ""):
            return val
    for name in names:
        if hasattr(cfg, name):
            val = getattr(cfg, name)
            if val not in (None, ""):
                return val
    return default


def main():
    if len(sys.argv) < 2:
        print("usage: tg_send_any.py /path/to/file [caption] [target]")
        raise SystemExit(2)

    path = Path(sys.argv[1])
    caption = sys.argv[2] if len(sys.argv) >= 3 else f"SKYNET file {path.name}"
    target = sys.argv[3] if len(sys.argv) >= 4 else None

    api_id = int(get_value("API_ID", default=0) or 0)
    api_hash = str(get_value("API_HASH", default="") or "")
    target = target or get_value("TG_TARGET", default=None) or "me"

    print("api_id_found:", bool(api_id))
    print("api_hash_found:", bool(api_hash))
    print("target:", target)
    print("file:", path)
    print("exists:", path.exists())
    print("size:", path.stat().st_size if path.exists() else None)

    if not api_id or not api_hash:
        print("ERROR: API_ID/API_HASH missing")
        raise SystemExit(3)

    if not path.exists():
        print("ERROR: file not found")
        raise SystemExit(4)

    # отдельная session, как в context_pack, чтобы не конфликтовать с ботом
    session = str(ROOT / "context_pack_session")

    with TelegramClient(session, api_id, api_hash) as client:
        client.send_file(target, str(path), caption=caption)

    print("TELETHON_SEND=OK")


if __name__ == "__main__":
    main()
