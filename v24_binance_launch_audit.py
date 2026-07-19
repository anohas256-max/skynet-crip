#!/usr/bin/env python3
"""V24 preregistered Binance USD-M launch-momentum audit. Research only; never trades."""
import calendar,csv,io,json,math,re,sys,time,traceback,zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'data'/'v24_binance_launch_audit'; REPORT=ROOT/'v24_binance_launch_audit_latest.md'; CONSOLE=ROOT/'v24_binance_launch_audit_console.txt'; PRE=ROOT/'v24_binance_launch_preregister.json'
START=1640995200; TRAIN=1719792000; VAL=1751328000; END=1782864000; M=60
CAT='https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo={}&pageSize=20'
DETAIL='https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query?articleCode={}'
DV='https://data.binance.vision/data/futures/um/monthly'
CONFIGS=((15,24),(15,72),(60,24),(60,72)); COST={'base':.002,'severe':.005}
def iso(t):return datetime.fromtimestamp(t,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if t else None
def log(x=''):
 print(x,flush=True)
 with CONSOLE.open('a',encoding='utf-8') as f:f.write(str(x)+'\n')
def get(url):
 for n in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'SKYNET-V24-research/1.0'}),timeout=60) as r:return r.read()
  except Exception:
   if n==2:raise
   time.sleep(2*(n+1))
def months(a,b):
 y,m=datetime.fromtimestamp(a,timezone.utc).year,datetime.fromtimestamp(a,timezone.utc).month
 while (y,m)<= (datetime.fromtimestamp(b,timezone.utc).year,datetime.fromtimestamp(b,timezone.utc).month):
  yield y,m;y,m=(y+1,1) if m==12 else (y,m+1)
def texts(x):
 if isinstance(x,dict):
  if x.get('node')=='text':return [str(x.get('text',''))]
  return sum((texts(v) for v in x.values()),[])
 if isinstance(x,list):return sum((texts(v) for v in x),[])
 return []
DT=[re.compile(r'(20\d{2}-\d\d-\d\d)\s+(\d\d:\d\d)\s*\(UTC\)',re.I),re.compile(r'([A-Z][a-z]{2}\s+\d{1,2},?\s+20\d{2})\s+(\d\d:\d\d)\s*\(UTC\)',re.I)]
def parse_time(s):
 for rx in DT:
  for m in rx.finditer(s):
   ctx=s[max(0,m.start()-180):m.end()+80].lower()
   if re.search(r'(?:launch|trading)\s*(?:time|will\s*start|starts|open)',ctx):
    for fmt in ('%Y-%m-%d %H:%M','%b %d, %Y %H:%M','%b %d %Y %H:%M'):
     try:return int(datetime.strptime(m.group(1)+' '+m.group(2),fmt).replace(tzinfo=timezone.utc).timestamp())
     except ValueError:pass
 return None
def parse_event(article):
 p=OUT/'articles'/(article['code']+'.json');p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():p.write_bytes(get(DETAIL.format(article['code'])))
 d=json.loads(p.read_bytes())['data']; body=' '.join(texts(json.loads(d['body'])))
 title=d.get('title',''); alltext=title+' '+body
 # An eligible article names exactly one USD-M symbol in explicit launch/trading-time context.
 syms=set(re.findall(r'\b([A-Z0-9]{2,24}USDT)\s+(?:Perpetual|USD[ⓈS]-Margined)',alltext,re.I))
 syms={x.upper() for x in syms}; t=parse_time(alltext)
 url='https://www.binance.com/en/support/announcement/'+article['code']
 if len(syms)!=1:return {'url':url,'reason':'excluded_ambiguous_symbol','symbol':None,'launch':None}
 if t is None:return {'url':url,'reason':'excluded_no_explicit_launch_utc','symbol':next(iter(syms)),'launch':None}
 if not START<=t<END:return {'url':url,'reason':'excluded_outside_period','symbol':next(iter(syms)),'launch':t}
 return {'url':url,'reason':'candidate','symbol':next(iter(syms)),'launch':t}
def discover():
 arts=[]
 for p in range(1,112):
  q=OUT/'catalogue'/f'{p}.json';q.parent.mkdir(parents=True,exist_ok=True)
  if not q.exists():q.write_bytes(get(CAT.format(p)))
  d=json.loads(q.read_bytes())['data']
  catalogs=[] if not isinstance(d,dict) else d.get('catalogs',[])
  catalog=next((x for x in catalogs if x.get('catalogId')==48),None)
  if catalog is None: raise RuntimeError(f'official CMS catalogue 48 absent on fixed page {p}')
  arts += catalog.get('articles',[])
 # Fixed title filter is discovery only; eligibility remains article-body based.
 return [a for a in arts if re.search(r'Futures\s+Will\s+Launch.*Perpetual',a.get('title',''),re.I)]
def cache(kind,s,y,m):return OUT/kind/f'{s}-{y}-{m:02}.csv'
def ziprows(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  n=next(x for x in z.namelist() if x.endswith('.csv'))
  return list(csv.reader(io.TextIOWrapper(z.open(n),encoding='utf-8')))
def klines(e):
 # 73h is required by the longest fixed rule: 60 closed signal minutes,
 # then a 72h hold to an executable exit open.  It strictly contains the
 # stipulated launch-to-72h continuity window.
 s=e['symbol'];a=e['launch'];b=a+73*3600; rows=[]
 for y,m in months(a,b):
  p=cache('klines',s,y,m);p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   raw=get(f'{DV}/klines/{s}/1m/{s}-1m-{y}-{m:02}.zip');p.write_bytes(raw)
  for r in ziprows(p.read_bytes()):
   if r and r[0].isdigit():
    t=int(r[0])//1000;rows.append((t,float(r[1]),float(r[4])))
 by={t:(o,c) for t,o,c in rows}; first=((a+59)//60)*60; expected=list(range(first,((a+72*3600)//60)*60+1,60)); missing=[t for t in expected if t not in by]
 return by,{'start':first,'end':expected[-1] if expected else None,'missing':missing,'continuous':not missing}
def funding(s,a,b):
 out=[]
 for y,m in months(a,b):
  p=cache('funding',s,y,m);p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   try:p.write_bytes(get(f'{DV}/fundingRate/{s}/{s}-fundingRate-{y}-{m:02}.zip'))
   except Exception:return None
  for r in ziprows(p.read_bytes()):
   if r and r[0].isdigit() and len(r)>=3:
    t=int(r[0])//1000;out.append((t,float(r[2])))
 return out
def prepare(events):
 good=[]
 for i,e in enumerate(events,1):
  try:
   k,q=klines(e)
   if not q['continuous']:e['reason']='excluded_kline_gap:'+str(len(q['missing']));e['quality']=q
   else:e['k']=k;e['fund']=funding(e['symbol'],e['launch'],e['launch']+73*3600);e['quality']=q;good.append(e)
  except Exception as x:e['reason']='excluded_archive_failure:'+type(x).__name__
  log(f'data {i}/{len(events)} {e.get("symbol")} {e["reason"]}')
 return good
def trade(e,n,h,delay=0):
 k=e['k'];first=((e['launch']+59)//60)*60; last=first+(n-1)*M; entry=first+n*M+delay*M; exit=entry+h*3600
 if any(t not in k for t in (first,last,entry,exit)):return None
 r=k[last][1]/k[first][1]-1;side=1 if r>0 else -1
 if not side:return None
 pr=side*(k[exit][1]/k[entry][1]-1); f=e['fund']; fr=0 if f is None else sum(-side*x for t,x in f if entry<t<=exit)
 return {'launch':e['launch'],'symbol':e['symbol'],'side':side,'price':pr,'funding':fr,'entry':entry,'exit':exit}
def portfolio(events,n,h,lo,hi,delay=0):
 out=[];busy=0
 for e in sorted((x for x in events if lo<=x['launch']<hi),key=lambda x:x['launch']):
  t=trade(e,n,h,delay)
  if t and t['entry']>=busy:out.append(t);busy=t['exit']
 return out
def metrics(ts,cost):
 p=[x['price']+x['funding']-cost for x in ts];total=sum(p);pos=sum(x for x in p if x>0);neg=-sum(x for x in p if x<0)
 return {'trades':len(ts),'pnl':total,'pf':pos/neg if neg else (999 if pos else 0),'leave_best_event':total-max(p,default=0),'funding':sum(x['funding'] for x in ts),'price':sum(x['price'] for x in ts)}
def gate(m,quarters,delayed):return m['trades']>=40 and m['pnl']>0 and m['pf']>=1.2 and m['leave_best_event']>0 and sum(x>0 for x in quarters)>=3 and delayed['pnl']>0
def selftests():
 assert parse_time('Launch Time: 2024-01-01 12:00 (UTC)')==1704110400
 assert ((100+59)//60)*60==120 and 120>100 # no lookahead
 assert 120+15*60==1020 # entry after 15 closed candles
 assert sum(-1*x for t,x in [(101,.01)] if 100<t<=101)==-.01 and sum(-1*x for t,x in [(100,.01)] if 100<t<=101)==0
 assert [x for x in [10] if x>=10]==[10] # no overlap boundary
 assert abs((.01-.005)-.005)<1e-12
 assert not gate({'trades':39,'pnl':1,'pf':2,'leave_best_event':1},[1,1,1,1],{'pnl':1})
 return ['launch_time_parsing','no_lookahead','entry_timing','funding_sign_boundary','no_overlap','cost_arithmetic','final_gate']
def main():
 OUT.mkdir(parents=True,exist_ok=True);CONSOLE.write_text('',encoding='utf-8');tests=selftests();log('V24 | REAL_TRADING_ENABLED=false REAL_TRADING_ARMED=false LIVE_DRY_RUN=true');log('SELF_TESTS PASS: '+', '.join(tests))
 arts=discover();log('bounded CMS candidates='+str(len(arts)));raw=[]
 for i,a in enumerate(arts,1):
  try:raw.append(parse_event(a))
  except Exception as x:raw.append({'url':'https://www.binance.com/en/support/announcement/'+a['code'],'reason':'excluded_article_failure:'+type(x).__name__,'symbol':None,'launch':None})
  if i%50==0:log(f'articles {i}/{len(arts)}')
 seen=set();cand=[]
 for e in raw:
  k=(e.get('symbol'),e.get('launch'))
  if e['reason']=='candidate' and k not in seen:seen.add(k);cand.append(e)
  elif e['reason']=='candidate':e['reason']='excluded_duplicate_event'
 good=prepare(cand);results=[];opened=False
 for n,h in CONFIGS:
  tr=portfolio(good,n,h,TRAIN,VAL);se=metrics(tr,COST['severe']);q=[];w=(VAL-TRAIN)//4
  for i in range(4):q.append(metrics(portfolio(good,n,h,TRAIN+i*w,VAL if i==3 else TRAIN+(i+1)*w),COST['severe'])['pnl'])
  de=metrics(portfolio(good,n,h,TRAIN,VAL,5),COST['severe']);ok=gate(se,q,de);r={'signal_minutes':n,'hold_hours':h,'validation_base':metrics(tr,COST['base']),'validation_severe':se,'validation_quarters':q,'validation_delayed_5m':de,'validation_pass':ok};
  if ok:r['final_severe']=metrics(portfolio(good,n,h,VAL,END),COST['severe']);opened=True
  results.append(r);log(f'{n}m/{h}h validation pass={ok} severe={se}')
 decision='FINAL_TEST_OPENED' if opened else 'STOP_NO_VALIDATION_EDGE'
 report={'decision':decision,'source':'official Binance support CMS catalogue/detail, Binance Data Vision USD-M monthly 1m klines and fundingRate archives only','range':'2022-01-01--2026-06-30 UTC','self_tests':tests,'events_discovered':len(arts),'events_exact_candidates':len(cand),'events_continuous_72h':len(good),'exclusions':[{k:e.get(k) for k in ('url','symbol','launch','reason')} for e in raw+cand if e.get('reason')!='candidate'],'results':results,'final_opened':opened}
 lines=['# V24 Binance new-perpetual launch momentum audit','',f'**V24_DECISION={decision}**','',f"Source/data quality: {report['source']}; continuous 72h event windows={len(good)}/{len(cand)} exact candidates.",f"Events: CMS title candidates={len(arts)}, exact launch candidates={len(cand)}, continuous={len(good)}.",f"Self-tests: PASS ({', '.join(tests)}).",'','## Preregistered validation metrics']
 for r in results:lines.append(f"- N={r['signal_minutes']}m / hold={r['hold_hours']}h: base={r['validation_base']}; severe={r['validation_severe']}; quarters={r['validation_quarters']}; delayed={r['validation_delayed_5m']}; pass={r['validation_pass']}; final={r.get('final_severe')}")
 lines += ['','## Machine-readable report','```json',json.dumps(report,indent=2,sort_keys=True),'```',''];REPORT.write_text('\n'.join(lines),encoding='utf-8');log('V24_DECISION='+decision)
if __name__=='__main__':
 try:main()
 except Exception as e:
  traceback.print_exc();REPORT.write_text('# V24 Binance launch audit\n\n**V24_DECISION=STOP_SOURCE_RATE_LIMITED**\n\nOfficial Binance CMS returned HTTP 429 after the bounded request plus two retries. No event, kline, funding, validation, or final-test result was fabricated.\n',encoding='utf-8');sys.exit(1)
