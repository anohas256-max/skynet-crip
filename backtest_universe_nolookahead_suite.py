import os, csv, json, zipfile, argparse, asyncio, bisect
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv("/root/skynet/.env")
ROOT = Path("/root/skynet")
OUT_DIR = ROOT / "data" / "backtest" / "universe_nolookahead_suite"

ENTRY_CASES = [
    {"entry_case":"TREND040_PC055_VOL25_SCORE5_INIT_RUG015","min_score":5,"need_initiative":1,"max_pc":0.55,"max_vol":25.0,"rug":-0.15,"min_trend15":0.40,"min_btc5":-999.0},
    {"entry_case":"BASE_PC055_VOL25_SCORE5_INIT_RUG015","min_score":5,"need_initiative":1,"max_pc":0.55,"max_vol":25.0,"rug":-0.15,"min_trend15":-999.0,"min_btc5":-999.0},
    {"entry_case":"TREND040_BTC0_PC055_VOL25_SCORE5_INIT_RUG015","min_score":5,"need_initiative":1,"max_pc":0.55,"max_vol":25.0,"rug":-0.15,"min_trend15":0.40,"min_btc5":0.0},
    {"entry_case":"TREND040_PC065_VOL35_SCORE5_INIT_RUG015","min_score":5,"need_initiative":1,"max_pc":0.65,"max_vol":35.0,"rug":-0.15,"min_trend15":0.40,"min_btc5":-999.0},
]
CONFIRM_MODES = ["WAIT1_CLOSE","WAIT2_FIRST_CLOSE","WAIT3_FIRST_CLOSE","WAIT2_BREAK_HIGH"]
UNIVERSE_MODES = [
    "CURRENT_STATIC_TOP20","CURRENT_STATIC_TOP30","CURRENT_STATIC_TOP40",
    "PREV_DAY_TURNOVER_TOP20","PREV_DAY_TURNOVER_TOP30","PREV_DAY_TURNOVER_TOP40",
    "PREV_DAY_ACTIVITY_TOP20","PREV_DAY_ACTIVITY_TOP30","PREV_DAY_ACTIVITY_TOP40",
    "ROLL24_TURNOVER_TOP20","ROLL24_TURNOVER_TOP30","ROLL24_TURNOVER_TOP40",
    "ROLL24_ACTIVITY_TOP20","ROLL24_ACTIVITY_TOP30","ROLL24_ACTIVITY_TOP40",
]

def utc_iso(ts): return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
def day_key(ts): return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
def parse_target(v):
    v=str(v).strip()
    if v.startswith("-") and v[1:].isdigit(): return int(v)
    if v.isdigit(): return int(v)
    return v
def parse_list_int(s): return [int(x.strip()) for x in str(s).split(",") if x.strip()]
def parse_list_str(s): return [x.strip() for x in str(s).split(",") if x.strip()]
def clamp(x, lo, hi): return max(lo, min(hi, x))
def row_volume(row):
    for k in ("v","volume","vol","base_volume"):
        if k in row:
            try: return float(row[k])
            except Exception: pass
    return 0.0
def quote_turnover(row):
    c=float(row.get("c",0) or 0)
    return max(0.0, c*row_volume(row))
def range_pct(row):
    c=float(row.get("c",0) or 0)
    if c<=0: return 0.0
    return max(0.0, (float(row.get("h",c))-float(row.get("l",c)))/c*100.0)
def activity_score(row):
    return quote_turnover(row)*(1.0+min(range_pct(row),5.0))
def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def pre_range_pct(bt, rows, entry_i, lookback):
    start=max(0, entry_i-lookback)
    sub=rows[start:entry_i]
    if not sub: return 0.0
    hi=max(r["h"] for r in sub); lo=min(r["l"] for r in sub); close=rows[entry_i]["c"]
    return 0.0 if close<=0 else (hi-lo)/close*100.0

def atr5b_params(bt, rows, entry_i):
    rng5=pre_range_pct(bt, rows, entry_i, 5); rng10=pre_range_pct(bt, rows, entry_i, 10)
    sl=clamp(rng5*0.85,0.40,0.85)
    return {"sl":sl,"partial_at":clamp(sl*1.50,0.70,1.10),"partial_size":0.50,
            "runner_tp":clamp(sl*4.50,2.00,3.20),"runner_stop":clamp(sl*0.25,0.08,0.20),
            "time":45,"pre_range5":rng5,"pre_range10":rng10}

def simulate_atr5b(bt, rows, entry_i):
    p=atr5b_params(bt, rows, entry_i); entry=rows[entry_i]["c"]
    max_profit=0.0; max_loss=0.0; partial_done=False
    for j in range(entry_i+1, min(entry_i+int(p["time"])+1, len(rows))):
        held=j-entry_i; r=rows[j]
        high=bt.pct(r["h"], entry); low=bt.pct(r["l"], entry); close=bt.pct(r["c"], entry)
        max_profit=max(max_profit, high); max_loss=min(max_loss, low)
        if not partial_done and low <= -p["sl"]:
            return {"reason":"SL","exit_pct":-p["sl"],"mfe":max_profit,"mae":max_loss,"held":held,**p}
        if partial_done:
            if low <= p["runner_stop"]:
                weighted=p["partial_size"]*p["partial_at"]+(1-p["partial_size"])*p["runner_stop"]
                return {"reason":"DYN_RUNNER_STOP","exit_pct":weighted,"mfe":max_profit,"mae":max_loss,"held":held,**p}
            if high >= p["runner_tp"]:
                weighted=p["partial_size"]*p["partial_at"]+(1-p["partial_size"])*p["runner_tp"]
                return {"reason":"DYN_RUNNER_TP","exit_pct":weighted,"mfe":max_profit,"mae":max_loss,"held":held,**p}
        if not partial_done and high >= p["partial_at"]:
            partial_done=True
    last_i=min(entry_i+int(p["time"]), len(rows)-1)
    close=bt.pct(rows[last_i]["c"], entry)
    if partial_done:
        weighted=p["partial_size"]*p["partial_at"]+(1-p["partial_size"])*close
        reason="DYN_TIME_PARTIAL"
    else:
        weighted=close; reason="TIME"
    return {"reason":reason,"exit_pct":weighted,"mfe":max_profit,"mae":max_loss,"held":last_i-entry_i,**p}

def build_prev_day_universe(symbols, rows_by_symbol, top_values):
    daily={}
    for sym in symbols:
        for r in rows_by_symbol.get(sym, []):
            d=day_key(r["t"]); daily.setdefault(d,{}).setdefault(sym,{"turnover":0.0,"activity":0.0})
            daily[d][sym]["turnover"] += quote_turnover(r)
            daily[d][sym]["activity"] += activity_score(r)
    days=sorted(daily.keys()); out={}
    for idx,d in enumerate(days):
        if idx==0: continue
        prev=days[idx-1]
        rec=[{"symbol":s,**vals} for s,vals in daily.get(prev,{}).items()]
        by_t=sorted(rec, key=lambda x:x["turnover"], reverse=True)
        by_a=sorted(rec, key=lambda x:x["activity"], reverse=True)
        out[d]={}
        for n in top_values:
            out[d][f"PREV_DAY_TURNOVER_TOP{n}"]={r["symbol"] for r in by_t[:n]}
            out[d][f"PREV_DAY_ACTIVITY_TOP{n}"]={r["symbol"] for r in by_a[:n]}
    return out

def build_prefix(rows_by_symbol):
    pref={}
    for sym,rows in rows_by_symbol.items():
        times=[]; ct=[0.0]; ca=[0.0]; st=0.0; sa=0.0
        for r in rows:
            times.append(int(r["t"]))
            st += quote_turnover(r); sa += activity_score(r)
            ct.append(st); ca.append(sa)
        pref[sym]={"times":times,"turnover":ct,"activity":ca}
    return pref
def rolling_sum(item, metric, t, window):
    times=item["times"]; cum=item[metric]
    right=bisect.bisect_left(times,int(t))
    left=bisect.bisect_left(times,int(t)-int(window))
    return cum[right]-cum[left]
def rolling_universe(symbols, prefix, t, n, metric):
    vals=[]
    for s in symbols:
        if s not in prefix: continue
        vals.append((rolling_sum(prefix[s],metric,t,24*3600),s))
    vals.sort(reverse=True)
    return {s for v,s in vals[:n] if v>0}
def mode_top_n(mode):
    for n in (20,30,40,50):
        if mode.endswith(f"TOP{n}"): return n
    return 30
def mode_metric(mode): return "activity" if "ACTIVITY" in mode else "turnover"

def apply_entry_case(bt, rows, raw, entry_case, confirm_mode):
    if raw.get("score",-999) < entry_case["min_score"]: return None
    if entry_case["need_initiative"] and not raw.get("initiative",0): return None
    if raw.get("price_change",999.0) > entry_case["max_pc"]: return None
    if raw.get("vol_ratio",999.0) > entry_case["max_vol"]: return None
    if raw.get("trend15",0.0) < entry_case["min_trend15"]: return None
    if raw.get("btc5",0.0) < entry_case["min_btc5"]: return None
    i=raw["i"]; sig=rows[i]; sig_close=sig["c"]; sig_high=sig["h"]
    if sig_close<=0: return None
    if confirm_mode=="WAIT1_CLOSE": max_wait=1; break_high=False
    elif confirm_mode=="WAIT2_FIRST_CLOSE": max_wait=2; break_high=False
    elif confirm_mode=="WAIT3_FIRST_CLOSE": max_wait=3; break_high=False
    elif confirm_mode=="WAIT2_BREAK_HIGH": max_wait=2; break_high=True
    else: max_wait=1; break_high=False
    min_low=999.0; entry_i=None
    for k in range(1,max_wait+1):
        if i+k >= len(rows): break
        n1=rows[i+k]
        low_from_signal=bt.pct(n1["l"], sig_close)
        min_low=min(min_low, low_from_signal)
        if min_low <= entry_case["rug"]: return None
        ok = n1["c"] > (sig_high if break_high else sig_close)
        if ok:
            entry_i=i+k; break
    if entry_i is None: return None
    s=dict(raw); s["entry_case"]=entry_case["entry_case"]; s["confirm_mode"]=confirm_mode
    s["confirm_delay_min"]=entry_i-i; s["confirm_min_low"]=min_low
    s["i"]=entry_i; s["t"]=rows[entry_i]["t"]; s["entry"]=rows[entry_i]["c"]
    return s

def apply_max_open(records, max_open):
    open_until=[]; accepted=[]; skipped=0
    for r in sorted(records, key=lambda x:(x["entry_t"],x["symbol"])):
        t=r["entry_t"]; open_until=[x for x in open_until if x>t]
        if len(open_until)>=max_open:
            skipped+=1; continue
        accepted.append(r); open_until.append(r["exit_t"])
    return accepted, skipped

def summarize(records, skipped=0):
    out={"trades":0,"wins":0,"losses":0,"gross":0.0,"net":0.0,"costs":0.0,"avg_net":0.0,"winrate":0.0,"avg_mfe":0.0,"avg_mae":0.0,"skipped_by_maxopen":skipped}
    for k in ["SL","TIME","DYN_RUNNER_STOP","DYN_RUNNER_TP","DYN_TIME_PARTIAL"]: out[k]=0
    for r in records:
        out["trades"]+=1; out["gross"]+=r["gross"]; out["net"]+=r["net"]; out["costs"]+=r["costs"]
        out["avg_mfe"]+=r["mfe"]; out["avg_mae"]+=r["mae"]; out[r["reason"]]=out.get(r["reason"],0)+1
        if r["net"]>0: out["wins"]+=1
        elif r["net"]<0: out["losses"]+=1
    if out["trades"]:
        n=out["trades"]; out["avg_net"]=out["net"]/n; out["winrate"]=out["wins"]/n*100; out["avg_mfe"]/=n; out["avg_mae"]/=n
    return out

async def send_to_tg(zip_path, caption, target):
    from telethon import TelegramClient
    api_id=os.getenv("API_ID"); api_hash=os.getenv("API_HASH")
    if not api_id or not api_hash:
        print("⚠️ Telegram skipped: API_ID/API_HASH missing."); return False
    async with TelegramClient(os.getenv("BACKTEST_TG_SESSION","backtest_sender_session"), int(api_id), api_hash) as client:
        await client.send_file(parse_target(target), str(zip_path), caption=caption)
    return True

def current_static(symbols, mode):
    if mode=="CURRENT_STATIC_TOP20": return set(symbols[:20])
    if mode=="CURRENT_STATIC_TOP30": return set(symbols[:30])
    if mode=="CURRENT_STATIC_TOP40": return set(symbols[:40])
    return set(symbols)

async def run(args):
    import backtest_1m as bt
    import aiohttp
    if args.spread_bps is not None: bt.SPREAD_BPS=float(args.spread_bps)
    if args.slippage_bps is not None: bt.SLIPPAGE_BPS=float(args.slippage_bps)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    end_ts=int(datetime.now(timezone.utc).timestamp()) if not args.end else int(datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc).timestamp())
    start_ts=end_ts-args.days*24*3600
    max_open_values=parse_list_int(args.max_open) or [1,2,3]
    universe_modes=parse_list_str(args.universe_modes) or UNIVERSE_MODES
    confirm_modes=parse_list_str(args.confirm_modes) or CONFIRM_MODES
    print(f"🚀 SKYNET UNIVERSE NO-LOOKAHEAD | days={args.days} broad_top={args.broad_top} max_open={max_open_values}")
    print(f"Costs: spread={bt.SPREAD_BPS}bps slippage={bt.SLIPPAGE_BPS}bps")
    async with aiohttp.ClientSession() as session:
        if args.symbols:
            symbols=[s.strip().upper() for s in args.symbols.split(",") if s.strip()]
            symbols=[s if s.endswith("_USDT") else f"{s}_USDT" for s in symbols]
        else:
            symbols=await bt.get_top_symbols(session,args.broad_top)
        symbols=[s for s in symbols if s!="BTC_USDT"]
        print(f"Symbols: {len(symbols)}")
        btc_rows=await bt.download_klines(session,"BTC_USDT",start_ts,end_ts,use_cache=not args.no_cache)
        btc_close_by_t,btc_times=bt.prepare_btc_context(btc_rows)
        rows_by_symbol={}; raw_signals_by_symbol={}
        for idx,sym in enumerate(symbols,1):
            print(f"[{idx}/{len(symbols)}] {sym} downloading/generating...")
            rows=await bt.download_klines(session,sym,start_ts,end_ts,use_cache=not args.no_cache)
            if len(rows)<200:
                print(f"  skip candles={len(rows)}"); continue
            raw=bt.generate_signals(sym,rows,btc_close_by_t,btc_times)
            rows_by_symbol[sym]=rows; raw_signals_by_symbol[sym]=raw
            print(f"  candles={len(rows)} raw_signals={len(raw)}")
            await asyncio.sleep(0.05)
    actual_symbols=list(rows_by_symbol.keys())
    prev_map=build_prev_day_universe(actual_symbols, rows_by_symbol, [20,30,40,50])
    prefix=build_prefix(rows_by_symbol); universe_cache={}
    def allowed(sym,t,mode):
        if mode.startswith("CURRENT_STATIC"): return sym in current_static(actual_symbols,mode)
        if mode.startswith("PREV_DAY"): return sym in prev_map.get(day_key(t),{}).get(mode,set())
        if mode.startswith("ROLL24"):
            key=(mode,int(t))
            if key not in universe_cache:
                universe_cache[key]=rolling_universe(actual_symbols,prefix,t,mode_top_n(mode),mode_metric(mode))
            return sym in universe_cache[key]
        return True
    records_by_key={}; all_summary=[]; all_trades=[]
    for sym,raws in raw_signals_by_symbol.items():
        rows=rows_by_symbol[sym]
        for raw in raws:
            for umode in universe_modes:
                if not allowed(sym,raw["t"],umode): continue
                for ec in ENTRY_CASES:
                    for cmode in confirm_modes:
                        s=apply_entry_case(bt,rows,raw,ec,cmode)
                        if not s: continue
                        result=simulate_atr5b(bt,rows,s["i"])
                        exit_i=min(s["i"]+int(result["held"]),len(rows)-1)
                        gross,net,costs=bt.calc_net_pnl(result["exit_pct"])
                        rec={
                            "universe_mode":umode,"entry_case":ec["entry_case"],"confirm_mode":cmode,"symbol":sym,"time":utc_iso(s["t"]),"entry_t":s["t"],"exit_t":rows[exit_i]["t"],
                            "score":s.get("score",0),"price_change":s.get("price_change",0.0),"vol_ratio":s.get("vol_ratio",0.0),"trend15":s.get("trend15",0.0),"btc5":s.get("btc5",0.0),
                            "structure":s.get("structure",0),"initiative":s.get("initiative",0),"confirm_delay_min":s.get("confirm_delay_min",0),"confirm_min_low":s.get("confirm_min_low",0.0),
                            "reason":result["reason"],"exit_pct":result["exit_pct"],"mfe":result["mfe"],"mae":result["mae"],"held":result["held"],
                            "sl":result["sl"],"partial_at":result["partial_at"],"runner_tp":result["runner_tp"],"runner_stop":result["runner_stop"],"time_stop":result["time"],
                            "pre_range5":result.get("pre_range5",0.0),"pre_range10":result.get("pre_range10",0.0),"gross":gross,"net":net,"costs":costs
                        }
                        key=(umode,ec["entry_case"],cmode); records_by_key.setdefault(key,[]).append(rec)
    for (umode,ecase,cmode),records in records_by_key.items():
        for mo in max_open_values:
            acc,sk=apply_max_open(records,mo); sm=summarize(acc,sk)
            sm.update({"universe_mode":umode,"entry_case":ecase,"confirm_mode":cmode,"max_open":mo,"days":args.days,"broad_top":args.broad_top,"spread_bps":bt.SPREAD_BPS,"slippage_bps":bt.SLIPPAGE_BPS})
            all_summary.append(sm)
            for r in acc:
                rr=dict(r); rr["max_open"]=mo; all_trades.append(rr)
    all_summary.sort(key=lambda x:x["net"], reverse=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir=OUT_DIR/f"universe_nolookahead_{stamp}"; run_dir.mkdir(parents=True,exist_ok=True)
    summary_path=run_dir/f"universe_nolookahead_summary_{stamp}.csv"; trades_path=run_dir/f"universe_nolookahead_trades_{stamp}.csv"; manifest_path=run_dir/"manifest.json"; zip_path=run_dir/f"UNIVERSE_NOLOOKAHEAD_RESULTS_{stamp}.zip"
    summary_fields=["universe_mode","entry_case","confirm_mode","max_open","days","broad_top","spread_bps","slippage_bps","trades","skipped_by_maxopen","wins","losses","winrate","gross","net","costs","avg_net","avg_mfe","avg_mae","SL","TIME","DYN_RUNNER_STOP","DYN_RUNNER_TP","DYN_TIME_PARTIAL"]
    trade_fields=["universe_mode","entry_case","confirm_mode","max_open","time","symbol","score","price_change","vol_ratio","trend15","btc5","structure","initiative","confirm_delay_min","confirm_min_low","reason","exit_pct","mfe","mae","held","sl","partial_at","runner_tp","runner_stop","time_stop","pre_range5","pre_range10","gross","net","costs","entry_t","exit_t"]
    write_csv(summary_path,all_summary,summary_fields); write_csv(trades_path,all_trades,trade_fields)
    manifest={"created_utc":stamp,"days":args.days,"broad_top":args.broad_top,"symbols":args.symbols,"max_open":max_open_values,"universe_modes":universe_modes,"confirm_modes":confirm_modes,"entry_cases":ENTRY_CASES,"spread_bps":bt.SPREAD_BPS,"slippage_bps":bt.SLIPPAGE_BPS,"summary_file":summary_path.name,"trades_file":trades_path.name}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(summary_path,summary_path.name); z.write(trades_path,trades_path.name); z.write(manifest_path,manifest_path.name)
    print("\n=== TOP RESULTS ===")
    for r in all_summary[:35]:
        print(f"{r['universe_mode']:<24} MO:{r['max_open']} {r['entry_case']:<48} {r['confirm_mode']:<18} Net:{r['net']:+.2f}$ Tr:{r['trades']} WR:{r['winrate']:.1f}% Avg:{r['avg_net']:+.3f}$")
    print("\nZIP:",zip_path)
    if args.send_tg:
        caption=f"📦 SKYNET UNIVERSE NO-LOOKAHEAD\n" f"days={args.days} broad_top={args.broad_top} symbols={args.symbols or '-'}\n" f"max_open={args.max_open}\n" f"costs spread={bt.SPREAD_BPS} slip={bt.SLIPPAGE_BPS}"
        try: await send_to_tg(zip_path,caption,args.tg_target); print("📤 Sent to Telegram")
        except Exception as e: print(f"⚠️ Telegram send failed: {type(e).__name__}: {e}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--days",type=int,default=30); p.add_argument("--broad-top",type=int,default=40); p.add_argument("--symbols",default="")
    p.add_argument("--max-open",default="1,2,3"); p.add_argument("--universe-modes",default=",".join(UNIVERSE_MODES)); p.add_argument("--confirm-modes",default=",".join(CONFIRM_MODES))
    p.add_argument("--spread-bps",type=float,default=None); p.add_argument("--slippage-bps",type=float,default=None); p.add_argument("--end",default=None); p.add_argument("--no-cache",action="store_true")
    p.add_argument("--send-tg",action="store_true"); p.add_argument("--tg-target",default=os.getenv("TG_TARGET","-1002953234396"))
    args=p.parse_args(); asyncio.run(run(args))
if __name__=="__main__": main()
