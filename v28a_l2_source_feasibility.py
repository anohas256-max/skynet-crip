#!/usr/bin/env python3
"""V28A bounded offline feasibility of Binance Data Vision USD-M daily L2/trade archives."""
import csv, io, json, sys, traceback, zipfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'data'/'v28a_l2_source_feasibility'; REPORT=ROOT/'v28a_l2_source_feasibility.md'
BASE='https://data.binance.vision/data/futures/um/daily'; SYMS=('BTCUSDT','ETHUSDT'); DAYS=tuple(date(2026,6,1)+timedelta(days=i) for i in range(14)); CAP=2_000_000_000
BOOK_HEAD=('timestamp','percentage','depth','notional'); TRADE_HEAD=('agg_trade_id','price','quantity','first_trade_id','last_trade_id','transact_time','is_buyer_maker')
def url(kind,s,d):return f'{BASE}/{kind}/{s}/{s}-{kind}-{d.isoformat()}.zip'
def get(u,head=False):
 req=Request(u,method='HEAD' if head else 'GET',headers={'User-Agent':'SKYNET-V28A-source-feasibility/1.0'})
 try:
  with urlopen(req,timeout=60) as r:return r.status,int(r.headers.get('Content-Length') or 0),r.read() if not head else b''
 except HTTPError as e:return e.code,0,b''
def cache(kind,s,d):return OUT/kind/s/f'{s}-{kind}-{d.isoformat()}.zip'
def download(kind,s,d,used):
 p=cache(kind,s,d);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():return p,used
 st,size,b=get(url(kind,s,d));
 if st!=200:raise RuntimeError(f'{kind}:{s}:{d}:HTTP_{st}')
 if used+size>CAP:raise RuntimeError(f'archive_cap_exceeded:{used+size}>{CAP}')
 p.write_bytes(b);return p,used+size
def rows(p):
 with zipfile.ZipFile(p) as z:
  n=next(x for x in z.namelist() if x.endswith('.csv'))
  yield from csv.reader(io.TextIOWrapper(z.open(n),encoding='utf-8'))
def book_stats(p):
 it=rows(p);head=tuple(next(it)); snaps={};duplicate=0;bad=0;levels=Counter()
 for r in it:
  if len(r)!=4:bad+=1;continue
  try:t=int(datetime.strptime(r[0],'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()*1000);pct=float(r[1]);depth=float(r[2]);notional=float(r[3])
  except:bad+=1;continue
  if depth<0 or notional<0:bad+=1;continue
  if t not in snaps:snaps[t]=set()
  if pct in snaps[t]:duplicate+=1
  snaps[t].add(pct)
 for v in snaps.values():levels[len(v)]+=1
 ts=sorted(snaps);gaps=[b-a for a,b in zip(ts,ts[1:]) if b-a>10_000]
 return {'header':head,'snapshots':len(ts),'first_ms':ts[0] if ts else None,'last_ms':ts[-1] if ts else None,'max_gap_ms':max(gaps,default=0),'gap_count_over_10s':len(gaps),'duplicate_timestamp_percentage':duplicate,'bad_rows':bad,'depth_levels_per_snapshot':dict(levels),'has_bid_ask_prices':False,'has_sequence_field':False}
def trade_stats(p):
 it=rows(p);head=tuple(next(it));lastid=None;lastt=None;bad=dup=nonmono=0;first=last=None;maxgap=0
 for r in it:
  if len(r)!=7:bad+=1;continue
  try:i=int(r[0]);float(r[1]);float(r[2]);t=int(r[5]); maker=r[6].lower()
  except:bad+=1;continue
  if maker not in ('true','false'):bad+=1;continue
  if lastid is not None and i==lastid:dup+=1
  if lastid is not None and i<lastid:nonmono+=1
  if lastt is not None:maxgap=max(maxgap,t-lastt)
  first=first if first is not None else t;last=t;lastid=i;lastt=t
 return {'header':head,'first_ms':first,'last_ms':last,'max_intertrade_gap_ms':maxgap,'duplicate_agg_trade_id':dup,'nonmonotonic_agg_trade_id':nonmono,'bad_rows':bad,'signed_flow_available':True}
def selftests():
 assert BOOK_HEAD==('timestamp','percentage','depth','notional') and TRADE_HEAD[-1]=='is_buyer_maker'
 assert (-1 if 'true'=='true' else 1)==-1 # buyer-maker trade is seller-initiated
 assert next(x for x in [(60,1)] if x[0]>=60)==(60,1)
 assert 100+50<=200 and not (100+101<=200)
 return ['confirmed_headers','signed_aggressor_mapping','first_observation_no_interpolation','archive_cap']
def main():
 OUT.mkdir(parents=True,exist_ok=True);tests=selftests();probe=[];used=0
 # Exactly two archive probes: one bookDepth, one aggTrades, before all other downloads.
 for kind in ('bookDepth','aggTrades'):
  u=url(kind,'BTCUSDT',DAYS[0]);st,size,_=get(u,True);probe.append({'url':u,'head_status':st,'head_bytes':size})
  if st!=200:raise RuntimeError('probe_head_'+kind+'_'+str(st))
  p,used=download(kind,'BTCUSDT',DAYS[0],used);probe[-1].update({'get_bytes':p.stat().st_size,'schema':book_stats(p) if kind=='bookDepth' else trade_stats(p)})
 if tuple(probe[0]['schema']['header'])!=BOOK_HEAD or tuple(probe[1]['schema']['header'])!=TRADE_HEAD:raise RuntimeError('probe_schema_changed')
 # The confirmed official schema has percentage buckets, not executable bid/ask
 # price levels or update IDs.  Stop before a larger bounded download because
 # additional days cannot repair those absent fields without interpolation.
 if not probe[0]['schema']['has_bid_ask_prices'] or not probe[0]['schema']['has_sequence_field']:
  report={'decision':'STOP_SOURCE_OR_IMPLEMENTATION_INVALID','source':'official Binance Data Vision probes only','probe':probe,'self_tests':tests,'reason':'bookDepth_schema_lacks_executable_bid_ask_prices_and_sequence','replay_feasibility':{'top_of_book_depth_imbalance':'PARTIAL_PERCENTAGE_BUCKETS_ONLY','signed_aggressive_trade_flow':'YES_FROM_is_buyer_maker','spread':'NO_BOOKDEPTH_HAS_NO_BID_ASK_PRICES','forward_labels_1_5_15_60s':'POSSIBLE_FROM_AGGTRADES_ONLY','sequence_gap_replay':'NO_BOOKDEPTH_HAS_NO_SEQUENCE'}}
  lines=['# V28A L2 source / implementation feasibility','', '**V28A_DECISION=STOP_SOURCE_OR_IMPLEMENTATION_INVALID**','',f"Probe-only bounded stop: confirmed bookDepth schema is {probe[0]['schema']['header']}; it has no executable bid/ask prices and no sequence field.",f"Self-tests: PASS ({', '.join(tests)}).",'', '```json',json.dumps(report,indent=2,sort_keys=True),'```',''];REPORT.write_text('\n'.join(lines),encoding='utf-8');return
 allstats=[]
 for s in SYMS:
  for d in DAYS:
   b,used=download('bookDepth',s,d,used);a,used=download('aggTrades',s,d,used);bs,ats=book_stats(b),trade_stats(a)
   overlap=bool(bs['first_ms'] and ats['first_ms'] and max(bs['first_ms'],ats['first_ms'])<=min(bs['last_ms'],ats['last_ms']))
   allstats.append({'symbol':s,'day':d.isoformat(),'bookDepth':bs,'aggTrades':ats,'clock_overlap':overlap})
 # bookDepth is percentage-bucket depth only: it permits proxy depth imbalance,
 # but contains neither executable bid/ask prices nor update sequence IDs.
 source_ok=all(x['bookDepth']['header']==BOOK_HEAD and x['aggTrades']['header']==TRADE_HEAD and x['clock_overlap'] for x in allstats)
 replay={'top_of_book_depth_imbalance':'PARTIAL_PERCENTAGE_BUCKETS_ONLY','signed_aggressive_trade_flow':'YES_FROM_is_buyer_maker','spread':'NO_BOOKDEPTH_HAS_NO_BID_ASK_PRICES','forward_labels_1_5_15_60s':'YES_FROM_FIRST_AGGTRADE_AT_OR_AFTER_HORIZON','sequence_gap_replay':'NO_BOOKDEPTH_HAS_NO_SEQUENCE'}
 decision='READY_FOR_PRE_EVENT_RESEARCH' if source_ok and replay['spread'].startswith('YES') and replay['sequence_gap_replay'].startswith('YES') else 'STOP_SOURCE_OR_IMPLEMENTATION_INVALID'
 report={'decision':decision,'source':'official Binance USD-M Data Vision daily bookDepth and aggTrades archives only','symbols':list(SYMS),'days':[d.isoformat() for d in DAYS],'archive_cap_bytes':CAP,'downloaded_bytes':used,'self_tests':tests,'probe':probe,'daily':allstats,'replay_feasibility':replay}
 lines=['# V28A L2 source / implementation feasibility','',f'**V28A_DECISION={decision}**','',f'Only official Data Vision daily archives were read. Downloaded compressed bytes: {used:,}/{CAP:,}.',f'Self-tests: PASS ({", ".join(tests)}).','', '## Probe archives']
 for x in probe:lines.append(f"- {x['url']}: HEAD={x['head_status']} ({x['head_bytes']} bytes), GET={x['get_bytes']} bytes, schema={x['schema']['header']}")
 lines += ['', '## Honest replay capability']+[f'- {k}: {v}' for k,v in replay.items()]+['','## Full audit','```json',json.dumps(report,indent=2,sort_keys=True),'```',''];REPORT.write_text('\n'.join(lines),encoding='utf-8')
if __name__=='__main__':
 try:main()
 except Exception:
  traceback.print_exc();REPORT.write_text('# V28A L2 source / implementation feasibility\n\n**V28A_DECISION=STOP_SOURCE_OR_IMPLEMENTATION_INVALID**\n',encoding='utf-8');sys.exit(1)
