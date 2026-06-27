#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

ROOT = Path("/root/skynet")
LOGS = [ROOT / "skynet_3h.log", ROOT / "skynet_12h.log", ROOT / "skynet_48h.log"]
OUT = ROOT / "xpl_near_signature_lab_latest.txt"

GOOD = {"XPL", "NEAR"}
TOXIC = {"JUP", "ENA", "AAVE", "TIA", "INJ"}

cand_re = re.compile(
    r"\[(?P<t>[0-9:]+)\] (?P<sym>[A-Z0-9]+) \| Vol:x(?P<vol>[0-9.]+) \| Price:(?P<pc>[+-]?[0-9.]+)% \| "
    r"OI:(?P<oi>[+-]?[0-9.]+)% \| Trend15M:(?P<trend>[+-]?[0-9.]+)% \| BTC_5M:(?P<btc>[+-]?[0-9.]+)% \| "
    r"Score:(?P<score>[+-]?\d+) \| Struct:(?P<struct>\d+) \| BRisk:(?P<brisk>\d+) FB:(?P<fb>\d+) .*? Rank:(?P<rank>\d+|-).*?CP:(?P<cp>[0-9.]+) \| Body:(?P<body>[0-9.]+)"
)

depth_re = re.compile(
    r"DEPTH_(?P<status>OK|SKIP) \| (?P<sym>[A-Z0-9]+).*?spread=(?P<spread>[0-9.]+)bps "
    r"\| bid5=\$(?P<bid5>[0-9.]+) ask5=\$(?P<ask5>[0-9.]+) imb5=(?P<imb5>[+-]?[0-9.]+)"
)

close_re = re.compile(
    r"SHADOW_CLOSE \| (?P<strategy>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<reason>[^|]+) \| "
    r".*?(?:FinalNet|Net):(?P<net>[+-]?\d+\.\d+)\$.*?MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

skip_close_re = re.compile(
    r"SKIP_TRACK_CLOSE \| (?P<strategy>[^|]+) \| (?P<sym>[A-Z0-9]+) \| (?P<outcome>[^|]+) \| "
    r"original_skip=(?P<skip>[^|]+) \| HypoNet:(?P<net>[+-]?\d+\.\d+)\$ \| MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

def f(x, d=0.0):
    try:
        if x is None or x == "-":
            return d
        return float(x)
    except Exception:
        return d

def bucket_ctx(c):
    out = []
    pc = abs(f(c.get("pc")))
    vol = f(c.get("vol"))
    oi = f(c.get("oi"))
    trend = f(c.get("trend"))
    btc = f(c.get("btc"))
    score = f(c.get("score"))
    struct = f(c.get("struct"), 999)
    brisk = f(c.get("brisk"), 999)
    fb = f(c.get("fb"), 999)
    rank = f(c.get("rank"), 999999)
    cp = f(c.get("cp"))
    body = f(c.get("body"))
    spread = f(c.get("spread"), 999)
    bid5 = f(c.get("bid5"))
    ask5 = f(c.get("ask5"))
    imb5 = f(c.get("imb5"))

    checks = [
        ("pc_020_040", 0.20 <= pc < 0.40),
        ("pc_040_070", 0.40 <= pc < 0.70),
        ("pc_070_plus", pc >= 0.70),
        ("vol_8_15", 8 <= vol < 15),
        ("vol_15_plus", vol >= 15),
        ("oi_neg", oi < 0),
        ("oi_0_1", 0 <= oi < 1),
        ("oi_1_plus", oi >= 1),
        ("trend_neg", trend < 0),
        ("trend_0_05", 0 <= trend < 0.5),
        ("trend_05_plus", trend >= 0.5),
        ("btc_neg", btc < 0),
        ("btc_pos", btc >= 0),
        ("score_0_2", 0 <= score <= 2),
        ("score_3_4", 3 <= score <= 4),
        ("score_5_plus", score >= 5),
        ("struct_0_1", struct <= 1),
        ("struct_2_3", 2 <= struct <= 3),
        ("struct_4_plus", struct >= 4),
        ("brisk_0_2", brisk <= 2),
        ("brisk_3_4", 3 <= brisk <= 4),
        ("brisk_5_plus", brisk >= 5),
        ("fb_0_1", fb <= 1),
        ("fb_2_plus", fb >= 2),
        ("rank_1_20", rank <= 20),
        ("rank_21_50", 20 < rank <= 50),
        ("rank_50_plus", rank > 50),
        ("cp_075_plus", cp >= 0.75),
        ("body_075_plus", body >= 0.75),
        ("spread_0_2", spread <= 2),
        ("spread_2_5", 2 < spread <= 5),
        ("spread_5_plus", spread > 5 and spread < 999),
        ("bid5_5k_plus", bid5 >= 5000),
        ("ask5_5k_plus", ask5 >= 5000),
        ("imb_bid", imb5 >= 0.10),
        ("imb_ask", imb5 <= -0.10),
        ("imb_flat", -0.10 < imb5 < 0.10),
    ]
    return [name for name, ok in checks if ok]

def stat(vals):
    if not vals:
        return "n=0"
    s = sum(vals)
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    pf = pos / neg if neg > 0 else 999 if pos > 0 else 0
    return f"n={len(vals):3d} sum={s:+6.2f}$ avg={s/len(vals):+6.3f}$ wr={sum(v>0 for v in vals)/len(vals)*100:5.1f}% pf={pf:5.2f}"

def main():
    last = {}
    records = []
    skip_records = []
    seen = set()

    for path in LOGS:
        if not path.exists():
            continue
        for raw in path.read_text(errors="ignore").splitlines():
            if raw in seen:
                continue
            seen.add(raw)

            m = cand_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d.pop("sym")
                last.setdefault(sym, {}).update(d)
                continue

            m = depth_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d.pop("sym")
                last.setdefault(sym, {}).update(d)
                continue

            m = close_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d["sym"]
                ctx = dict(last.get(sym, {}))
                rec = {
                    "type": "close",
                    "sym": sym,
                    "strategy": d["strategy"].strip(),
                    "reason": d["reason"].strip(),
                    "net": f(d["net"]),
                    "mfe": f(d["mfe"]),
                    "mae": f(d["mae"]),
                    "ctx": ctx,
                    "buckets": bucket_ctx(ctx),
                }
                records.append(rec)
                continue

            m = skip_close_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d["sym"]
                ctx = dict(last.get(sym, {}))
                rec = {
                    "type": "skip",
                    "sym": sym,
                    "strategy": d["strategy"].strip(),
                    "outcome": d["outcome"].strip(),
                    "skip": d["skip"].strip(),
                    "net": f(d["net"]),
                    "mfe": f(d["mfe"]),
                    "mae": f(d["mae"]),
                    "ctx": ctx,
                    "buckets": bucket_ctx(ctx),
                }
                skip_records.append(rec)
                continue

    good = [r for r in records if r["sym"] in GOOD]
    toxic = [r for r in records if r["sym"] in TOXIC]
    other = [r for r in records if r["sym"] not in GOOD and r["sym"] not in TOXIC]

    by_bucket_good = defaultdict(list)
    by_bucket_toxic = defaultdict(list)
    by_bucket_other = defaultdict(list)

    for r in good:
        for b in r["buckets"]:
            by_bucket_good[b].append(r["net"])
    for r in toxic:
        for b in r["buckets"]:
            by_bucket_toxic[b].append(r["net"])
    for r in other:
        for b in r["buckets"]:
            by_bucket_other[b].append(r["net"])

    lines = []
    lines.append("=" * 120)
    lines.append(f"XPL/NEAR SIGNATURE LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    lines.append("=" * 120)
    lines.append("Goal: decide if XPL/NEAR winners have reusable features or are just symbol episodes.")
    lines.append("Diagnostics only. Real trading OFF.")
    lines.append(f"records={len(records)} skip_records={len(skip_records)}")
    lines.append("")
    lines.append("GROUP TOTALS")
    lines.append(f"GOOD XPL/NEAR: {stat([r['net'] for r in good])}")
    lines.append(f"TOXIC set:     {stat([r['net'] for r in toxic])}")
    lines.append(f"OTHER:         {stat([r['net'] for r in other])}")

    lines.append("")
    lines.append("=" * 120)
    lines.append("BUCKET CONTRAST: GOOD vs TOXIC vs OTHER")
    lines.append("=" * 120)

    all_buckets = sorted(set(by_bucket_good) | set(by_bucket_toxic) | set(by_bucket_other))
    contrast = []
    for b in all_buckets:
        g = by_bucket_good.get(b, [])
        t = by_bucket_toxic.get(b, [])
        o = by_bucket_other.get(b, [])
        if len(g) < 2:
            continue
        g_avg = sum(g) / len(g)
        t_avg = sum(t) / len(t) if t else 0
        o_avg = sum(o) / len(o) if o else 0
        contrast.append((g_avg - min(t_avg, o_avg), b, g, t, o))

    contrast.sort(reverse=True)
    for _, b, g, t, o in contrast[:80]:
        lines.append(f"{b:<24} GOOD {stat(g)} | TOXIC {stat(t)} | OTHER {stat(o)}")

    lines.append("")
    lines.append("=" * 120)
    lines.append("GOOD RECORDS")
    lines.append("=" * 120)
    for r in good[:80]:
        c = r["ctx"]
        lines.append(
            f"{r['sym']:<6} {r['strategy']:<34} {r['reason']:<8} net={r['net']:+.2f}$ "
            f"mfe={r['mfe']:+.2f}% mae={r['mae']:+.2f}% | "
            f"pc={c.get('pc','?')} vol={c.get('vol','?')} oi={c.get('oi','?')} "
            f"trend={c.get('trend','?')} btc={c.get('btc','?')} score={c.get('score','?')} "
            f"struct={c.get('struct','?')} brisk={c.get('brisk','?')} fb={c.get('fb','?')} "
            f"rank={c.get('rank','?')} spread={c.get('spread','?')} "
            f"buckets={','.join(r['buckets'])}"
        )

    lines.append("")
    lines.append("=" * 120)
    lines.append("TOXIC RECORDS")
    lines.append("=" * 120)
    for r in toxic[:120]:
        c = r["ctx"]
        lines.append(
            f"{r['sym']:<6} {r['strategy']:<34} {r['reason']:<8} net={r['net']:+.2f}$ "
            f"mfe={r['mfe']:+.2f}% mae={r['mae']:+.2f}% | "
            f"pc={c.get('pc','?')} vol={c.get('vol','?')} oi={c.get('oi','?')} "
            f"trend={c.get('trend','?')} btc={c.get('btc','?')} score={c.get('score','?')} "
            f"struct={c.get('struct','?')} brisk={c.get('brisk','?')} fb={c.get('fb','?')} "
            f"rank={c.get('rank','?')} spread={c.get('spread','?')} "
            f"buckets={','.join(r['buckets'])}"
        )

    lines.append("")
    lines.append("=" * 120)
    lines.append("DECISION")
    lines.append("=" * 120)
    lines.append("If contrast buckets are only symbol identity and not shared features, do NOT build a strategy.")
    lines.append("If 2-3 buckets separate GOOD from TOXIC/OTHER, create a tiny shadow lane using those buckets.")
    lines.append("Never real from this lab; it is feature discovery only.")

    OUT.write_text("\n".join(lines))
    print(OUT)
    print("\n".join(lines[:260]))

if __name__ == "__main__":
    main()
