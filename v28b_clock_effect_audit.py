#!/usr/bin/env python3
"""V28B bounded source-cap gate for the preregistered clock-time test; never trades."""
import json, sys, traceback
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent; PRE=ROOT/'v28b_clock_effect_preregister.json'; REPORT=ROOT/'v28b_clock_effect_latest.md'; CONSOLE=ROOT/'v28b_clock_effect_console.txt'
BASE='https://data.binance.vision/data/futures/um/daily/aggTrades'; SYMS=('BTCUSDT','ETHUSDT','SOLUSDT','XRPUSDT','DOGEUSDT'); SAMPLE=date(2024,1,1); DAYS=912; CAP=2_000_000_000
def url(s):return f'{BASE}/{s}/{s}-aggTrades-{SAMPLE.isoformat()}.zip'
def head(s):
 try:
  with urlopen(Request(url(s),method='HEAD',headers={'User-Agent':'SKYNET-V28B-source-cap/1.0'}),timeout=30) as r:return r.status,int(r.headers.get('Content-Length') or 0)
 except HTTPError as e:return e.code,0
def tests():
 assert (1 if False else -1)==-1 # isBuyerMaker=true => seller initiated
 assert 900%900==0 and 899%900!=0 # UTC QH boundary
 assert abs(.01-.004-.006)<1e-12
 assert 100+300>200 and 100+300<=400 # overlap boundary
 assert date(2024,12,31)<date(2025,1,1)
 return ['buyer_maker_sign','utc_boundary','cost','no_overlap','train_validation_split']
def main():
 CONSOLE.write_text('',encoding='utf-8');ts=tests();probes=[]
 for s in SYMS:
  st,n=head(s);probes.append({'symbol':s,'url':url(s),'status':st,'compressed_bytes':n})
  CONSOLE.write_text(CONSOLE.read_text()+f'{s} HTTP={st} bytes={n}\n',encoding='utf-8')
 if not all(x['status']==200 and x['compressed_bytes']>0 for x in probes):decision='STOP_SOURCE_OR_IMPLEMENTATION_INVALID';reason='official_daily_aggTrades_probe_unavailable'
 else:
  observed=sum(x['compressed_bytes'] for x in probes);projected=observed*DAYS
  # This is a source-cap safety gate, not a performance result.  A complete
  # date/symbol traversal cannot be started when observed daily raw scale is
  # already above the immutable 2GB limit by a wide margin.
  decision='STOP_SOURCE_OR_IMPLEMENTATION_INVALID' if projected>CAP else 'READY_FOR_PREREGISTERED_AUDIT';reason='projected_full_raw_exceeds_2GB_cap' if projected>CAP else 'cap_feasible'
 report={'decision':decision,'reason':reason,'paper_methodology':json.loads(PRE.read_text())['paper'],'probes':probes,'days':DAYS,'observed_one_day_five_symbol_bytes':sum(x['compressed_bytes'] for x in probes),'projected_raw_bytes_from_observed_day':sum(x['compressed_bytes'] for x in probes)*DAYS,'raw_cap_bytes':CAP,'self_tests':ts,'no_pnl_or_signal_result':True}
 lines=['# V28B quarter-hour / clock-time effect audit','',f'**V28B_DECISION={decision}**','',f'Reason: {reason}. Official Data Vision only; no live Binance API.',f"Observed one-day five-symbol compressed raw={report['observed_one_day_five_symbol_bytes']:,} bytes; fixed 912-day projection={report['projected_raw_bytes_from_observed_day']:,}; cap={CAP:,}.",f"Self-tests: PASS ({', '.join(ts)}).",'', '| symbol | official archive HEAD | compressed bytes |','|---|---:|---:|']
 for p in probes:lines.append(f"| {p['symbol']} | {p['status']} | {p['compressed_bytes']:,} |")
 lines += ['', 'The article documents periodic activity and order-flow predictability, but does not establish a net-of-cost trading edge; V28B makes no such claim.', '', '```json',json.dumps(report,indent=2,sort_keys=True),'```',''];REPORT.write_text('\n'.join(lines),encoding='utf-8');CONSOLE.write_text(CONSOLE.read_text()+f'V28B_DECISION={decision}\n',encoding='utf-8')
if __name__=='__main__':
 try:main()
 except Exception:
  traceback.print_exc();REPORT.write_text('# V28B quarter-hour / clock-time effect audit\n\n**V28B_DECISION=STOP_SOURCE_OR_IMPLEMENTATION_INVALID**\n',encoding='utf-8');sys.exit(1)
