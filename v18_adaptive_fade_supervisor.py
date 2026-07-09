#!/usr/bin/env python3
import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT = Path("/root/skynet")
ENV = ROOT / ".env"
LOG = ROOT / "v18_fade_db_shadow.log"
ACTIVE_PROFILE = ROOT / "v18_active_fade_profile.json"
REPORT = ROOT / "v18_adaptive_fade_supervisor_latest.txt"

HARD_SAFETY = {
    "REAL_TRADING_ENABLED": "false",
    "REAL_TRADING_ARMED": "false",
    "LIVE_DRY_RUN": "true",
    "CLEAN_CORE_ONLY": "true",
    "RESEARCH_FADE_V1_ENABLED": "false",
}

DEFAULT_MIN_NEW_CLOSES_BEFORE_ADAPT = 20

OPEN_RE = re.compile(
    r"\[(?P<ts>.*?) UTC\] V18_FADE_DB_OPEN .*? SHORT \| (?P<sym>[A-Z0-9]+) \| "
    r"entry=(?P<entry>[0-9.]+) signal_id=(?P<sid>[0-9]+) "
    r"pc=\+(?P<pc>[0-9.]+)% vol=x(?P<vol>[0-9.]+) spread=(?P<spread>[0-9.]+)bps rank=(?P<rank>[0-9]+)"
)

CLOSE_RE = re.compile(
    r"\[(?P<ts>.*?) UTC\] V18_FADE_DB_CLOSE .*? SHORT \| (?P<sym>[A-Z0-9]+) \| (?P<reason>TP|SL|TIME) \| "
    r"entry=(?P<entry>[0-9.]+) exit=(?P<exit>[0-9.]+) move=(?P<move>[+-]?[0-9.]+)% "
    r"gross=\$(?P<gross>[+-]?[0-9.]+) net=\$(?P<net>[+-]?[0-9.]+) cost=\$(?P<cost>[0-9.]+) "
    r"age=(?P<age>[0-9.]+)s signal_id=(?P<sid>[0-9]+)"
)

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def read_env() -> dict:
    data = {}
    if not ENV.exists():
        return data
    for line in ENV.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        data[k.strip()] = v.strip()
    return data

def write_env(updates: dict) -> bool:
    old = read_env()
    changed = any(str(old.get(k, "")) != str(v) for k, v in updates.items())
    if not changed:
        return False

    lines = ENV.read_text(errors="ignore").splitlines() if ENV.exists() else []
    seen = set()
    out = []

    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            k = line.split("=", 1)[0].strip()
            if k in updates:
                out.append(f"{k}={updates[k]}")
                seen.add(k)
            else:
                out.append(line)
        else:
            out.append(line)

    for k, v in updates.items():
        if k not in seen:
            out.append(f"{k}={v}")

    ENV.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.chmod(ENV, 0o600)
    return True

def load_active_profile() -> dict:
    if not ACTIVE_PROFILE.exists():
        raise FileNotFoundError(f"missing active profile: {ACTIVE_PROFILE}")
    profile = json.loads(ACTIVE_PROFILE.read_text(encoding="utf-8"))
    if "env" not in profile or not isinstance(profile["env"], dict):
        raise ValueError("active profile must contain object field: env")
    return profile

def restart_fade_service() -> None:
    subprocess.run(["systemctl", "restart", "skynet-v18-fade-db-shadow.service"], check=False)

def pc_bucket(pc: float) -> str:
    if pc < 0.50:
        return "pc_030_050"
    if pc < 0.80:
        return "pc_050_080"
    if pc < 1.20:
        return "pc_080_120"
    return "pc_120_plus"

def parse_current_log():
    if not LOG.exists():
        return []

    opens = {}
    rows = []

    for line in LOG.read_text(errors="ignore").splitlines():
        mo = OPEN_RE.search(line)
        if mo:
            sid = mo.group("sid")
            opens[sid] = {
                "sym": mo.group("sym").upper(),
                "pc": float(mo.group("pc")),
                "vol": float(mo.group("vol")),
                "spread": float(mo.group("spread")),
                "rank": int(mo.group("rank")),
                "line": line,
            }
            continue

        mc = CLOSE_RE.search(line)
        if mc:
            sid = mc.group("sid")
            op = opens.get(sid)
            if not op:
                continue
            row = dict(op)
            row.update({
                "reason": mc.group("reason"),
                "net": float(mc.group("net")),
                "gross": float(mc.group("gross")),
                "cost": float(mc.group("cost")),
                "move": float(mc.group("move")),
                "age": float(mc.group("age")),
                "bucket": pc_bucket(float(op["pc"])),
                "line": line,
            })
            rows.append(row)

    return rows

def pf(values):
    gp = sum(x for x in values if x > 0)
    gl = -sum(x for x in values if x < 0)
    if gl == 0 and gp > 0:
        return 999.0
    if gl == 0:
        return 0.0
    return gp / gl

def summarize(rows):
    vals = [r["net"] for r in rows]
    if not vals:
        return {"n": 0, "net": 0.0, "avg": 0.0, "pf": 0.0, "wr": 0.0, "sl": 0, "time": 0, "tp": 0, "cost": 0.0}
    n = len(vals)
    return {
        "n": n,
        "net": sum(vals),
        "avg": sum(vals) / n,
        "pf": pf(vals),
        "wr": 100.0 * sum(1 for x in vals if x > 0) / n,
        "sl": sum(1 for r in rows if r["reason"] == "SL"),
        "time": sum(1 for r in rows if r["reason"] == "TIME"),
        "tp": sum(1 for r in rows if r["reason"] == "TP"),
        "cost": sum(r["cost"] for r in rows),
    }

def maybe_adapt_profile(profile: dict, rows: list):
    """
    Conservative rule:
    - If fewer than MIN_NEW_CLOSES, do NOT change active profile.
    - If enough rows but forward stats are bad, tighten only inside active profile:
      rank<=30 stays, real stays OFF, blacklist can expand by toxic symbols.
    - Never falls back to hardcoded pc<=0.8/rank<=50 defaults.
    """
    min_n = int(profile.get("min_new_closes_before_adapt", DEFAULT_MIN_NEW_CLOSES_BEFORE_ADAPT))
    if len(rows) < min_n:
        return profile, "NO_ADAPT_NOT_ENOUGH_NEW_CLOSES"

    s = summarize(rows)
    new_profile = json.loads(json.dumps(profile))
    env = dict(new_profile["env"])

    by_sym = defaultdict(list)
    for r in rows:
        by_sym[r["sym"]].append(r)

    current_bl = set(x.strip().upper() for x in env.get("V18_FADE_DB_BLACKLIST", "").replace(";", ",").split(",") if x.strip())

    added = []
    for sym, rs in by_sym.items():
        ss = summarize(rs)
        fast_sl = sum(1 for r in rs if r["reason"] == "SL" and r["age"] <= 90)
        if ss["n"] >= 2 and ss["net"] < 0 and (ss["sl"] >= 2 or fast_sl >= 1):
            if sym not in current_bl:
                current_bl.add(sym)
                added.append(sym)

    if added:
        env["V18_FADE_DB_BLACKLIST"] = ",".join(sorted(current_bl))
        new_profile["env"] = env
        new_profile["updated_utc"] = utc_now()
        new_profile["reason"] = (
            str(new_profile.get("reason", "")) +
            f" | adaptive added blacklist symbols after forward shadow: {','.join(sorted(added))}"
        )
        ACTIVE_PROFILE.write_text(json.dumps(new_profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return new_profile, "ADAPT_BLACKLIST_EXPANDED"

    if s["net"] <= 0 or s["pf"] < 1.15:
        return profile, "FORWARD_BAD_BUT_NO_SAFE_ADAPT_FOUND"

    return profile, "FORWARD_OK_KEEP_PROFILE"

def main():
    lines = []
    changed = False
    restarted = False

    try:
        profile = load_active_profile()
        rows = parse_current_log()

        profile, decision = maybe_adapt_profile(profile, rows)

        desired_env = {}
        desired_env.update(profile.get("env", {}))
        desired_env.update(HARD_SAFETY)

        changed = write_env(desired_env)

        if changed:
            restart_fade_service()
            restarted = True

        s = summarize(rows)

        by_sym = defaultdict(list)
        by_bucket = defaultdict(list)
        for r in rows:
            by_sym[r["sym"]].append(r)
            by_bucket[r["bucket"]].append(r)

        lines.append("=" * 100)
        lines.append(f"V18 ADAPTIVE FADE SUPERVISOR UTC={utc_now()}")
        lines.append("=" * 100)
        lines.append(f"profile_name={profile.get('profile_name', '-')}")
        lines.append(f"active_profile={ACTIVE_PROFILE}")
        lines.append(f"events_parsed={len(rows)}")
        lines.append(f"decision={decision}")
        lines.append(f"env_changed={changed}")
        lines.append(f"service_restarted={restarted}")
        lines.append("")
        lines.append("TOTAL CURRENT LOG, NET AFTER COMMISSION:")
        lines.append(
            f"n={s['n']} net=${s['net']:+.4f} avg=${s['avg']:+.5f} WR={s['wr']:.1f}% "
            f"PF={s['pf']:.2f} SL={s['sl']} TIME={s['time']} TP={s['tp']} cost=${s['cost']:.4f}"
        )
        lines.append("")
        lines.append("APPLIED ENV:")
        for k in sorted(desired_env):
            lines.append(f"{k}={desired_env[k]}")
        lines.append("")
        lines.append("SYMBOL STATS:")
        for sym, rs in sorted(by_sym.items(), key=lambda kv: summarize(kv[1])["net"]):
            ss = summarize(rs)
            lines.append(
                f"{sym:12s} n={ss['n']:3d} net={ss['net']:+.4f} avg={ss['avg']:+.5f} "
                f"PF={ss['pf']:.2f} SL={ss['sl']} TIME={ss['time']} TP={ss['tp']}"
            )
        lines.append("")
        lines.append("BUCKET STATS:")
        for b, rs in sorted(by_bucket.items()):
            bs = summarize(rs)
            lines.append(
                f"{b:14s} n={bs['n']:3d} net={bs['net']:+.4f} avg={bs['avg']:+.5f} "
                f"PF={bs['pf']:.2f} SL={bs['sl']} TIME={bs['time']} TP={bs['tp']}"
            )
        lines.append("")
        lines.append("REAL_TRADING remains OFF by hard safety.")

    except Exception as e:
        lines.append("=" * 100)
        lines.append(f"V18 ADAPTIVE FADE SUPERVISOR FAILED UTC={utc_now()}")
        lines.append("=" * 100)
        lines.append(f"ERROR={type(e).__name__}: {e}")
        lines.append("No env write attempted after failure.")

    text = "\n".join(lines)
    REPORT.write_text(text + "\n", encoding="utf-8")
    print(text)

if __name__ == "__main__":
    main()
