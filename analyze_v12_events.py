import csv
from collections import Counter, defaultdict
from pathlib import Path

PATH = Path("/root/skynet/data/v12_market_events.csv")
LOG = Path("/root/skynet/skynet_48h.log")

def sf(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default

def si(x, default=0):
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default

rows = []
if PATH.exists():
    with PATH.open("r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)

print("=== V12 MARKET EVENTS ===")
print("file:", PATH)
print("rows:", len(rows))

if not rows:
    raise SystemExit("NO_ROWS")

def flag_meta_like(r):
    score = si(r.get("score"))
    pc = sf(r.get("price_change"))
    vol = sf(r.get("vol_ratio"))
    trend = sf(r.get("trend_15m"))
    btc = sf(r.get("btc_5m_change"))
    oi = sf(r.get("oi_change"))
    spread = sf(r.get("spread_bps"), 999)
    struct = si(r.get("structure_risk"), 999)
    br = si(r.get("breakout_risk_score"), 999)
    fb = si(r.get("false_breakouts_15m"), 999)
    init = si(r.get("initiative"), 0)
    meta = r.get("meta_sources_v12", "")

    return (
        score >= 4
        and 0.20 <= pc <= 0.65
        and vol <= 35
        and trend >= 0.30
        and btc >= -0.10
        and oi >= -0.50
        and spread <= 5
        and struct <= 2
        and br <= 3
        and fb <= 1
        and init == 1
        and bool(meta)
    )

def flag_micro_lite(r):
    score = si(r.get("score"))
    pc = sf(r.get("price_change"))
    vol = sf(r.get("vol_ratio"))
    trend = sf(r.get("trend_15m"))
    btc = sf(r.get("btc_5m_change"))
    oi = sf(r.get("oi_change"))
    spread = sf(r.get("spread_bps"), 999)
    struct = si(r.get("structure_risk"), 999)
    br = si(r.get("breakout_risk_score"), 999)
    fb = si(r.get("false_breakouts_15m"), 999)
    init = si(r.get("initiative"), 0)

    # DOGE-like: low spread, depth-ok implied if spread exists, lower score allowed.
    return (
        score >= 4
        and 0.20 <= pc <= 0.55
        and vol <= 35
        and trend >= 0.20
        and btc >= -0.10
        and oi >= -0.50
        and spread <= 2.0
        and struct <= 1
        and br <= 5
        and fb <= 2
        and init == 1
    )

meta_like = [r for r in rows if flag_meta_like(r)]
lite_like = [r for r in rows if flag_micro_lite(r)]

print()
print("=== COUNTS ===")
print("meta_like:", len(meta_like))
print("micro_lite_like:", len(lite_like))

print()
print("=== TOP SYMBOLS all ===")
print(Counter(r.get("symbol") for r in rows).most_common(20))

print()
print("=== TOP SYMBOLS meta_like ===")
print(Counter(r.get("symbol") for r in meta_like).most_common(20))

print()
print("=== TOP SYMBOLS micro_lite_like ===")
print(Counter(r.get("symbol") for r in lite_like).most_common(20))

def show(title, arr, n=30):
    print()
    print(title)
    arr = sorted(
        arr,
        key=lambda r: (
            si(r.get("score")),
            sf(r.get("trend_15m")),
            -sf(r.get("spread_bps"), 999),
            -si(r.get("breakout_risk_score"), 999),
        ),
        reverse=True
    )
    for r in arr[:n]:
        print(
            f"{r.get('ts','')} {r.get('symbol','')} "
            f"score={r.get('score')} pc={sf(r.get('price_change')):.2f}% "
            f"vol=x{sf(r.get('vol_ratio')):.1f} trend={sf(r.get('trend_15m')):.2f}% "
            f"btc={sf(r.get('btc_5m_change')):.2f}% oi={sf(r.get('oi_change')):.2f}% "
            f"spread={sf(r.get('spread_bps'),999):.2f} "
            f"struct={r.get('structure_risk')} br={r.get('breakout_risk_score')} fb={r.get('false_breakouts_15m')} "
            f"rank={r.get('current_turnover_rank')} init={r.get('initiative')} meta={r.get('meta_sources_v12')}"
        )

show("=== META-LIKE CANDIDATES ===", meta_like)
show("=== MICRO-LITE CANDIDATES ===", lite_like)

print()
print("=== LOG REAL/META EVENTS ===")
if LOG.exists():
    keys = ("REAL_MICRO", "DRY_LIVE_OPEN", "DRY_LIVE_CLOSE", "CONFIRM_OPEN", "CONFIRM_DROP", "META_V12_EXEC_SAFE_MO1", "LOOP_EXCEPTION", "Traceback")
    hits = []
    with LOG.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if any(k in line for k in keys):
                hits.append(line.rstrip())
    for line in hits[-120:]:
        print(line)
    print("log_hits:", len(hits))
else:
    print("no log:", LOG)
