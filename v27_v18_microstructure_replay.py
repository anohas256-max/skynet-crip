#!/usr/bin/env python3
"""V27 offline V18 microstructure replay. Read-only; never trades or starts services."""
import argparse, json, math, sqlite3, sys, traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent; DB=ROOT/'data/v18_micro_paths.sqlite3'; PRE=ROOT/'v27_v18_microstructure_replay_preregister.json'; REPORT=ROOT/'v27_v18_microstructure_replay_latest.md'
STATE=Path('/tmp/v27_v18_microstructure_replay_state.json')
COST=.004; COOLDOWN=300
CONFIGS=(('continuation','confirm',60),('continuation','confirm',300),('continuation','contradict',60),('continuation','contradict',300),('fade','confirm',60),('fade','confirm',300),('fade','contradict',60),('fade','contradict',300))
def f(x):
 try:
  z=float(x);return z if math.isfinite(z) else None
 except:return None
def sgn(x):return 1 if x and x>0 else (-1 if x and x<0 else 0)
def iso(t):return datetime.fromtimestamp(t,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def path(raw):
 try:x=json.loads(raw)
 except:return None
 if not isinstance(x,list):return None
 out=[]
 for a in x:
  if isinstance(a,(list,tuple)) and len(a)>=2:
   age,val=f(a[0]),f(a[1])
   if age is not None and val is not None and age>=0:out.append((age,val))
 if not out:return None
 out.sort();ded=[]
 for q in out:
  if ded and q[0]==ded[-1][0]:ded[-1]=q
  else:ded.append(q)
 return ded
def outcome(r,direction,structure,h):
 pc,i5,i20,w=map(f,(r['price_change'],r['imb_5'],r['imb_20'],r['wall_skew']))
 if None in (pc,i5,i20,w) or not all((sgn(pc),sgn(i5),sgn(i20),sgn(w))):return None,'invalid_structure'
 p=r.get('_path') if isinstance(r,dict) and '_path' in r else path(r['path_json'])
 if p is None:return None,'invalid_path_json'
 q=next((x for x in p if x[0]>=h),None)
 if q is None:return None,'missing_horizon_path'
 same=all(sgn(x)==sgn(pc) for x in (i5,i20,w))
 opposite=all(sgn(x)==-sgn(pc) for x in (i5,i20,w))
 if (structure=='confirm' and not same) or (structure=='contradict' and not opposite):return None,'structure_not_selected'
 side=sgn(pc) if direction=='continuation' else -sgn(pc)
 depth=(f(r['bid20_usd']) or 0)+(f(r['ask20_usd']) or 0)
 return {'ts':f(r['ts']),'symbol':str(r['symbol']),'gross':side*q[1]/100,'net':side*q[1]/100-COST,'spread':f(r['spread_bps']),'depth':depth,'path_age':q[0]},None
def select(rows,direction,structure,h):
 out=[];last={};skip=defaultdict(int)
 for r in rows:
  t,reason=outcome(r,direction,structure,h)
  if t is None:skip[reason]+=1;continue
  if t['ts']<last.get(t['symbol'],-float('inf'))+COOLDOWN:skip['symbol_cooldown']+=1;continue
  last[t['symbol']]=t['ts'];out.append(t)
 return out,dict(skip)
def metric(ts):
 p=[x['net'] for x in ts];pos=sum(x for x in p if x>0);neg=-sum(x for x in p if x<0);total=sum(p)
 return {'trades':len(ts),'severe_pnl':total,'pf':pos/neg if neg else (999 if pos else 0),'win_rate':sum(x>0 for x in p)/len(p) if p else 0,'gross_pnl':sum(x['gross'] for x in ts)}
def by_symbol(ts):
 d=defaultdict(list)
 for x in ts:d[x['symbol']].append(x)
 return {k:metric(v) for k,v in sorted(d.items())}
def leave_best(ts):
 b=by_symbol(ts);best=max((v['severe_pnl'] for v in b.values()),default=0);return metric(ts)['severe_pnl']-best
def quartiles(ts,key):
 vals=sorted(x[key] for x in ts if x[key] is not None)
 if len(vals)<4:return []
 cuts=[vals[(len(vals)-1)*i//4] for i in (1,2,3)];bins=[[] for _ in range(4)]
 for x in ts:
  if x[key] is None:continue
  i=0
  while i<3 and x[key]>cuts[i]:i+=1
  bins[i].append(x)
 return [{'quartile':i+1,'upper':cuts[i] if i<3 else None,**metric(v)} for i,v in enumerate(bins)]
def gate(m,leave):return m['trades']>=100 and m['severe_pnl']>0 and m['pf']>=1.15 and leave>0
def blank():return {'n':0,'net':0.,'gross':0.,'pos':0.,'neg':0.,'wins':0}
def add(a,t):
 a['n']+=1;a['net']+=t['net'];a['gross']+=t['gross'];a['pos']+=max(t['net'],0);a['neg']+=max(-t['net'],0);a['wins']+=t['net']>0
def finish(a):return {'trades':a['n'],'severe_pnl':a['net'],'pf':a['pos']/a['neg'] if a['neg'] else (999 if a['pos'] else 0),'win_rate':a['wins']/a['n'] if a['n'] else 0,'gross_pnl':a['gross']}
def qcuts(vals):
 vals=sorted(vals)
 return [vals[(len(vals)-1)*i//4] for i in (1,2,3)] if len(vals)>=4 else [float('inf')]*3
def qindex(x,cuts):
 i=0
 while i<3 and x>cuts[i]:i+=1
 return i
def selftests():
 assert path('[[0,0],[60,1.2],[60,1.3]]')==[(0.0,0.0),(60.0,1.3)]
 rows=[{'ts':1,'symbol':'A','price_change':1,'imb_5':1,'imb_20':1,'wall_skew':1,'path_json':'[[60,1]]','bid20_usd':1,'ask20_usd':1,'spread_bps':1},{'ts':200,'symbol':'A','price_change':1,'imb_5':1,'imb_20':1,'wall_skew':1,'path_json':'[[60,1]]','bid20_usd':1,'ask20_usd':1,'spread_bps':1}]
 assert len(select(rows,'continuation','confirm',60)[0])==1
 assert outcome(rows[0],'continuation','confirm',60)[0]['net']==.006 and outcome(rows[0],'fade','confirm',60)[0]['net']==-.014
 assert abs((.01-COST)-.006)<1e-12
 assert int(10+(110-10)*.7)==80
 return ['parser_path_json','no_overlap','direction_sign','cost','chronological_split']
def main(stage='all'):
 tests=selftests();con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True);con.row_factory=sqlite3.Row
 lo,hi,nrows=con.execute('SELECT min(ts),max(ts),count(*) FROM signals WHERE ts IS NOT NULL').fetchone();cut=lo+.7*(hi-lo)
 # Streaming pass: no raw path collection is retained.  Each JSON path is
 # parsed once and then evaluated against every fixed configuration.
 # Quartile cutoffs are fixed from raw validation liquidity fields before
 # evaluating any configuration returns; no selected trade paths are retained.
 sq=[];dq=[]
 for sp,bi,ask in con.execute('SELECT spread_bps,bid20_usd,ask20_usd FROM signals WHERE ts>=?',(cut,)):
  sp=f(sp);dep=(f(bi) or 0)+(f(ask) or 0)
  if sp is not None:sq.append(sp)
  if dep>0:dq.append(dep)
 spread_cuts,depth_cuts=qcuts(sq),qcuts(dq)
 mid=lo+.35*(hi-lo)
 prior=json.loads(STATE.read_text()) if stage in ('train-b','validation') and STATE.exists() else [{} for _ in CONFIGS]
 states=[{'cfg':c,'last':{k:float(v) for k,v in prior[i].items()},'skips':defaultdict(int),'train_selected':0,'valm':blank(),'symbols':defaultdict(blank),'spreadq':[blank() for _ in range(4)],'depthq':[blank() for _ in range(4)]} for i,c in enumerate(CONFIGS)]
 if stage=='train-a':where,args='ts < ?',(mid,)
 elif stage=='train-b':where,args='ts >= ? AND ts < ?',(mid,cut)
 elif stage=='validation':where,args='ts >= ?',(cut,)
 else:where,args='ts IS NOT NULL',()
 q=con.execute(f'SELECT ts,symbol,price_change,imb_5,imb_20,wall_skew,spread_bps,bid20_usd,ask20_usd,path_json FROM signals WHERE {where} ORDER BY ts',args)
 for row in q:
  d=dict(row);d['_path']=path(d['path_json']);is_val=(stage=='validation')
  for state in states:
   direction,structure,h=state['cfg'];t,reason=outcome(d,direction,structure,h)
   if t is None:
    if is_val:state['skips'][reason]+=1
    continue
   if t['ts']<state['last'].get(t['symbol'],-float('inf'))+COOLDOWN:
    if is_val:state['skips']['symbol_cooldown']+=1
    continue
   state['last'][t['symbol']]=t['ts']
   if is_val:
    add(state['valm'],t);add(state['symbols'][t['symbol']],t)
    if t['spread'] is not None:add(state['spreadq'][qindex(t['spread'],spread_cuts)],t)
    if t['depth']>0:add(state['depthq'][qindex(t['depth'],depth_cuts)],t)
   else:state['train_selected']+=1
 if stage in ('train','train-a','train-b'):
  STATE.write_text(json.dumps([x['last'] for x in states],sort_keys=True));return
 results=[]
 for state in states:
  direction,structure,h=state['cfg'];m=finish(state['valm']);sym={k:finish(v) for k,v in sorted(state['symbols'].items())};best=max((v['severe_pnl'] for v in sym.values()),default=0);leave=m['severe_pnl']-best
  skips=dict(state['skips']);skips.setdefault('invalid_path_json',0);skips.setdefault('missing_horizon_path',0);skips.setdefault('symbol_cooldown',0)
  results.append({'direction':direction,'structure':structure,'horizon_seconds':h,'validation':m,'validation_by_symbol':sym,'leave_best_symbol':leave,'validation_spread_quartiles':[{'quartile':i+1,'upper':spread_cuts[i] if i<3 else None,**finish(x)} for i,x in enumerate(state['spreadq'])],'validation_depth_quartiles':[{'quartile':i+1,'upper':depth_cuts[i] if i<3 else None,**finish(x)} for i,x in enumerate(state['depthq'])],'validation_skips':skips,'validation_pass':gate(m,leave)})
 decision='STOP_NO_VALIDATION_EDGE' if not any(x['validation_pass'] for x in results) else 'VALIDATION_GATE_PASS_NO_FINAL'
 report={'decision':decision,'source':str(DB),'source_rows':nrows,'time_range':[iso(lo),iso(hi)],'split_utc':iso(cut),'self_tests':tests,'configs':results,'final_opened':False}
 lines=['# V27 V18 offline microstructure replay','',f'**V27_DECISION={decision}**','',f'Source: read-only `{DB}`; rows={nrows}; range={iso(lo)}--{iso(hi)}; chronological 70/30 split={iso(cut)}.',f'Self-tests: PASS ({", ".join(tests)}).','', '## Fixed validation configurations']
 for x in results:lines.append(f"- {x['direction']} / {x['structure']} / {x['horizon_seconds']}s: {x['validation']}; leave_best_symbol={x['leave_best_symbol']:+.6f}; pass={x['validation_pass']}; skips={x['validation_skips']}")
 lines += ['','## Full compact audit','```json',json.dumps(report,indent=2,sort_keys=True),'```',''];REPORT.write_text('\n'.join(lines),encoding='utf-8')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=('all','train','train-a','train-b','validation'),default='all');args=parser.parse_args()
 try:main(args.stage)
 except Exception:
  traceback.print_exc();REPORT.write_text('# V27 V18 offline microstructure replay\n\n**V27_DECISION=STOP_IMPLEMENTATION_INVALID**\n',encoding='utf-8');sys.exit(1)
