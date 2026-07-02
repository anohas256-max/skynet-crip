#!/usr/bin/env python3
import asyncio
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone

import aiohttp

ROOT = Path("/root/skynet")
DB = ROOT / "data/v18_micro_paths.sqlite3"
STATE = ROOT / "v18_fade_db_shadow_state.json"
LOG = ROOT / "v18_fade_db_shadow.log"
REPORT = ROOT / "v18_fade_db_shadow_report_latest.txt"

PROFILE = "V18_DB_SHORT_PC030_SP3_R150_V5"
PC_MIN = float(os.getenv("V18_FADE_DB_PC_MIN", "0.30"))
VOL_MIN = float(os.getenv("V18_FADE_DB_VOL_MIN", "5.0"))
SPREAD_MAX = float(os.getenv("V18_FADE_DB_SPREAD_MAX", "3.0"))
RANK_MAX = int(float(os.getenv("V18_FADE_DB_RANK_MAX", "150")))
TP_PCT = float(os.getenv("V18_FADE_DB_TP_PCT", "3.0"))
SL_PCT = float(os.getenv("V18_FADE_DB_SL_PCT", "0.3"))
TTL_SECONDS = float(os.getenv("V18_FADE_DB_TTL_SECONDS", "300"))
COOLDOWN_SECONDS = float(os.getenv("V18_FADE_DB_COOLDOWN_SECONDS", "180"))
MAX_OPEN_TOTAL = int(float(os.getenv("V18_FADE_DB_MAX_OPEN_TOTAL", "3")))
POLL_SECONDS = float(os.getenv("V18_FADE_DB_POLL_SECONDS", "5"))
COST_PCT = float(os.getenv("V18_FADE_DB_COST_PCT", "0.03"))

MARGIN = float(os.getenv("V18_FADE_DB_MARGIN", "3.0"))
LEVERAGE = int(float(os.getenv("V18_FADE_DB_LEVERAGE", "4")))
NOTIONAL = MARGIN * LEVERAGE

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def log(line):
    s = f"[{now_iso()}] {line}"
    print(s, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(s + "\n")

def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {
        "last_id": None,
        "active": {},
        "last_open_by_symbol": {},
        "stats": {"opened": 0, "closed": 0, "wins": 0, "losses": 0, "net": 0.0, "gross": 0.0, "costs": 0.0},
    }

def save_state(st):
    tmp = STATE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=2))
    tmp.replace(STATE)

def db_connect():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=5)

def init_last_id(st):
    if st.get("last_id") is not None:
        return
    con = db_connect()
    try:
        row = con.execute("SELECT COALESCE(MAX(id), 0) FROM signals").fetchone()
        st["last_id"] = int(row[0] or 0)
        log(f"INIT | start_from_id={st['last_id']} db={DB}")
    finally:
        con.close()
    save_state(st)

def fetch_new_signals(last_id):
    con = db_connect()
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT id, time_iso, symbol, clean_symbol, entry_price, price_change, vol_ratio, spread_bps, rank
            FROM signals
            WHERE id > ?
            ORDER BY id ASC
            LIMIT 500
            """,
            (int(last_id),),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()

def passes(r):
    try:
        return (
            float(r.get("price_change") or 0) >= PC_MIN
            and float(r.get("vol_ratio") or 0) >= VOL_MIN
            and float(r.get("spread_bps") or 999) <= SPREAD_MAX
            and int(float(r.get("rank") or 999999)) <= RANK_MAX
            and float(r.get("entry_price") or 0) > 0
        )
    except Exception:
        return False

async def get_price(session, symbol):
    url = f"https://contract.mexc.com/api/v1/contract/ticker?symbol={symbol}"
    async with session.get(url, timeout=5) as res:
        data = await res.json()

    if not isinstance(data, dict):
        return 0.0

    d = data.get("data")
    if isinstance(d, list):
        d = d[0] if d else {}
    if not isinstance(d, dict):
        return 0.0

    try:
        return float(d.get("lastPrice") or d.get("last_price") or d.get("fairPrice") or 0)
    except Exception:
        return 0.0

def net_calc(short_profit_pct):
    gross = NOTIONAL * (short_profit_pct / 100.0)
    costs = NOTIONAL * (COST_PCT / 100.0)
    return gross, gross - costs, costs

def write_report(st):
    stats = st["stats"]
    active = st["active"]

    lines = []
    lines.append("=" * 100)
    lines.append(f"V18 FADE DB SHADOW REPORT UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 100)
    lines.append("source=/root/skynet/data/v18_micro_paths.sqlite3")
    lines.append("real_trading=OFF")
    lines.append(f"profile={PROFILE}")
    lines.append(f"rule=SHORT pc>={PC_MIN} vol>={VOL_MIN} spread<={SPREAD_MAX} rank<={RANK_MAX} TP={TP_PCT} SL={SL_PCT} TTL={TTL_SECONDS}s cost={COST_PCT}%")
    lines.append("")
    lines.append(
        f"opened={stats['opened']} closed={stats['closed']} active={len(active)} "
        f"wins={stats['wins']} losses={stats['losses']} "
        f"net=${stats['net']:+.4f} gross=${stats['gross']:+.4f} costs=${stats['costs']:.4f}"
    )
    lines.append("")
    lines.append("ACTIVE:")
    for k, w in active.items():
        age = time.time() - float(w["open_ts"])
        lines.append(
            f"  {k} entry={w['entry']:.8f} age={age:.0f}s "
            f"pc={w.get('pc',0):+.2f}% vol={w.get('vol',0):.1f} sp={w.get('spread',999):.2f} rank={w.get('rank',999999)}"
        )
    REPORT.write_text("\n".join(lines), encoding="utf-8")

async def main():
    st = load_state()
    init_last_id(st)

    log(
        f"START | {PROFILE} pc>={PC_MIN} vol>={VOL_MIN} spread<={SPREAD_MAX} rank<={RANK_MAX} "
        f"TP={TP_PCT} SL={SL_PCT} TTL={TTL_SECONDS}s cost={COST_PCT}% real=OFF"
    )

    last_report = 0.0

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                rows = fetch_new_signals(st["last_id"])
                for r in rows:
                    st["last_id"] = max(int(st["last_id"]), int(r["id"]))

                    if not passes(r):
                        continue

                    symbol = r["symbol"]
                    clean = r.get("clean_symbol") or symbol.replace("_USDT", "")
                    key = f"{PROFILE}:{symbol}"

                    if key in st["active"]:
                        continue

                    now = time.time()
                    last = float(st["last_open_by_symbol"].get(symbol, 0))
                    if now - last < COOLDOWN_SECONDS:
                        continue

                    if len(st["active"]) >= MAX_OPEN_TOTAL:
                        log(f"SKIP_MAX_OPEN | {clean} | active={len(st['active'])}")
                        continue

                    entry = float(r["entry_price"])
                    st["active"][key] = {
                        "symbol": symbol,
                        "clean": clean,
                        "entry": entry,
                        "open_ts": now,
                        "signal_id": int(r["id"]),
                        "pc": float(r.get("price_change") or 0),
                        "vol": float(r.get("vol_ratio") or 0),
                        "spread": float(r.get("spread_bps") or 999),
                        "rank": int(float(r.get("rank") or 999999)),
                    }
                    st["last_open_by_symbol"][symbol] = now
                    st["stats"]["opened"] += 1

                    log(
                        f"V18_FADE_DB_OPEN | {PROFILE} | SHORT | {clean} | "
                        f"entry={entry:.8f} signal_id={r['id']} "
                        f"pc={float(r.get('price_change') or 0):+.2f}% vol=x{float(r.get('vol_ratio') or 0):.1f} "
                        f"spread={float(r.get('spread_bps') or 999):.2f}bps rank={int(float(r.get('rank') or 999999))}"
                    )

                to_close = []
                for key, w in list(st["active"].items()):
                    price = await get_price(session, w["symbol"])
                    if price <= 0:
                        continue

                    entry = float(w["entry"])
                    short_profit_pct = ((entry - price) / entry) * 100.0
                    age = time.time() - float(w["open_ts"])

                    reason = None
                    if short_profit_pct <= -SL_PCT:
                        reason = "SL"
                    elif short_profit_pct >= TP_PCT:
                        reason = "TP"
                    elif age >= TTL_SECONDS:
                        reason = "TIME"

                    if not reason:
                        continue

                    gross, net, costs = net_calc(short_profit_pct)
                    st["stats"]["closed"] += 1
                    st["stats"]["gross"] += gross
                    st["stats"]["net"] += net
                    st["stats"]["costs"] += costs
                    if net > 0:
                        st["stats"]["wins"] += 1
                    else:
                        st["stats"]["losses"] += 1

                    log(
                        f"V18_FADE_DB_CLOSE | {PROFILE} | SHORT | {w['clean']} | {reason} | "
                        f"entry={entry:.8f} exit={price:.8f} move={short_profit_pct:+.3f}% "
                        f"gross=${gross:+.4f} net=${net:+.4f} cost=${costs:.4f} "
                        f"age={age:.0f}s signal_id={w.get('signal_id')}"
                    )
                    to_close.append(key)

                for key in to_close:
                    st["active"].pop(key, None)

                if time.time() - last_report >= 60:
                    write_report(st)
                    last_report = time.time()

                save_state(st)
                await asyncio.sleep(POLL_SECONDS)

            except Exception as e:
                log(f"LOOP_EXCEPTION | {type(e).__name__}: {e}")
                save_state(st)
                await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
