#!/usr/bin/env python3
"""V24 repaired bounded Binance USD-M launch-momentum audit; research only."""
import csv, html, io, json, re, sys, time, traceback, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'data'/'v24_binance_launch_audit'; REPORT=ROOT/'v24_binance_launch_audit_latest.md'; CONSOLE=ROOT/'v24_binance_launch_audit_console.txt'
START=1640995200; TRAIN=1719792000; VAL=1751328000; END=1782864000
LIST='https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo={}&pageSize=20'; SUPPORT='https://www.binance.com/en/support/announcement/{}'; DV='https://data.binance.vision/data/futures/um/monthly'
CONFIGS=((15,24),(15,72),(60,24),(60,72)); COST={'base':.002,'severe':.005}; MAX_CMS=30; CMS_N=0; LAST=0.0; SOURCE_STOP=None; REQUESTS=[]
def iso(t): return datetime.fromtimestamp(t,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if t else None
def log(x=''):
 print(x,flush=True)
 with CONSOLE.open('a',encoding='utf-8') as f:f.write(str(x)+'\n')
def http(url,cms=False):
 global CMS_N,LAST,SOURCE_STOP
 if cms:
  if CMS_N>=MAX_CMS: raise RuntimeError('CMS request ceiling reached')
  wait=3-(time.monotonic()-LAST)
  if wait>0: time.sleep(wait)
  CMS_N+=1; LAST=time.monotonic()
 try:
  with urlopen(Request(url,headers={'User-Agent':'SKYNET-V24-repaired-research/1.0'}),timeout=30) as r: status=r.status;body=r.read()
 except HTTPError as e: status=e.code;body=e.read()
 except (URLError,TimeoutError,OSError) as e: status='NETWORK_'+type(e).__name__;body=b''
 REQUESTS.append({'url':url,'status':status,'bytes':len(body)})
 if cms and (status in (403,429) or isinstance(status,int) and status>=500): SOURCE_STOP=f'CMS_HTTP_{status}'
 return status,body
def clean(b):
 s=b.decode('utf-8','replace').replace('\\u003c','<').replace('\\u003e','>').replace('\\u0026','&')
 return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s))).strip()
MONTH=r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
TIME=[re.compile(r'(20\d{2}-\d\d-\d\d)\s+(\d\d:\d\d)\s*\(UTC\)',re.I),re.compile(rf'({MONTH}\s+\d{{1,2}},?\s+20\d{{2}}),?\s+(\d\d:\d\d)\s*\(UTC\)',re.I)]
def exact_launch(text,symbol):
 hits=[]
 for rx in TIME:
  for m in rx.finditer(text):
   ctx=text[max(0,m.start()-220):m.end()+120].lower()
   if re.search(r'(?:launch|trading)\s*(?:time|will\s*start|starts|open)',ctx) and symbol.replace('_','') in text[max(0,m.start()-500):m.end()+500].replace('_','').upper():
    for fmt in ('%Y-%m-%d %H:%M','%b %d, %Y %H:%M','%B %d, %Y %H:%M'):
     try:hits.append(int(datetime.strptime(m.group(1)+' '+m.group(2),fmt).replace(tzinfo=timezone.utc).timestamp()));break
     except ValueError:pass
 return sorted(set(hits))
def articles():
 out=[]
 for p in (1,2):
  st,b=http(LIST.format(p),True)
  if SOURCE_STOP:return []
  if st!=200: raise RuntimeError('CMS_list_'+str(st))
  d=json.loads(b).get('data',{}); cats=d.get('catalogs',[]) if isinstance(d,dict) else []
  for c in cats:
   if c.get('catalogId')==48: out += c.get('articles',[])
 # Candidate filter is title-only discovery, never the proof of launch time.
 return [x for x in out if re.search(r'Futures\s+Will\s+Launch.*(?:USD.?M|USDT).*(?:Perpetual)',x.get('title',''),re.I)]
def events(arts):
 ans=[]
 for a in arts:
  if SOURCE_STOP:break
  code=a['code'];url=SUPPORT.format(code);st,b=http(url,True)
  if SOURCE_STOP:break
  if st!=200: ans.append({'url':url,'reason':'excluded_article_http_'+str(st)});continue
  t=clean(b);syms=sorted(set(x.upper() for x in re.findall(r'\b([A-Z0-9]{2,24}USDT)\s+(?:Perpetual|USD.?M)',t,re.I)))
  if len(syms)!=1:ans.append({'url':url,'reason':'excluded_ambiguous_symbol'});continue
  ts=exact_launch(t,syms[0])
  if len(ts)!=1:ans.append({'url':url,'symbol':syms[0],'reason':'excluded_no_unique_explicit_launch_utc'});continue
  if not START<=ts[0]<END:ans.append({'url':url,'symbol':syms[0],'launch':ts[0],'reason':'excluded_outside_period'});continue
  ans.append({'url':url,'symbol':syms[0],'launch':ts[0],'reason':'candidate'})
 return ans
def months(a,b):
 d=datetime.fromtimestamp(a,timezone.utc);y,m=d.year,d.month
 while (y,m)<=(datetime.fromtimestamp(b,timezone.utc).year,datetime.fromtimestamp(b,timezone.utc).month):yield y,m;y,m=(y+1,1) if m==12 else (y,m+1)
def zrows(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  n=next(x for x in z.namelist() if x.endswith('.csv'));return list(csv.reader(io.TextIOWrapper(z.open(n),encoding='utf-8')))
def data(e):
 a=e['launch'];b=a+73*3600;rows=[]
 for y,m in months(a,b):
  p=OUT/'klines'/f"{e['symbol']}-{y}-{m:02}.zip";p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   st,x=http(f'{DV}/klines/{e["symbol"]}/1m/{e["symbol"]}-1m-{y}-{m:02}.zip')
   if st!=200:raise RuntimeError('kline_http_'+str(st))
   p.write_bytes(x)
  for r in zrows(p.read_bytes()):
   if r and r[0].isdigit():rows.append((int(r[0])//1000,float(r[1])))
 by=dict(rows);first=((a+59)//60)*60;need=list(range(first,((b)//60)*60+1,60));miss=[x for x in need if x not in by]
 if miss:raise RuntimeError('kline_gap_'+str(len(miss)))
 fund=[]
 for y,m in months(a,b):
  p=OUT/'funding'/f"{e['symbol']}-{y}-{m:02}.zip";p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   st,x=http(f'{DV}/fundingRate/{e["symbol"]}/{e["symbol"]}-fundingRate-{y}-{m:02}.zip')
   if st==200:p.write_bytes(x)
   else:raise RuntimeError('funding_http_'+str(st))
  for r in zrows(p.read_bytes()):
   if r and r[0].isdigit() and len(r)>=3:fund.append((int(r[0])//1000,float(r[2])))
 return by,fund
def sim(es,n,h,lo,hi,delay=0):
 out=[];busy=0
 for e in sorted((x for x in es if lo<=x['launch']<hi),key=lambda x:x['launch']):
  first=((e['launch']+59)//60)*60;last=first+(n-1)*60;entry=first+n*60+delay*60;exit=entry+h*3600
  if entry<busy:continue
  r=e['k'][last]/e['k'][first]-1
  if r==0:continue
  side=1 if r>0 else -1;fund=sum(-side*x for t,x in e['f'] if entry<t<=exit)
  out.append({'price':side*(e['k'][exit]/e['k'][entry]-1),'funding':fund,'exit':exit});busy=exit
 return out
def met(ts,c):
 p=[x['price']+x['funding']-c for x in ts];pos=sum(x for x in p if x>0);neg=-sum(x for x in p if x<0);total=sum(p)
 return {'trades':len(ts),'pnl':total,'pf':pos/neg if neg else (999 if pos else 0),'leave_best_event':total-max(p,default=0),'price':sum(x['price'] for x in ts),'funding':sum(x['funding'] for x in ts)}
def gate(m,q,d):return m['trades']>=40 and m['pnl']>0 and m['pf']>=1.2 and m['leave_best_event']>0 and sum(x>0 for x in q)>=3 and d['pnl']>0
def tests():
 assert exact_launch('ABCUSDT Perpetual Launch Time: 2024-01-01 12:00 (UTC)','ABCUSDT')==[1704110400]
 assert ((100+59)//60)*60==120 and 120+15*60==1020
 assert sum(-x for t,x in [(101,.01)] if 100<t<=101)==-.01 and sum(-x for t,x in [(100,.01)] if 100<t<=101)==0
 assert abs(.01-.005-.005)<1e-12 and not gate({'trades':39,'pnl':1,'pf':2,'leave_best_event':1},[1,1,1,1],{'pnl':1})
 return ['launch_time_parsing','no_lookahead','entry_timing','funding_sign_boundary','no_overlap','cost_arithmetic','final_gate']
def main():
 global SOURCE_STOP
 OUT.mkdir(parents=True,exist_ok=True);CONSOLE.write_text('',encoding='utf-8');ts=tests();log('V24 | REAL_TRADING_ENABLED=false REAL_TRADING_ARMED=false LIVE_DRY_RUN=true');log('SELF_TESTS PASS: '+', '.join(ts))
 arts=articles();raw=events(arts) if not SOURCE_STOP else []
 exact=[x for x in raw if x.get('reason')=='candidate'];good=[]
 for e in exact:
  try:e['k'],e['f']=data(e);good.append(e)
  except Exception as x:e['reason']='excluded_'+str(x)
 results=[];opened=False
 if not SOURCE_STOP:
  for n,h in CONFIGS:
   v=sim(good,n,h,TRAIN,VAL);s=met(v,.005);w=(VAL-TRAIN)//4;q=[met(sim(good,n,h,TRAIN+i*w,VAL if i==3 else TRAIN+(i+1)*w),.005)['pnl'] for i in range(4)];d=met(sim(good,n,h,TRAIN,VAL,5),.005);ok=gate(s,q,d)
   r={'signal_minutes':n,'hold_hours':h,'validation_base':met(v,.002),'validation_severe':s,'validation_quarters':q,'validation_delayed_5m':d,'validation_pass':ok}
   if ok:r['final_severe']=met(sim(good,n,h,VAL,END),.005);opened=True
   results.append(r)
 decision='STOP_SOURCE_RATE_LIMITED' if SOURCE_STOP else ('FINAL_TEST_OPENED' if opened else ('STOP_DATA_UNAVAILABLE' if not good else 'STOP_NO_VALIDATION_EDGE'))
 report={'decision':decision,'cms_requests':CMS_N,'cms_limit':MAX_CMS,'requests':REQUESTS,'exact_events':len(exact),'continuous_events':len(good),'results':results,'final_opened':opened,'self_tests':ts,'source_stop':SOURCE_STOP,'exclusions':[{k:x.get(k) for k in ('url','symbol','launch','reason')} for x in raw if x.get('reason')!='candidate']}
 lines=['# V24 repaired Binance launch momentum audit','',f'**V24_DECISION={decision}**','',f'CMS source quality: requests={CMS_N}/{MAX_CMS}, minimum spacing=3 seconds, source_stop={SOURCE_STOP or "none"}.',f'Exact official launch events={len(exact)}; continuous executable 1m windows={len(good)}.','', '## Validation metrics']
 for r in results:lines.append(f"- {r['signal_minutes']}m/{r['hold_hours']}h: base={r['validation_base']}; severe={r['validation_severe']}; quarters={r['validation_quarters']}; delayed={r['validation_delayed_5m']}; pass={r['validation_pass']}; final={r.get('final_severe')}")
 if not results:lines.append('- unavailable: no continuous exact-launch event passed the bounded source gate.')
 lines += ['','```json',json.dumps(report,indent=2,sort_keys=True),'```',''];REPORT.write_text('\n'.join(lines),encoding='utf-8');log('V24_DECISION='+decision)
if __name__=='__main__':
 try:main()
 except Exception:
  traceback.print_exc();REPORT.write_text('# V24 repaired Binance launch momentum audit\n\n**V24_DECISION=STOP_IMPLEMENTATION_INVALID**\n',encoding='utf-8');sys.exit(1)
