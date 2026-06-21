import asyncio
import time
import json
import os
from typing import Dict, List, Tuple, Any

import skynet_config as cfg
try:
    import skynet_live_mexc
except Exception:
    skynet_live_mexc = None

_LOG_WRITER = None
_MICRO_LIVE_EXECUTOR = skynet_live_mexc.MexcMicroLiveExecutor() if skynet_live_mexc else None


def set_log_writer(fn):
    global _LOG_WRITER
    _LOG_WRITER = fn


def log(msg: str):
    if _LOG_WRITER:
        _LOG_WRITER(msg)
    else:
        print(msg, end="")


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def calc_net_pnl(margin, leverage, price_diff_pct):
    notional = margin * leverage
    gross_pnl = notional * (price_diff_pct / 100.0)
    commission_cost = notional * cfg.COMMISSION_RATE * 2
    spread_cost = notional * (cfg.SPREAD_BPS / 10000.0)
    slippage_cost = notional * (cfg.SLIPPAGE_BPS / 10000.0) * 2
    costs = commission_cost + spread_cost + slippage_cost
    net_pnl = gross_pnl - costs
    return gross_pnl, net_pnl, costs


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def calc_atr5b_exit_params(candidate: dict) -> dict:
    """Live-compatible ATR5_B from pre-entry 5m range.

    The candidate provides pre_range_5m_pct from already-known 1m candles.
    Fallback is conservative if the API did not provide enough candle history.
    """
    rng5 = safe_float(candidate.get("pre_range_5m_pct"), cfg.ATR5B_DEFAULT_PRE_RANGE_5M)
    if rng5 <= 0:
        rng5 = cfg.ATR5B_DEFAULT_PRE_RANGE_5M

    sl = clamp(rng5 * cfg.ATR5B_SL_MULT, cfg.ATR5B_SL_MIN, cfg.ATR5B_SL_MAX)
    partial = clamp(sl * cfg.ATR5B_PARTIAL_MULT, cfg.ATR5B_PARTIAL_MIN, cfg.ATR5B_PARTIAL_MAX)
    runner_tp = clamp(sl * cfg.ATR5B_RUNNER_TP_MULT, cfg.ATR5B_RUNNER_TP_MIN, cfg.ATR5B_RUNNER_TP_MAX)
    runner_stop = clamp(sl * cfg.ATR5B_RUNNER_STOP_MULT, cfg.ATR5B_RUNNER_STOP_MIN, cfg.ATR5B_RUNNER_STOP_MAX)

    return {
        "pre_range_5m_pct": rng5,
        "stop_loss_pct": sl,
        "partial_trigger_pct": partial,
        "runner_tp_pct": runner_tp,
        "runner_stop_pct": runner_stop,
        "time_stop_min": cfg.ATR5B_TIME_STOP_MINUTES,
    }


def get_empty_stats():
    return {
        "TP": 0,
        "SL": 0,
        "TIME": 0,
        "BE_V2": 0,
        "NO_REWARD_EXIT": 0,
        "FAST_FAIL": 0,
        "MICRO_LOCK": 0,
        "RUNNER_STOP": 0,
        "PARTIAL_TP": 0,
        "RUNNER_TP": 0,
        "BE_CANDIDATE": 0,
        "NO_FOLLOW": 0,
        "trades": 0,
        "net_profit": 0.0,
        "net_loss": 0.0,
        "total_gross_pnl": 0.0,
        "net_pnl": 0.0,
        "costs": 0.0,
        "selector_candidates": 0,
        "selector_opened": 0,
        "depth_ok": 0,
        "depth_skip": 0,
        "depth_fail": 0,
        "skip_tracks_opened": 0,
        "structure_flags": 0,
    }


def make_book(scfg: cfg.StrategyConfig):
    return {
        "config": scfg,
        "balance": cfg.VIRTUAL_BALANCE,
        "start_balance": cfg.VIRTUAL_BALANCE,
        "peak_balance": cfg.VIRTUAL_BALANCE,
        "active": {},
        "last_trade": {},
        "banned_until": {},
        "locked": False,
        "lock_reason": "",
        "stats": get_empty_stats(),
    }


def build_books():
    return {name: make_book(scfg) for name, scfg in cfg.build_strategy_configs().items()}


# ============================================================
# DRY-LIVE MULTI TRACKS
# ============================================================

class DryLiveManager:
    def __init__(self, track_names: List[str]):
        self.track_names = set(track_names)
        self.slip_pct = cfg.DRY_RUN_EXECUTION_SLIPPAGE_BPS / 10000.0
        self.tracks = {}
        for name in self.track_names:
            self.tracks[name] = {
                "balance_start": cfg.VIRTUAL_BALANCE,
                "balance": cfg.VIRTUAL_BALANCE,
                "peak_balance": cfg.VIRTUAL_BALANCE,
                "gross_pnl": 0.0,
                "net_pnl": 0.0,
                "costs": 0.0,
                "shadow_net_pnl": 0.0,
                "diff": 0.0,
                "trades": 0,
                "TP": 0,
                "SL": 0,
                "TIME": 0,
                "BE_V2": 0,
                "NO_REWARD_EXIT": 0,
                "FAST_FAIL": 0,
                "MICRO_LOCK": 0,
                "RUNNER_STOP": 0,
                "PARTIAL_TP": 0,
                "RUNNER_TP": 0,
                "failed_entries": 0,
                "open": None,
                "locked": False,
                "lock_reason": "",
                "last_error": "",
            }

    def is_tracked(self, strategy_name: str) -> bool:
        return cfg.LIVE_ENABLED and strategy_name in self.track_names

    async def maybe_open(self, strategy_name, book, candidate, shadow_trade_id, time_str):
        if not self.is_tracked(strategy_name):
            return

        track = self.tracks[strategy_name]
        scfg = book["config"]

        if track["locked"]:
            log(f"[{time_str}] DRY_LIVE_SKIP | {strategy_name} | {candidate['clean_symbol']} | LOCKED_{track['lock_reason']}\n")
            return

        if track["open"] is not None:
            log(f"[{time_str}] DRY_LIVE_SKIP | {strategy_name} | {candidate['clean_symbol']} | LIVE_MAX_OPEN\n")
            return

        if not cfg.LIVE_DRY_RUN and not (getattr(cfg, "REAL_TRADING_ENABLED", False) and getattr(cfg, "REAL_TRADING_ARMED", False)):
            track["failed_entries"] += 1
            track["last_error"] = "LIVE_DRY_RUN=false blocked because real trading is not armed."
            log(f"[{time_str}] DRY_LIVE_BLOCKED_REAL | {strategy_name} | {candidate['clean_symbol']} | NOT_ARMED\n")
            return

        price = candidate["price"]
        live_entry_price = price * (1 + self.slip_pct)

        track["open"] = {
            "symbol": candidate["symbol"],
            "clean_symbol": candidate["clean_symbol"],
            "entry": live_entry_price,
            "shadow_entry": price,
            "margin": scfg.margin,
            "leverage": scfg.leverage,
            "time": time.time(),
            "shadow_id": shadow_trade_id,
            "max_profit_pct": 0.0,
            "max_loss_pct": 0.0,
            "remaining_fraction": 1.0,
        }

        log(
            f"[{time_str}] DRY_LIVE_OPEN | {strategy_name} | {candidate['clean_symbol']} | "
            f"entry={live_entry_price:.8f} shadow_entry={price:.8f} "
            f"margin=${scfg.margin:.2f} lev={scfg.leverage}x dry=True\n"
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
                            f"actualMargin=${res.get('meta',{}).get('actual_margin',0):.2f} lev={getattr(cfg,'REAL_LEVERAGE',0)}x\n"
                        )
                    else:
                        track["failed_entries"] += 1
                        track["last_error"] = str(res)[:500]
                        log(f"[{time_str}] REAL_MICRO_OPEN_BLOCKED | {strategy_name} | {candidate['clean_symbol']} | {res}\n")
                except Exception as e:
                    track["failed_entries"] += 1
                    track["last_error"] = f"REAL_OPEN_EXCEPTION {type(e).__name__}: {e}"
                    log(f"[{time_str}] REAL_MICRO_OPEN_EXCEPTION | {strategy_name} | {candidate['clean_symbol']} | {type(e).__name__}: {e}\n")
            elif why not in ("REAL_DISABLED", "NOT_REAL_STRATEGY"):
                log(f"[{time_str}] REAL_MICRO_SKIP | {strategy_name} | {candidate['clean_symbol']} | {why}\n")

    async def maybe_partial(self, strategy_name, symbol, clean_symbol, price, fraction, shadow_net_pnl, time_str):
        if strategy_name not in self.tracks:
            return
        track = self.tracks[strategy_name]
        pos = track["open"]
        if not pos or pos["symbol"] != symbol:
            return

        fraction = max(0.0, min(float(fraction), pos.get("remaining_fraction", 1.0)))
        if fraction <= 0:
            return

        live_exit_price = price * (1 - self.slip_pct)
        price_diff = ((live_exit_price - pos["entry"]) / pos["entry"]) * 100.0
        gross_pnl, net_pnl, costs = calc_net_pnl(pos["margin"] * fraction, pos["leverage"], price_diff)

        pos["remaining_fraction"] = max(0.0, pos.get("remaining_fraction", 1.0) - fraction)

        track["balance"] += net_pnl
        track["peak_balance"] = max(track["peak_balance"], track["balance"])
        track["gross_pnl"] += gross_pnl
        track["net_pnl"] += net_pnl
        track["shadow_net_pnl"] += shadow_net_pnl
        track["costs"] += costs
        track["diff"] += net_pnl - shadow_net_pnl
        track["PARTIAL_TP"] += 1

        log(
            f"[{time_str}] DRY_LIVE_PARTIAL | {strategy_name} | {clean_symbol} | "
            f"fraction={fraction:.2f} LiveNet:{net_pnl:+.2f}$ ShadowNet:{shadow_net_pnl:+.2f}$ "
            f"Diff:{net_pnl - shadow_net_pnl:+.2f}$ | remaining={pos['remaining_fraction']:.2f} | LiveBal:${track['balance']:.2f}\n"
        )

        if _MICRO_LIVE_EXECUTOR is not None and pos.get("real_open", {}).get("ok"):
            try:
                import aiohttp
                async with aiohttp.ClientSession() as real_session:
                    res = await _MICRO_LIVE_EXECUTOR.close_long(real_session, strategy_name, symbol, fraction, "PARTIAL_TP")
                log(f"[{time_str}] REAL_MICRO_PARTIAL | {strategy_name} | {clean_symbol} | fraction={fraction:.2f} res={res}\n")
            except Exception as e:
                log(f"[{time_str}] REAL_MICRO_PARTIAL_EXCEPTION | {strategy_name} | {clean_symbol} | {type(e).__name__}: {e}\n")

    async def maybe_close(self, strategy_name, symbol, clean_symbol, price, reason, shadow_net_pnl, time_str):
        if strategy_name not in self.tracks:
            return
        track = self.tracks[strategy_name]
        pos = track["open"]
        if not pos or pos["symbol"] != symbol:
            return

        live_exit_price = price * (1 - self.slip_pct)
        price_diff = ((live_exit_price - pos["entry"]) / pos["entry"]) * 100.0
        remaining_fraction = max(0.0, pos.get("remaining_fraction", 1.0))
        gross_pnl, net_pnl, costs = calc_net_pnl(pos["margin"] * remaining_fraction, pos["leverage"], price_diff)

        track["balance"] += net_pnl
        track["peak_balance"] = max(track["peak_balance"], track["balance"])
        track["gross_pnl"] += gross_pnl
        track["net_pnl"] += net_pnl
        track["shadow_net_pnl"] += shadow_net_pnl
        track["costs"] += costs
        track["diff"] += net_pnl - shadow_net_pnl
        track["trades"] += 1
        if reason in ("TP", "SL", "TIME", "BE_V2", "NO_REWARD_EXIT", "FAST_FAIL", "MICRO_LOCK", "RUNNER_STOP", "RUNNER_TP"):
            track[reason] += 1

        log(
            f"[{time_str}] DRY_LIVE_CLOSE | {strategy_name} | {clean_symbol} | {reason} | "
            f"LiveNet:{net_pnl:+.2f}$ ShadowNet:{shadow_net_pnl:+.2f}$ "
            f"Diff:{net_pnl - shadow_net_pnl:+.2f}$ | exit={live_exit_price:.8f} "
            f"shadow_exit={price:.8f} | LiveBal:${track['balance']:.2f}\n"
        )

        if _MICRO_LIVE_EXECUTOR is not None and pos.get("real_open", {}).get("ok"):
            try:
                import aiohttp
                async with aiohttp.ClientSession() as real_session:
                    res = await _MICRO_LIVE_EXECUTOR.close_long(real_session, strategy_name, symbol, 1.0, reason)
                log(f"[{time_str}] REAL_MICRO_CLOSE | {strategy_name} | {clean_symbol} | {reason} | res={res}\n")
            except Exception as e:
                log(f"[{time_str}] REAL_MICRO_CLOSE_EXCEPTION | {strategy_name} | {clean_symbol} | {type(e).__name__}: {e}\n")

        track["open"] = None
        self._update_lock(strategy_name)

    def _update_lock(self, strategy_name):
        track = self.tracks[strategy_name]
        if track["locked"]:
            return
        # Use strategy-specific locks if available.
        scfg = cfg.build_strategy_configs().get(strategy_name)
        p_lock = scfg.p_lock if scfg else 0.60
        l_lock = scfg.l_lock if scfg else -0.35
        give_act = scfg.give_act if scfg else 0.40
        give_drop = scfg.give_drop if scfg else 0.22

        profit = track["balance"] - track["balance_start"]
        peak_profit = track["peak_balance"] - track["balance_start"]
        giveback = track["peak_balance"] - track["balance"]

        if profit >= p_lock:
            track["locked"] = True
            track["lock_reason"] = "PROFIT_TARGET"
            log(f"🔒 DRY_LIVE {strategy_name} LOCKED PROFIT_TARGET +${p_lock}\n")
        elif peak_profit >= give_act and giveback >= give_drop:
            track["locked"] = True
            track["lock_reason"] = "GIVEBACK"
            log(f"🛡 DRY_LIVE {strategy_name} LOCKED GIVEBACK ${giveback:.2f}\n")
        elif profit <= l_lock:
            track["locked"] = True
            track["lock_reason"] = "MAX_LOSS"
            log(f"🛑 DRY_LIVE {strategy_name} LOCKED MAX_LOSS {profit:.2f}$\n")

    def reset_if_no_open(self):
        if any(t["open"] for t in self.tracks.values()):
            return False
        for t in self.tracks.values():
            t["balance_start"] = t["balance"]
            t["peak_balance"] = t["balance"]
            t["gross_pnl"] = 0.0
            t["net_pnl"] = 0.0
            t["costs"] = 0.0
            t["shadow_net_pnl"] = 0.0
            t["diff"] = 0.0
            t["trades"] = 0
            for k in ("TP", "SL", "TIME", "BE_V2", "NO_REWARD_EXIT", "FAST_FAIL", "MICRO_LOCK", "RUNNER_STOP", "PARTIAL_TP", "RUNNER_TP"):
                t[k] = 0
            t["failed_entries"] = 0
            t["locked"] = False
            t["lock_reason"] = ""
            t["last_error"] = ""
        return True

    def format_report(self) -> str:
        lines = [
            "=== MULTI DRY-LIVE REPORT ===",
            f"LIVE_ENABLED={cfg.LIVE_ENABLED} | LIVE_DRY_RUN={cfg.LIVE_DRY_RUN} | "
            f"TRACKS={','.join(sorted(self.track_names))} | DRY_EXEC_SLIP={cfg.DRY_RUN_EXECUTION_SLIPPAGE_BPS}bps",
        ]

        for name in sorted(self.tracks):
            t = self.tracks[name]
            day_pnl = t["balance"] - t["balance_start"]
            dd = t["peak_balance"] - t["balance"]
            open_txt = "-"
            if t["open"]:
                p = t["open"]
                open_txt = f"{p['clean_symbol']} entry={p['entry']:.8f} shadow={p['shadow_entry']:.8f}"

            real_txt = ""
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

        return "\n".join(lines) + "\n"


# ============================================================
# SKIP TRACKER
# ============================================================

class SkipTracker:
    def __init__(self):
        self.active = []
        self.last_open = {}
        self.last_learn = {}
        self.stats = {
            "opened": 0,
            "WOULD_TP": 0,
            "WOULD_SL": 0,
            "WOULD_TIME": 0,
            "hypo_net": 0.0,
            "hypo_costs": 0.0,
        }

    def open(self, strategy_name, candidate, reason, scfg, current_time, time_str, force=False):
        if not scfg.skip_track and not force:
            return

        key = (strategy_name, candidate["symbol"], reason)
        if key in self.last_open and current_time - self.last_open[key] < cfg.SKIP_TRACK_COOLDOWN:
            return

        self.last_open[key] = current_time
        self.stats["opened"] += 1
        watch = {
            "strategy": strategy_name,
            "symbol": candidate["symbol"],
            "clean_symbol": candidate["clean_symbol"],
            "entry": candidate["price"],
            "margin": scfg.margin,
            "leverage": scfg.leverage,
            "tp": scfg.tp,
            "time": current_time,
            "reason": reason,
            "observer_kind": "REJECT" if str(reason).startswith(getattr(cfg, "REJECT_OBSERVER_REASON_PREFIX", "REJECT_")) else "SKIP",
            "max_profit_pct": 0.0,
            "max_loss_pct": 0.0,
        }
        self.active.append(watch)

        log(
            f"[{time_str}] SKIP_TRACK_OPEN | {strategy_name} | {candidate['clean_symbol']} | "
            f"reason={reason} | entry={candidate['price']} | spread={candidate.get('spread_bps', 999):.2f}bps "
            f"depth_reason={candidate.get('depth_reason','-')} | "
            f"obs={('REJECT' if str(reason).startswith(getattr(cfg, 'REJECT_OBSERVER_REASON_PREFIX', 'REJECT_')) else 'SKIP')} | "
            f"score={candidate.get('score','-')} vol=x{candidate.get('vol_ratio',0):.1f} "
            f"pc={candidate.get('price_change',0):+.2f}% rank={candidate.get('current_turnover_rank',999999)}\n"
        )

    def _learn_skip_outcome(self, w, net, reason, current_time, time_str):
        if not getattr(cfg, "V15_SKIP_LEARNING_ENABLED", False):
            return

        original_skip = str(w.get("reason", ""))
        skip_kind = None

        if original_skip == "DEPTH_THIN":
            if not getattr(cfg, "V15_SKIP_LEARN_DEPTH_THIN", True):
                return
            skip_kind = "DEPTH_THIN"
        elif original_skip.startswith("SPREAD_WIDE"):
            if not getattr(cfg, "V15_SKIP_LEARN_SPREAD_WIDE", True):
                return
            skip_kind = "SPREAD_WIDE"
        else:
            return

        # Убираем дубли: skip tracker открывается многими стратегиями на один и тот же сигнал.
        # Для паспорта нужен один outcome на symbol/skip_kind/15m bucket.
        symbol = w.get("symbol", "")
        clean_symbol = w.get("clean_symbol", symbol)
        bucket = int(current_time // max(60, getattr(cfg, "V15_SKIP_LEARN_COOLDOWN", 900)))
        key = (symbol, skip_kind, bucket)
        if self.last_learn.get(key):
            return
        self.last_learn[key] = True

        learn_reason = reason
        if reason == "WOULD_TP":
            learn_reason = "RUNNER_TP"
        elif reason == "WOULD_SL":
            learn_reason = "SL"
        elif reason == "WOULD_TIME":
            learn_reason = "TIME"

        if getattr(cfg, "V15_SKIP_LEARN_TIME_AS_NEUTRAL", True) and learn_reason == "TIME":
            # TIME часто около нуля, не хотим забивать паспорт шумом.
            if abs(float(net)) < 0.05:
                return

        try:
            q = _smart_v2_quality(symbol)
            q.update(float(net), float(w.get("max_profit_pct", 0.0)), learn_reason, current_time)
            _smart_v2_save_passports()

            _SMART_V2_STATS["V15_SKIP_LEARN"] = _SMART_V2_STATS.get("V15_SKIP_LEARN", 0) + 1
            if skip_kind == "DEPTH_THIN":
                _SMART_V2_STATS["V15_SKIP_LEARN_DEPTH_THIN"] = _SMART_V2_STATS.get("V15_SKIP_LEARN_DEPTH_THIN", 0) + 1
            if skip_kind == "SPREAD_WIDE":
                _SMART_V2_STATS["V15_SKIP_LEARN_SPREAD_WIDE"] = _SMART_V2_STATS.get("V15_SKIP_LEARN_SPREAD_WIDE", 0) + 1

            f = q.features()
            log(
                f"[{time_str}] V15_SKIP_LEARN | {clean_symbol} | {skip_kind} -> {learn_reason} | "
                f"net={net:+.2f}$ MFE=+{w.get('max_profit_pct',0.0):.2f}% "
                f"Qobs={f['obs']} Qavg={f['avg_net']:+.2f}$ Qsl={f['sl_rate']:.2f} "
                f"bad={f['bad_streak']} tox={f.get('toxic_reason','')}\n"
            )
        except Exception as e:
            log(f"[{time_str}] V15_SKIP_LEARN_ERROR | {clean_symbol} | {type(e).__name__}: {e}\n")

    def update_symbol(self, symbol, clean_symbol, price, current_time, time_str):
        remaining = []
        for w in self.active:
            if w["symbol"] != symbol:
                remaining.append(w)
                continue

            price_diff = ((price - w["entry"]) / w["entry"]) * 100.0
            w["max_profit_pct"] = max(w["max_profit_pct"], price_diff)
            w["max_loss_pct"] = min(w["max_loss_pct"], price_diff)
            held = (current_time - w["time"]) / 60.0

            reason = None
            if price_diff >= w["tp"]:
                reason = "WOULD_TP"
            elif price_diff <= -cfg.STOP_LOSS:
                reason = "WOULD_SL"
            elif held >= cfg.SKIP_TRACK_TTL_MINUTES:
                reason = "WOULD_TIME"

            if reason:
                gross, net, costs = calc_net_pnl(w["margin"], w["leverage"], price_diff)
                self.stats[reason] += 1
                self.stats["hypo_net"] += net
                self.stats["hypo_costs"] += costs
                log(
                    f"[{time_str}] SKIP_TRACK_CLOSE | {w['strategy']} | {clean_symbol} | {reason} | "
                    f"original_skip={w['reason']} | HypoNet:{net:+.2f}$ | "
                    f"MFE:+{w['max_profit_pct']:.2f}% MAE:{w['max_loss_pct']:.2f}% | "
                    f"obs={w.get('observer_kind','SKIP')}\n"
                )
                self._learn_skip_outcome(w, net, reason, current_time, time_str)
            else:
                remaining.append(w)

        self.active = remaining

    def format_report(self) -> str:
        st = self.stats
        return (
            "=== SKIP TRACKER REPORT ===\n"
            f"Opened:{st['opened']} | WOULD_TP:{st['WOULD_TP']} | WOULD_SL:{st['WOULD_SL']} | "
            f"WOULD_TIME:{st['WOULD_TIME']} | HypoNet:{st['hypo_net']:+.2f}$ | "
            f"HypoCosts:-${st['hypo_costs']:.2f} | Active:{len(self.active)}\n"
        )



def should_observe_reject(candidate: dict) -> bool:
    """Cheap guard to avoid observing every microscopic reject."""
    if not getattr(cfg, "REJECT_OBSERVER_ENABLED", False):
        return False

    try:
        score = float(candidate.get("score", -999))
        vol = float(candidate.get("vol_ratio", 0.0))
        pc = abs(float(candidate.get("price_change", 0.0)))
    except Exception:
        return False

    return (
        score >= float(getattr(cfg, "REJECT_OBSERVER_MIN_SCORE", 3))
        and vol >= float(getattr(cfg, "REJECT_OBSERVER_MIN_VOL_RATIO", 8.0))
        and pc >= float(getattr(cfg, "REJECT_OBSERVER_MIN_ABS_PRICE_CHANGE", 0.20))
    )



def should_observe_reject_strategy(strategy_name: str) -> bool:
    """
    REJECT_OBSERVER_V2:
    Avoid N duplicate virtual trades for the same candidate across dozens of
    experimental strategies. We only observe representative lanes.
    """
    raw = str(getattr(cfg, "REJECT_OBSERVER_STRATEGY_ALLOWLIST", "") or "")
    allowed = {x.strip() for x in raw.split(",") if x.strip()}
    if not allowed:
        return True
    return str(strategy_name) in allowed


def cost_gate_reason_tag(candidate: dict, lane: str = "normal", mode: str = "taker") -> str:
    """
    Compact reason tag. Full debug stays available in code, but logs should not
    explode with huge repeated COST_GATE strings.
    """
    try:
        exp_bps = expected_move_bps(candidate, lane=lane)
        req_bps = required_move_bps(candidate, lane=lane, mode=mode)
        cost_bps = execution_roundtrip_cost_bps(candidate, mode=mode)
        return f"COST_FAIL_E{exp_bps:.0f}_R{req_bps:.0f}_C{cost_bps:.0f}"
    except Exception:
        return "COST_FAIL"



def reject_reason_for_strategy(scfg, candidate: dict) -> str:
    """Compact reason label for a strategy that did not pass should_enter_strategy."""
    family = str(getattr(scfg, "family", "unknown"))

    bits = [f"RULES_NOT_MET_{family}"]

    try:
        score = float(candidate.get("score", -999))
        vol = float(candidate.get("vol_ratio", 0.0))
        pc = float(candidate.get("price_change", 0.0))
        trend = float(candidate.get("trend_15m", 0.0))
        btc = float(candidate.get("btc_5m_change", 0.0))
        oi = float(candidate.get("oi_change", 0.0))
        br = int(candidate.get("breakout_risk_score", 0))
        fb = int(candidate.get("false_breakouts_15m", 0))
        struct = int(candidate.get("structure_risk", 0))
    except Exception:
        return "REJECT_RULES_NOT_MET_PARSE_FAIL"

    # Not exact per-family internals, but enough to price which gates are killing opportunities.
    lane = "fast" if family in ("yellow_score3", "yellow_score3_fast") else "normal"
    if not cost_gate_long(candidate, lane=lane, mode="taker"):
        if getattr(cfg, "REJECT_OBSERVER_COMPACT_REASONS", True):
            bits.append(cost_gate_reason_tag(candidate, lane=lane, mode="taker"))
        else:
            bits.append("COST_GATE_FAIL")
            bits.append(cost_gate_debug(candidate, lane=lane, mode="taker").replace(" ", "_"))

    if score < 3:
        bits.append("SCORE_LOW")
    if abs(pc) < 0.20:
        bits.append("PC_LOW")
    if pc > 1.20:
        bits.append("PC_HIGH")
    if vol < 8:
        bits.append("VOL_LOW")
    if trend <= 0:
        bits.append("TREND_WEAK")
    if btc < -0.05:
        bits.append("BTC_WEAK")
    if oi < 0:
        bits.append("OI_NEG")
    if struct > 3:
        bits.append("STRUCT_HIGH")
    if br > 3:
        bits.append("BRISK_HIGH")
    if fb > 1:
        bits.append("FB_HIGH")
    if candidate.get("absorption_risk_long"):
        bits.append("ABSORPTION")
    if candidate.get("high_effort_low_result"):
        bits.append("HIGH_EFFORT_LOW_RESULT")
    if candidate.get("weak_long_result"):
        bits.append("WEAK_LONG_RESULT")
    if not candidate.get("initiative_buying_proxy", False):
        bits.append("NO_INITIATIVE")

    # Keep reason length sane for logs/grouping.
    return "REJECT_" + "|".join(bits[:8])



# ============================================================
# GLOBAL TOXIC BAN FOR EXEC/RUNNER
# ============================================================

_GLOBAL_TOXIC_BAN_UNTIL = {}

def is_global_toxic_banned(symbol: str, current_time: float) -> bool:
    return current_time < _GLOBAL_TOXIC_BAN_UNTIL.get(symbol, 0.0)

def set_global_toxic_ban(symbol: str, clean_symbol: str, current_time: float, time_str: str, reason: str):
    _GLOBAL_TOXIC_BAN_UNTIL[symbol] = current_time + cfg.GLOBAL_TOXIC_BAN_SECONDS
    log(
        f"[{time_str}] GLOBAL_TOXIC_BAN | {clean_symbol} | "
        f"{int(cfg.GLOBAL_TOXIC_BAN_SECONDS/60)}m | reason={reason}\n"
    )

# ============================================================
# HTTP DEPTH
# ============================================================

_depth_cache = {}


def parse_depth_level(level):
    if isinstance(level, dict):
        p = safe_float(level.get("price") or level.get("p") or level.get("0"))
        q = safe_float(level.get("vol") or level.get("quantity") or level.get("q") or level.get("1"))
        return p, q
    if isinstance(level, (list, tuple)) and len(level) >= 2:
        return safe_float(level[0]), safe_float(level[1])
    return 0.0, 0.0


async def get_depth_metrics(session, symbol):
    try:
        url = f"https://contract.mexc.com/api/v1/contract/depth/{symbol}?limit={cfg.DEPTH_LIMIT}"
        async with session.get(url, timeout=cfg.DEPTH_TIMEOUT) as res:
            if res.status != 200:
                return {"depth_available": False, "depth_reason": f"HTTP_{res.status}"}

            payload = await res.json()
            d = payload.get("data", payload)
            asks = d.get("asks") or d.get("asksList") or []
            bids = d.get("bids") or d.get("bidsList") or []

            if not asks or not bids:
                return {"depth_available": False, "depth_reason": "EMPTY_BOOK"}

            ask0, _ = parse_depth_level(asks[0])
            bid0, _ = parse_depth_level(bids[0])

            if ask0 <= 0 or bid0 <= 0 or ask0 <= bid0:
                return {"depth_available": False, "depth_reason": "BAD_BID_ASK", "bid": bid0, "ask": ask0}

            spread_bps = ((ask0 - bid0) / bid0) * 10000.0
            top_asks = [parse_depth_level(x) for x in asks[:cfg.DEPTH_LIMIT]]
            top_bids = [parse_depth_level(x) for x in bids[:cfg.DEPTH_LIMIT]]
            top5_ask_usdt = sum(p * q for p, q in top_asks if p > 0 and q > 0)
            top5_bid_usdt = sum(p * q for p, q in top_bids if p > 0 and q > 0)

            # Microstructure fields compatible with v17 recorder naming.
            # imb_5 < 0 means ASK side dominates top levels, useful for SHORT/fade research.
            imb_5 = 0.0
            if (top5_bid_usdt + top5_ask_usdt) > 0:
                imb_5 = (top5_bid_usdt - top5_ask_usdt) / (top5_bid_usdt + top5_ask_usdt)

            bid_wall = 0.0
            ask_wall = 0.0
            if top5_bid_usdt > 0 and top_bids:
                bid_wall = max((p * q for p, q in top_bids if p > 0 and q > 0), default=0.0) / top5_bid_usdt
            if top5_ask_usdt > 0 and top_asks:
                ask_wall = max((p * q for p, q in top_asks if p > 0 and q > 0), default=0.0) / top5_ask_usdt
            wall_skew = bid_wall - ask_wall

            depth_thin = top5_bid_usdt < cfg.MIN_TOP5_BID_USDT or top5_ask_usdt < cfg.MIN_TOP5_ASK_USDT

            return {
                "depth_available": True,
                "depth_reason": "DEPTH_OK" if not depth_thin else "DEPTH_THIN",
                "bid": bid0,
                "ask": ask0,
                "spread_bps": spread_bps,
                "top5_bid_usdt": top5_bid_usdt,
                "top5_ask_usdt": top5_ask_usdt,
                "imb_5": imb_5,
                "imb_20": imb_5,
                "wall_skew": wall_skew,
                "depth_thin": depth_thin,
            }
    except Exception as e:
        return {"depth_available": False, "depth_reason": f"EXC_{type(e).__name__}", "error": str(e)}


async def enrich_selector_candidates_with_depth(session, selector_candidates: Dict[str, List[dict]], time_str: str):
    unique = {}
    for cand_list in selector_candidates.values():
        for cand in cand_list:
            unique[cand["symbol"]] = cand

    if not unique:
        return

    # Prioritize only top-N symbols to avoid 429 / slow snapshots.
    ordered = sorted(unique.values(), key=lambda c: candidate_priority(c, None), reverse=True)
    selected = ordered[:cfg.MAX_DEPTH_CANDIDATES_PER_SNAPSHOT]
    selected_symbols = {c["symbol"] for c in selected}
    skipped = [c for c in ordered if c["symbol"] not in selected_symbols]

    now = time.time()
    semaphore = asyncio.Semaphore(max(1, cfg.DEPTH_CONCURRENCY))

    async def get_cached(c):
        symbol = c["symbol"]
        cached = _depth_cache.get(symbol)
        if cached and now - cached["time"] <= cfg.DEPTH_CACHE_TTL:
            m = dict(cached["metrics"])
            m["cache"] = True
            return symbol, m
        async with semaphore:
            m = await get_depth_metrics(session, symbol)
        _depth_cache[symbol] = {"time": time.time(), "metrics": dict(m)}
        m["cache"] = False
        return symbol, m

    tasks = [asyncio.create_task(get_cached(c)) for c in selected]
    results = {}
    for t in tasks:
        try:
            symbol, metrics = await t
            results[symbol] = metrics
        except Exception as e:
            results["UNKNOWN"] = {"depth_available": False, "depth_reason": f"TASK_{type(e).__name__}", "error": str(e)}

    for c in skipped:
        c.update({
            "depth_available": False,
            "depth_reason": "DEPTH_NOT_CHECKED_LIMIT",
            "depth_thin": True,
            "spread_bps": 999.0,
            "top5_bid_usdt": 0.0,
            "top5_ask_usdt": 0.0,
            "best_bid": 0.0,
            "best_ask": 0.0,
        })
        log(
            f"[{time_str}] DEPTH_LIMIT_SKIP | {c['clean_symbol']} | "
            f"priority={candidate_priority(c, None):.2f} | "
            f"top_limit={cfg.MAX_DEPTH_CANDIDATES_PER_SNAPSHOT} total_candidates={len(unique)}\n"
        )

    for cand_list in selector_candidates.values():
        for c in cand_list:
            if c["symbol"] not in selected_symbols:
                continue
            m = results.get(c["symbol"], {"depth_available": False, "depth_reason": "NO_RESULT"})
            c["depth_available"] = bool(m.get("depth_available"))
            c["depth_reason"] = m.get("depth_reason", "UNKNOWN")
            c["depth_thin"] = bool(m.get("depth_thin", False))
            c["spread_bps"] = safe_float(m.get("spread_bps"), 999.0)
            c["top5_bid_usdt"] = safe_float(m.get("top5_bid_usdt"), 0.0)
            c["top5_ask_usdt"] = safe_float(m.get("top5_ask_usdt"), 0.0)
            c["best_bid"] = safe_float(m.get("bid"), 0.0)
            c["best_ask"] = safe_float(m.get("ask"), 0.0)
            c["imb_5"] = safe_float(m.get("imb_5"), 0.0)
            c["imb_20"] = safe_float(m.get("imb_20"), c["imb_5"])
            c["wall_skew"] = safe_float(m.get("wall_skew"), 0.0)
            c["depth_cache"] = bool(m.get("cache", False))

    for c in selected:
        if c.get("depth_available") and not c.get("depth_thin"):
            log(
                f"[{time_str}] DEPTH_OK | {c['clean_symbol']} | "
                f"spread={c.get('spread_bps',999):.2f}bps | "
                f"bid5=${c.get('top5_bid_usdt',0):.0f} ask5=${c.get('top5_ask_usdt',0):.0f} "
                f"imb5={c.get('imb_5',0):+.2f} | "
                f"checked_top={len(selected)}/{len(unique)} cache={1 if c.get('depth_cache') else 0}\n"
            )
        else:
            tag = "DEPTH_SKIP"
            if not c.get("depth_available"):
                tag = "DEPTH_FAIL"
            log(
                f"[{time_str}] {tag} | {c['clean_symbol']} | {c.get('depth_reason','UNKNOWN')} | "
                f"spread={c.get('spread_bps',999):.2f}bps | "
                f"bid5=${c.get('top5_bid_usdt',0):.0f} ask5=${c.get('top5_ask_usdt',0):.0f} "
                f"imb5={c.get('imb_5',0):+.2f} | "
                f"checked_top={len(selected)}/{len(unique)}\n"
            )


# ============================================================
# SIGNAL METRICS
# ============================================================

def is_exhaustion(vol_ratio, price_change):
    return vol_ratio > cfg.EXHAUSTION_VOL_RATIO and price_change > cfg.EXHAUSTION_PRICE_CHANGE


def enrich_candidate_structure(cand: dict):
    # kline metrics are crude REST proxies for orderflow ideas:
    # effort/result, absorption, initiative buying, weak close.
    close_pos = safe_float(cand.get("close_position"), 0.5)
    body_ratio = safe_float(cand.get("body_ratio"), 0.0)
    upper_wick_ratio = safe_float(cand.get("upper_wick_ratio"), 0.0)
    vol_ratio = safe_float(cand.get("vol_ratio"), 0.0)

    weak_long_result = vol_ratio >= cfg.VOL_MULTIPLIER and close_pos < 0.55
    absorption_risk_long = vol_ratio >= cfg.VOL_MULTIPLIER and upper_wick_ratio >= 0.45 and close_pos < 0.60
    initiative_buying_proxy = close_pos >= 0.75 and body_ratio >= 0.40
    high_effort_low_result = vol_ratio >= cfg.VOL_MULTIPLIER and body_ratio < 0.25

    middle_range_noise = bool(cand.get("middle_range_noise", False))

    risk = 0
    if weak_long_result:
        risk += 2
    if absorption_risk_long:
        risk += 3
    if high_effort_low_result:
        risk += 2
    if middle_range_noise:
        risk += 1
    if safe_float(cand.get("oi_change"), 0) <= 0:
        risk += 1
    if safe_float(cand.get("btc_5m_change"), 0) < 0:
        risk += 1

    cand.update({
        "weak_long_result": weak_long_result,
        "absorption_risk_long": absorption_risk_long,
        "initiative_buying_proxy": initiative_buying_proxy,
        "high_effort_low_result": high_effort_low_result,
        "structure_risk": risk,
    })
    return cand



# === V11.5 PATCH START: breakout-risk filters ===
def passes_breakout_risk_mode(c: dict, mode: str) -> bool:
    mode = (mode or "NONE").upper()
    if mode in ("NONE", "NO_FILTER"):
        return True

    risk = safe_float(c.get("breakout_risk_score"), 999.0)
    red_share = safe_float(c.get("red_volume_share_10m"), 1.0)
    reject = safe_float(c.get("rejection_count_10m"), 99.0)
    false_bo = safe_float(c.get("false_breakouts_15m"), 99.0)
    flush = int(safe_float(c.get("recent_flush_15m"), 1.0))
    wick_pressure = safe_float(c.get("upper_wick_pressure_10m"), 999.0)
    ema_slope = safe_float(c.get("ema9_slope_3m_pct"), -999.0)
    close_vs_ema = safe_float(c.get("close_vs_ema9_pct"), -999.0)

    if mode == "NO_FALSE_BREAKOUT":
        return false_bo <= cfg.BREAKOUT_FALSE_BREAKOUT_MAX

    if mode == "COMBO_BALANCED":
        return (
            risk <= cfg.BREAKOUT_COMBO_RISK_MAX
            and red_share < cfg.BREAKOUT_COMBO_RED_SHARE_MAX
            and reject <= cfg.BREAKOUT_COMBO_REJECTION_MAX
            and false_bo <= cfg.BREAKOUT_FALSE_BREAKOUT_MAX
            and flush == 0
            and wick_pressure < cfg.BREAKOUT_COMBO_WICK_PRESSURE_MAX
            and ema_slope >= cfg.BREAKOUT_COMBO_EMA9_SLOPE_MIN
            and close_vs_ema >= cfg.BREAKOUT_COMBO_CLOSE_VS_EMA9_MIN
        )

    return True
# === V11.5 PATCH END: breakout-risk filters ===



# === V12 PATCH START: meta selector rules ===
def meta_v12_sources(c: dict, scfg: cfg.StrategyConfig) -> list:
    # Return live-compatible source labels.
    # Raw old strategies are not opened directly here.
    sources = []

    score = int(safe_float(c.get("score"), -999))
    pc = safe_float(c.get("price_change"), 999.0)
    vol = safe_float(c.get("vol_ratio"), 999.0)
    trend = safe_float(c.get("trend_15m"), -999.0)
    btc5 = safe_float(c.get("btc_5m_change"), -999.0)
    oi = safe_float(c.get("oi_change"), -999.0)
    struct = int(safe_float(c.get("structure_risk"), 999))
    brisk = int(safe_float(c.get("breakout_risk_score"), 999))
    fb = int(safe_float(c.get("false_breakouts_15m"), 999))
    rank = int(safe_float(c.get("current_turnover_rank"), 999999))

    if score < cfg.META_V12_MIN_SCORE:
        return sources
    if not (cfg.PRICE_CHANGE_MIN <= pc <= cfg.META_V12_MAX_PRICE_CHANGE):
        return sources
    if vol > cfg.META_V12_MAX_VOL_RATIO:
        return sources
    if trend < getattr(scfg, "meta_trend_min", cfg.META_V12_MIN_TREND_15M):
        return sources
    if btc5 < cfg.META_V12_MIN_BTC_5M:
        return sources
    if oi < getattr(scfg, "meta_oi_min", cfg.META_V12_OI_SOFT_MIN):
        return sources
    if struct > cfg.META_V12_MAX_STRUCTURE_RISK:
        return sources
    if brisk > getattr(scfg, "meta_risk_max", cfg.META_V12_MAX_BRISK):
        return sources
    if fb > getattr(scfg, "meta_false_bo_max", cfg.META_V12_MAX_FALSE_BREAKOUTS):
        return sources
    if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
        return sources
    if not c.get("initiative_buying_proxy"):
        return sources

    if "passes_breakout_risk_mode" in globals() and passes_breakout_risk_mode(c, "COMBO_BALANCED"):
        sources.append("BREAKOUT_COMBO")

    if score >= 4 and 0.25 <= pc <= 0.55 and trend >= cfg.META_V12_MIN_TREND_15M and not is_exhaustion(vol, pc):
        sources.append("FILTERED_055_EXEC_SAFE")

    if (
        (score >= 4 and 0.25 <= pc <= 0.45)
        or (score >= 6 and 0.45 < pc <= cfg.META_V12_MAX_PRICE_CHANGE and trend >= cfg.META_V12_STRICT_TREND_15M)
    ):
        sources.append("HYBRID_SCALP_EXEC_SAFE")

    if rank <= cfg.META_V12_ROLL_TOP_N and trend >= cfg.META_V12_STRICT_TREND_15M:
        sources.append(f"ROLL24_TOP{cfg.META_V12_ROLL_TOP_N}")

    if oi >= cfg.META_V12_OI_STRICT_MIN:
        sources.append("OI_FRESH")

    return sources
# === V12 PATCH END: meta selector rules ===



# ============================================================
# V13 SMART UNIVERSE V2
# ============================================================

class SmartV2SymbolQuality:
    def __init__(self, maxlen: int = None):
        self.items = []
        self.maxlen = int(maxlen or getattr(cfg, "SMART_V2_TOXIC_WINDOW", 4))
        self.bad_streak = 0
        self.cooldown_until = 0.0
        self.last_toxic_reason = ""

    def update(self, net: float, mfe: float, reason: str, exit_time: float):
        # V14: не вечный blacklist, а временный toxic-score.
        # Символ может восстановиться: хорошие outcomes уменьшают bad_streak.
        sl = reason == "SL"
        bad = (
            sl
            or net < -0.05
            or (net < 0 and mfe < getattr(cfg, "SMART_V2_TOXIC_MIN_AVG_MFE", 0.60))
        )
        good = net > 0 and mfe >= getattr(cfg, "SMART_V2_GOOD_MFE", 0.80)

        if bad:
            self.bad_streak += 1
        elif good:
            self.bad_streak = max(0, self.bad_streak - 1)

        self.items.append({"net": float(net), "mfe": float(mfe), "reason": reason, "bad": bool(bad), "good": bool(good)})
        if len(self.items) > self.maxlen:
            self.items = self.items[-self.maxlen:]

        if self._is_toxic_now():
            self.cooldown_until = exit_time + getattr(cfg, "SMART_V2_TOXIC_COOLDOWN_HOURS", cfg.SMART_V2_COOLDOWN_HOURS) * 3600.0

    def _is_toxic_now(self) -> bool:
        if len(self.items) < 2:
            return False

        n = len(self.items)
        avg_net = sum(x["net"] for x in self.items) / n
        avg_mfe = sum(x["mfe"] for x in self.items) / n
        sl_rate = sum(1 for x in self.items if x["reason"] == "SL") / n

        if self.bad_streak >= cfg.SMART_V2_MAX_BAD_STREAK and avg_net <= getattr(cfg, "SMART_V2_TOXIC_SL_AVG_NET_MAX", 0.02):
            self.last_toxic_reason = "BAD_STREAK"
            return True

        if sl_rate >= getattr(cfg, "SMART_V2_TOXIC_MAX_SL_RATE", 0.50) and avg_net < getattr(cfg, "SMART_V2_TOXIC_SL_AVG_NET_MAX", 0.02):
            self.last_toxic_reason = "SL_RATE"
            return True

        if avg_net < getattr(cfg, "SMART_V2_TOXIC_MIN_AVG_NET", -0.05):
            self.last_toxic_reason = "AVG_NET"
            return True

        if avg_mfe < getattr(cfg, "SMART_V2_TOXIC_MIN_AVG_MFE", 0.60) and avg_net <= 0:
            self.last_toxic_reason = "LOW_MFE"
            return True

        self.last_toxic_reason = ""
        return False

    def features(self):
        n = len(self.items)
        if n <= 0:
            return {
                "obs": 0,
                "avg_net": 0.0,
                "avg_mfe": 0.0,
                "sl_rate": 0.0,
                "good_rate": 0.0,
                "bad_streak": self.bad_streak,
                "cooldown_until": self.cooldown_until,
                "toxic_reason": self.last_toxic_reason,
            }

        return {
            "obs": n,
            "avg_net": sum(x["net"] for x in self.items) / n,
            "avg_mfe": sum(x["mfe"] for x in self.items) / n,
            "sl_rate": sum(1 for x in self.items if x["reason"] == "SL") / n,
            "good_rate": sum(1 for x in self.items if x.get("good")) / n,
            "bad_streak": self.bad_streak,
            "cooldown_until": self.cooldown_until,
            "toxic_reason": self.last_toxic_reason,
        }

    def to_dict(self):
        return {
            "items": self.items,
            "maxlen": self.maxlen,
            "bad_streak": self.bad_streak,
            "cooldown_until": self.cooldown_until,
            "last_toxic_reason": self.last_toxic_reason,
        }

    @classmethod
    def from_dict(cls, data):
        q = cls(maxlen=int(data.get("maxlen", getattr(cfg, "SMART_V2_TOXIC_WINDOW", 4))))
        q.items = list(data.get("items", []))[-q.maxlen:]
        q.bad_streak = int(data.get("bad_streak", 0))
        q.cooldown_until = float(data.get("cooldown_until", 0.0))
        q.last_toxic_reason = str(data.get("last_toxic_reason", ""))
        return q


_SMART_V2_QUALITY = {}
_SMART_V2_WATCHES = []
_SMART_V2_LAST_WATCH = {}
_SMART_V2_STATS = {
    "watched": 0,
    "closed": 0,
    "would_trade": 0,
    "rejects": 0,
    "CORE": 0,
    "MID_COLD_ULTRA": 0,
    "MID_QUALITY_OK": 0,
    "MID_STRONG_OVERRIDE": 0,
    "MID_ULTRA_OVERRIDE": 0,
    "COOLDOWN_ULTRA_OVERRIDE": 0,
    "BAD_STREAK_ULTRA_OVERRIDE": 0,
    "EXPLORE_MONITOR_ONLY": 0,
    "MID_COLD_REJECT": 0,
    "MID_QUALITY_REJECT": 0,
    "COOLDOWN": 0,
    "BAD_STREAK": 0,
    "V15_SKIP_LEARN": 0,
    "V15_SKIP_LEARN_DEPTH_THIN": 0,
    "V15_SKIP_LEARN_SPREAD_WIDE": 0,
}


def _smart_v2_load_passports():
    if not getattr(cfg, "SMART_V2_PERSIST_ENABLED", True):
        return
    path = getattr(cfg, "SMART_V2_PASSPORT_PATH", "/root/skynet/data/smart_v2_passport.json")
    try:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        now = time.time()
        loaded = 0
        for symbol, data in raw.get("symbols", {}).items():
            q = SmartV2SymbolQuality.from_dict(data)
            # Не тащим древние cooldown навсегда.
            if q.cooldown_until and q.cooldown_until < now - 86400:
                q.cooldown_until = 0.0
            _SMART_V2_QUALITY[symbol] = q
            loaded += 1
        if loaded:
            log(f"🧠 SMART_V2_PASSPORT_LOADED symbols={loaded} path={path}\n")
    except Exception as e:
        log(f"⚠️ SMART_V2_PASSPORT_LOAD_ERROR | {type(e).__name__}: {e}\n")


def _smart_v2_save_passports():
    if not getattr(cfg, "SMART_V2_PERSIST_ENABLED", True):
        return
    path = getattr(cfg, "SMART_V2_PASSPORT_PATH", "/root/skynet/data/smart_v2_passport.json")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {
            "version": "v14",
            "updated": time.time(),
            "symbols": {symbol: q.to_dict() for symbol, q in _SMART_V2_QUALITY.items()},
        }
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception as e:
        log(f"⚠️ SMART_V2_PASSPORT_SAVE_ERROR | {type(e).__name__}: {e}\n")


_smart_v2_load_passports()


def _smart_v2_quality(symbol: str) -> SmartV2SymbolQuality:
    q = _SMART_V2_QUALITY.get(symbol)
    if q is None:
        q = SmartV2SymbolQuality()
        _SMART_V2_QUALITY[symbol] = q
    return q


def _smart_v2_filtered_055(c: dict) -> bool:
    return (
        c.get("score", -999) >= 4
        and 0.25 <= c.get("price_change", 999.0) <= 0.55
        and c.get("trend_15m", -999.0) > 0
    )


def _smart_v2_clean_candidate(c: dict) -> bool:
    return (
        c.get("score", 0) >= 4
        and c.get("btc_5m_change", -999.0) >= -0.05
        and c.get("oi_change", -999.0) >= -0.50
        and c.get("structure_risk", 999) <= 2
        and c.get("breakout_risk_score", 999) <= 4
        and c.get("false_breakouts_15m", 999) <= 3
    )


def _smart_v2_strong_candidate(c: dict) -> bool:
    return (
        c.get("score", 0) >= 5
        and c.get("btc_5m_change", -999.0) >= 0.0
        and c.get("oi_change", -999.0) >= 0.0
        and c.get("structure_risk", 999) <= 1
        and c.get("breakout_risk_score", 999) <= 3
        and c.get("false_breakouts_15m", 999) <= 1
    )


def _smart_v2_ultra_candidate(c: dict) -> bool:
    return (
        c.get("score", 0) >= 6
        and c.get("btc_5m_change", -999.0) >= 0.10
        and c.get("oi_change", -999.0) >= 0.50
        and c.get("structure_risk", 999) <= 1
        and c.get("breakout_risk_score", 999) <= 2
        and c.get("false_breakouts_15m", 999) <= 1
        and c.get("price_change", 999.0) <= 0.65
    )


def _smart_v2_core_candidate(c: dict) -> bool:
    # V14: core/top30 больше не автопроход.
    # Вырезает ситуации типа score=7, rank=14, но BRisk=4 / FB=3.
    if not getattr(cfg, "SMART_V2_CORE_RISK_GATE_ENABLED", True):
        return True

    return (
        c.get("score", 0) >= getattr(cfg, "SMART_V2_CORE_MIN_SCORE", 5)
        and c.get("breakout_risk_score", 999) <= getattr(cfg, "SMART_V2_CORE_MAX_BRISK", 3)
        and c.get("false_breakouts_15m", 999) <= getattr(cfg, "SMART_V2_CORE_MAX_FALSE_BREAKOUTS", 2)
        and c.get("structure_risk", 999) <= getattr(cfg, "SMART_V2_CORE_MAX_STRUCTURE_RISK", 2)
        and c.get("trend_15m", -999.0) >= getattr(cfg, "SMART_V2_CORE_MIN_TREND_15M", 0.30)
        and c.get("btc_5m_change", -999.0) >= getattr(cfg, "SMART_V2_CORE_MIN_BTC_5M", -0.05)
        and c.get("oi_change", -999.0) >= getattr(cfg, "SMART_V2_CORE_MIN_OI", -0.50)
        and c.get("initiative_buying_proxy", False)
    )


def smart_v2_pass_guard(c: dict, guard: str) -> bool:
    guard = (guard or "CLEAN_EXEC").upper()

    if not _smart_v2_filtered_055(c):
        return False

    if guard == "CLEAN_EXEC":
        return (
            c.get("breakout_risk_score", 999) <= 4
            and c.get("false_breakouts_15m", 999) <= 3
            and c.get("structure_risk", 999) <= 2
            and c.get("initiative_buying_proxy", False)
            and c.get("oi_change", -999.0) >= -0.50
            and c.get("btc_5m_change", -999.0) >= -0.10
            and c.get("trend_15m", -999.0) >= 0.30
        )

    if guard == "OI0_CLEAN":
        return (
            c.get("breakout_risk_score", 999) <= 4
            and c.get("false_breakouts_15m", 999) <= 3
            and c.get("structure_risk", 999) <= 2
            and c.get("initiative_buying_proxy", False)
            and c.get("oi_change", -999.0) >= 0.0
            and c.get("btc_5m_change", -999.0) >= -0.10
            and c.get("trend_15m", -999.0) >= 0.30
        )

    if guard == "BTC0_CLEAN":
        return (
            c.get("breakout_risk_score", 999) <= 4
            and c.get("false_breakouts_15m", 999) <= 3
            and c.get("structure_risk", 999) <= 2
            and c.get("initiative_buying_proxy", False)
            and c.get("oi_change", -999.0) >= -0.50
            and c.get("btc_5m_change", -999.0) >= 0.0
            and c.get("trend_15m", -999.0) >= 0.30
        )

    return False


def smart_v2_register_watch(c: dict, current_time: float, time_str: str):
    symbol = c.get("symbol", "")
    if not symbol:
        return

    # One monitor per symbol per ~15 minutes is enough; otherwise identical
    # CLEAN/OI/BTC strategy checks will spam the passport.
    key = (symbol, int(current_time // 900))
    if _SMART_V2_LAST_WATCH.get(key):
        return
    _SMART_V2_LAST_WATCH[key] = True

    dynamic_exit = calc_atr5b_exit_params(c)

    watch = {
        "symbol": symbol,
        "clean_symbol": c.get("clean_symbol", symbol),
        "entry": c.get("price", 0.0),
        "time": current_time,
        "max_profit_pct": 0.0,
        "max_loss_pct": 0.0,
        "partial_taken": False,
        "remaining_fraction": 1.0,
        "margin": cfg.SMART_V2_MARGIN,
        "leverage": cfg.SMART_V2_LEVERAGE,
        **dynamic_exit,
    }
    if watch["entry"] <= 0:
        return

    _SMART_V2_WATCHES.append(watch)
    _SMART_V2_STATS["watched"] += 1

    log(
        f"[{time_str}] SMART_V2_WATCH | {watch['clean_symbol']} | "
        f"rank={c.get('current_turnover_rank', 999999)} guard={c.get('smart_v2_guard','-')} "
        f"entry={watch['entry']:.8f} score={c.get('score')} "
        f"brisk={c.get('breakout_risk_score', 999)} fb={c.get('false_breakouts_15m', 999)}\n"
    )


def smart_v2_decision(c: dict, scfg) -> Tuple[bool, str]:
    rank = int(c.get("current_turnover_rank", 999999))
    core_top = int(getattr(scfg, "smart_core_top", cfg.SMART_V2_CORE_TOP) or cfg.SMART_V2_CORE_TOP)
    mid_top = int(getattr(scfg, "smart_mid_top", cfg.SMART_V2_MID_TOP) or cfg.SMART_V2_MID_TOP)

    q = _smart_v2_quality(c.get("symbol", "")).features()
    current_time = safe_float(c.get("_current_time"), time.time())

    # V14: временный toxic cooldown работает даже для core/top30.
    if q["cooldown_until"] and current_time < q["cooldown_until"]:
        if cfg.SMART_V2_ALLOW_ULTRA_OVERRIDE and _smart_v2_ultra_candidate(c):
            return True, "COOLDOWN_ULTRA_OVERRIDE"
        return False, "COOLDOWN"

    if q["bad_streak"] >= cfg.SMART_V2_MAX_BAD_STREAK and q["obs"] >= 2:
        if cfg.SMART_V2_ALLOW_ULTRA_OVERRIDE and _smart_v2_ultra_candidate(c):
            return True, "BAD_STREAK_ULTRA_OVERRIDE"
        return False, "BAD_STREAK"

    if rank <= core_top:
        if not _smart_v2_core_candidate(c):
            return False, "CORE_RISK_REJECT"
        return True, "CORE_CLEAN"

    if rank > mid_top:
        return False, "EXPLORE_MONITOR_ONLY"

    if q["obs"] < cfg.SMART_V2_MIN_OBS:
        # V2_STRICT cold policy: only ultra current signal may spend money in MID.
        if _smart_v2_ultra_candidate(c):
            return True, "MID_COLD_ULTRA"
        return False, "MID_COLD_REJECT"

    quality_ok = (
        q["avg_net"] >= cfg.SMART_V2_MIN_AVG_NET
        and q["sl_rate"] <= cfg.SMART_V2_MAX_SL_RATE
        and q["avg_mfe"] >= cfg.SMART_V2_MIN_AVG_MFE
        and _smart_v2_clean_candidate(c)
    )
    if quality_ok:
        return True, "MID_QUALITY_OK"

    if cfg.SMART_V2_ALLOW_STRONG_OVERRIDE and _smart_v2_strong_candidate(c) and q["sl_rate"] <= min(0.75, cfg.SMART_V2_MAX_SL_RATE + 0.15):
        return True, "MID_STRONG_OVERRIDE"

    if cfg.SMART_V2_ALLOW_ULTRA_OVERRIDE and _smart_v2_ultra_candidate(c) and q["sl_rate"] <= 0.75:
        return True, "MID_ULTRA_OVERRIDE"

    return False, "MID_QUALITY_REJECT"

def smart_v2_should_enter(c: dict, scfg) -> bool:
    guard = getattr(scfg, "smart_guard", "CLEAN_EXEC")
    if not smart_v2_pass_guard(c, guard):
        return False

    c["smart_v2_guard"] = guard
    current_time = safe_float(c.get("_current_time"), time.time())
    time_str = c.get("_time_str") or time.strftime("%H:%M:%S")
    smart_v2_register_watch(c, current_time, time_str)

    ok, reason = smart_v2_decision(c, scfg)
    c["smart_v2_reason"] = reason
    c["smart_v2_rank"] = c.get("current_turnover_rank", 999999)
    _SMART_V2_STATS[reason] = _SMART_V2_STATS.get(reason, 0) + 1

    if ok:
        _SMART_V2_STATS["would_trade"] += 1
        return True

    _SMART_V2_STATS["rejects"] += 1
    return False


def _smart_v2_close_watch(w, reason: str, exit_pct: float, current_time: float, time_str: str):
    gross, net, costs = calc_net_pnl(w["margin"], w["leverage"], exit_pct)
    q = _smart_v2_quality(w["symbol"])
    q.update(net, w["max_profit_pct"], reason, current_time)
    _smart_v2_save_passports()
    _SMART_V2_STATS["closed"] += 1

    log(
        f"[{time_str}] SMART_V2_WATCH_CLOSE | {w['clean_symbol']} | {reason} | "
        f"HypoNet:{net:+.2f}$ MFE:+{w['max_profit_pct']:.2f}% MAE:{w['max_loss_pct']:.2f}% | "
        f"Qobs={q.features()['obs']} Qavg={q.features()['avg_net']:+.2f}$ "
        f"Qsl={q.features()['sl_rate']:.2f} BadStreak={q.features()['bad_streak']}\n"
    )


def smart_v2_update_symbol(symbol: str, clean_symbol: str, price: float, current_time: float, time_str: str):
    if not _SMART_V2_WATCHES:
        return

    remaining = []
    for w in _SMART_V2_WATCHES:
        if w["symbol"] != symbol:
            remaining.append(w)
            continue

        if w["entry"] <= 0:
            continue

        price_diff = ((price - w["entry"]) / w["entry"]) * 100.0
        w["max_profit_pct"] = max(w["max_profit_pct"], price_diff)
        w["max_loss_pct"] = min(w["max_loss_pct"], price_diff)
        held = (current_time - w["time"]) / 60.0

        reason = None
        exit_pct = price_diff

        if not w.get("partial_taken", False):
            if price_diff <= -safe_float(w.get("stop_loss_pct"), cfg.STOP_LOSS):
                reason = "SL"
                exit_pct = -safe_float(w.get("stop_loss_pct"), cfg.STOP_LOSS)
            elif price_diff >= safe_float(w.get("partial_trigger_pct"), cfg.PARTIAL_TRIGGER_PCT):
                w["partial_taken"] = True
        else:
            runner_tp = safe_float(w.get("runner_tp_pct"), cfg.PARTIAL_RUNNER_TP_PCT)
            runner_stop = safe_float(w.get("runner_stop_pct"), cfg.PARTIAL_RUNNER_STOP_PCT)
            partial = safe_float(w.get("partial_trigger_pct"), cfg.PARTIAL_TRIGGER_PCT)
            if price_diff >= runner_tp:
                reason = "RUNNER_TP"
                exit_pct = 0.5 * partial + 0.5 * runner_tp
            elif price_diff <= runner_stop:
                reason = "RUNNER_STOP"
                exit_pct = 0.5 * partial + 0.5 * runner_stop

        if reason is None and held >= safe_float(w.get("time_stop_min"), cfg.ATR5B_TIME_STOP_MINUTES):
            reason = "TIME_PARTIAL" if w.get("partial_taken") else "TIME"
            if w.get("partial_taken"):
                partial = safe_float(w.get("partial_trigger_pct"), cfg.PARTIAL_TRIGGER_PCT)
                exit_pct = 0.5 * partial + 0.5 * price_diff
            else:
                exit_pct = price_diff

        if reason:
            _smart_v2_close_watch(w, reason, exit_pct, current_time, time_str)
        else:
            remaining.append(w)

    _SMART_V2_WATCHES[:] = remaining


def format_smart_v2_report() -> str:
    q_items = []
    for symbol, q in _SMART_V2_QUALITY.items():
        f = q.features()
        if f["obs"] <= 0:
            continue
        q_items.append((symbol, f))
    q_items.sort(key=lambda x: (x[1]["avg_net"], x[1]["avg_mfe"]), reverse=True)

    lines = ["=== SMART V2 SYMBOL PASSPORT REPORT ==="]
    lines.append(
        "Stats: "
        + " ".join([f"{k}:{v}" for k, v in sorted(_SMART_V2_STATS.items()) if isinstance(v, (int, float))])
        + f" ActiveWatch:{len(_SMART_V2_WATCHES)} Symbols:{len(q_items)}"
    )

    if q_items:
        lines.append("--- Top quality symbols ---")
        for symbol, f in q_items[:12]:
            lines.append(
                f"{symbol.replace('_USDT','')}: obs={f['obs']} avgNet={f['avg_net']:+.2f}$ "
                f"avgMFE={f['avg_mfe']:.2f}% slRate={f['sl_rate']:.2f} bad={f['bad_streak']} tox={f.get('toxic_reason','')}"
            )
        lines.append("--- Worst quality symbols ---")
        for symbol, f in list(reversed(q_items[-12:])):
            lines.append(
                f"{symbol.replace('_USDT','')}: obs={f['obs']} avgNet={f['avg_net']:+.2f}$ "
                f"avgMFE={f['avg_mfe']:.2f}% slRate={f['sl_rate']:.2f} bad={f['bad_streak']} tox={f.get('toxic_reason','')}"
            )

    return "\n".join(lines) + "\n"


# ============================================================
# STRATEGY RULES
# ============================================================

def is_safe_rule(c):
    return (
        c["score"] >= 4
        and 0.25 <= c["price_change"] <= 0.45
        and 0 < c["trend_15m"] <= 2.5
        and not is_exhaustion(c["vol_ratio"], c["price_change"])
    )


def is_safe_strict_rule(c):
    return (
        c["score"] >= 5
        and 0.25 <= c["price_change"] <= 0.45
        and 0.30 <= c["trend_15m"] <= 2.5
        and c["oi_change"] >= 1.0
        and c["btc_5m_change"] > -0.05
        and not is_exhaustion(c["vol_ratio"], c["price_change"])
    )





def normalized_spread_bps(c: dict) -> tuple[float, bool]:
    """
    Returns (spread_bps, is_real_depth_value).

    Before depth check candidate often has no spread_bps yet.
    Old code treated missing spread as 999 and cost-gated everything too early.
    For pre-depth cost model we use cfg.SPREAD_BPS as estimate.
    Real spread hard rejection is allowed only when spread was actually measured.
    """
    raw = c.get("spread_bps", None)

    try:
        if raw is None:
            return float(getattr(cfg, "SPREAD_BPS", 3.0)), False

        spread = float(raw)

        # 999/999.0 is our sentinel for "unknown/not measured", not a real spread.
        if spread >= 900:
            return float(getattr(cfg, "SPREAD_BPS", 3.0)), False

        return spread, True

    except Exception:
        return float(getattr(cfg, "SPREAD_BPS", 3.0)), False



def execution_roundtrip_cost_bps(c: dict, mode: str = "taker") -> float:
    """
    Estimated roundtrip cost in bps:
    entry fee + exit fee + spread + entry slippage + exit slippage.
    """
    if not getattr(cfg, "EXEC_COST_MODEL_ENABLED", True):
        return 0.0

    spread, _spread_is_real = normalized_spread_bps(c)
    spread = max(spread, float(getattr(cfg, "EXEC_MIN_SPREAD_BPS_FLOOR", 1.0)))

    if mode == "maker":
        fee_side = float(getattr(cfg, "EXEC_FEE_MAKER_BPS_PER_SIDE", 0.0))
        # maker is not free in reality: queue miss/adverse selection still exists,
        # but direct slippage is lower than taker.
        slip_side = min(float(getattr(cfg, "EXEC_DEFAULT_SLIPPAGE_BPS_PER_SIDE", 5.0)), 1.0)
    else:
        fee_side = float(getattr(cfg, "EXEC_FEE_TAKER_BPS_PER_SIDE", 8.0))
        slip_side = float(getattr(cfg, "EXEC_DEFAULT_SLIPPAGE_BPS_PER_SIDE", 5.0))

    return fee_side * 2.0 + spread + slip_side * 2.0


def expected_move_bps(c: dict, lane: str = "normal") -> float:
    """
    Very conservative expected move proxy.
    price_change is current impulse in percent.
    We only assume part of it is capturable.
    """
    try:
        pc_bps = abs(float(c.get("price_change", 0.0))) * 100.0
    except Exception:
        pc_bps = 0.0

    if lane == "fast":
        mult = float(getattr(cfg, "EXEC_EXPECTED_MOVE_MULTIPLIER_FAST", 0.90))
    elif lane == "escape":
        mult = float(getattr(cfg, "EXEC_EXPECTED_MOVE_MULTIPLIER_ESCAPE", 0.80))
    else:
        mult = float(getattr(cfg, "EXEC_EXPECTED_MOVE_MULTIPLIER_NORMAL", 0.85))

    return pc_bps * mult


def required_move_bps(c: dict, lane: str = "normal", mode: str = "taker") -> float:
    cost = execution_roundtrip_cost_bps(c, mode=mode)

    if lane == "fast":
        buf = float(getattr(cfg, "EXEC_COST_BUFFER_FAST", 1.30))
        floor = float(getattr(cfg, "EXEC_MIN_EXPECTED_MOVE_BPS_FAST", 30.0))
    elif lane == "escape":
        buf = float(getattr(cfg, "EXEC_COST_BUFFER_ESCAPE", 1.20))
        floor = float(getattr(cfg, "EXEC_MIN_EXPECTED_MOVE_BPS_ESCAPE", 30.0))
    else:
        buf = float(getattr(cfg, "EXEC_COST_BUFFER_NORMAL", 1.60))
        floor = float(getattr(cfg, "EXEC_MIN_EXPECTED_MOVE_BPS_NORMAL", 35.0))

    return max(floor, cost * buf)


def cost_gate_long(c: dict, lane: str = "normal", mode: str = "taker") -> bool:
    """
    Cost-aware long gate.
    Rejects tiny gross-positive signals that are likely to become net-negative.
    """
    if not getattr(cfg, "COST_AWARE_ENABLED", True):
        return True
    if not getattr(cfg, "EXEC_COST_MODEL_ENABLED", True):
        return True

    try:
        score = float(c.get("score", -999))
        vol = float(c.get("vol_ratio", 0.0))
        spread, spread_is_real = normalized_spread_bps(c)
    except Exception:
        return False

    if score < float(getattr(cfg, "COST_GATE_MIN_SCORE_LONG", 3)):
        return False
    if vol < float(getattr(cfg, "COST_GATE_MIN_VOL_LONG", 8.0)):
        return False

    # Only reject wide spread if spread was actually measured.
    # Pre-depth candidates must not be killed by sentinel 999.
    if spread_is_real and spread > float(getattr(cfg, "COST_GATE_MAX_SPREAD_LONG_BPS", 5.0)):
        return False

    exp_bps = expected_move_bps(c, lane=lane)
    req_bps = required_move_bps(c, lane=lane, mode=mode)

    return exp_bps >= req_bps


def cost_gate_debug(c: dict, lane: str = "normal", mode: str = "taker") -> str:
    try:
        exp_bps = expected_move_bps(c, lane=lane)
        req_bps = required_move_bps(c, lane=lane, mode=mode)
        cost_bps = execution_roundtrip_cost_bps(c, mode=mode)
        spread, spread_is_real = normalized_spread_bps(c)
        pc = float(c.get("price_change", 0.0))
        vol = float(c.get("vol_ratio", 0.0))
        score = c.get("score", "-")
        spread_src = "real" if spread_is_real else "est"
        return (
            f"exp={exp_bps:.1f}bps req={req_bps:.1f}bps cost={cost_bps:.1f}bps "
            f"pc={pc:+.2f}% vol=x{vol:.1f} spread={spread:.2f}bps/{spread_src} score={score}"
        )
    except Exception as e:
        return f"cost_debug_error={e}"


def is_depth_thin_escape_candidate(c: dict) -> bool:
    """Strong rejected DEPTH_THIN signal that deserves shadow observation."""
    if not getattr(cfg, "DEPTH_THIN_ESCAPE_ENABLED", True):
        return False

    try:
        score = float(c.get("score", -999))
        pc = abs(float(c.get("price_change", 0.0)))
        vol = float(c.get("vol_ratio", 0.0))
        rank = float(c.get("current_turnover_rank", 999999))
    except Exception:
        return False

    return (
        score >= float(getattr(cfg, "DEPTH_THIN_ESCAPE_MIN_SCORE", 5))
        and vol >= float(getattr(cfg, "DEPTH_THIN_ESCAPE_MIN_VOL", 15.0))
        and pc >= float(getattr(cfg, "DEPTH_THIN_ESCAPE_MIN_PC", 0.30))
        and rank <= float(getattr(cfg, "DEPTH_THIN_ESCAPE_MAX_RANK", 80))
    )




def is_cost_near_miss_fast(c: dict) -> bool:
    """
    Shadow-only lane:
    global cost gate stays strict, but we separately test clean near-misses.
    Example target: TNSR-like case that failed E39/R46 but then produced strong MFE.
    """
    if not getattr(cfg, "COST_NEAR_MISS_FAST_ENABLED", True):
        return False

    try:
        score = float(c.get("score", -999))
        vol = float(c.get("vol_ratio", 0.0))
        pc = float(c.get("price_change", 0.0))
        trend = float(c.get("trend_15m", 0.0))
        btc = float(c.get("btc_5m_change", 0.0))
        oi = float(c.get("oi_change", 0.0))
        rank = float(c.get("current_turnover_rank", 999999))
        struct = float(c.get("structure_risk", 999))
        brisk = float(c.get("breakout_risk_score", 999))
        fb = float(c.get("false_breakouts_15m", 999))
    except Exception:
        return False

    # It must FAIL normal cost gate, otherwise it belongs to normal strategies.
    if cost_gate_long(c, lane="normal", mode="taker"):
        return False

    exp_bps = expected_move_bps(c, lane="normal")
    req_bps = required_move_bps(c, lane="normal", mode="taker")
    if req_bps <= 0:
        return False

    near_ratio = exp_bps / req_bps

    return (
        near_ratio >= float(getattr(cfg, "COST_NEAR_MISS_MIN_EXPECTED_TO_REQUIRED", 0.80))
        and score >= float(getattr(cfg, "COST_NEAR_MISS_MIN_SCORE", 4))
        and vol >= float(getattr(cfg, "COST_NEAR_MISS_MIN_VOL", 8.0))
        and float(getattr(cfg, "COST_NEAR_MISS_MIN_PC", 0.40)) <= pc <= float(getattr(cfg, "COST_NEAR_MISS_MAX_PC", 0.55))
        and trend >= float(getattr(cfg, "COST_NEAR_MISS_MIN_TREND", 1.0))
        and btc >= float(getattr(cfg, "COST_NEAR_MISS_MIN_BTC", -0.08))
        and oi >= float(getattr(cfg, "COST_NEAR_MISS_MIN_OI", -2.0))
        and rank <= float(getattr(cfg, "COST_NEAR_MISS_MAX_RANK", 50))
        and struct <= float(getattr(cfg, "COST_NEAR_MISS_MAX_STRUCT", 2))
        and brisk <= float(getattr(cfg, "COST_NEAR_MISS_MAX_BRISK", 2))
        and fb <= float(getattr(cfg, "COST_NEAR_MISS_MAX_FB", 1))
        and not c.get("absorption_risk_long")
        and not c.get("high_effort_low_result")
        and not c.get("weak_long_result")
    )



def should_enter_strategy(scfg: cfg.StrategyConfig, c: dict) -> bool:
    f = scfg.family

    # COST_AWARE_V1:
    # Do not spend taker-like costs on microscopic long moves.
    # Keep reject observer active separately; this gate only affects entries.
    if f not in ("yellow_score2", "yellow_score2_tight", "cost_near_miss_fast"):
        lane = "fast" if f in ("yellow_score3", "yellow_score3_fast") else "normal"
        if not cost_gate_long(c, lane=lane, mode="taker"):
            return False

    if f == "safe_045":
        return is_safe_rule(c)

    if f == "safe_045_strict":
        return is_safe_strict_rule(c)



    if f == "v15_spread_scout":
        # Dry-only scout: проверяем прибыльную часть SPREAD_WIDE, но не лезем в DEPTH_THIN.
        # Spread-границы проверятся позже после depth enrich через validate_depth_for_strategy().
        q = _smart_v2_quality(c.get("symbol", "")).features()
        now = safe_float(c.get("_current_time"), time.time())

        if q.get("cooldown_until") and now < q.get("cooldown_until"):
            return False
        if q.get("bad_streak", 0) >= cfg.SMART_V2_MAX_BAD_STREAK and q.get("obs", 0) >= 2:
            if not _smart_v2_ultra_candidate(c):
                return False

        return (
            c.get("score", -999) >= cfg.V15_SCOUT_MIN_SCORE
            and cfg.PRICE_CHANGE_MIN <= c.get("price_change", 999.0) <= cfg.V15_SCOUT_MAX_PRICE_CHANGE
            and c.get("vol_ratio", 999.0) <= cfg.V15_SCOUT_MAX_VOL_RATIO
            and c.get("trend_15m", -999.0) >= cfg.V15_SCOUT_MIN_TREND_15M
            and c.get("btc_5m_change", -999.0) >= cfg.V15_SCOUT_MIN_BTC_5M
            and c.get("oi_change", -999.0) >= cfg.V15_SCOUT_MIN_OI
            and c.get("breakout_risk_score", 999) <= cfg.V15_SCOUT_MAX_BRISK
            and c.get("false_breakouts_15m", 999) <= cfg.V15_SCOUT_MAX_FALSE_BREAKOUTS
            and c.get("structure_risk", 999) <= cfg.V15_SCOUT_MAX_STRUCTURE_RISK
            and c.get("initiative_buying_proxy", False)
            and not c.get("absorption_risk_long")
            and not c.get("high_effort_low_result")
            and not c.get("weak_long_result")
        )

    if f == "smart_v2_strict":
        return smart_v2_should_enter(c, scfg)

    if f in ("meta_v12_exec_safe", "meta_v12_oi_safe"):
        sources = meta_v12_sources(c, scfg)
        if not sources:
            return False
        c["meta_sources_v12"] = ",".join(sources)
        c["meta_source_count_v12"] = len(sources)
        return True



    if f == "breakout_confirm_atr":
        if c.get("score", -999) < cfg.BREAKOUT_MIN_SCORE:
            return False
        if not c.get("initiative_buying_proxy"):
            return False
        if not (0.25 <= c.get("price_change", 999.0) <= getattr(scfg, "confirm_max_price_change", cfg.BREAKOUT_MAX_PRICE_CHANGE)):
            return False
        if c.get("vol_ratio", 999.0) > getattr(scfg, "confirm_max_vol_ratio", cfg.BREAKOUT_MAX_VOL_RATIO):
            return False
        if c.get("trend_15m", -999.0) < getattr(scfg, "min_trend_15m_override", cfg.BREAKOUT_MIN_TREND_15M):
            return False
        if c.get("btc_5m_change", 0.0) < cfg.BREAKOUT_MIN_BTC_5M:
            return False
        if c.get("structure_risk", 0) > cfg.BREAKOUT_MAX_STRUCTURE_RISK:
            return False
        if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
            return False
        if not passes_breakout_risk_mode(c, getattr(scfg, "breakout_risk_mode", "NONE")):
            return False
        return True



    if f == "initiative_confirm_trend_atr":
        if getattr(scfg, "universe_top_n", 0) > 0:
            if int(c.get("current_turnover_rank", 999999)) > int(scfg.universe_top_n):
                return False
        if c.get("price_change", 999.0) > getattr(scfg, "confirm_max_price_change", cfg.TREND_ATR_MAX_PRICE_CHANGE):
            return False
        if c.get("vol_ratio", 999.0) > getattr(scfg, "confirm_max_vol_ratio", cfg.TREND_ATR_MAX_VOL_RATIO):
            return False
        if c.get("score", -999) < cfg.TREND_ATR_MIN_SCORE:
            return False
        if not (0.25 <= c.get("price_change", 999.0) <= cfg.TREND_ATR_MAX_PRICE_CHANGE):
            return False
        if c.get("trend_15m", -999.0) < max(cfg.TREND_ATR_MIN_TREND_15M, getattr(scfg, "min_trend_15m_override", -999.0)):
            return False
        if c.get("btc_5m_change", 0.0) < cfg.RUNNER_MIN_BTC_5M:
            return False
        if c.get("structure_risk", 0) > cfg.RUNNER_MAX_STRUCTURE_RISK:
            return False
        if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
            return False
        if not c.get("initiative_buying_proxy"):
            return False
        return True

    if f == "initiative_confirm_runner":
        if c.get("price_change", 999.0) > getattr(scfg, "confirm_max_price_change", cfg.CONFIRM_MAX_PRICE_CHANGE_DEFAULT):
            return False
        if c.get("vol_ratio", 999.0) > getattr(scfg, "confirm_max_vol_ratio", cfg.CONFIRM_MAX_VOL_RATIO_DEFAULT):
            return False
        if not (cfg.RUNNER_MIN_SCORE <= c["score"] and 0.25 <= c["price_change"] <= cfg.RUNNER_MAX_PRICE_CHANGE):
            return False
        if c["trend_15m"] < cfg.RUNNER_MIN_TREND_15M or c["btc_5m_change"] < cfg.RUNNER_MIN_BTC_5M:
            return False
        if c.get("structure_risk", 0) > cfg.RUNNER_MAX_STRUCTURE_RISK:
            return False
        if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
            return False
        if not c.get("initiative_buying_proxy"):
            return False
        # Archive tests show overheated FOMO is weaker; require extra support if allowed by PC065 branch.
        if c["price_change"] > 0.55:
            return (
                c["score"] >= cfg.FOMO_RUNNER_MIN_SCORE
                and c["trend_15m"] >= cfg.FOMO_RUNNER_MIN_TREND_15M
                and c["btc_5m_change"] >= cfg.FOMO_RUNNER_MIN_BTC_5M
            )
        return True

    if f == "initiative_runner":
        if not (cfg.RUNNER_MIN_SCORE <= c["score"] and 0.25 <= c["price_change"] <= cfg.RUNNER_MAX_PRICE_CHANGE):
            return False
        if c["trend_15m"] < cfg.RUNNER_MIN_TREND_15M or c["btc_5m_change"] < cfg.RUNNER_MIN_BTC_5M:
            return False
        if c.get("structure_risk", 0) > cfg.RUNNER_MAX_STRUCTURE_RISK:
            return False
        if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
            return False
        if not c.get("initiative_buying_proxy"):
            return False
        # Late FOMO requires stronger market support.
        if c["price_change"] > 0.55:
            return (
                c["score"] >= cfg.FOMO_RUNNER_MIN_SCORE
                and c["trend_15m"] >= cfg.FOMO_RUNNER_MIN_TREND_15M
                and c["btc_5m_change"] >= cfg.FOMO_RUNNER_MIN_BTC_5M
            )
        return True

    if f == "main_context_strict_runner":
        if not (cfg.RUNNER_MIN_SCORE <= c["score"] and 0.25 <= c["price_change"] <= 0.75):
            return False
        if c["trend_15m"] < max(cfg.RUNNER_MIN_TREND_15M, 0.50):
            return False
        if c["btc_5m_change"] < cfg.RUNNER_MIN_BTC_5M:
            return False
        if c.get("structure_risk", 0) > cfg.RUNNER_MAX_STRUCTURE_RISK:
            return False
        if c.get("absorption_risk_long") or c.get("high_effort_low_result") or c.get("weak_long_result"):
            return False
        if c["price_change"] > 0.55 and (c["score"] < cfg.FOMO_RUNNER_MIN_SCORE or c["btc_5m_change"] < cfg.FOMO_RUNNER_MIN_BTC_5M):
            return False
        return True

    if f == "main_tp08_exec":
        # Based on historically strong MAIN_V92_TP08, not over-filtered.
        return c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.75 and c["trend_15m"] > 0

    if f == "hybrid_full_main_fomo_exec":
        main_rule = c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.75 and c["trend_15m"] > 0
        fomo_extension = c["score"] >= 4 and 0.75 < c["price_change"] <= 0.85 and c["trend_15m"] > 0
        return main_rule or fomo_extension

    if f == "hybrid_full_main_fomo":
        main_rule = c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.75 and c["trend_15m"] > 0
        fomo_extension = c["score"] >= 4 and 0.75 < c["price_change"] <= 0.85 and c["trend_15m"] > 0
        return main_rule or fomo_extension

    if f == "hybrid_full_all":
        main_rule = c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.75 and c["trend_15m"] > 0
        fomo_extension = c["score"] >= 4 and 0.75 < c["price_change"] <= 0.85 and c["trend_15m"] > 0
        yellow_full = (
            c["score"] in (2, 3)
            and 0.25 <= c["price_change"] <= 0.45
            and c["trend_15m"] > 0
            and c["btc_5m_change"] > -0.10
            and c["oi_change"] > -2.0
        )
        return main_rule or fomo_extension or yellow_full

    if f == "hybrid_full_all_safe_shadow":
        classic = c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.55 and 0 < c["trend_15m"] <= 2.5 and not is_exhaustion(c["vol_ratio"], c["price_change"])
        controlled_fomo = c["score"] >= 6 and 0.55 < c["price_change"] <= 0.75 and 0 < c["trend_15m"] <= 2.5 and c["btc_5m_change"] >= 0.15 and c["oi_change"] > 1.0 and c["vol_ratio"] <= 25
        yellow_quality = c["score"] == 3 and 0.25 <= c["price_change"] <= 0.45 and c["trend_15m"] >= 0.30 and c["btc_5m_change"] >= 0.10 and c["oi_change"] > 0
        yellow_2_tight = c["score"] == 2 and 0.25 <= c["price_change"] <= 0.38 and c["trend_15m"] >= 0.30 and c["btc_5m_change"] > 0.05 and c["oi_change"] > 0
        return classic or controlled_fomo or yellow_quality or yellow_2_tight

    if f == "hybrid_core":
        classic = c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.55 and 0 < c["trend_15m"] <= 2.5 and not is_exhaustion(c["vol_ratio"], c["price_change"])
        controlled_fomo = c["score"] >= 5 and 0.55 < c["price_change"] <= 0.85 and 0 < c["trend_15m"] <= 3.0 and c["btc_5m_change"] >= 0.10 and c["oi_change"] > -1.0 and c["vol_ratio"] <= 25
        yellow_quality = c["score"] == 3 and 0.25 <= c["price_change"] <= 0.45 and c["trend_15m"] >= 0.30 and c["btc_5m_change"] >= 0.10 and c["oi_change"] > 0
        return classic or controlled_fomo or yellow_quality

    if f == "hybrid_scalp":
        filtered = c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.45 and 0 < c["trend_15m"] <= 2.5 and not is_exhaustion(c["vol_ratio"], c["price_change"])
        strong_main = c["score"] >= 6 and 0.25 <= c["price_change"] <= 0.55 and 0 < c["trend_15m"] <= 2.5 and c["btc_5m_change"] >= 0 and c["oi_change"] > -1.0 and not is_exhaustion(c["vol_ratio"], c["price_change"])
        very_clean_fomo = c["score"] >= 6 and 0.55 < c["price_change"] <= 0.75 and 0.30 <= c["trend_15m"] <= 2.5 and c["btc_5m_change"] >= 0.10 and c["oi_change"] > 1.0 and c["vol_ratio"] <= 25
        return filtered or strong_main or very_clean_fomo

    if f in ("main_v92_tp08", "main_v92_tp10"):
        return c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.75 and c["trend_15m"] > 0

    if f == "filtered_055":
        return c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.55 and 0 < c["trend_15m"] <= 2.5

    if f == "filtered_045":
        return c["score"] >= 4 and 0.25 <= c["price_change"] <= 0.45 and 0 < c["trend_15m"] <= 2.5

    if f == "fomo_test":
        return c["score"] >= 4 and 0.55 < c["price_change"] <= 0.85 and c["trend_15m"] > 0

    if f == "yellow_score3":
        return c["score"] == 3 and 0.25 <= c["price_change"] <= 0.45 and c["trend_15m"] > 0 and c["btc_5m_change"] > -0.10 and c["oi_change"] > -2.0

    if f == "cost_near_miss_fast":
        return is_cost_near_miss_fast(c)

    if f == "yellow_score3_fast":
        return (
            c["score"] == 3
            and getattr(cfg, "YELLOW_SCORE3_FAST_MIN_PC", 0.30) <= c["price_change"] <= getattr(cfg, "YELLOW_SCORE3_FAST_MAX_PC", 0.50)
            and c["vol_ratio"] >= getattr(cfg, "YELLOW_SCORE3_FAST_MIN_VOL", 8.0)
            and c["trend_15m"] >= getattr(cfg, "YELLOW_SCORE3_FAST_MIN_TREND", 0.20)
            and c["btc_5m_change"] >= getattr(cfg, "YELLOW_SCORE3_FAST_MIN_BTC", -0.05)
            and c["oi_change"] >= getattr(cfg, "YELLOW_SCORE3_FAST_MIN_OI", -1.0)
            and c.get("structure_risk", 0) <= getattr(cfg, "YELLOW_SCORE3_FAST_MAX_STRUCT", 3)
            and c.get("breakout_risk_score", 0) <= getattr(cfg, "YELLOW_SCORE3_FAST_MAX_BRISK", 4)
            and c.get("false_breakouts_15m", 0) <= getattr(cfg, "YELLOW_SCORE3_FAST_MAX_FB", 2)
        )

    if f == "yellow_score2":
        return c["score"] == 2 and 0.25 <= c["price_change"] <= 0.45 and c["trend_15m"] > 0 and c["btc_5m_change"] > -0.10 and c["oi_change"] > -2.0

    if f == "yellow_score2_tight":
        return c["score"] == 2 and 0.25 <= c["price_change"] <= 0.38 and c["trend_15m"] >= 0.30 and c["btc_5m_change"] > 0.05 and c["oi_change"] > 0

    return False


def candidate_priority(c: dict, scfg: cfg.StrategyConfig = None) -> float:
    # Price center depends on strategy family: safe likes early 0.35, fomo can accept later.
    fam = scfg.family if scfg else ""

    if fam == "v15_spread_scout":
        score = safe_float(c.get("score"), 0)
        pc = safe_float(c.get("price_change"), 0)
        trend = safe_float(c.get("trend_15m"), 0)
        btc5 = safe_float(c.get("btc_5m_change"), 0)
        oi = safe_float(c.get("oi_change"), 0)
        spread = safe_float(c.get("spread_bps"), 8.0)
        brisk = safe_float(c.get("breakout_risk_score"), 5)
        fb = safe_float(c.get("false_breakouts_15m"), 2)
        struct = safe_float(c.get("structure_risk"), 3)
        depth = min((safe_float(c.get("top5_bid_usdt"), 0) + safe_float(c.get("top5_ask_usdt"), 0)) / 10000.0, 8.0)
        rank = safe_float(c.get("current_turnover_rank"), 999)

        # Scout предпочитает spread около 6-8bps, не погоню за 12bps.
        return (
            score * 100.0
            + min(trend, 2.5) * 12.0
            + btc5 * 10.0
            + max(min(oi, 8.0), -2.0) * 3.0
            + depth * 4.0
            + (12.0 if rank <= 50 else 0.0)
            - abs(pc - 0.45) * 18.0
            - abs(spread - 7.0) * 8.0
            - brisk * 28.0
            - fb * 45.0
            - struct * 22.0
        )

    if fam in ("meta_v12_exec_safe", "meta_v12_oi_safe"):
        score = safe_float(c.get("score"), 0)
        pc = safe_float(c.get("price_change"), 0)
        trend = safe_float(c.get("trend_15m"), 0)
        btc5 = safe_float(c.get("btc_5m_change"), 0)
        oi = safe_float(c.get("oi_change"), 0)
        spread = safe_float(c.get("spread_bps"), 7.0)
        brisk = safe_float(c.get("breakout_risk_score"), 5)
        fb = safe_float(c.get("false_breakouts_15m"), 2)
        struct = safe_float(c.get("structure_risk"), 3)
        src_count = safe_float(c.get("meta_source_count_v12"), 0)
        rank = safe_float(c.get("current_turnover_rank"), 999)

        return (
            score * 100.0
            + min(trend, 2.0) * 10.0
            + btc5 * 6.0
            + max(min(oi, 10.0), -3.0) * 4.0
            + src_count * 18.0
            - abs(pc - 0.42) * 20.0
            - spread * 3.0
            - brisk * 18.0
            - fb * 35.0
            - struct * 10.0
            + (10.0 if rank <= cfg.META_V12_ROLL_TOP_N else 0.0)
        )

    if fam in ("initiative_runner", "main_context_strict_runner", "initiative_confirm_trend_atr", "initiative_confirm_runner", "breakout_confirm_atr", "meta_v12_exec_safe", "meta_v12_oi_safe"):
        target_price_change = 0.55
    elif fam in ("hybrid_full_main_fomo_exec", "hybrid_full_main_fomo"):
        target_price_change = 0.55
    elif fam == "main_tp08_exec":
        target_price_change = 0.45
    else:
        target_price_change = 0.35

    price_center_bonus = -abs(c["price_change"] - target_price_change) * 14.0
    trend_quality = min(c["trend_15m"], 1.5) * 2.0
    oi_quality = max(min(c["oi_change"], 8.0), -3.0)
    btc_quality = c["btc_5m_change"] * 3.0
    vol_quality = min(c["vol_ratio"], 25.0) / 10.0
    spread_quality = -safe_float(c.get("spread_bps"), 7.0) * 1.0
    depth_quality = min((safe_float(c.get("top5_bid_usdt"), 0) + safe_float(c.get("top5_ask_usdt"), 0)) / 10000.0, 5.0)
    initiative_bonus = 8.0 if c.get("initiative_buying_proxy") else 0.0
    structure_penalty = min(safe_float(c.get("structure_risk"), 0), 8.0) * 2.0

    return (
        c["score"] * 100.0
        + oi_quality * 3.0
        + trend_quality
        + btc_quality
        + price_center_bonus
        + vol_quality
        + spread_quality
        + depth_quality
        + initiative_bonus
        - structure_penalty
    )


# ============================================================
# OPEN/CLOSE/RISK
# ============================================================

def can_open_strategy(name, book, symbol, current_time, skip_reasons):
    scfg = book["config"]
    if scfg.global_toxic_ban and is_global_toxic_banned(symbol, current_time):
        skip_reasons.append(f"{name}: GLOBAL_TOXIC_BAN")
        return False

    if book["locked"]:
        skip_reasons.append(f"{name}: LOCKED_{book['lock_reason']}")
        return False

    if symbol in book["banned_until"] and current_time < book["banned_until"][symbol]:
        skip_reasons.append(f"{name}: COIN_BANNED_AFTER_SL")
        return False

    if symbol in book["last_trade"] and current_time - book["last_trade"][symbol] < cfg.TRADE_COOLDOWN:
        skip_reasons.append(f"{name}: COOLDOWN")
        return False

    if symbol in book["active"]:
        return False

    if len(book["active"]) >= scfg.max_open:
        skip_reasons.append(f"{name}: MAX_OPEN")
        return False

    locked_margin = sum(t["margin"] for t in book["active"].values())
    free_margin = book["balance"] - locked_margin
    if free_margin < scfg.margin:
        skip_reasons.append(f"{name}: NO_MARGIN")
        return False

    return True


def update_locks_after_close(name, book):
    scfg = book["config"]
    if book["locked"]:
        return

    book["peak_balance"] = max(book["peak_balance"], book["balance"])
    profit = book["balance"] - book["start_balance"]
    peak_profit = book["peak_balance"] - book["start_balance"]
    giveback = book["peak_balance"] - book["balance"]

    if profit >= scfg.p_lock:
        book["locked"] = True
        book["lock_reason"] = "PROFIT_TARGET"
        log(f"🔒 {name} LOCKED PROFIT_TARGET +${scfg.p_lock}\n")
    elif peak_profit >= scfg.give_act and giveback >= scfg.give_drop:
        book["locked"] = True
        book["lock_reason"] = "GIVEBACK"
        log(f"🛡 {name} LOCKED GIVEBACK ${giveback:.2f}\n")
    elif profit <= scfg.l_lock:
        book["locked"] = True
        book["lock_reason"] = "MAX_LOSS"
        log(f"🛑 {name} LOCKED MAX_LOSS {profit:.2f}$\n")


async def open_shadow_trade(name, book, candidate, current_time, time_str, dry_live: DryLiveManager):
    scfg = book["config"]
    symbol = candidate["symbol"]
    trade_id = f"{name}_{symbol}_{int(current_time)}"

    dynamic_exit = calc_atr5b_exit_params(candidate) if getattr(scfg, "atr5b_exit", False) else {}

    book["active"][symbol] = {
        "id": trade_id,
        "entry": candidate["price"],
        "margin": scfg.margin,
        "leverage": scfg.leverage,
        "time": current_time,
        "max_profit_pct": 0.0,
        "max_loss_pct": 0.0,
        "be_armed": False,
        "micro_lock_armed": False,
        "partial_taken": False,
        "remaining_fraction": 1.0,
        "realized_gross_pnl": 0.0,
        "realized_net_pnl": 0.0,
        "realized_costs": 0.0,
        "no_follow_logged": False,
        "atr5b_exit": bool(getattr(scfg, "atr5b_exit", False)),
        **dynamic_exit,
        "entry_context": {
            "oi_change": candidate.get("oi_change", 0.0),
            "spread_bps": candidate.get("spread_bps", 999.0),
            "structure_risk": candidate.get("structure_risk", 0),
            "absorption_risk_long": candidate.get("absorption_risk_long", False),
            "middle_range_noise": candidate.get("middle_range_noise", False),
            "weak_long_result": candidate.get("weak_long_result", False),
            "current_turnover_rank": candidate.get("current_turnover_rank", 999999),
            "pre_range_5m_pct": candidate.get("pre_range_5m_pct", 0.0),
            "confirm_move_pct": candidate.get("confirm_move_pct", 0.0),
            "meta_sources_v12": candidate.get("meta_sources_v12", ""),
            "meta_source_count_v12": candidate.get("meta_source_count_v12", 0),
            "breakout_risk_score": candidate.get("breakout_risk_score", 0),
            "false_breakouts_15m": candidate.get("false_breakouts_15m", 0),
            "red_volume_share_10m": candidate.get("red_volume_share_10m", 0.0),
            "ema9_slope_3m_pct": candidate.get("ema9_slope_3m_pct", 0.0),
        },
    }
    book["last_trade"][symbol] = current_time
    book["stats"]["trades"] += 1
    if candidate.get("structure_risk", 0) >= 4:
        book["stats"]["structure_flags"] += 1

    log(
        f"[{time_str}] SHADOW_OPEN | {name} | {candidate['clean_symbol']} | "
        f"Entry:{candidate['price']} | Score:{candidate['score']} | "
        f"StructRisk:{candidate.get('structure_risk',0)} | TradeID:{trade_id}\n"
    )

    await dry_live.maybe_open(name, book, candidate, trade_id, time_str)
    return trade_id


def validate_depth_for_strategy(scfg: cfg.StrategyConfig, cand: dict) -> Tuple[bool, str]:
    if not scfg.require_depth:
        return True, "DEPTH_NOT_REQUIRED"
    if not cand.get("depth_available", False):
        return False, cand.get("depth_reason", "DEPTH_FAIL")
    if cand.get("depth_thin", False):
        return False, "DEPTH_THIN"
    spread_bps = safe_float(cand.get("spread_bps"), 999.0)
    if spread_bps > scfg.spread_limit_bps:
        return False, f"SPREAD_WIDE_{spread_bps:.2f}bps_GT_{scfg.spread_limit_bps:.0f}"

    min_spread = safe_float(getattr(scfg, "min_spread_bps", 0.0), 0.0)
    if min_spread > 0 and spread_bps < min_spread:
        return False, f"V15_SCOUT_SPREAD_TOO_TIGHT_{spread_bps:.2f}bps_LT_{min_spread:.0f}"

    return True, "DEPTH_OK"


async def process_selector_strategy(name, candidates, books, current_time, time_str, dry_live, skip_tracker):
    book = books[name]
    scfg = book["config"]
    skip_reasons = []

    if not candidates:
        return [], skip_reasons

    book["stats"]["selector_candidates"] += len(candidates)

    if book["locked"]:
        skip_reasons.append(f"{name}: LOCKED_{book['lock_reason']}")
        return [], skip_reasons

    ordered = sorted(candidates, key=lambda c: candidate_priority(c, scfg), reverse=True)
    opened = []

    for cand in ordered:
        if len(book["active"]) >= scfg.max_open:
            skip_reasons.append(f"{name}: MAX_OPEN")
            break

        ok_depth, depth_reason = validate_depth_for_strategy(scfg, cand)
        if not ok_depth:
            if "HTTP" in depth_reason or "EXC" in depth_reason or "FAIL" in depth_reason or "NO_RESULT" in depth_reason:
                book["stats"]["depth_fail"] += 1
            else:
                book["stats"]["depth_skip"] += 1
            skip_reasons.append(f"{name}: {depth_reason}")
            skip_tracker.open(name, cand, depth_reason, scfg, current_time, time_str)
            continue

        book["stats"]["depth_ok"] += 1

        if not can_open_strategy(name, book, cand["symbol"], current_time, skip_reasons):
            if (
                getattr(cfg, "REJECT_OBSERVER_TRACK_CAN_OPEN", True)
                and getattr(scfg, "skip_track", False)
                and should_observe_reject_strategy(name)
                and should_observe_reject(cand)
            ):
                can_reason = ",".join(skip_reasons) if skip_reasons else "CAN_OPEN_FALSE"
                skip_tracker.open(
                    name,
                    cand,
                    "REJECT_CAN_OPEN_" + can_reason.replace(" ", "_").replace(":", ""),
                    scfg,
                    current_time,
                    time_str,
                    force=True,
                )
            continue

        await open_shadow_trade(name, book, cand, current_time, time_str, dry_live)
        opened.append(cand["clean_symbol"])
        book["stats"]["selector_opened"] += 1

        log(
            f"[{time_str}] SELECTOR_PICK | {name} | {cand['clean_symbol']} | "
            f"priority={candidate_priority(cand, scfg):.2f} | score={cand['score']} | "
            f"price={cand['price_change']:.2f}% | oi={cand['oi_change']:.1f}% | "
            f"trend={cand['trend_15m']:.2f}% | btc={cand['btc_5m_change']:.2f}% | "
            f"spread={cand.get('spread_bps',999):.2f}bps/{scfg.spread_limit_bps:.0f} | "
            f"bid5=${cand.get('top5_bid_usdt',0):.0f} ask5=${cand.get('top5_ask_usdt',0):.0f} | "
            f"struct={cand.get('structure_risk',0)} init={int(cand.get('initiative_buying_proxy',False))}\n"
        )

    return opened, skip_reasons



async def _take_partial(name, book, symbol, clean_symbol, trade, price_diff, current_time, time_str, dry_live):
    scfg = book["config"]
    if not scfg.partial_take_test or trade.get("partial_taken", False):
        return False
    partial_trigger = safe_float(trade.get("partial_trigger_pct"), cfg.PARTIAL_TRIGGER_PCT)
    partial_fraction = safe_float(trade.get("partial_close_fraction"), cfg.PARTIAL_CLOSE_FRACTION)
    if price_diff < partial_trigger:
        return False

    fraction = max(0.0, min(partial_fraction, trade.get("remaining_fraction", 1.0)))
    if fraction <= 0:
        return False

    exit_pct = partial_trigger
    gross, net, costs = calc_net_pnl(trade["margin"] * fraction, trade["leverage"], exit_pct)

    trade["partial_taken"] = True
    trade["remaining_fraction"] = max(0.0, trade.get("remaining_fraction", 1.0) - fraction)
    trade["realized_gross_pnl"] += gross
    trade["realized_net_pnl"] += net
    trade["realized_costs"] += costs

    book["balance"] += net
    st = book["stats"]
    st["PARTIAL_TP"] += 1
    st["total_gross_pnl"] += gross
    st["net_pnl"] += net
    st["costs"] += costs
    if net > 0:
        st["net_profit"] += net
    elif net < 0:
        st["net_loss"] += abs(net)

    partial_price = trade["entry"] * (1 + exit_pct / 100.0)
    await dry_live.maybe_partial(name, symbol, clean_symbol, partial_price, fraction, net, time_str)

    log(
        f"[{time_str}] PARTIAL_TP | {name} | {clean_symbol} | "
        f"fraction={fraction:.2f} exit=+{exit_pct:.2f}% Net:{net:+.2f}$ "
        f"remaining={trade['remaining_fraction']:.2f} | Bal:${book['balance']:.2f}\n"
    )
    return True

def _runner_final_reason(scfg, trade, price_diff, time_held):
    # MFE-based rules are live-compatible: trade['max_profit_pct'] is accumulated only after entry.
    if scfg.fast_fail_test and time_held >= cfg.FAST_FAIL_AFTER_MINUTES:
        if trade["max_profit_pct"] < cfg.FAST_FAIL_MFE_PCT and price_diff <= cfg.FAST_FAIL_LOSS_PCT:
            return "FAST_FAIL", price_diff

    if scfg.micro_lock_test and not trade.get("micro_lock_armed", False):
        if trade["max_profit_pct"] >= cfg.MICRO_LOCK_TRIGGER_PCT:
            trade["micro_lock_armed"] = True

    if scfg.micro_lock_test and trade.get("micro_lock_armed", False) and price_diff <= cfg.MICRO_LOCK_STOP_PCT:
        return "MICRO_LOCK", cfg.MICRO_LOCK_STOP_PCT

    if trade.get("partial_taken", False):
        runner_tp = safe_float(trade.get("runner_tp_pct"), cfg.PARTIAL_RUNNER_TP_PCT)
        runner_stop = safe_float(trade.get("runner_stop_pct"), cfg.PARTIAL_RUNNER_STOP_PCT)
        if price_diff >= runner_tp:
            return "RUNNER_TP", runner_tp
        if price_diff <= runner_stop:
            return "RUNNER_STOP", runner_stop
    else:
        if price_diff >= scfg.tp:
            return "TP", scfg.tp

    return None, price_diff


async def manage_open_trade(name, book, symbol, clean_symbol, price, current_time, time_str, dry_live):
    if symbol not in book["active"]:
        return False

    scfg = book["config"]
    trade = book["active"][symbol]
    price_diff = ((price - trade["entry"]) / trade["entry"]) * 100.0
    time_held = (current_time - trade["time"]) / 60.0
    trade["max_profit_pct"] = max(trade["max_profit_pct"], price_diff)
    trade["max_loss_pct"] = min(trade["max_loss_pct"], price_diff)

    if (
        not trade.get("no_follow_logged", False)
        and time_held >= cfg.NO_FOLLOW_MINUTES
        and trade["max_profit_pct"] < cfg.NO_FOLLOW_MFE
    ):
        trade["no_follow_logged"] = True
        book["stats"]["NO_FOLLOW"] += 1
        log(
            f"[{time_str}] NO_FOLLOW_THROUGH | {name} | {clean_symbol} | "
            f"held={time_held:.1f}m MFE:+{trade['max_profit_pct']:.2f}%\n"
        )

    if scfg.be_v2_test and not trade.get("be_armed", False) and trade["max_profit_pct"] >= cfg.BE_V2_TRIGGER_PCT:
        trade["be_armed"] = True
        log(
            f"[{time_str}] BE_V2_ARMED | {name} | {clean_symbol} | "
            f"MFE:+{trade['max_profit_pct']:.2f}% virtual_stop=+{cfg.BE_V2_STOP_PCT:.2f}%\n"
        )

    if scfg.micro_lock_test and not trade.get("micro_lock_armed", False) and trade["max_profit_pct"] >= cfg.MICRO_LOCK_TRIGGER_PCT:
        trade["micro_lock_armed"] = True
        log(
            f"[{time_str}] MICRO_LOCK_ARMED | {name} | {clean_symbol} | "
            f"MFE:+{trade['max_profit_pct']:.2f}% virtual_stop={cfg.MICRO_LOCK_STOP_PCT:+.2f}%\n"
        )

    # Partial is processed before final close checks.
    await _take_partial(name, book, symbol, clean_symbol, trade, price_diff, current_time, time_str, dry_live)

    reason = None
    exit_price_diff = price_diff

    runner_reason, runner_exit = _runner_final_reason(scfg, trade, price_diff, time_held)
    if runner_reason:
        reason = runner_reason
        exit_price_diff = runner_exit
        book["stats"][reason] += 1
    elif scfg.be_v2_test and trade.get("be_armed", False) and price_diff <= cfg.BE_V2_STOP_PCT:
        reason = "BE_V2"
        exit_price_diff = cfg.BE_V2_STOP_PCT
        book["stats"]["BE_V2"] += 1
    elif scfg.no_reward_exit_test and should_no_reward_exit(trade, price_diff, time_held):
        reason = "NO_REWARD_EXIT"
        exit_price_diff = price_diff
        book["stats"]["NO_REWARD_EXIT"] += 1
    elif price_diff <= -safe_float(trade.get("stop_loss_pct"), cfg.STOP_LOSS):
        reason = "SL"
        exit_price_diff = -safe_float(trade.get("stop_loss_pct"), cfg.STOP_LOSS)
        book["stats"]["SL"] += 1
        if scfg.coin_ban_after_sl:
            book["banned_until"][symbol] = current_time + cfg.COIN_BAN_AFTER_SL
    elif time_held >= safe_float(trade.get("time_stop_min"), scfg.time_stop_min):
        reason = "TIME"
        exit_price_diff = price_diff
        book["stats"]["TIME"] += 1

    if not reason:
        return False

    remaining_fraction = max(0.0, trade.get("remaining_fraction", 1.0))
    gross, net, costs = calc_net_pnl(trade["margin"] * remaining_fraction, trade["leverage"], exit_price_diff)

    total_gross = trade.get("realized_gross_pnl", 0.0) + gross
    total_net = trade.get("realized_net_pnl", 0.0) + net
    total_costs = trade.get("realized_costs", 0.0) + costs

    mfe = trade["max_profit_pct"]
    mae = trade["max_loss_pct"]

    msg = ""
    if reason in ("SL", "TIME") and mfe >= cfg.BE_CANDIDATE_MFE:
        book["stats"]["BE_CANDIDATE"] += 1
        msg = " [BE_CANDIDATE]"
    if reason == "BE_V2":
        msg = f" [BE_V2_EXIT +{cfg.BE_V2_STOP_PCT:.2f}%]"
    if reason == "NO_REWARD_EXIT":
        msg = " [NO_REWARD_EXIT_TEST]"
    if reason == "FAST_FAIL":
        msg = " [FAST_FAIL]"
    if reason == "MICRO_LOCK":
        msg = f" [MICRO_LOCK {cfg.MICRO_LOCK_STOP_PCT:+.2f}%]"
    if reason in ("RUNNER_STOP", "RUNNER_TP"):
        msg = f" [PARTIAL_RUNNER rem={remaining_fraction:.2f}]"
    if trade.get("atr5b_exit"):
        msg += (
            f" [ATR5B SL={safe_float(trade.get('stop_loss_pct'), cfg.STOP_LOSS):.2f} "
            f"PT={safe_float(trade.get('partial_trigger_pct'), cfg.PARTIAL_TRIGGER_PCT):.2f} "
            f"RTP={safe_float(trade.get('runner_tp_pct'), cfg.PARTIAL_RUNNER_TP_PCT):.2f} "
            f"RST={safe_float(trade.get('runner_stop_pct'), cfg.PARTIAL_RUNNER_STOP_PCT):.2f}]"
        )

    book["balance"] += net
    st = book["stats"]
    st["total_gross_pnl"] += gross
    st["net_pnl"] += net
    st["costs"] += costs
    if net > 0:
        st["net_profit"] += net
    elif net < 0:
        st["net_loss"] += abs(net)

    if scfg.global_toxic_ban and reason == "SL" and mfe < cfg.GLOBAL_TOXIC_BAN_MFE_PCT:
        set_global_toxic_ban(symbol, clean_symbol, current_time, time_str, f"SL_MFE_{mfe:.2f}")

    del book["active"][symbol]

    log(
        f"[{time_str}] SHADOW_CLOSE | {name} | {clean_symbol} | {reason} | "
        f"Gross:{total_gross:+.2f}$ Net:{total_net:+.2f}$ Cost:{total_costs:.2f}$ | "
        f"FinalNet:{net:+.2f}$ Rem:{remaining_fraction:.2f} | "
        f"MFE:+{mfe:.2f}% MAE:{mae:.2f}% | Bal:${book['balance']:.2f}{msg}\n"
    )

    await dry_live.maybe_close(name, symbol, clean_symbol, price, reason, net, time_str)
    update_locks_after_close(name, book)
    return True


def should_no_reward_exit(trade, price_diff, time_held) -> bool:
    if time_held < cfg.NO_REWARD_EXIT_MINUTES:
        return False
    if trade["max_profit_pct"] >= cfg.NO_REWARD_EXIT_MFE:
        return False
    if price_diff > 0:
        return False

    ctx = trade.get("entry_context", {})
    toxic = (
        ctx.get("oi_change", 0.0) <= 0
        or safe_float(ctx.get("spread_bps"), 0.0) > 7
        or ctx.get("absorption_risk_long", False)
        or ctx.get("middle_range_noise", False)
        or ctx.get("weak_long_result", False)
        or safe_float(ctx.get("structure_risk"), 0) >= 4
    )
    return toxic


def reset_books_if_no_open(books):
    if any(book["active"] for book in books.values()):
        return False

    for book in books.values():
        book["locked"] = False
        book["lock_reason"] = ""
        book["start_balance"] = book["balance"]
        book["peak_balance"] = book["balance"]
        book["stats"] = get_empty_stats()
        book["banned_until"].clear()
    return True


def format_strategy_report(books) -> str:
    lines = ["=== STRATEGY REPORT | TOTAL SINCE START/RESET ==="]
    lines.append(
        f"Costs: commission={cfg.COMMISSION_RATE:.5f} per side | "
        f"spread={cfg.SPREAD_BPS}bps | slippage_base={cfg.SLIPPAGE_BPS}bps per side | "
        f"dry_exec_slip={cfg.DRY_RUN_EXECUTION_SLIPPAGE_BPS}bps"
    )
    lines.append("")

    groups = [
        ("V15 SPREAD SCOUT", lambda n, b: n.startswith("V15_SPREAD_SCOUT")),
        ("SMART/META SAFE DRY", lambda n, b: n.startswith("SMART_V2_") or n.startswith("META_V12_")),
        ("EXEC_SAFE STRATEGIES", lambda n, b: "_EXEC_" in n),
        ("OLD SAFE CONTROL", lambda n, b: n.startswith("FILTERED_045_SAFE")),
        ("BASE SHADOW STRATEGIES", lambda n, b: "_EXEC_" not in n and not n.startswith("FILTERED_045_SAFE") and not n.startswith("V15_SPREAD_SCOUT") and not n.startswith("SMART_V2_") and not n.startswith("META_V12_")),
    ]

    for group_name, pred in groups:
        lines.append(f"--- {group_name} ---")
        for name, book in books.items():
            if not pred(name, book):
                continue
            st = book["stats"]
            scfg = book["config"]
            pf = st["net_profit"] / st["net_loss"] if st["net_loss"] > 0 else 999.0
            avg = st["net_pnl"] / st["trades"] if st["trades"] > 0 else 0.0
            day_pnl = book["balance"] - book["start_balance"]
            dd = book["peak_balance"] - book["balance"]
            lock = f"[L:{book['lock_reason']}]" if book["locked"] else "[ACTIVE]"
            silent = "[SILENT]" if scfg.silent else "[VISIBLE]"
            selector = " [SELECTOR]" if scfg.selector else ""

            lines.append(
                f"{name} {silent}{selector} {lock}:\n"
                f"  Bal:${book['balance']:.2f} | DayPnL:{day_pnl:+.2f}$ | Peak:${book['peak_balance']:.2f} | DD:-${dd:.2f}\n"
                f"  NetPnL:{st['net_pnl']:+.2f}$ | GrossPnL:{st['total_gross_pnl']:+.2f}$ | Costs:-${st['costs']:.2f}\n"
                f"  Trds:{st['trades']} | TP:{st['TP']} | SL:{st['SL']} | TIME:{st['TIME']} | "
                f"FF:{st['FAST_FAIL']} | ML:{st['MICRO_LOCK']} | PTP:{st['PARTIAL_TP']} | "
                f"RTP:{st['RUNNER_TP']} | RSTOP:{st['RUNNER_STOP']} | "
                f"BE_V2:{st['BE_V2']} | NF_EXIT:{st['NO_REWARD_EXIT']} | BE_CAND:{st['BE_CANDIDATE']} | "
                f"NO_FOLLOW:{st['NO_FOLLOW']} | PF_NET:{pf:.2f} | AvgNet:${avg:.2f}\n"
                f"  SelectorCand:{st['selector_candidates']} | SelectorOpened:{st['selector_opened']} | "
                f"DepthOK:{st['depth_ok']} Skip:{st['depth_skip']} Fail:{st['depth_fail']} | "
                f"StructFlags:{st['structure_flags']} | Active:{len(book['active'])}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"
