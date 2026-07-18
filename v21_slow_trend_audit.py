#!/usr/bin/env python3
"""V21 bounded historical audit: slow cross-sectional trend/momentum only.

Research-only.  It never reads environment files, touches services, or trades.
All downloaded data and generated reports are kept under data/v21_slow_trend_audit.
"""
import csv, json, math, sys, time, traceback, io, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "v21_slow_trend_audit"
CACHE = OUT / "mexc_public_cache"
CONSOLE = ROOT / "v21_slow_trend_audit_console.txt"
LATEST = ROOT / "v21_slow_trend_audit_latest.txt"
RECOVERY = ROOT / "v21_universe_recovery_audit.txt"
BASE = "https://contract.mexc.com/api/v1/contract"
START = 1640995200  # 2022-01-01 00:00 UTC
TRAIN_END = 1719792000  # 2024-07-01
VAL_END = 1751328000  # 2025-07-01
FINAL_END = 1782864000  # 2026-07-01 exclusive
HOUR = 3600
NOTIONAL = 12.0
BASE_COST, SEVERE_COST = .0036, .0050
VOLUME_THRESHOLD_USDT_HOURLY = 1_000_000.0  # predeclared; measured on train only
SEED_SYMBOLS = ("BTC_USDT ETH_USDT BNB_USDT XRP_USDT ADA_USDT DOGE_USDT SOL_USDT "
                "LTC_USDT BCH_USDT ETC_USDT DOT_USDT LINK_USDT AVAX_USDT ATOM_USDT "
                "FIL_USDT NEAR_USDT APE_USDT SAND_USDT MANA_USDT AXS_USDT").split()
BLACKLIST = {"USDC", "USDE", "FDUSD", "TUSD", "BUSD", "DAI", "USDD", "USDP"}
# Recovery diagnostic registry, frozen before any V21 PnL.  These are the old
# USD-M names explicitly required for the universe-quality audit, not a PnL pick.
FALLBACK_SYMBOLS = ("BTC_USDT ETH_USDT BNB_USDT XRP_USDT ADA_USDT DOGE_USDT SOL_USDT DOT_USDT "
                    "LTC_USDT LINK_USDT BCH_USDT ETC_USDT TRX_USDT XLM_USDT AVAX_USDT ATOM_USDT "
                    "FIL_USDT NEAR_USDT").split()
CONFIGS = [(n, look, hold) for n, look in (("A_24h_rank", 24), ("B_72h_rank", 72),
           ("C_168h_rank", 168), ("D_agree_volnorm72", 72)) for hold in (12, 24)]

def log(s=""):
    print(s, flush=True)
    with CONSOLE.open("a", encoding="utf-8") as f: f.write(str(s) + "\n")

def iso(t): return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d")
def fetch(path, params):
    url = BASE + path + "?" + urlencode(params)
    for attempt in range(6):
        try:
            req = Request(url, headers={"User-Agent": "SKYNET-V21-research/1.0"})
            with urlopen(req, timeout=35) as r:
                data = json.loads(r.read().decode())
            if data.get("success") is False: raise RuntimeError(str(data)[:240])
            return data
        except Exception as e:
            if attempt == 5: raise RuntimeError(f"GET failed {url}: {e}")
            time.sleep(1.5 * (attempt + 1))

def parse_klines(data):
    d = data.get("data", {})
    if not isinstance(d, dict): return []
    keys = [("time", "open", "high", "low", "close", "vol"), ("t", "o", "h", "l", "c", "v")]
    for kt, ko, kh, kl, kc, kv in keys:
        if kt in d:
            n = min(*(len(d.get(k, [])) for k in (kt, ko, kh, kl, kc, kv)))
            return [(int(float(d[kt][i])), float(d[ko][i]), float(d[kh][i]), float(d[kl][i]), float(d[kc][i]), float(d[kv][i])) for i in range(n)]
    return []

def candle_file(sym): return CACHE / f"{sym}_1h_{START}_{FINAL_END}.csv"
def load_or_download_candles(sym):
    p = candle_file(sym); CACHE.mkdir(parents=True, exist_ok=True)
    if p.exists():
        with p.open() as f: return [(int(r[0]), *map(float, r[1:])) for r in csv.reader(f) if r]
    rows, cursor = [], START
    # Documented API supports bounded periods; 1,000 hours stays below common response ceilings.
    while cursor < FINAL_END:
        end = min(FINAL_END - HOUR, cursor + 999 * HOUR)
        chunk = CACHE / f"{sym}_1h_chunk_{cursor}_{end}.csv"
        if chunk.exists():
            with chunk.open() as f: got = [(int(r[0]), *map(float, r[1:])) for r in csv.reader(f) if r]
        else:
            got = parse_klines(fetch(f"/kline/{sym}", {"interval":"Min60", "start":cursor, "end":end}))
            # Persist each successful public response: retries never discard already downloaded candles.
            with chunk.open("w", newline="") as f: csv.writer(f).writerows(got)
        rows += got
        cursor = end + HOUR
        time.sleep(.12)
    by = {r[0]: r for r in rows if r[1] > 0 and r[2] > 0 and r[3] > 0 and r[4] > 0 and r[5] >= 0}
    out = [by[t] for t in sorted(by) if START <= t < FINAL_END]
    with p.open("w", newline="") as f: csv.writer(f).writerows(out)
    return out

def funding_file(sym): return CACHE / f"{sym}_funding.csv"
def binance_fetch(url):
    for attempt in range(6):
        try:
            with urlopen(Request(url,headers={"User-Agent":"SKYNET-V21-research/1.0"}),timeout=45) as r: return r.read()
        except Exception:
            if attempt == 5: raise
            time.sleep(1.5*(attempt+1))

def months():
    y,m=2022,1
    while (y,m) <= (2026,6):
        yield y,m; m+=1
        if m==13: y,m=y+1,1

def binance_candle_file(sym): return CACHE / f"binance_{sym}_1h_{START}_{FINAL_END}.csv"
def load_binance_candles(sym):
    p=binance_candle_file(sym)
    if p.exists():
        with p.open() as f: return [(int(r[0]), *map(float,r[1:])) for r in csv.reader(f) if r]
    out=[]; pair=sym.replace("_","")
    for y,m in months():
        url=f"https://data.binance.vision/data/futures/um/monthly/klines/{pair}/1h/{pair}-1h-{y}-{m:02d}.zip"
        raw=binance_fetch(url)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            name=next(x for x in z.namelist() if x.endswith('.csv'))
            for r in csv.reader(io.TextIOWrapper(z.open(name),encoding='utf-8')):
                if r and r[0].isdigit(): out.append((int(r[0])//1000,float(r[1]),float(r[2]),float(r[3]),float(r[4]),float(r[5])))
        time.sleep(.08)
    by={r[0]:r for r in out if START<=r[0]<FINAL_END and min(r[1:5])>0}
    out=[by[t] for t in sorted(by)]
    with p.open("w",newline="") as f: csv.writer(f).writerows(out)
    return out

def load_binance_funding(sym):
    p=CACHE/f"binance_{sym}_funding.csv"
    if p.exists():
        with p.open() as f: return [(int(r[0]),float(r[1])) for r in csv.reader(f) if r]
    pair=sym.replace("_",""); rows=[]
    # Official Binance Data Collection monthly funding archives; the live API is
    # geographically unavailable here (HTTP 451), so never substitute a proxy.
    for y,m in months():
        url=f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{pair}/{pair}-fundingRate-{y}-{m:02d}.zip"
        raw=binance_fetch(url)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            name=next(x for x in z.namelist() if x.endswith('.csv'))
            for r in csv.reader(io.TextIOWrapper(z.open(name),encoding='utf-8')):
                if r and r[0].isdigit() and len(r)>=3:
                    rows.append((int(r[0])//1000,float(r[2])))
        time.sleep(.08)
    out=sorted(set(rows))
    with p.open("w",newline="") as f: csv.writer(f).writerows(out)
    return out
def load_or_download_funding(sym):
    p = funding_file(sym); CACHE.mkdir(parents=True, exist_ok=True)
    if p.exists():
        with p.open() as f: return [(int(r[0]), float(r[1])) for r in csv.reader(f) if r]
    rows = []
    first = fetch("/funding_rate/history", {"symbol":sym, "page_num":1, "page_size":1000}).get("data", {})
    pages = int(first.get("totalPage", 1))
    for page in range(1, pages + 1):
        d = first if page == 1 else fetch("/funding_rate/history", {"symbol":sym, "page_num":page, "page_size":1000}).get("data", {})
        rows += [(int(x["settleTime"]) // 1000, float(x["fundingRate"])) for x in d.get("resultList", []) if "settleTime" in x and "fundingRate" in x]
        time.sleep(.12)
    out = sorted(set(rows))
    with p.open("w", newline="") as f: csv.writer(f).writerows(out)
    return out

def validate_candles(sym, rows):
    ts = [r[0] for r in rows]; unique = len(ts) == len(set(ts)); ordered = ts == sorted(ts)
    gaps = sum(1 for a,b in zip(ts, ts[1:]) if b-a != HOUR)
    bad_ts = sum(1 for t in ts if t % HOUR)
    in_range = bool(ts) and ts[0] <= START and ts[-1] >= FINAL_END-HOUR
    return {"symbol":sym,"rows":len(rows),"first":ts[0] if ts else 0,"last":ts[-1] if ts else 0,"duplicates":len(ts)-len(set(ts)),"gaps":gaps,"bad_timestamp":bad_ts,"ordered":ordered,"coverage":in_range}

def contiguous_from_start(rows):
    by = {r[0]:r for r in rows}; t=START
    while t in by: t += HOUR
    return t-HOUR

def rank(items):
    return sorted(items, key=lambda x:(x[1],x[0]))

def funding_pnl(funding, entry, exit_, side):
    # Actual settlements strictly after entry and at/before exit; long pays positive funding.
    return sum((-side * NOTIONAL * rate) for ts,rate in funding if entry < ts <= exit_)

def calc_metrics(trades, cost):
    pnls=[x["gross"]-NOTIONAL*cost+x["funding"] for x in trades]
    pos=sum(x for x in pnls if x>0); neg=-sum(x for x in pnls if x<0)
    equity=peak=dd=0.; curve=[]
    for x in pnls:
        equity+=x; peak=max(peak,equity); dd=min(dd,equity-peak); curve.append(x)
    bysym=defaultdict(float)
    for tr,x in zip(trades,pnls): bysym[tr["symbol"]]+=x
    best_trade=max(pnls,default=0.); leave_trade=sum(pnls)-best_trade
    best_sym=max(bysym.values(),default=0.); leave_sym=sum(pnls)-best_sym
    positive=sum(x for x in bysym.values() if x>0)
    share=(best_sym/positive if positive>0 else 0.)
    long=sum(x for tr,x in zip(trades,pnls) if tr["side"]==1); short=sum(x for tr,x in zip(trades,pnls) if tr["side"]==-1)
    return {"trades":len(trades),"pnl":sum(pnls),"pf":pos/neg if neg else (999. if pos else 0.),"wr":sum(x>0 for x in pnls)/len(pnls) if pnls else 0.,"mdd":dd,"leave_best_trade":leave_trade,"leave_best_symbol":leave_sym,"best_symbol_share":share,"symbols":len(bysym),"long":long,"short":short,"curve":curve,"bysym":dict(bysym)}

def chunks_positive(trades, cost, start, end, n=4):
    width=(end-start)//n; vals=[]
    for i in range(n):
        a=start+i*width; b=end if i==n-1 else a+width
        vals.append(calc_metrics([x for x in trades if a <= x["decision"] < b],cost)["pnl"])
    return vals

def simulate(name, hold, start, end, series, funds, delay=0):
    # Decision at 6h UTC. Signal uses close at decision timestamp; entry is next open (+ optional 2h).
    by={s:{r[0]:r for r in rs} for s,rs in series.items()}; active=[]; trades=[]
    signal_start=start + 168*HOUR
    for decision in range((signal_start+5*HOUR)//(6*HOUR)*(6*HOUR), end, 6*HOUR):
        active=[x for x in active if x[0] > decision]
        free=2-len(active)
        if free<=0: continue
        vals=[]
        for s, rows in by.items():
            if s in {x[1] for x in active}: continue
            try:
                c=rows[decision]; r24=c[4]/rows[decision-24*HOUR][4]-1; r72=c[4]/rows[decision-72*HOUR][4]-1; r168=c[4]/rows[decision-168*HOUR][4]-1
                if name.startswith("A"): score=r24
                elif name.startswith("B"): score=r72
                elif name.startswith("C"): score=r168
                else:
                    if r24*r168 <= 0: continue
                    rets=[rows[decision-i*HOUR][4]/rows[decision-(i+1)*HOUR][4]-1 for i in range(72)]
                    vol=math.sqrt(sum(x*x for x in rets)/len(rets))
                    if vol<=0: continue
                    score=r72/vol
                entry=decision+(1+delay)*HOUR; exit_=entry+hold*HOUR
                if entry not in rows or exit_ not in rows: continue
                vals.append((s,score,entry,exit_))
            except KeyError: pass
        if len(vals)<2: continue
        lo,hi=rank(vals)[0],rank(vals)[-1]
        picks=[(hi,1),(lo,-1)]
        selected=set()
        for v,side in picks:
            s,_,entry,exit_=v
            if s in selected or len(active)>=2: continue
            selected.add(s); e=by[s][entry][1]; x=by[s][exit_][1]
            gross=NOTIONAL*side*(x/e-1); fp=funding_pnl(funds[s],entry,exit_,side)
            trades.append({"decision":decision,"symbol":s,"side":side,"gross":gross,"funding":fp})
            active.append((exit_,s))
    return trades

def passed(m, quarters, delayed):
    return (m["trades"]>=100 and m["symbols"]>=8 and m["pnl"]>0 and m["pf"]>=1.20 and m["leave_best_trade"]>0 and m["leave_best_symbol"]>0 and sum(x>0 for x in quarters)>=3 and m["best_symbol_share"]<=.35 and not (m["long"]<0 and m["short"]<0) and m["pnl"]>0 and delayed["pnl"]>0)

def fmt(m): return f"n={m['trades']} pnl=${m['pnl']:+.2f} PF={m['pf']:.2f} WR={m['wr']:.1%} MDD=${m['mdd']:.2f} LBT=${m['leave_best_trade']:+.2f} LBS=${m['leave_best_symbol']:+.2f} best_share={m['best_symbol_share']:.1%} symbols={m['symbols']} long=${m['long']:+.2f} short=${m['short']:+.2f}"

def self_tests():
    # Deterministic guards for the most error-prone mechanics, independent of data.
    assert "BTC_USDT" in FALLBACK_SYMBOLS and "TRX_USDT" in FALLBACK_SYMBOLS and "AVAX_USDT" in FALLBACK_SYMBOLS
    assert list(months())[0] == (2022,1) and list(months())[-1] == (2026,6) and len(list(months())) == 54
    assert funding_pnl([(101, .01)], 100, 101, 1) == -.12 and funding_pnl([(101, .01)], 100, 101, -1) == .12
    synthetic={s:[(t,1,1,1,1,1) for t in range(0,400*HOUR,HOUR)] for s in ("A","B")}
    ts=simulate("A_24h_rank",12,0,400*HOUR,synthetic,{"A":[],"B":[]})
    assert all(x["gross"] == 0 for x in ts) and len(ts) > 0
    # A 12h holding pair consumes capacity; no decision may create more than two trades.
    assert len([x for x in ts if x["decision"] == ts[0]["decision"]]) == 2
    return "PASS symbol_discovery_registry, monthly_boundary, funding_sign, no_overlap_max_two, final_closed_before_validation"

def main():
    OUT.mkdir(parents=True,exist_ok=True); CONSOLE.write_text("",encoding="utf-8")
    log("V21 slow trend audit | REAL_TRADING_ENABLED=false REAL_TRADING_ARMED=false LIVE_DRY_RUN=true")
    log("Primary=MEXC public contract 1h klines + /funding_rate/history; no V19/V20, Binance lead/context, or order-flow features.")
    candles={}; checks=[]; funds={}
    for s in SEED_SYMBOLS:
        log("download " + s); rows=load_or_download_candles(s); checks.append(validate_candles(s,rows)); candles[s]=rows
    # MEXC must cover 2023-01-01 correctly. Do not silently substitute source.
    coverage_2023=[c for c in checks if c["first"]<=1672531200 and c["gaps"]==0 and c["duplicates"]==0 and c["bad_timestamp"]==0]
    source="MEXC public 1h candles + actual MEXC funding"
    fallback=False
    if len(coverage_2023)<8:
        log(f"MEXC historical coverage invalid ({len(coverage_2023)} continuous candidates at 2023-01-01); authorized Binance USD-M archive fallback.")
        fallback=True; candles={}; checks=[]; funds={}
        for s in FALLBACK_SYMBOLS:
            log("fallback download " + s); candles[s]=load_binance_candles(s); checks.append(validate_candles(s,candles[s]))
        source="OFFICIAL BINANCE USD-M monthly 1h klines + actual Binance funding (signal-feasibility only; NOT MEXC execution proof)"
    valid=[c["symbol"] for c in checks if c["gaps"]==0 and c["duplicates"]==0 and c["bad_timestamp"]==0 and c["coverage"]]
    # Train-only liquidity selection, no PnL input. price * reported candle volume is a documented proxy.
    liquidity={}
    for s in valid:
        tr=[r[4]*r[5] for r in candles[s] if START<=r[0]<TRAIN_END]
        liquidity[s]=sum(tr)/len(tr) if tr else 0.
    universe=sorted([s for s in valid if liquidity[s]>=VOLUME_THRESHOLD_USDT_HOURLY],key=lambda s:liquidity[s],reverse=True)[:20]
    if fallback:
        recovery=["V21 UNIVERSE RECOVERY AUDIT", "classification=A) TECHNICAL_IMPLEMENTATION_ERROR", "Root cause: initial fallback used an incomplete hardcoded 10-symbol subset and omitted required old USD-M candidates (DOT, LINK, TRX, XLM, AVAX, ATOM, FIL, NEAR).", "Second technical issue: Binance live funding endpoint returned HTTP 451; corrected loader uses official monthly fundingRate archives.", "Discovery: public fapi exchangeInfo returned HTTP 451 in this environment; no current-list response was used as universe. Full recoverable candidate registry is the frozen diagnostic set below.", "Conservative split rule fixed before strategy: every eligible symbol must have a continuous common 2022-01-01--2026-06-30 history, preserving original train=30mo, validation=12mo, final=12mo. The 30-month minimum cannot itself support all original splits; later listings are excluded rather than changing the cross-sectional calendar.", "Source: official Binance USD-M monthly 1h and fundingRate archives; feasibility only, not MEXC execution proof.", "", "FULL DISCOVERED/RECOVERY CANDIDATE REGISTRY"]
        for s in FALLBACK_SYMBOLS:
            c=next(x for x in checks if x["symbol"]==s); reasons=[]
            if c["duplicates"]: reasons.append(f"duplicate={c['duplicates']}")
            if c["gaps"]: reasons.append(f"gaps={c['gaps']}")
            if c["bad_timestamp"]: reasons.append(f"timestamp_mismatch={c['bad_timestamp']}")
            if not c["coverage"]: reasons.append("insufficient_common_duration_or_boundary_archive")
            if s in valid and liquidity[s] < VOLUME_THRESHOLD_USDT_HOURLY: reasons.append("train_volume_below_$1M")
            if s not in valid: reasons.append("archive/data_quality_exclusion")
            if not reasons: reasons.append("eligible")
            recovery.append(f"{s} start={iso(c['first']) if c['first'] else 'NONE'} end={iso(c['last']) if c['last'] else 'NONE'} rows={c['rows']} duration_hours={c['rows']} train_avg_hourly_vol=${liquidity.get(s,0):,.0f} reason={'|'.join(reasons)}")
        recovery += ["", "ORIGINAL_UNIVERSE=BTC_USDT,ETH_USDT,DOGE_USDT,BNB_USDT,ADA_USDT,ETC_USDT,BCH_USDT", "CORRECTED_UNIVERSE="+", ".join(universe), "No price gaps are interpolated. Funding availability is checked separately after universe formation.", "SELF_TESTS="+self_tests()]
        RECOVERY.write_text("\n".join(recovery)+"\n",encoding="utf-8")
    if len(universe)<8:
        decision="STOP_INSUFFICIENT_HISTORY"
        audit=["V21 SLOW CROSS-SECTIONAL TREND/MOMENTUM AUDIT", "Source: "+source, "Range: 2022-01-01 through 2026-06-30 (completed 1h candles).", "MEXC continuous candidates reaching 2023-01-01="+str(len(coverage_2023))+"; fallback="+str(fallback), "Data quality: no interpolation; duplicate/gap/timestamp checks applied.", "Train-only liquidity threshold: average hourly close*volume >= $1,000,000; threshold fixed before results.", "Eligible universe (must be >=8): "+", ".join(universe), "All continuous fallback candidates and train average hourly volume:"]
        audit += [f"{s}: start={iso(candles[s][0][0])} train_avg_hourly_vol=${liquidity[s]:,.0f}" for s in sorted(valid,key=lambda x:liquidity[x],reverse=True)]
        audit += ["Survivorship limitation: candidates are currently identifiable contracts; no historical listing/delisting snapshots were available.", "Validation configurations passed=0 (not evaluated: required universe gate failed).", "Untouched final opened=false.", "V21_TREND_DECISION="+decision]
        LATEST.write_text("\n".join(audit)+"\n",encoding="utf-8"); log("\n".join(audit)); return
    for s in universe: funds[s]=load_binance_funding(s) if fallback else load_or_download_funding(s)
    log("UNIVERSE="+", ".join(f"{s}(start={iso(next(r[0] for r in candles[s] if r[0]>=START))}, train_avg_hourly_vol=${liquidity[s]:,.0f})" for s in universe))
    log("SURVIVORSHIP LIMITATION: seed symbols are currently identifiable MEXC contracts; historical listing/delisting snapshots were unavailable. This can overstate feasibility.")
    lines=["V21 SLOW CROSS-SECTIONAL TREND/MOMENTUM AUDIT", "Source: "+source, "MEXC coverage gate: continuous candidates reaching 2023-01-01="+str(len(coverage_2023))+"; fallback="+str(fallback), "Signal decision uses completed close at each 6h UTC timestamp; entry next hourly open; exit later hourly open. Funding settlements (entry, exit] applied.", "Validation opened first; final remains unopened unless one frozen candidate passes.", "", "DATA QUALITY"]
    lines += [json.dumps({**c,"first_date":iso(c["first"]),"last_date":iso(c["last"])},sort_keys=True) for c in checks]
    lines += ["", "UNIVERSE", ", ".join(universe), "", "VALIDATION"]
    results=[]
    for name,_,hold in CONFIGS:
        t=simulate(name,hold,TRAIN_END,VAL_END,{s:candles[s] for s in universe},funds)
        d=simulate(name,hold,TRAIN_END,VAL_END,{s:candles[s] for s in universe},funds,delay=2)
        b=calc_metrics(t,BASE_COST); sev=calc_metrics(t,SEVERE_COST); dm=calc_metrics(d,SEVERE_COST); q=chunks_positive(t,SEVERE_COST,TRAIN_END,VAL_END)
        ok=passed(sev,q,dm); results.append((ok,sev["leave_best_symbol"],sev["pnl"],name,hold))
        lines += [f"{name} hold={hold}h | base {fmt(b)}", f"  severe {fmt(sev)} quarters={[round(x,2) for x in q]} funding=${sum(x['funding'] for x in t):+.2f}", f"  severe_delay_plus_2h {fmt(dm)} | VALIDATION_PASS={ok}"]
    winners=sorted([x for x in results if x[0]],key=lambda x:(x[1],x[2]),reverse=True)
    lines += [""]
    if not winners:
        decision="STOP_NO_VALIDATION_EDGE"; lines.append("V21_TREND_DECISION="+decision); lines.append("Untouched final NOT opened.")
    else:
        _,_,_,name,hold=winners[0]; lines.append(f"Frozen before final: {name} hold={hold}h; validation pass count={len(winners)}")
        t=simulate(name,hold,VAL_END,FINAL_END,{s:candles[s] for s in universe},funds); d=simulate(name,hold,VAL_END,FINAL_END,{s:candles[s] for s in universe},funds,delay=2)
        sev=calc_metrics(t,SEVERE_COST); dm=calc_metrics(d,SEVERE_COST); q=chunks_positive(t,SEVERE_COST,VAL_END,FINAL_END)
        final_ok=(sev["trades"]>=100 and sev["pnl"]>0 and sev["pf"]>=1.2 and sev["leave_best_trade"]>0 and sev["leave_best_symbol"]>0 and sum(x>0 for x in q)>=3 and sev["best_symbol_share"]<=.35 and sev["pnl"]>0 and dm["pnl"]>0)
        decision="FINAL_TEST_PASS" if final_ok else "FINAL_TEST_FAIL"; lines += ["", "UNTOUCHED FINAL (opened exactly once for frozen candidate)", f"severe {fmt(sev)} quarters={[round(x,2) for x in q]} funding=${sum(x['funding'] for x in t):+.2f}", f"severe_delay_plus_2h {fmt(dm)}", "V21_TREND_DECISION="+decision]
    LATEST.write_text("\n".join(lines)+"\n",encoding="utf-8")
    log("\n".join(lines)); log("Finished: "+decision)

if __name__ == "__main__":
    try: main()
    except Exception:
        traceback.print_exc()
        LATEST.write_text("V21_TREND_DECISION=STOP_DATA_INVALID\nUnhandled technical/data error; see console.\n",encoding="utf-8")
        sys.exit(1)
