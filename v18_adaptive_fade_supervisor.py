#!/usr/bin/env python3
import os
import re
import json
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
ENV = ROOT / ".env"
LOG = ROOT / "v18_fade_db_shadow.log"
STATE = ROOT / "v18_adaptive_fade_supervisor_state.json"
REPORT = ROOT / "v18_adaptive_fade_supervisor_latest.txt"

BASE_BLACKLIST = {"ALLO", "XPL", "TAC", "SOXL"}
LOOKBACK_HOURS = 48

# стартовый режим: НЕ широкий, но и не вечный тупик
SAFE_PC_MIN = "0.30"
SAFE_PC_MAX = "0.80"

# жестко запрещаем то, что уже доказало токсичность
HARD_PC_MAX_FOR_NOW = 0.80

def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def read_env():
    d = {}
    if ENV.exists():
        for line in ENV.read_text(errors="ignore").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    return d

def write_env(upd):
    lines = ENV.read_text(errors="ignore").splitlines() if ENV.exists() else []
    seen = set()
    out = []
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            k = line.split("=", 1)[0].strip()
            if k in upd:
                out.append(f"{k}={upd[k]}")
                seen.add(k)
            else:
                out.append(line)
        else:
            out.append(line)
    for k, v in upd.items():
        if k not in seen:
            out.append(f"{k}={v}")
    ENV.write_text("\n".join(out) + "\n")
    os.chmod(ENV, 0o600)

def pc_bucket(pc):
    if pc < 0.50:
        return "pc_030_050"
    if pc < 0.80:
        return "pc_050_080"
    if pc < 1.20:
        return "pc_080_120"
    return "pc_120_plus"

pat_close = re.compile(
    r"\[(?P<ts>.*?) UTC\] V18_FADE_DB_CLOSE .*? SHORT \| (?P<sym>[A-Z0-9]+) \| (?P<reason>SL|TP|TIME) \| .*? move=(?P<move>[+-]?[0-9.]+)% .*? net=\$(?P<net>[+-]?[0-9.]+).*? age=(?P<age>[0-9.]+)s"
)

pat_open = re.compile(
    r"\[(?P<ts>.*?) UTC\] V18_FADE_DB_OPEN .*? SHORT \| (?P<sym>[A-Z0-9]+) \| .*? pc=(?P<pc>[+-]?[0-9.]+)% .*? vol=x(?P<vol>[0-9.]+).*? spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>[0-9]+)"
)

def parse_events():
    if not LOG.exists():
        return [], {}

    lines = LOG.read_text(errors="ignore").splitlines()
    opens_by_sym = {}
    closes = []

    for line in lines:
        mo = pat_open.search(line)
        if mo:
            sym = mo.group("sym").upper()
            opens_by_sym.setdefault(sym, [])
            opens_by_sym[sym].append({
                "pc": float(mo.group("pc")),
                "vol": float(mo.group("vol")),
                "spread": float(mo.group("spread")),
                "rank": int(mo.group("rank")),
                "line": line,
            })
            continue

        mc = pat_close.search(line)
        if mc:
            sym = mc.group("sym").upper()
            last_open = opens_by_sym.get(sym, [{}])[-1]
            pc = float(last_open.get("pc", 999.0))
            closes.append({
                "sym": sym,
                "reason": mc.group("reason"),
                "net": float(mc.group("net")),
                "move": float(mc.group("move")),
                "age": float(mc.group("age")),
                "pc": pc,
                "bucket": pc_bucket(pc),
                "line": line,
            })

    return closes, opens_by_sym

def main():
    env = read_env()
    closes, _ = parse_events()

    # Берём последние события из текущего лога. Если лог reset — ок, значит supervisor начнёт с чистой статы.
    recent = closes[-80:]

    sym_stats = {}
    bucket_stats = {}

    for e in recent:
        s = sym_stats.setdefault(e["sym"], {"n": 0, "sl": 0, "net": 0.0, "fast_sl": 0})
        s["n"] += 1
        s["net"] += e["net"]
        if e["reason"] == "SL":
            s["sl"] += 1
            if e["age"] <= 90:
                s["fast_sl"] += 1

        b = bucket_stats.setdefault(e["bucket"], {"n": 0, "sl": 0, "net": 0.0})
        b["n"] += 1
        b["net"] += e["net"]
        if e["reason"] == "SL":
            b["sl"] += 1

    dynamic_blacklist = set(BASE_BLACKLIST)

    # Баним монеты, которые уже показали токсичность в этом shadow-логе
    for sym, st in sym_stats.items():
        if st["sl"] >= 2:
            dynamic_blacklist.add(sym)
        if st["fast_sl"] >= 1 and st["net"] < 0:
            dynamic_blacklist.add(sym)

    # pc>=1.2 прямо запрещён сейчас, потому что он убил широкий тест
    pc_max = SAFE_PC_MAX

    # Если даже pc_050_080 в текущем логе опять токсичный — сужаем до 0.50
    b5080 = bucket_stats.get("pc_050_080")
    if b5080 and b5080["n"] >= 4 and b5080["net"] < 0 and b5080["sl"] >= 2:
        pc_max = "0.50"

    upd = {
        "REAL_TRADING_ENABLED": "false",
        "REAL_TRADING_ARMED": "false",
        "LIVE_DRY_RUN": "true",
        "CLEAN_CORE_ONLY": "true",
        "RESEARCH_FADE_V1_ENABLED": "false",

        "V18_FADE_DB_PC_MIN": SAFE_PC_MIN,
        "V18_FADE_DB_PC_MAX": pc_max,
        "V18_FADE_DB_VOL_MIN": "12.0",
        "V18_FADE_DB_SPREAD_MAX": "2.0",
        "V18_FADE_DB_RANK_MAX": "50",
        "V18_FADE_DB_MAX_OPEN_TOTAL": "1",
        "V18_FADE_DB_BLACKLIST": ",".join(sorted(dynamic_blacklist)),
        "V18_FADE_DB_AUTO_BAN_AFTER_SL": "1",
    }

    before = {k: env.get(k) for k in upd}
    changed = any(str(before.get(k)) != str(v) for k, v in upd.items())

    write_env(upd)

    lines = []
    lines.append("=" * 100)
    lines.append(f"V18 ADAPTIVE FADE SUPERVISOR UTC={utc()}")
    lines.append("=" * 100)
    lines.append(f"events_parsed={len(closes)} recent_used={len(recent)}")
    lines.append(f"changed={changed}")
    lines.append("")
    lines.append("APPLIED ENV:")
    for k in sorted(upd):
        lines.append(f"{k}={upd[k]}")
    lines.append("")
    lines.append("SYMBOL STATS:")
    for sym, st in sorted(sym_stats.items(), key=lambda x: x[1]['net']):
        lines.append(f"{sym:12s} n={st['n']:3d} sl={st['sl']:3d} fast_sl={st['fast_sl']:3d} net={st['net']:+.4f}")
    lines.append("")
    lines.append("BUCKET STATS:")
    for b, st in sorted(bucket_stats.items()):
        lines.append(f"{b:14s} n={st['n']:3d} sl={st['sl']:3d} net={st['net']:+.4f}")
    lines.append("")
    lines.append("DECISION:")
    if len(recent) == 0:
        lines.append("No current closes in reset log yet. Adaptive layer armed; collecting.")
    else:
        lines.append("Adaptive blacklist/filter applied from recent shadow closes.")
    lines.append("Real trading remains OFF.")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

    if changed:
        os.system("systemctl restart skynet-v18-fade-db-shadow.service")

if __name__ == "__main__":
    main()
