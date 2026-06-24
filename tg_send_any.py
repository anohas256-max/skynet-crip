#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path("/root/skynet")
os.chdir(ROOT)


def load_dotenv():
    p = ROOT / ".env"
    if not p.exists():
        return
    for raw in p.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()


def cfg_get(names):
    try:
        import skynet_config as cfg
    except Exception:
        return ""

    for name in names:
        if hasattr(cfg, name):
            val = getattr(cfg, name)
            if val not in (None, "", False):
                return str(val)
    return ""


def env_get(names):
    for name in names:
        val = os.getenv(name)
        if val not in (None, ""):
            return str(val)
    return ""


TOKEN_NAMES = [
    "TG_BOT_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_TOKEN",
    "TG_TOKEN",
    "BOT_TOKEN",
    "TELEGRAM_API_TOKEN",
    "TG_API_TOKEN",
]

CHAT_NAMES = [
    "TG_TARGET",
    "TG_CHAT_ID",
    "TELEGRAM_CHAT_ID",
    "TELEGRAM_TARGET",
    "CHAT_ID",
    "TELEGRAM_CHANNEL_ID",
    "TG_CHANNEL_ID",
]

token = env_get(TOKEN_NAMES) or cfg_get(TOKEN_NAMES)
chat_id = env_get(CHAT_NAMES) or cfg_get(CHAT_NAMES)

# Fallback: some configs store names with lowercase or mixed names.
if not token or not chat_id:
    try:
        import skynet_config as cfg
        for k in dir(cfg):
            ku = k.upper()
            val = getattr(cfg, k, None)
            if not isinstance(val, (str, int)):
                continue
            sval = str(val)
            if not token and ("TOKEN" in ku) and ("TG" in ku or "TELEGRAM" in ku or "BOT" in ku):
                token = sval
            if not chat_id and ("CHAT" in ku or "TARGET" in ku or "CHANNEL" in ku) and ("TG" in ku or "TELEGRAM" in ku):
                chat_id = sval
    except Exception:
        pass

if len(sys.argv) < 2:
    print("usage: tg_send_any.py /path/to/file [caption]")
    sys.exit(2)

path = Path(sys.argv[1])
caption = sys.argv[2] if len(sys.argv) >= 3 else path.name

print("token_found:", bool(token))
print("chat_found:", bool(chat_id))
print("file:", path)
print("exists:", path.exists())
print("size:", path.stat().st_size if path.exists() else None)

if not token or not chat_id:
    print("ERROR: Telegram config not found by universal sender.")
    print("Checked token names:", ", ".join(TOKEN_NAMES))
    print("Checked chat names:", ", ".join(CHAT_NAMES))
    sys.exit(3)

if not path.exists():
    print("ERROR: file not found")
    sys.exit(4)


def send_message(text: str):
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        print("sendMessage:", r.read().decode(errors="ignore"))


def send_document(file_path: Path, caption: str):
    boundary = "----SKYNETBOUNDARYTGFILE"
    url = "https://api.telegram.org/bot" + token + "/sendDocument"

    body = bytearray()

    def add(s: str):
        body.extend(s.encode())

    add(f"--{boundary}\r\n")
    add('Content-Disposition: form-data; name="chat_id"\r\n\r\n')
    add(str(chat_id) + "\r\n")

    add(f"--{boundary}\r\n")
    add('Content-Disposition: form-data; name="caption"\r\n\r\n')
    add(caption + "\r\n")

    add(f"--{boundary}\r\n")
    add(f'Content-Disposition: form-data; name="document"; filename="{file_path.name}"\r\n')
    add("Content-Type: application/octet-stream\r\n\r\n")
    body.extend(file_path.read_bytes())
    add(f"\r\n--{boundary}--\r\n")

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        print("sendDocument:", r.read().decode(errors="ignore"))


send_message("📎 SKYNET file sender test: sending " + path.name)
time.sleep(0.5)
send_document(path, caption)
