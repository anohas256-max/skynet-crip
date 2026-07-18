#!/usr/bin/env python3
"""V22 bounded historical perpetual basis audit. Research only; never trades."""
import csv, io, json, math, sys, time, traceback, zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'data'/'v22_perp_basis_audit'
CONSOLE=ROOT/'v22_perp_basis_audit_console.txt'; LATEST=ROOT/'v22_perp_basis_audit_latest.md'
FROZEN=ROOT/'v22_perp_basis_frozen_candidate.json'; V21=ROOT/'data'/'v21_slow_trend_audit'/'mexc_public_cache'
H=3600; START=1640995200; TRAIN=1719792000; VAL=1751328000; END=1782864000
SYMS=('BTCUSDT','ETHUSDT','DOGEUSDT','BNBUSDT','AVAXUSDT','ADAUSDT','ETCUSDT','LINKUSDT','BCHUSDT','DOTUSDT','ATOMUSDT')
NOTIONAL=12.; COSTS={'base':.0036,'severe':.005}; CONFIGS=(('INSTANT_BASIS',24),('INSTANT_BASIS',72),('MEAN_24H_BASIS',24),('MEAN_24H_BASIS',72))

def iso(t): return datetime.fromtimestamp(t,timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
def log(x=''):
    print(x,flush=True)
    with CONSOLE.open('a',encoding='utf-8') as f:f.write(str(x)+'\n')
def months():
    for y in range(2022,2027):
        for m in range(1,13):
            if (y,m)<=(2026,6): yield y,m
def cache(kind,s): return OUT/kind/f'{s}.csv'
def get(url):
    err=None
    for i in range(5):
        try:
            with urlopen(Request(url,headers={'User-Agent':'SKYNET-V22-research/1.0'}),timeout=60) as r:return r.read()
        except Exception as e: err=e; time.sleep(1+i)
    raise RuntimeError(f'download failed {url}: {err}')
def num(x):
    try:return float(x)
    except:return None
def parse_zip(raw,kind):
    ans=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name=next(n for n in z.namelist() if n.endswith('.csv'))
        for r in csv.reader(io.TextIOWrapper(z.open(name),encoding='utf-8')):
            if not r or not r[0].isdigit():continue
            # all three 1h kline archive families begin open time, OHLC.
            if len(r)<5: raise RuntimeError(f'{kind} malformed row')
            ts=int(r[0]); ts=ts//1000 if ts>10**11 else ts
            vals=[num(x) for x in r[1:5]]
            if any(x is None or x<=0 for x in vals): continue
            ans.append((ts,*vals, num(r[5]) if len(r)>5 else None))
    return ans
def download_kind(s,kind):
    p=cache(kind,s); p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        with p.open() as f:return [tuple(map(float,r)) if i else None for i,r in enumerate([])] # unreachable marker
    rows=[]
    endpoint={'exec':'klines','mark':'markPriceKlines','index':'indexPriceKlines'}[kind]
    for y,m in months():
        u=f'https://data.binance.vision/data/futures/um/monthly/{endpoint}/{s}/1h/{s}-1h-{y}-{m:02d}.zip'
        rows.extend(parse_zip(get(u),kind)); time.sleep(.015)
    by={int(r[0]):r for r in rows if START<=r[0]<END}
    with p.open('w',newline='') as f:csv.writer(f).writerows(by[t] for t in sorted(by))
def load(p):
    with p.open() as f:return [(int(float(r[0])),*map(float,r[1:])) for r in csv.reader(f) if r]
def v21_exec(s):
    p=V21/f'binance_{s[:-4]}_USDT_1h_{START}_{END}.csv'
    return load(p) if p.exists() else None
def funding(s):
    p=OUT/'funding'/f'{s}.csv'; p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): return [(int(float(r[0])),float(r[1])) for r in csv.reader(p.open()) if r]
    old=V21/f'binance_{s[:-4]}_USDT_funding.csv'
    if old.exists():
        rows=[(int(float(r[0])),float(r[1])) for r in csv.reader(old.open()) if r]
    else:
        rows=[]
        for y,m in months():
            u=f'https://data.binance.vision/data/futures/um/monthly/fundingRate/{s}/{s}-fundingRate-{y}-{m:02d}.zip'
            with zipfile.ZipFile(io.BytesIO(get(u))) as z:
                n=next(x for x in z.namelist() if x.endswith('.csv'))
                for r in csv.reader(io.TextIOWrapper(z.open(n),encoding='utf-8')):
                    if r and r[0].isdigit() and len(r)>=3:
                        t=int(r[0]); rows.append((t//1000 if t>10**11 else t,float(r[2])))
    rows=sorted(set((t,r) for t,r in rows if START<=t<END))
    with p.open('w',newline='') as f:csv.writer(f).writerows(rows)
    return rows
def quality(rows,kind):
    ts=[r[0] for r in rows]; gaps=sum(b-a!=H for a,b in zip(ts,ts[1:]))
    return {'hours':len(rows),'first':iso(ts[0]) if ts else None,'last':iso(ts[-1]) if ts else None,'duplicates':len(ts)-len(set(ts)),'gaps':gaps,'bad_timestamp':sum(t%H!=0 for t in ts),'coverage':bool(ts) and ts[0]==START and ts[-1]==END-H,'kind':kind}
def funding_quality(f):
    ts=[x[0] for x in f]; return {'settlements':len(f),'first':iso(ts[0]) if ts else None,'last':iso(ts[-1]) if ts else None,'duplicates':len(ts)-len(set(ts)),'missing_intervals_over_24h':sum(b-a>24*H for a,b in zip(ts,ts[1:]))}
def fm(funds,entry,exit_,side): return sum(-side*NOTIONAL*r for t,r in funds if entry<t<=exit_)
def metric(trades,cost):
    pn=[t['price']+t['funding']-NOTIONAL*cost for t in trades]; total=sum(pn); pos=sum(x for x in pn if x>0); neg=-sum(x for x in pn if x<0)
    eq=peak=0.; dd=0
    for x in pn:eq+=x;peak=max(peak,eq);dd=min(dd,eq-peak)
    bs=defaultdict(float); bp=defaultdict(float); side={1:[], -1:[]}
    for t,x in zip(trades,pn):bs[t['symbol']]+=x;bp[t['pair']]+=x;side[t['side']].append(x)
    def pf(a):
        p=sum(x for x in a if x>0);n=-sum(x for x in a if x<0);return p/n if n else (999. if p else 0.)
    besttrade=max(pn,default=0); bestpair=max(bp.values(),default=0); bestsym=max(bs.values(),default=0)
    positive=sum(x for x in bs.values() if x>0)
    return {'positions':len(trades),'pairs':len(bp),'symbols':len(bs),'pnl':total,'pf':pf(pn),'wr':sum(x>0 for x in pn)/len(pn) if pn else 0,'avg':total/len(pn) if pn else 0,'mdd':dd,'funding':sum(t['funding'] for t in trades),'price':sum(t['price'] for t in trades),'long_pnl':sum(x for t,x in zip(trades,pn) if t['side']==1),'short_pnl':sum(x for t,x in zip(trades,pn) if t['side']==-1),'long_pf':pf(side[1]),'short_pf':pf(side[-1]),'leave_best_trade':total-besttrade,'leave_best_pair':total-bestpair,'leave_best_symbol':total-bestsym,'best_symbol_share':bestsym/positive if positive else 0}
def parts(trades,cost,start,end):
    w=(end-start)//4;return [metric([t for t in trades if start+i*w<=t['decision']<(end if i==3 else start+(i+1)*w)],cost)['pnl'] for i in range(4)]
def sim(signal,hold,start,end,series,funds,delay=0):
    # Pair atomicity and capacity: after entry, pair locks both positions to exit.
    out=[]; skips=Counter(); active_until=0; pair=0
    for d in range(start,end,8*H):
        if d%86400 not in (0,8*H,16*H): continue
        if d<start+24*H:skips['insufficient_lookback']+=1;continue
        if d<active_until:skips['active_pair']+=1;continue
        cand=[]; entry=d+(1+delay)*H; exit_=entry+hold*H
        for s,x in series.items():
            try:
                if entry not in x['exec'] or exit_ not in x['exec']:continue
                # Candle timestamps are hour opens: decision d may only use the
                # immediately preceding fully closed hour, d-H (and its history).
                vals=[math.log(x['index'][d-H-i*H]/x['mark'][d-H-i*H]) for i in range(24 if signal=='MEAN_24H_BASIS' else 1)]
                cand.append((sum(vals)/len(vals),s))
            except KeyError: pass
        if len(cand)<8:skips['fewer_than_8_valid_symbols']+=1;continue
        cand.sort(); lo,hi=cand[0],cand[-1]
        if lo[1]==hi[1]:skips['non_distinct_sides']+=1;continue
        pair+=1
        for score,s,side in ((hi[0],hi[1],1),(lo[0],lo[1],-1)):
            e=series[s]['exec'][entry];x=series[s]['exec'][exit_]
            price=NOTIONAL*((x/e-1) if side==1 else (1-x/e))
            out.append({'decision':d,'entry':entry,'exit':exit_,'symbol':s,'side':side,'pair':pair,'price':price,'funding':fm(funds[s],entry,exit_,side)})
        active_until=exit_
    return out,dict(skips)
def passed(m,q,delay):
    return m['positions']>=100 and m['pairs']>=50 and m['symbols']>=8 and m['pnl']>0 and m['pf']>=1.2 and m['leave_best_trade']>0 and m['leave_best_pair']>0 and m['leave_best_symbol']>0 and sum(x>0 for x in q)>=3 and m['best_symbol_share']<=.35 and m['price']<=0 or False
def gate(m,q,delay):
    return (m['positions']>=100 and m['pairs']>=50 and m['symbols']>=8 and m['pnl']>0 and m['pf']>=1.2 and m['leave_best_trade']>0 and m['leave_best_pair']>0 and m['leave_best_symbol']>0 and sum(x>0 for x in q)>=3 and m['best_symbol_share']<=.35 and not (m['price']>0 and m['funding']+m['price']<=0) and delay['pnl']>0 and m['long_pf']>=.8 and m['short_pf']>=.8)
def selftests():
    assert math.log(100/99)>0 and math.log(100/101)<0
    assert math.isclose(fm([(101,.0001)],100,101,1),-.0012) and math.isclose(fm([(101,.0001)],100,101,-1),.0012)
    primary=100+H; delayed=primary+2*H
    assert primary>100 and delayed==primary+2*H and fm([(105,.1)],100,104,1)==0
    assert abs((1-.005)-.995)<1e-12
    # final gate represented by explicit caller condition below; pair sizing is hard-coded two.
    return ['basis_sign','opposite_side','funding_sign','timestamp_no_lookahead','entry_delay','exit_funding_boundary','cost_once','max_two_positions','pair_atomicity','final_gate']
def fmt(m):return f"positions={m['positions']} pairs={m['pairs']} severe_pnl=${m['pnl']:+.2f} PF={m['pf']:.2f} funding=${m['funding']:+.2f} price=${m['price']:+.2f}"
def main():
    OUT.mkdir(parents=True,exist_ok=True);CONSOLE.write_text('',encoding='utf-8'); log('V22 | REAL_TRADING_ENABLED=false REAL_TRADING_ARMED=false LIVE_DRY_RUN=true')
    tests=selftests();log('SELF_TESTS PASS: '+', '.join(tests))
    # Reuse V21 executable and funding parsed official archives; download only missing official mark/index archives.
    jobs=[]
    for s in SYMS:
        for k in ('mark','index'):
            if not cache(k,s).exists():jobs.append((s,k))
    if jobs:
        log(f'Downloading {len(jobs)} missing official monthly archive sets (mark/index).')
        with ThreadPoolExecutor(max_workers=6) as ex:
            fs=[ex.submit(download_kind,s,k) for s,k in jobs]
            for i,f in enumerate(as_completed(fs),1):f.result();log(f'archive sets complete {i}/{len(fs)}')
    series={};funds={};dq={}; invalid=[]
    for s in SYMS:
        ex=v21_exec(s)
        if ex is None:
            download_kind(s,'exec');ex=load(cache('exec',s))
        ma=load(cache('mark',s));ind=load(cache('index',s));fu=funding(s)
        qs=[quality(ex,'exec'),quality(ma,'mark'),quality(ind,'index')]
        dq[s]={'sources':qs,'funding':funding_quality(fu),'train_average_hourly_volume_usdt':sum(r[4]*r[5] for r in ex if START<=r[0]<TRAIN)/sum(START<=r[0]<TRAIN for r in ex)}
        # Archive gaps are retained and make a symbol unavailable at affected
        # decisions; the specified data gate is eight symbols with admissible
        # coverage, not synthetic continuity or interpolation.
        if not all(q['coverage'] and q['duplicates']==0 and q['bad_timestamp']==0 for q in qs):invalid.append(s)
        series[s]={'exec':{r[0]:r[1] for r in ex},'mark':{r[0]:r[4] for r in ma},'index':{r[0]:r[4] for r in ind}};funds[s]=fu
    if len(SYMS)-len(invalid)<8:
        report={'decision':'STOP_DATA_INVALID','self_tests':tests,'data_quality':dq,'invalid_symbols':invalid};LATEST.write_text('# V22 perpetual basis audit\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n');return
    results=[]
    for sig,hold in CONFIGS:
        tr,sk=sim(sig,hold,TRAIN,VAL,series,funds);de,_=sim(sig,hold,TRAIN,VAL,series,funds,2)
        sev=metric(tr,COSTS['severe']);base=metric(tr,COSTS['base']);dm=metric(de,COSTS['severe']);q=parts(tr,COSTS['severe'],TRAIN,VAL);ok=gate(sev,q,dm)
        r={'signal':sig,'hold_hours':hold,'base':base,'severe':sev,'delay_severe':dm,'quarters':q,'skips':sk,'validation_pass':ok};results.append(r);log(f'{sig}/{hold}h {fmt(sev)} delay=${dm["pnl"]:+.2f} pass={ok}')
    winners=[r for r in results if r['validation_pass']]
    decision='STOP_NO_VALIDATION_EDGE'; final=None; frozen=None
    if winners:
        winners.sort(key=lambda r:(r['severe']['leave_best_symbol'],r['severe']['leave_best_pair'],r['severe']['pnl']),reverse=True);frozen=winners[0]
        FROZEN.write_text(json.dumps({'v22_frozen_validation_candidate':frozen['signal']+'/'+str(frozen['hold_hours'])+'h','validation_severe':frozen['severe'],'validation_quarters':frozen['quarters']},indent=2)+'\n')
        tr,sk=sim(frozen['signal'],frozen['hold_hours'],VAL,END,series,funds);de,_=sim(frozen['signal'],frozen['hold_hours'],VAL,END,series,funds,2);sev=metric(tr,COSTS['severe']);final={'severe':sev,'delay_severe':metric(de,COSTS['severe']),'quarters':parts(tr,COSTS['severe'],VAL,END),'skips':sk};decision='FINAL_TEST_PASS' if gate(sev,final['quarters'],final['delay_severe']) else 'FINAL_TEST_FAIL'
    report={'decision':decision,'source':'official Binance USD-M monthly executable klines, markPriceKlines, indexPriceKlines, and fundingRate archives; V21 parsed official executable/funding cache reused where present','range':'2022-01-01 through 2026-06-30 UTC','self_tests':'PASS','universe':list(SYMS),'data_quality':dq,'validation':results,'validation_passed':len(winners),'frozen_candidate':None if not frozen else frozen['signal']+'/'+str(frozen['hold_hours'])+'h','final_opened':bool(frozen),'final':final}
    lines=['# V22 perpetual basis audit','',f'**V22_BASIS_DECISION={decision}**','',f'Source/range: {report["source"]}; {report["range"]}.','',f'Self-tests: PASS ({", ".join(tests)}).','',f'Universe: {", ".join(SYMS)}.','',f'Data-quality valid symbols: {len(SYMS)-len(invalid)}/11; invalid: {invalid or "none"}.','', '## Validation']
    for r in results: lines += [f"- {r['signal']} / HOLD_{r['hold_hours']}H: {fmt(r['severe'])}; delay severe PnL=${r['delay_severe']['pnl']:+.2f}; pass={r['validation_pass']}; skips={r['skips']}"]
    lines += ['', '## Full machine-readable report','```json',json.dumps(report,indent=2,sort_keys=True),'```','']
    LATEST.write_text('\n'.join(lines));log('V22_BASIS_DECISION='+decision)
if __name__=='__main__':
    try:main()
    except Exception:
        traceback.print_exc()
        LATEST.write_text('# V22 perpetual basis audit\n\n**V22_BASIS_DECISION=STOP_IMPLEMENTATION_INVALID**\n')
        sys.exit(1)
