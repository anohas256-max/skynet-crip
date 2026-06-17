#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/root/skynet')
CFG = ROOT / 'skynet_config.py'
ENG = ROOT / 'skynet_engine.py'
MAIN = ROOT / 'skynet_main.py'
LIVE = ROOT / 'skynet_live_mexc.py'


def read(p):
    return p.read_text(encoding='utf-8')


def write(p, s):
    p.write_text(s, encoding='utf-8')


def backup():
    b = ROOT / f'backup_v16_micro_live_{time.strftime("%Y%m%d_%H%M%S")}'
    b.mkdir(parents=True, exist_ok=True)
    for p in (CFG, ENG, MAIN):
        shutil.copy2(p, b / p.name)
    print(f'BACKUP={b}')
    return b


def patch_config():
    s = read(CFG)
    s = re.sub(r'BOT_VERSION\s*=\s*"[^"]+"', 'BOT_VERSION = "SKYNET_PRO_V16_MICRO_LIVE_META_ONLY"', s, count=1)
    block = r'''
# ============================================================
# V16 MICRO-LIVE REAL EXECUTION GATE
# ============================================================
# Real trading is disabled unless ALL are true:
# REAL_TRADING_ENABLED=true, REAL_TRADING_ARMED=true, LIVE_DRY_RUN=false.
# Keep LIVE_DRY_TRACKS=META_V12_EXEC_SAFE_MO1 for first micro-live stage.
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET", "")
MEXC_FUTURES_BASE_URL = os.getenv("MEXC_FUTURES_BASE_URL", "https://api.mexc.com")
MEXC_RECV_WINDOW = int(os.getenv("MEXC_RECV_WINDOW", "10000"))

REAL_TRADING_ENABLED = os.getenv("REAL_TRADING_ENABLED", "false").lower() == "true"
REAL_TRADING_ARMED = os.getenv("REAL_TRADING_ARMED", "false").lower() == "true"
REAL_STRATEGY = os.getenv("REAL_STRATEGY", "META_V12_EXEC_SAFE_MO1")
REAL_MARGIN_USDT = float(os.getenv("REAL_MARGIN_USDT", "3.0"))
REAL_MAX_MARGIN_USDT = float(os.getenv("REAL_MAX_MARGIN_USDT", "3.0"))
REAL_MAX_ACTUAL_MARGIN_USDT = float(os.getenv("REAL_MAX_ACTUAL_MARGIN_USDT", "4.25"))
REAL_LEVERAGE = int(os.getenv("REAL_LEVERAGE", "4"))
REAL_MAX_TRADES_PER_DAY = int(os.getenv("REAL_MAX_TRADES_PER_DAY", "1"))
REAL_DAILY_MAX_LOSS_USDT = float(os.getenv("REAL_DAILY_MAX_LOSS_USDT", "0.35"))
REAL_MAX_SPREAD_BPS = float(os.getenv("REAL_MAX_SPREAD_BPS", "3.0"))
REAL_POSITION_MODE = int(os.getenv("REAL_POSITION_MODE", "1"))  # 1 dual-side, 2 one-way
'''
    if 'V16 MICRO-LIVE REAL EXECUTION GATE' not in s:
        anchor = '# ============================================================\n# STRATEGY CONFIGS\n# ============================================================'
        if anchor not in s:
            raise RuntimeError('config anchor not found')
        s = s.replace(anchor, block + '\n\n' + anchor)
    write(CFG, s)


def patch_engine():
    s = read(ENG)
    if 'import skynet_live_mexc' not in s:
        s = s.replace('import skynet_config as cfg\n', 'import skynet_config as cfg\ntry:\n    import skynet_live_mexc\nexcept Exception:\n    skynet_live_mexc = None\n', 1)
    if '_MICRO_LIVE_EXECUTOR' not in s:
        marker = '_LOG_WRITER = None\n'
        s = s.replace(marker, marker + '_MICRO_LIVE_EXECUTOR = skynet_live_mexc.MexcMicroLiveExecutor() if skynet_live_mexc else None\n', 1)

    # Unblock LIVE_DRY_RUN=false only when real executor is armed.
    old = '''        if not cfg.LIVE_DRY_RUN:
            track["failed_entries"] += 1
            track["last_error"] = "Real MEXC adapter not implemented. LIVE_DRY_RUN=false blocked."
            log(f"[{time_str}] DRY_LIVE_BLOCKED_REAL | {strategy_name} | {candidate['clean_symbol']}\\n")
            return
'''
    new = '''        if not cfg.LIVE_DRY_RUN and not (getattr(cfg, "REAL_TRADING_ENABLED", False) and getattr(cfg, "REAL_TRADING_ARMED", False)):
            track["failed_entries"] += 1
            track["last_error"] = "LIVE_DRY_RUN=false blocked because real trading is not armed."
            log(f"[{time_str}] DRY_LIVE_BLOCKED_REAL | {strategy_name} | {candidate['clean_symbol']} | NOT_ARMED\\n")
            return
'''
    if old in s:
        s = s.replace(old, new, 1)

    open_anchor = '''        log(
            f"[{time_str}] DRY_LIVE_OPEN | {strategy_name} | {candidate['clean_symbol']} | "
            f"entry={live_entry_price:.8f} shadow_entry={price:.8f} "
            f"margin=${scfg.margin:.2f} lev={scfg.leverage}x dry=True\\n"
        )
'''
    open_add = '''        log(
            f"[{time_str}] DRY_LIVE_OPEN | {strategy_name} | {candidate['clean_symbol']} | "
            f"entry={live_entry_price:.8f} shadow_entry={price:.8f} "
            f"margin=${scfg.margin:.2f} lev={scfg.leverage}x dry=True\\n"
        )

        if _MICRO_LIVE_EXECUTOR is not None:
            ok, why = _MICRO_LIVE_EXECUTOR.should_open(strategy_name, candidate, track)
            if ok:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as real_session:
                        res = await _MICRO_LIVE_EXECUTOR.open_long(real_session, strategy_name, candidate, time_str)
                    pos["real_open"] = res
                    if res.get("ok"):
                        log(
                            f"[{time_str}] REAL_MICRO_OPEN | {strategy_name} | {candidate['clean_symbol']} | "
                            f"order={res.get('order_id')} vol={res.get('meta',{}).get('vol')} "
                            f"actualMargin=${res.get('meta',{}).get('actual_margin',0):.2f} lev={getattr(cfg,'REAL_LEVERAGE',0)}x\\n"
                        )
                    else:
                        track["failed_entries"] += 1
                        track["last_error"] = str(res)[:500]
                        log(f"[{time_str}] REAL_MICRO_OPEN_BLOCKED | {strategy_name} | {candidate['clean_symbol']} | {res}\\n")
                except Exception as e:
                    track["failed_entries"] += 1
                    track["last_error"] = f"REAL_OPEN_EXCEPTION {type(e).__name__}: {e}"
                    log(f"[{time_str}] REAL_MICRO_OPEN_EXCEPTION | {strategy_name} | {candidate['clean_symbol']} | {type(e).__name__}: {e}\\n")
            elif why not in ("REAL_DISABLED", "NOT_REAL_STRATEGY"):
                log(f"[{time_str}] REAL_MICRO_SKIP | {strategy_name} | {candidate['clean_symbol']} | {why}\\n")
'''
    if 'REAL_MICRO_OPEN |' not in s:
        if open_anchor not in s:
            raise RuntimeError('engine open anchor not found')
        s = s.replace(open_anchor, open_add, 1)

    partial_anchor = '''        log(
            f"[{time_str}] DRY_LIVE_PARTIAL | {strategy_name} | {clean_symbol} | "
            f"fraction={fraction:.2f} LiveNet:{net_pnl:+.2f}$ ShadowNet:{shadow_net_pnl:+.2f}$ "
            f"Diff:{net_pnl - shadow_net_pnl:+.2f}$ | remaining={pos['remaining_fraction']:.2f} | LiveBal:${track['balance']:.2f}\\n"
        )
'''
    partial_add = partial_anchor + '''
        if _MICRO_LIVE_EXECUTOR is not None and pos.get("real_open", {}).get("ok"):
            try:
                import aiohttp
                async with aiohttp.ClientSession() as real_session:
                    res = await _MICRO_LIVE_EXECUTOR.close_long(real_session, strategy_name, symbol, fraction, "PARTIAL_TP")
                log(f"[{time_str}] REAL_MICRO_PARTIAL | {strategy_name} | {clean_symbol} | fraction={fraction:.2f} res={res}\\n")
            except Exception as e:
                log(f"[{time_str}] REAL_MICRO_PARTIAL_EXCEPTION | {strategy_name} | {clean_symbol} | {type(e).__name__}: {e}\\n")
'''
    if 'REAL_MICRO_PARTIAL |' not in s:
        if partial_anchor not in s:
            raise RuntimeError('engine partial anchor not found')
        s = s.replace(partial_anchor, partial_add, 1)

    close_anchor = '''        log(
            f"[{time_str}] DRY_LIVE_CLOSE | {strategy_name} | {clean_symbol} | {reason} | "
            f"LiveNet:{net_pnl:+.2f}$ ShadowNet:{shadow_net_pnl:+.2f}$ "
            f"Diff:{net_pnl - shadow_net_pnl:+.2f}$ | exit={live_exit_price:.8f} "
            f"shadow_exit={price:.8f} | LiveBal:${track['balance']:.2f}\\n"
        )

        track["open"] = None
'''
    close_add = '''        log(
            f"[{time_str}] DRY_LIVE_CLOSE | {strategy_name} | {clean_symbol} | {reason} | "
            f"LiveNet:{net_pnl:+.2f}$ ShadowNet:{shadow_net_pnl:+.2f}$ "
            f"Diff:{net_pnl - shadow_net_pnl:+.2f}$ | exit={live_exit_price:.8f} "
            f"shadow_exit={price:.8f} | LiveBal:${track['balance']:.2f}\\n"
        )

        if _MICRO_LIVE_EXECUTOR is not None and pos.get("real_open", {}).get("ok"):
            try:
                import aiohttp
                async with aiohttp.ClientSession() as real_session:
                    res = await _MICRO_LIVE_EXECUTOR.close_long(real_session, strategy_name, symbol, 1.0, reason)
                log(f"[{time_str}] REAL_MICRO_CLOSE | {strategy_name} | {clean_symbol} | {reason} | res={res}\\n")
            except Exception as e:
                log(f"[{time_str}] REAL_MICRO_CLOSE_EXCEPTION | {strategy_name} | {clean_symbol} | {type(e).__name__}: {e}\\n")

        track["open"] = None
'''
    if 'REAL_MICRO_CLOSE |' not in s:
        if close_anchor not in s:
            raise RuntimeError('engine close anchor not found')
        s = s.replace(close_anchor, close_add, 1)

    report_anchor = '''            lines.append(
                f"{name} {'[L:'+t['lock_reason']+']' if t['locked'] else '[ACTIVE]'}: "
                f"Bal:${t['balance']:.2f} Day:{day_pnl:+.2f}$ DD:-${dd:.2f} | "
                f"LiveNet:{t['net_pnl']:+.2f}$ ShadowNet:{t['shadow_net_pnl']:+.2f}$ Diff:{t['diff']:+.2f}$ | "
                f"Trds:{t['trades']} TP:{t['TP']} SL:{t['SL']} TIME:{t['TIME']} "
                f"FF:{t['FAST_FAIL']} ML:{t['MICRO_LOCK']} PTP:{t['PARTIAL_TP']} "
                f"RTP:{t['RUNNER_TP']} RSTOP:{t['RUNNER_STOP']} BE:{t['BE_V2']} "
                f"NF_EXIT:{t['NO_REWARD_EXIT']} Fail:{t['failed_entries']} | Open:{open_txt}"
            )
'''
    report_add = '''            real_txt = ""
            if _MICRO_LIVE_EXECUTOR is not None and name == getattr(cfg, "REAL_STRATEGY", ""):
                real_txt = " | " + _MICRO_LIVE_EXECUTOR.status_line()
            lines.append(
                f"{name} {'[L:'+t['lock_reason']+']' if t['locked'] else '[ACTIVE]'}: "
                f"Bal:${t['balance']:.2f} Day:{day_pnl:+.2f}$ DD:-${dd:.2f} | "
                f"LiveNet:{t['net_pnl']:+.2f}$ ShadowNet:{t['shadow_net_pnl']:+.2f}$ Diff:{t['diff']:+.2f}$ | "
                f"Trds:{t['trades']} TP:{t['TP']} SL:{t['SL']} TIME:{t['TIME']} "
                f"FF:{t['FAST_FAIL']} ML:{t['MICRO_LOCK']} PTP:{t['PARTIAL_TP']} "
                f"RTP:{t['RUNNER_TP']} RSTOP:{t['RUNNER_STOP']} BE:{t['BE_V2']} "
                f"NF_EXIT:{t['NO_REWARD_EXIT']} Fail:{t['failed_entries']} | Open:{open_txt}{real_txt}"
            )
'''
    if 'REAL_ENABLED=' not in s:
        if report_anchor in s:
            s = s.replace(report_anchor, report_add, 1)
    write(ENG, s)


def patch_main():
    s = read(MAIN)
    s = s.replace('V15 SPREAD SCOUT', 'V16 MICRO LIVE META')
    s = s.replace('v15 SpreadScout лог', 'v16 MicroLive лог')
    s = s.replace('SKYNET V15 DRY ЖИВ', 'SKYNET V16 MICRO-LIVE ЖИВ')
    write(MAIN, s)


def copy_live_file():
    src = Path(__file__).with_name('skynet_live_mexc.py')
    if not src.exists():
        raise RuntimeError('skynet_live_mexc.py not found next to patch script')
    if src.resolve() == LIVE.resolve():
        print(f"LIVE FILE already in place: {LIVE}")
        return
    shutil.copy2(src, LIVE)


def main():
    if not CFG.exists() or not ENG.exists() or not MAIN.exists():
        print('Run this from /root/skynet or copy files into /root/skynet first', file=sys.stderr)
        sys.exit(1)
    backup()
    copy_live_file()
    patch_config()
    patch_engine()
    patch_main()
    subprocess.check_call([sys.executable, '-m', 'py_compile', str(CFG), str(ENG), str(MAIN), str(LIVE)])
    print('OK: V16 micro-live patch applied and py_compile passed')
    print('IMPORTANT: real trading remains disabled until REAL_TRADING_ENABLED=true, REAL_TRADING_ARMED=true, LIVE_DRY_RUN=false')

if __name__ == '__main__':
    main()
