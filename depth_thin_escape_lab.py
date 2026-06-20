import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

LOGS = [Path("skynet_3h.log"), Path("skynet_12h.log"), Path("skynet_48h.log")]

candidate_re = re.compile(
    r"\[(?P<t>\d\d:\d\d:\d\d)\] (?P<sym>[A-Z0-9]+) \| "
    r"Vol:x(?P<vol>[0-9.]+) \| Price:(?P<pc>[+-]?[0-9.]+)% \| "
    r"OI:(?P<oi>[+-]?[0-9.]+)% \| Trend15M:(?P<trend>[+-]?[0-9.]+)% \| "
    r"BTC_5M:(?P<btc>[+-]?[0-9.]+)% \| Score:(?P<score>[+-]?\d+) \| "
    r"Struct:(?P<struct>\d+) \| BRisk:(?P<brisk>\d+) FB:(?P<fb>\d+) .*? Rank:(?P<rank>\d+|-)"
)

depth_skip_re = re.compile(
    r"\[(?P<t>\d\d:\d\d:\d\d)\] DEPTH_SKIP \| (?P<sym>[A-Z0-9]+) \| DEPTH_THIN \| "
    r"spread=(?P<spread>[0-9.]+)bps \| bid5=\$(?P<bid5>[0-9.]+) ask5=\$(?P<ask5>[0-9.]+) "
    r"imb5=(?P<imb5>[+-]?[0-9.]+)"
)

skip_close_re = re.compile(
    r"\[(?P<t>\d\d:\d\d:\d\d)\] SKIP_TRACK_CLOSE \| (?P<strat>[^|]+) \| (?P<sym>[A-Z0-9]+) \| "
    r"(?P<outcome>[^|]+) \| original_skip=DEPTH_THIN \| HypoNet:(?P<net>[+-]?\d+\.\d+)\$ "
    r"\| MFE:(?P<mfe>[+-]?\d+\.\d+)% MAE:(?P<mae>[+-]?\d+\.\d+)%"
)

def f(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def i(x, default=999):
    try:
        if x == "-":
            return default
        return int(float(x))
    except Exception:
        return default

def bucket_bool(name, ok):
    return f"{name}={'Y' if ok else 'N'}"

def stat(vals):
    n = len(vals)
    s = sum(vals)
    avg = s / n if n else 0
    wr = sum(v > 0 for v in vals) / n * 100 if n else 0
    pos = sum(v for v in vals if v > 0)
    neg = -sum(v for v in vals if v < 0)
    pf = pos / neg if neg > 0 else (999 if pos > 0 else 0)
    return n, s, avg, wr, pf

def line(name, vals):
    n, s, avg, wr, pf = stat(vals)
    return f"{name:<95} n={n:4d} sum={s:+8.2f}$ avg={avg:+7.3f}$ wr={wr:5.1f}% pf={pf:6.2f}"

def main():
    last_candidate = {}
    last_depth = {}
    rows = []

    for path in LOGS:
        if not path.exists():
            continue

        for raw in path.read_text(errors="ignore").splitlines():
            m = candidate_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d["sym"]
                last_candidate[sym] = {
                    "vol": f(d["vol"]),
                    "pc": f(d["pc"]),
                    "oi": f(d["oi"]),
                    "trend": f(d["trend"]),
                    "btc": f(d["btc"]),
                    "score": i(d["score"]),
                    "struct": i(d["struct"]),
                    "brisk": i(d["brisk"]),
                    "fb": i(d["fb"]),
                    "rank": i(d["rank"]),
                }
                continue

            m = depth_skip_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d["sym"]
                last_depth[sym] = {
                    "spread": f(d["spread"]),
                    "bid5": f(d["bid5"]),
                    "ask5": f(d["ask5"]),
                    "imb5": f(d["imb5"]),
                }
                continue

            m = skip_close_re.search(raw)
            if m:
                d = m.groupdict()
                sym = d["sym"]
                cand = dict(last_candidate.get(sym, {}))
                dep = dict(last_depth.get(sym, {}))
                net = f(d["net"])
                row = {
                    "sym": sym,
                    "strat": d["strat"].strip(),
                    "outcome": d["outcome"].strip(),
                    "net": net,
                    "mfe": f(d["mfe"]),
                    "mae": f(d["mae"]),
                    **cand,
                    **dep,
                }
                rows.append(row)

    groups = defaultdict(list)

    for r in rows:
        net = r["net"]

        rank = r.get("rank", 999)
        vol = r.get("vol", 0)
        pc = abs(r.get("pc", 0))
        score = r.get("score", 0)
        struct = r.get("struct", 999)
        brisk = r.get("brisk", 999)
        fb = r.get("fb", 999)
        spread = r.get("spread", 999)
        bid5 = r.get("bid5", 0)
        ask5 = r.get("ask5", 0)
        imb5 = r.get("imb5", 0)
        trend = r.get("trend", 0)
        btc = r.get("btc", 0)

        tests = [
            bucket_bool("rank<=40", rank <= 40),
            bucket_bool("rank<=80", rank <= 80),
            bucket_bool("vol>=10", vol >= 10),
            bucket_bool("vol>=15", vol >= 15),
            bucket_bool("pc>=0.30", pc >= 0.30),
            bucket_bool("pc>=0.50", pc >= 0.50),
            bucket_bool("score>=5", score >= 5),
            bucket_bool("struct<=1", struct <= 1),
            bucket_bool("struct<=3", struct <= 3),
            bucket_bool("brisk<=2", brisk <= 2),
            bucket_bool("fb<=1", fb <= 1),
            bucket_bool("spread<=2", spread <= 2),
            bucket_bool("spread<=3", spread <= 3),
            bucket_bool("bid5>=10000", bid5 >= 10000),
            bucket_bool("ask5>=10000", ask5 >= 10000),
            bucket_bool("imb5>=0", imb5 >= 0),
            bucket_bool("trend>0", trend > 0),
            bucket_bool("btc>0", btc > 0),
        ]

        for t in tests:
            groups[t].append(net)

        combos = [
            ("rank<=40 & vol>=10 & score>=5", rank <= 40 and vol >= 10 and score >= 5),
            ("rank<=40 & vol>=10 & struct<=1", rank <= 40 and vol >= 10 and struct <= 1),
            ("rank<=80 & vol>=10 & spread<=3", rank <= 80 and vol >= 10 and spread <= 3),
            ("rank<=40 & score>=5 & spread<=3", rank <= 40 and score >= 5 and spread <= 3),
            ("rank<=40 & vol>=10 & fb<=1", rank <= 40 and vol >= 10 and fb <= 1),
            ("rank<=40 & vol>=10 & brisk<=2", rank <= 40 and vol >= 10 and brisk <= 2),
            ("score>=5 & struct<=1 & spread<=3", score >= 5 and struct <= 1 and spread <= 3),
            ("vol>=15 & score>=5", vol >= 15 and score >= 5),
            ("pc>=0.50 & vol>=10 & rank<=40", pc >= 0.50 and vol >= 10 and rank <= 40),
            ("trend>0 & btc>0 & score>=5", trend > 0 and btc > 0 and score >= 5),
        ]

        for name, ok in combos:
            groups[f"COMBO {name}={'Y' if ok else 'N'}"].append(net)

        groups[f"SYM {r['sym']}"].append(net)
        groups[f"STRAT {r['strat']}"].append(net)
        groups[f"OUTCOME {r['outcome']}"].append(net)

    out = []
    out.append("=" * 130)
    out.append(f"DEPTH THIN ESCAPE LAB UTC={datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}")
    out.append("=" * 130)
    out.append("Goal: find a narrow exception lane for DEPTH_THIN instead of disabling depth guard globally.")
    out.append(f"depth_thin_skip_closes={len(rows)}")
    out.append("")

    out.append("=" * 130)
    out.append("BEST GROUPS, MIN N=3")
    out.append("=" * 130)
    best = [(k, v) for k, v in groups.items() if len(v) >= 3]
    best.sort(key=lambda kv: (sum(kv[1]), sum(x > 0 for x in kv[1]) / len(kv[1])), reverse=True)
    for k, vals in best[:80]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 130)
    out.append("WORST GROUPS, MIN N=3")
    out.append("=" * 130)
    worst = [(k, v) for k, v in groups.items() if len(v) >= 3]
    worst.sort(key=lambda kv: sum(kv[1]))
    for k, vals in worst[:80]:
        out.append(line(k, vals))

    out.append("")
    out.append("=" * 130)
    out.append("RAW WINNERS")
    out.append("=" * 130)
    winners = [r for r in rows if r["net"] > 0]
    winners.sort(key=lambda r: r["net"], reverse=True)
    for r in winners[:80]:
        out.append(
            f"{r['sym']:<8} {r['strat']:<40} net={r['net']:+.2f}$ outcome={r['outcome']:<10} "
            f"score={r.get('score')} rank={r.get('rank')} vol={r.get('vol')} pc={r.get('pc')} "
            f"struct={r.get('struct')} br={r.get('brisk')} fb={r.get('fb')} "
            f"spread={r.get('spread')} bid5={r.get('bid5')} ask5={r.get('ask5')} "
            f"imb5={r.get('imb5')} trend={r.get('trend')} btc={r.get('btc')}"
        )

    text = "\n".join(out)
    outdir = Path("safe_exports/filter_lab")
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"depth_thin_escape_lab_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')}.txt"
    fp.write_text(text)
    (outdir / "latest_depth_thin_escape_lab.txt").write_text(text)

    print(fp)
    print(text[:14000])

if __name__ == "__main__":
    main()
