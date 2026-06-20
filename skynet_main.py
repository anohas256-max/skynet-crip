import os
import csv
import gc
import time
import asyncio

import aiohttp
from telethon import TelegramClient

import skynet_config as cfg
import skynet_engine as eng
import research_fade_shadow


client = TelegramClient("volume_session", cfg.API_ID, cfg.API_HASH)


# ============================================================
# LOGGING
# ============================================================

def init_logs():
    for interval in ["3h", "12h"]:
        with open(f"skynet_{interval}.log", "w", encoding="utf-8") as f:
            f.write(f"=== START {cfg.BOT_VERSION} | V16 MICRO LIVE META ===\n")
    with open("skynet_48h.log", "a", encoding="utf-8") as f:
        f.write(f"\n=== START {cfg.BOT_VERSION} | V16 MICRO LIVE META ===\n")


def write_to_logs(log_str: str):
    for interval in ["3h", "12h", "48h"]:
        with open(f"skynet_{interval}.log", "a", encoding="utf-8") as f:
            f.write(log_str)


eng.set_log_writer(write_to_logs)

# === V12 PATCH START: market event logger ===
V12_EVENT_CSV = "/root/skynet/data/v12_market_events.csv"

def write_v12_event(candidate: dict, stage: str, note: str = ""):
    try:
        os.makedirs(os.path.dirname(V12_EVENT_CSV), exist_ok=True)
        exists = os.path.exists(V12_EVENT_CSV)
        fields = [
            "ts", "stage", "note", "symbol", "score", "price_change", "vol_ratio",
            "trend_15m", "btc_5m_change", "oi_change", "spread_bps", "structure_risk",
            "breakout_risk_score", "false_breakouts_15m", "current_turnover_rank",
            "initiative", "meta_sources_v12"
        ]
        row = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stage": stage,
            "note": note,
            "symbol": candidate.get("clean_symbol", candidate.get("symbol", "")),
            "score": candidate.get("score", ""),
            "price_change": candidate.get("price_change", ""),
            "vol_ratio": candidate.get("vol_ratio", ""),
            "trend_15m": candidate.get("trend_15m", ""),
            "btc_5m_change": candidate.get("btc_5m_change", ""),
            "oi_change": candidate.get("oi_change", ""),
            "spread_bps": candidate.get("spread_bps", ""),
            "structure_risk": candidate.get("structure_risk", ""),
            "breakout_risk_score": candidate.get("breakout_risk_score", ""),
            "false_breakouts_15m": candidate.get("false_breakouts_15m", ""),
            "current_turnover_rank": candidate.get("current_turnover_rank", ""),
            "initiative": int(bool(candidate.get("initiative_buying_proxy", False))),
            "meta_sources_v12": candidate.get("meta_sources_v12", ""),
        }
        with open(V12_EVENT_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            if not exists:
                w.writeheader()
            w.writerow(row)
    except Exception as e:
        write_to_logs(f"[{time.strftime('%H:%M:%S')}] V12_EVENT_LOG_ERROR | {type(e).__name__}: {e}\n")
# === V12 PATCH END: market event logger ===



async def dump_log_always(log_interval, date_postfix, books, dry_live, skip_tracker, fade_shadow=None):
    filename = f"skynet_{log_interval}.log"

    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                f"=== EMPTY REPORT {cfg.BOT_VERSION} | {log_interval} ===\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"No signals.\n"
            )

    with open(filename, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(dry_live.format_report())
        f.write("\n")
        f.write(skip_tracker.format_report())
        f.write("\n")
        if fade_shadow is not None:
            f.write(fade_shadow.format_report())
            f.write("\n")
        if hasattr(eng, "format_smart_v2_report"):
            f.write(eng.format_smart_v2_report())
            f.write("\n")
        f.write(eng.format_strategy_report(books))

    send_name = f"skynet_{log_interval}_{date_postfix}.log"
    os.rename(filename, send_name)
    await client.send_file(cfg.TG_TARGET, send_name, caption=f"📁 v16 MicroLive лог за {log_interval} ({date_postfix})")

    try:
        os.remove(send_name)
    except OSError:
        pass

    with open(filename, "w", encoding="utf-8") as f:
        f.write(
            f"=== CONTINUE {cfg.BOT_VERSION} | {log_interval} | "
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} ===\n"
        )


# ============================================================
# API HELPERS
# ============================================================

async def get_kline_1m_metrics(session, symbol):
    try:
        # limit=30 gives latest candle shape, ATR5_B pre-range and breakout-risk context.
        url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval=Min1&limit=30"
        async with session.get(url, timeout=5) as res:
            if res.status != 200:
                return None
            data = await res.json()
            d = data.get("data")
            if not d or not d.get("open") or not d.get("close"):
                return None

            opens = d.get("open") or []
            closes = d.get("close") or []
            highs = d.get("high") or []
            lows = d.get("low") or []
            vols = d.get("vol") or d.get("volume") or d.get("amount") or []

            n = min(len(opens), len(closes), len(highs), len(lows))
            if n <= 0:
                return None

            def sf(x, default=0.0):
                return eng.safe_float(x, default)

            opens = [sf(x) for x in opens[-n:]]
            closes = [sf(x) for x in closes[-n:]]
            highs = [sf(x) for x in highs[-n:]]
            lows = [sf(x) for x in lows[-n:]]
            if vols:
                vols = [sf(x) for x in vols[-n:]]
                if len(vols) < n:
                    vols = [0.0] * (n - len(vols)) + vols
            else:
                vols = [0.0] * n

            open_p = opens[-1]
            close_p = closes[-1]
            high_p = highs[-1]
            low_p = lows[-1]

            pre_range_5m_pct = 0.0
            if n >= 2 and close_p > 0:
                pre_highs = highs[max(0, n - 6): n - 1] or [high_p]
                pre_lows = lows[max(0, n - 6): n - 1] or [low_p]
                pre_hi = max([x for x in pre_highs if x > 0] or [high_p])
                pre_lo = min([x for x in pre_lows if x > 0] or [low_p])
                if pre_hi > 0 and pre_lo > 0 and pre_hi >= pre_lo:
                    pre_range_5m_pct = ((pre_hi - pre_lo) / close_p) * 100.0

            if min(open_p, close_p, high_p, low_p) <= 0:
                return None

            def candle_features(i):
                o = opens[i]
                c = closes[i]
                h = highs[i]
                l = lows[i]
                v = vols[i] if i < len(vols) else 0.0
                full = h - l
                if min(o, c, h, l) <= 0 or full <= 0:
                    return {
                        "is_red": 0, "close_position": 0.5, "body_ratio": 0.0,
                        "upper_wick_ratio": 0.0, "lower_wick_ratio": 0.0,
                        "range_pct": 0.0, "vol": v,
                    }
                upper = h - max(o, c)
                lower = min(o, c) - l
                body = abs(c - o)
                return {
                    "is_red": 1 if c < o else 0,
                    "close_position": (c - l) / full,
                    "body_ratio": body / full,
                    "upper_wick_ratio": max(0.0, upper / full),
                    "lower_wick_ratio": max(0.0, lower / full),
                    "range_pct": (full / c) * 100.0,
                    "vol": v,
                }

            latest = candle_features(n - 1)
            is_red = bool(latest["is_red"])
            close_position = latest["close_position"]
            body_ratio = latest["body_ratio"]
            upper_wick_ratio = latest["upper_wick_ratio"]
            lower_wick_ratio = latest["lower_wick_ratio"]
            has_tail = upper_wick_ratio > 0.4

            start10 = max(0, n - 10)
            start15 = max(0, n - 15)
            start30 = max(0, n - 30)
            stats10 = [candle_features(i) for i in range(start10, n)]

            total_vol10 = sum(s["vol"] for s in stats10)
            red_vol10 = sum(s["vol"] for s in stats10 if s["is_red"])
            red_volume_share_10m = red_vol10 / total_vol10 if total_vol10 > 0 else 0.0

            rejection_count_10m = sum(
                1 for s in stats10
                if s["upper_wick_ratio"] >= 0.45 and s["close_position"] <= 0.65
            )
            weak_close_count_10m = sum(1 for s in stats10 if s["close_position"] <= 0.45)
            upper_wick_pressure_10m = sum(s["upper_wick_ratio"] for s in stats10) / max(1, len(stats10))

            false_breakouts_15m = 0
            for i in range(max(5, start15), n):
                prev_high = max(highs[max(0, i - 5):i] or [highs[i]])
                s = candle_features(i)
                if highs[i] > prev_high and s["close_position"] < 0.60:
                    false_breakouts_15m += 1

            recent_flush_15m = 0
            for i in range(start15, n):
                if opens[i] > 0 and ((lows[i] - opens[i]) / opens[i]) * 100.0 <= -0.60:
                    recent_flush_15m = 1
                    break

            closes30 = closes[start30:n]
            ema9_vals = []
            if closes30:
                k = 2.0 / 10.0
                ema9_vals = [closes30[0]]
                for x in closes30[1:]:
                    ema9_vals.append(x * k + ema9_vals[-1] * (1.0 - k))

            if len(ema9_vals) >= 4 and ema9_vals[-1] > 0 and ema9_vals[-4] > 0:
                close_vs_ema9_pct = ((closes30[-1] - ema9_vals[-1]) / ema9_vals[-1]) * 100.0
                ema9_slope_3m_pct = ((ema9_vals[-1] - ema9_vals[-4]) / ema9_vals[-4]) * 100.0
            else:
                close_vs_ema9_pct = 0.0
                ema9_slope_3m_pct = 0.0

            breakout_risk_score = 0
            if red_volume_share_10m >= 0.60:
                breakout_risk_score += 2
            if rejection_count_10m >= 2:
                breakout_risk_score += 2
            if false_breakouts_15m >= 2:
                breakout_risk_score += 2
            if recent_flush_15m:
                breakout_risk_score += 1
            if upper_wick_pressure_10m >= 0.30:
                breakout_risk_score += 1
            if weak_close_count_10m >= 4:
                breakout_risk_score += 1
            if ema9_slope_3m_pct < 0:
                breakout_risk_score += 1
            if close_vs_ema9_pct < -0.05:
                breakout_risk_score += 1

            return {
                "open": open_p,
                "close": close_p,
                "high": high_p,
                "low": low_p,
                "is_red": is_red,
                "has_tail": has_tail,
                "close_position": close_position,
                "body_ratio": body_ratio,
                "upper_wick_ratio": upper_wick_ratio,
                "lower_wick_ratio": lower_wick_ratio,
                "pre_range_5m_pct": pre_range_5m_pct,

                "red_volume_share_10m": red_volume_share_10m,
                "rejection_count_10m": rejection_count_10m,
                "weak_close_count_10m": weak_close_count_10m,
                "upper_wick_pressure_10m": upper_wick_pressure_10m,
                "false_breakouts_15m": false_breakouts_15m,
                "recent_flush_15m": recent_flush_15m,
                "close_vs_ema9_pct": close_vs_ema9_pct,
                "ema9_slope_3m_pct": ema9_slope_3m_pct,
                "breakout_risk_score": breakout_risk_score,
            }
    except Exception:
        return None


async def get_15m_metrics(session, symbol, current_price):
    try:
        url = f"https://contract.mexc.com/api/v1/contract/kline/{symbol}?interval=Min15&limit=1"
        async with session.get(url, timeout=5) as res:
            if res.status != 200:
                return None
            data = await res.json()
            d = data.get("data")
            if not d or not d.get("open") or not d.get("close"):
                return None

            open_p = eng.safe_float(d["open"][0])
            close_p = eng.safe_float(d["close"][0])
            high_p = eng.safe_float(d["high"][0])
            low_p = eng.safe_float(d["low"][0])

            if open_p <= 0:
                return None

            trend = ((close_p - open_p) / open_p) * 100.0
            width = high_p - low_p
            if width > 0:
                range_position = (current_price - low_p) / width
                range_width_pct = (width / current_price) * 100.0 if current_price > 0 else 0.0
            else:
                range_position = 0.5
                range_width_pct = 0.0

            return {
                "trend_15m": trend,
                "range_position_15m": range_position,
                "range_width_15m_pct": range_width_pct,
                "middle_range_noise": 0.35 < range_position < 0.65,
            }
    except Exception:
        return None


# ============================================================
# SCORING
# ============================================================

def build_score_and_analysis(c, btc_15m_volatility):
    score = 0
    analysis = "🧠 **АНАЛИЗ И ПОДСКАЗКИ:**\n"

    if btc_15m_volatility < 0.15:
        analysis += f"⚠️ **РЕЖИМ:** Дед спит (волатильность {btc_15m_volatility:.2f}%).\n"
        score -= 3

    if c["btc_5m_change"] <= cfg.BTC_DUMP_LIMIT:
        analysis += f"🛑 **BTC-ЩИТ:** Дед льется ({c['btc_5m_change']:.2f}% за 5м).\n"
        score -= 10
    elif c["btc_5m_change"] >= 0.10:
        analysis += f"✅ **BTC:** Дед поддерживает рынок ({c['btc_5m_change']:.2f}% за 5м).\n"
        score += 1

    if c["trend_15m"] <= cfg.TREND_15M_LIMIT:
        analysis += f"🛑 **ТРЕНД (15m):** Монета падает ({c['trend_15m']:.2f}%). Запрет лонга!\n"
        score -= 10
    elif c["trend_15m"] >= 0.30:
        analysis += f"✅ **ТРЕНД (15m):** Монета в восходящем импульсе ({c['trend_15m']:.2f}%).\n"
        score += 1

    if c["is_red"] and c["price_change"] > 0:
        analysis += "🟡 **Тренд (1m):** Рост затормозился, идет фиксация.\n"
    else:
        analysis += "✅ **Тренд (1m):** Уверенный рост цены.\n"
        score += 2

    if c["has_tail"]:
        analysis += "❌ **Свеча (1m):** Тень сверху. Кит разгружается.\n"
        score -= 2
    elif not c["is_red"]:
        analysis += "✅ **Свеча (1m):** Покупатели давят без тени.\n"
        score += 1

    if c["oi_change"] <= -3.0:
        analysis += f"🛑 **OI:** Сильный отток {c['oi_change']:.1f}%. Деньги выходят.\n"
        score -= 4
    elif c["oi_change"] > 1.0:
        analysis += f"✅ **OI:** Рост на {c['oi_change']:.1f}%. Зашли свежие деньги!\n"
        score += 1
    elif c["oi_change"] < -1.0:
        analysis += f"❌ **OI:** Падение на {abs(c['oi_change']):.1f}%. Вынос стопов.\n"
        score -= 1
    else:
        analysis += f"🟡 **OI:** Нейтральный ({c['oi_change']:.1f}%).\n"

    if c["funding"] <= -0.01:
        analysis += f"✅ **Фандинг:** {c['funding']:.4f}% (Short Squeeze риск!)\n"
        score += 1

    if eng.is_exhaustion(c["vol_ratio"], c["price_change"]):
        analysis += f"⚠️ **EXHAUSTION:** volume x{int(c['vol_ratio'])} при росте {c['price_change']:.2f}%.\n"

    c["score"] = score
    c["analysis"] = analysis
    eng.enrich_candidate_structure(c)

    if c.get("weak_long_result"):
        c["analysis"] += "⚠️ **EFFORT/RESULT:** объём есть, но свеча закрылась слабо.\n"
    if c.get("absorption_risk_long"):
        c["analysis"] += "❌ **ABSORPTION_PROXY:** верхняя тень/слабый результат на объёме.\n"
    if c.get("initiative_buying_proxy"):
        c["analysis"] += "✅ **INITIATIVE_PROXY:** свеча закрылась ближе к high, есть reward за effort.\n"
    if c.get("middle_range_noise"):
        c["analysis"] += f"🟡 **STRUCTURE:** цена в середине 15m range ({c.get('range_position_15m',0.5):.2f}).\n"

    return c



# ============================================================
# V11.3 CONFIRMATION ENTRY
# ============================================================

def _confirm_key(strategy_name: str, symbol: str):
    return f"{strategy_name}:{symbol}"


def _confirmation_condition(scfg, pending, price):
    signal_price = pending["signal_price"]
    if signal_price <= 0:
        return False, "BAD_SIGNAL_PRICE", 0.0, 0.0

    low_pct = ((pending["min_price"] - signal_price) / signal_price) * 100.0
    move_pct = ((price - signal_price) / signal_price) * 100.0
    mode = getattr(scfg, "confirm_mode", "NO_RUG_CLOSE")

    if low_pct <= getattr(scfg, "confirm_no_rug_pct", cfg.CONFIRM_NO_RUG_PCT):
        return False, f"RUG_LOW_{low_pct:.2f}%_LE_{getattr(scfg, 'confirm_no_rug_pct', cfg.CONFIRM_NO_RUG_PCT):.2f}%", move_pct, low_pct

    max_move = getattr(scfg, "confirm_max_move_pct", getattr(cfg, "CONFIRM_MAX_MOVE_PCT_DEFAULT", 999.0))
    if move_pct > max_move:
        return False, f"CHASE_MOVE_{move_pct:.2f}%_GT_{max_move:.2f}%", move_pct, low_pct

    if mode in ("NO_RUG_CLOSE", "CLOSE_1"):
        if price <= signal_price:
            return False, f"NO_CLOSE_FOLLOW_{move_pct:.2f}%", move_pct, low_pct
        return True, "CONFIRMED_CLOSE", move_pct, low_pct

    if mode in ("NO_RUG_BREAK_HIGH", "BREAK_HIGH_1"):
        signal_high = pending.get("signal_high", signal_price)
        if price <= signal_high:
            high_gap = ((price - signal_high) / signal_high) * 100.0 if signal_high > 0 else 0.0
            return False, f"NO_BREAK_HIGH_{high_gap:.2f}%", move_pct, low_pct
        return True, "CONFIRMED_BREAK_HIGH", move_pct, low_pct

    if price <= signal_price:
        return False, f"NO_CONFIRM_{move_pct:.2f}%", move_pct, low_pct
    return True, "CONFIRMED", move_pct, low_pct


async def update_pending_confirmations(pending_confirms, symbol, clean_symbol, price, current_time, time_str, books, dry_live):
    to_delete = []

    for key, pending in list(pending_confirms.items()):
        if pending["symbol"] != symbol:
            continue

        pending["last_price"] = price
        pending["min_price"] = min(pending["min_price"], price)
        pending["max_price"] = max(pending["max_price"], price)

        s_name = pending["strategy"]
        book = books.get(s_name)
        if not book:
            to_delete.append(key)
            continue

        scfg = book["config"]
        age = current_time - pending["created"]

        if age < getattr(scfg, "confirm_wait_seconds", cfg.CONFIRM_WAIT_SECONDS):
            continue

        ok, reason, move_pct, low_pct = _confirmation_condition(scfg, pending, price)
        max_age = getattr(scfg, "confirm_max_seconds", cfg.CONFIRM_MAX_SECONDS)
        keep_until_max = bool(getattr(scfg, "confirm_keep_until_max", False))

        if age > max_age:
            to_delete.append(key)
            write_to_logs(
                f"[{time_str}] CONFIRM_DROP | {s_name} | {clean_symbol} | TIMEOUT age={age:.0f}s "
                f"move={move_pct:+.2f}% low={low_pct:+.2f}%\n"
            )
            continue

        if not ok:
            # WAIT2/WAIT3-style modes: keep watching if there is no close-follow yet.
            # Hard failures such as rug or anti-chase are dropped immediately.
            soft_no_follow = reason.startswith("NO_CLOSE_FOLLOW") or reason.startswith("NO_BREAK_HIGH") or reason.startswith("NO_CONFIRM")
            if keep_until_max and soft_no_follow:
                if current_time - pending.get("last_wait_log", 0) >= 60:
                    pending["last_wait_log"] = current_time
                    write_to_logs(
                        f"[{time_str}] CONFIRM_WAIT_MORE | {s_name} | {clean_symbol} | {reason} | "
                        f"age={age:.0f}s/{max_age:.0f}s move={move_pct:+.2f}% low={low_pct:+.2f}%\n"
                    )
                continue

            to_delete.append(key)
            write_to_logs(
                f"[{time_str}] CONFIRM_DROP | {s_name} | {clean_symbol} | {reason} | "
                f"age={age:.0f}s move={move_pct:+.2f}% low={low_pct:+.2f}% "
                f"signal={pending['signal_price']:.8f} now={price:.8f}\n"
            )
            continue

        to_delete.append(key)

        skip_reasons = []
        if not eng.can_open_strategy(s_name, book, symbol, current_time, skip_reasons):
            can_reason = ",".join(skip_reasons) if skip_reasons else "CAN_OPEN_FALSE"
            if (
                getattr(cfg, "REJECT_OBSERVER_TRACK_CAN_OPEN", True)
                and getattr(book["config"], "skip_track", False)
                and eng.should_observe_reject(pending["candidate"])
            ):
                skip_tracker.open(
                    s_name,
                    pending["candidate"],
                    "REJECT_CONFIRM_CAN_OPEN_" + can_reason.replace(" ", "_").replace(":", ""),
                    book["config"],
                    current_time,
                    time_str,
                    force=True,
                )
            write_to_logs(
                f"[{time_str}] CONFIRM_DROP | {s_name} | {clean_symbol} | "
                f"{can_reason}\n"
            )
            continue

        candidate = dict(pending["candidate"])
        candidate["price"] = price
        candidate["confirm_move_pct"] = move_pct
        candidate["confirm_low_pct"] = low_pct
        candidate["confirm_age_sec"] = age

        write_to_logs(
            f"[{time_str}] CONFIRM_OPEN | {s_name} | {clean_symbol} | {reason} | "
            f"age={age:.0f}s move={move_pct:+.2f}% low={low_pct:+.2f}% "
            f"signal={pending['signal_price']:.8f} entry={price:.8f} | "
            f"pc={candidate.get('price_change',0):.2f}% vol=x{int(candidate.get('vol_ratio',0))} "
            f"spread={candidate.get('spread_bps',999):.2f}bps\n"
        )

        await eng.open_shadow_trade(s_name, book, candidate, current_time, time_str, dry_live)
        book["stats"]["selector_opened"] += 1

    for key in to_delete:
        pending_confirms.pop(key, None)


async def process_confirm_selector_strategy(name, candidates, books, current_time, time_str, dry_live, skip_tracker, pending_confirms):
    book = books[name]
    scfg = book["config"]
    skip_reasons = []

    if not candidates:
        return [], skip_reasons

    book["stats"]["selector_candidates"] += len(candidates)

    if book["locked"]:
        skip_reasons.append(f"{name}: LOCKED_{book['lock_reason']}")
        return [], skip_reasons

    ordered = sorted(candidates, key=lambda c: eng.candidate_priority(c, scfg), reverse=True)
    opened = []

    for cand in ordered:
        if len(book["active"]) >= scfg.max_open:
            skip_reasons.append(f"{name}: MAX_OPEN")
            break

        pkey = _confirm_key(name, cand["symbol"])
        if pkey in pending_confirms:
            skip_reasons.append(f"{name}: CONFIRM_ALREADY_PENDING")
            continue

        ok_depth, depth_reason = eng.validate_depth_for_strategy(scfg, cand)
        if not ok_depth:
            if "HTTP" in depth_reason or "EXC" in depth_reason or "FAIL" in depth_reason or "NO_RESULT" in depth_reason:
                book["stats"]["depth_fail"] += 1
            else:
                book["stats"]["depth_skip"] += 1
            skip_reasons.append(f"{name}: {depth_reason}")
            skip_tracker.open(name, cand, depth_reason, scfg, current_time, time_str)
            continue

        book["stats"]["depth_ok"] += 1

        # Do not open immediately. Put into 1-minute confirmation watch.
        pending_confirms[pkey] = {
            "strategy": name,
            "symbol": cand["symbol"],
            "clean_symbol": cand["clean_symbol"],
            "candidate": dict(cand),
            "signal_price": cand["price"],
            "signal_high": cand.get("high", cand["price"]),
            "created": current_time,
            "min_price": cand["price"],
            "max_price": cand["price"],
            "last_price": cand["price"],
            "last_wait_log": 0.0,
        }
        opened.append(f"{cand['clean_symbol']}:PENDING")

        write_to_logs(
            f"[{time_str}] CONFIRM_PENDING | {name} | {cand['clean_symbol']} | "
            f"mode={getattr(scfg,'confirm_mode','NO_RUG_CLOSE')} wait={getattr(scfg,'confirm_wait_seconds',cfg.CONFIRM_WAIT_SECONDS):.0f}s "
            f"no_rug={getattr(scfg,'confirm_no_rug_pct',cfg.CONFIRM_NO_RUG_PCT):+.2f}% | "
            f"signal={cand['price']:.8f} | score={cand['score']} pc={cand['price_change']:.2f}% "
            f"vol=x{int(cand.get('vol_ratio',0))} trend={cand['trend_15m']:.2f}% btc={cand['btc_5m_change']:.2f}% "
            f"spread={cand.get('spread_bps',999):.2f}bps/{scfg.spread_limit_bps:.0f} "
            f"br={cand.get('breakout_risk_score',0)} fb={cand.get('false_breakouts_15m',0)} "
            f"meta={cand.get('meta_sources_v12','-')}\n"
        )

        # One pending per strategy per snapshot is enough; mirrors selector max_open=1.
        break

    return opened, skip_reasons


# ============================================================
# MAIN LOOP
# ============================================================

async def scan_futures():
    print(f"🚀 {cfg.BOT_VERSION} запущен.")
    print(f"Dry tracks: {cfg.LIVE_DRY_TRACKS}")

    ticker_url = "https://contract.mexc.com/api/v1/contract/ticker"

    books = eng.build_books()
    dry_live = eng.DryLiveManager(cfg.LIVE_DRY_TRACKS)
    skip_tracker = eng.SkipTracker()
    fade_shadow = research_fade_shadow.ResearchFadeV1Shadow(write_to_logs)

    history = {}
    last_alert_time = {}
    last_pulse_time = time.time()
    last_tg_pulse_time = time.time()
    last_reset_time = time.time()

    last_dump_3h = time.time()
    last_dump_12h = time.time()
    last_dump_48h = time.time()

    btc_history = []
    strategy_configs = cfg.build_strategy_configs()
    selector_names = [name for name, scfg in strategy_configs.items() if scfg.selector]
    pending_confirms = {}

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(ticker_url, timeout=10) as r:
                    if r.status == 429:
                        print("⚠️ 429 rate limit. Sleep 60s.")
                        await asyncio.sleep(60)
                        continue
                    if r.status != 200:
                        await asyncio.sleep(5)
                        continue

                    data = await r.json()
                    market_data = data.get("data", [])
                    if not isinstance(market_data, list):
                        await asyncio.sleep(5)
                        continue

                    current_time = time.time()
                    snapshot_time_str = time.strftime("%H:%M:%S")

                    # --- RESET 24H ---
                    if current_time - last_reset_time >= 86400:
                        no_shadow_open = eng.reset_books_if_no_open(books)
                        no_dry_open = dry_live.reset_if_no_open()
                        if no_shadow_open and no_dry_open:
                            write_to_logs("\n🔄 RESET 24H: locks/stats/bans reset.\n")
                            await client.send_message(cfg.TG_TARGET, "🔄 **RESET 24H:** stats, locks and bans reset.")
                            last_reset_time = current_time
                        else:
                            write_to_logs("⏳ RESET delayed: active shadow/dry-live trades exist.\n")

                    # --- BTC CONTEXT ---
                    btc_price = next(
                        (eng.safe_float(coin.get("lastPrice", 0)) for coin in market_data if coin.get("symbol") == "BTC_USDT"),
                        0.0
                    )

                    btc_5m_change = 0.0
                    btc_15m_volatility = 100.0

                    if btc_price > 0:
                        btc_history.append((current_time, btc_price))
                        btc_history = [x for x in btc_history if current_time - x[0] <= 900]

                    if len(btc_history) >= 2:
                        h5 = [x for x in btc_history if current_time - x[0] <= 300]
                        if len(h5) >= 2:
                            oldest = h5[0][1]
                            if oldest > 0:
                                btc_5m_change = ((btc_price - oldest) / oldest) * 100.0
                        if len(btc_history) > 5:
                            hi = max(x[1] for x in btc_history)
                            lo = min(x[1] for x in btc_history)
                            if lo > 0:
                                btc_15m_volatility = ((hi - lo) / lo) * 100.0

                    selector_candidates = {name: [] for name in selector_names}

                    # Current rolling-24h turnover universe rank from MEXC ticker amount24.
                    # This is live-compatible and approximates ROLL24_TURNOVER_TOP_N.
                    turnover_rows = []
                    for _coin in market_data:
                        _sym = _coin.get("symbol", "")
                        if not _sym.endswith("_USDT"):
                            continue
                        _clean = _sym.replace("_USDT", "")
                        if _clean in cfg.EXACT_BLACKLIST or any(bad in _clean for bad in cfg.PARTIAL_BLACKLIST):
                            continue
                        turnover_rows.append((eng.safe_float(_coin.get("amount24", 0)), _sym))
                    turnover_rows.sort(reverse=True)
                    current_turnover_rank = {sym: i + 1 for i, (_, sym) in enumerate(turnover_rows)}

                    # --- MARKET LOOP ---
                    for coin in market_data:
                        symbol = coin.get("symbol", "")
                        if not symbol.endswith("_USDT"):
                            continue

                        clean_symbol = symbol.replace("_USDT", "")
                        if clean_symbol in cfg.EXACT_BLACKLIST or any(bad in clean_symbol for bad in cfg.PARTIAL_BLACKLIST):
                            continue

                        price = eng.safe_float(coin.get("lastPrice", 0))
                        vol_24h = eng.safe_float(coin.get("amount24", 0))
                        funding = eng.safe_float(coin.get("fundingRate", 0)) * 100.0
                        current_oi = eng.safe_float(coin.get("holdVol", 0))

                        if price <= 0:
                            continue

                        time_str = time.strftime("%H:%M:%S")

                        # Update skip tracker and smart-universe symbol passports.
                        skip_tracker.update_symbol(symbol, clean_symbol, price, current_time, time_str)
                        if hasattr(eng, "smart_v2_update_symbol"):
                            eng.smart_v2_update_symbol(symbol, clean_symbol, price, current_time, time_str)

                        # Manage open trades.
                        for s_name, book in books.items():
                            await eng.manage_open_trade(s_name, book, symbol, clean_symbol, price, current_time, time_str, dry_live)

                        # Research-only SHORT fade shadow tracker.
                        # Important: update on every ticker price tick, otherwise OPEN trades never close by TTL.
                        fade_shadow.update_price(symbol, clean_symbol, price, current_time, time_str)

                        # Manage V11.3 pending confirmation entries.
                        await update_pending_confirmations(
                            pending_confirms,
                            symbol,
                            clean_symbol,
                            price,
                            current_time,
                            time_str,
                            books,
                            dry_live,
                        )

                        # Seed history.
                        if symbol not in history:
                            history[symbol] = {"vol": vol_24h, "price": price, "time": current_time, "oi": current_oi}
                            continue

                        time_since_last = current_time - history[symbol]["time"]
                        if time_since_last < 60:
                            continue

                        if time_since_last > 120:
                            history[symbol] = {"vol": vol_24h, "price": price, "time": current_time, "oi": current_oi}
                            continue

                        old = history[symbol]
                        old_vol = old["vol"]
                        old_price = old["price"]
                        old_oi = old["oi"]

                        vol_1m = vol_24h - old_vol
                        price_change = ((price - old_price) / old_price) * 100.0 if old_price > 0 else 0.0
                        avg_1m_vol = vol_24h / (24 * 60) if vol_24h > 0 else 1.0
                        oi_change = ((current_oi - old_oi) / old_oi) * 100.0 if old_oi > 0 else 0.0
                        vol_ratio = vol_1m / avg_1m_vol if avg_1m_vol > 0 else 0.0

                        history[symbol] = {"vol": vol_24h, "price": price, "time": current_time, "oi": current_oi}

                        if not (vol_ratio > cfg.VOL_MULTIPLIER and vol_1m > cfg.MIN_VOL_1M and avg_1m_vol > cfg.MIN_AVG_1M_VOL):
                            continue

                        if not (cfg.PRICE_CHANGE_MIN <= price_change <= cfg.PRICE_CHANGE_MAX):
                            continue

                        if vol_ratio > 100 or abs(oi_change) > 20:
                            continue

                        k1 = await get_kline_1m_metrics(session, symbol)
                        k15 = await get_15m_metrics(session, symbol, price)

                        if not k1 or not k15:
                            continue

                        if abs(k15["trend_15m"]) > 10:
                            continue

                        candidate = {
                            "symbol": symbol,
                            "clean_symbol": clean_symbol,
                            "price": price,
                            "vol_1m": vol_1m,
                            "vol_ratio": vol_ratio,
                            "price_change": price_change,
                            "avg_1m_vol": avg_1m_vol,
                            "oi_change": oi_change,
                            "current_oi": current_oi,
                            "trend_15m": k15["trend_15m"],
                            "range_position_15m": k15["range_position_15m"],
                            "range_width_15m_pct": k15["range_width_15m_pct"],
                            "middle_range_noise": k15["middle_range_noise"],
                            "btc_5m_change": btc_5m_change,
                            "funding": funding,
                            "current_turnover_rank": current_turnover_rank.get(symbol, 999999),
                            "link_pc": f"https://futures.mexc.com/exchange/{symbol}",
                            "_current_time": current_time,
                            "_time_str": time_str,
                            **k1,
                        }

                        candidate = build_score_and_analysis(candidate, btc_15m_volatility)

                        all_entered = []
                        visible_entered = []
                        skip_reasons = []

                        # 1) selector strategies collected for best-candidate selection.
                        # REJECT_OBSERVER_V1:
                        # If strategy rules reject a strong enough anomaly, we still open a virtual
                        # rejected-opportunity watch. This does NOT affect dry/real execution.
                        for s_name in selector_names:
                            scfg = strategy_configs[s_name]
                            if eng.should_enter_strategy(scfg, candidate):
                                selector_candidates[s_name].append(candidate)
                            else:
                                if (
                                    getattr(cfg, "REJECT_OBSERVER_TRACK_RULES_NOT_MET", True)
                                    and getattr(scfg, "skip_track", False)
                                    and eng.should_observe_reject(candidate)
                                ):
                                    r_reason = eng.reject_reason_for_strategy(scfg, candidate)
                                    skip_tracker.open(
                                        s_name,
                                        candidate,
                                        r_reason,
                                        scfg,
                                        current_time,
                                        time_str,
                                        force=True,
                                    )

                        # 2) non-selector legacy strategies opened immediately.
                        for s_name, scfg in strategy_configs.items():
                            if scfg.selector:
                                continue

                            if not eng.should_enter_strategy(scfg, candidate):
                                continue

                            book = books[s_name]
                            if not eng.can_open_strategy(s_name, book, symbol, current_time, skip_reasons):
                                continue

                            await eng.open_shadow_trade(s_name, book, candidate, current_time, time_str, dry_live)
                            all_entered.append(s_name)
                            if not scfg.silent:
                                visible_entered.append(s_name)

                        if all_entered:
                            verdict = f"📈 Скор: {candidate['score']}. Зашли сразу: {', '.join(all_entered)}"
                        else:
                            if candidate["score"] >= 4:
                                reason_str = ", ".join(sorted(set(skip_reasons))) if skip_reasons else "RULES_NOT_MET_OR_SELECTOR_PENDING"
                                verdict = f"🔴 Скор: {candidate['score']}. Пропуск/ожидание селектора. Причины: {reason_str}"
                            else:
                                verdict = f"🔴 Скор: {candidate['score']}. Пропуск."

                        write_to_logs(
                            f"[{time_str}] {clean_symbol} | Vol:x{int(vol_ratio)} | "
                            f"Price:{price_change:.2f}% | OI:{oi_change:.1f}% | "
                            f"Trend15M:{k15['trend_15m']:.2f}% | BTC_5M:{btc_5m_change:.2f}% | "
                            f"Score:{candidate['score']} | Struct:{candidate.get('structure_risk',0)} | "
                            f"BRisk:{candidate.get('breakout_risk_score',0)} FB:{candidate.get('false_breakouts_15m',0)} | "
                            f"Smart:{candidate.get('smart_v2_reason','-')} Rank:{candidate.get('current_turnover_rank',999999)} | "
                            f"Meta:{candidate.get('meta_sources_v12','-')} | "
                            f"CP:{candidate.get('close_position',0.5):.2f} | Body:{candidate.get('body_ratio',0):.2f} | "
                            f"{verdict}\n"
                        )

                        is_tg_cooldown_ok = symbol not in last_alert_time or current_time - last_alert_time[symbol] >= cfg.TG_COOLDOWN
                        # V12: write every anomaly to CSV, even if no selector opens it.
                        write_v12_event(candidate, "ANOMALY", verdict)

                        if (candidate["score"] > 0 or visible_entered) and is_tg_cooldown_ok:
                            alert_strats = ""
                            if visible_entered:
                                alert_strats = "\n\n🤖 **SHADOW IMMEDIATE:**\n" + "\n".join([f"✅ {s}" for s in visible_entered])
                            else:
                                alert_strats = "\n\n⏳ **SELECTOR:** кандидат будет выбран в конце snapshot."

                            msg = (
                                f"🚀 **АНОМАЛИЯ (1 МИНУТА)** 🚀\n"
                                f"⏱ **Время:** {time_str}\n\n"
                                f"🪙 Монета: **{clean_symbol}**\n"
                                f"💵 Цена: {price:.8f}$\n"
                                f"🔥 ВЛИЛИ ПРЯМО СЕЙЧАС: **${int(vol_1m)}** (x{int(vol_ratio)})\n"
                                f"📈 Изм. цены (1М): {price_change:.2f}%\n"
                                f"💎 OI: **{int(current_oi)}** контр. ({oi_change:.1f}%)\n"
                                f"🌐 Тренд (15М): **{k15['trend_15m']:.2f}%**\n"
                                f"👑 Дед (BTC 5М): **{btc_5m_change:.2f}%**\n"
                                f"🧩 StructureRisk: **{candidate.get('structure_risk',0)}** | "
                                f"ClosePos: {candidate.get('close_position',0.5):.2f} | Body: {candidate.get('body_ratio',0):.2f}\n"
                                f"🧪 BRisk: **{candidate.get('breakout_risk_score',0)}** | "
                                f"FalseBO: {candidate.get('false_breakouts_15m',0)} | "
                                f"EMA9Slope: {candidate.get('ema9_slope_3m_pct',0):+.3f}% | "
                                f"RedVol10m: {candidate.get('red_volume_share_10m',0):.2f}\n\n"
                                f"{candidate['analysis']}"
                                f"{alert_strats}\n\n"
                                f"⚙️ DRY_TRACKS={','.join(cfg.LIVE_DRY_TRACKS)}\n"
                                f"🖥 [ПК (Браузер)]({candidate['link_pc']})"
                            )
                            await client.send_message(cfg.TG_TARGET, msg, link_preview=False)
                            last_alert_time[symbol] = current_time

                    # --- PROCESS SELECTOR STRATEGIES AFTER FULL SNAPSHOT ---
                    await eng.enrich_selector_candidates_with_depth(session, selector_candidates, snapshot_time_str)

                    # Research-only fade shadow opens after depth enrichment.
                    # It observes the same live candidate stream but never affects selector/dry/real.
                    fade_unique = {}
                    for _cand_list in selector_candidates.values():
                        for _cand in _cand_list:
                            fade_unique[_cand["symbol"]] = _cand
                    for _cand in fade_unique.values():
                        fade_shadow.maybe_open(_cand, current_time, snapshot_time_str)

                    # Direct close polling for active fade positions.
                    # This is independent from candidate/ticker recurrence.
                    await fade_shadow.poll_active_prices(session, current_time, snapshot_time_str)

                    for s_name in selector_names:
                        scfg = strategy_configs[s_name]
                        if getattr(scfg, "confirm_entry", False):
                            opened, reasons = await process_confirm_selector_strategy(
                                s_name,
                                selector_candidates[s_name],
                                books,
                                current_time,
                                snapshot_time_str,
                                dry_live,
                                skip_tracker,
                                pending_confirms,
                            )
                        else:
                            opened, reasons = await eng.process_selector_strategy(
                                s_name,
                                selector_candidates[s_name],
                                books,
                                current_time,
                                snapshot_time_str,
                                dry_live,
                                skip_tracker,
                            )

                        if opened:
                            write_to_logs(
                                f"[{snapshot_time_str}] SELECTOR_RESULT | {s_name} | "
                                f"opened={opened} | candidates={len(selector_candidates[s_name])}\n"
                            )
                        elif selector_candidates[s_name]:
                            write_to_logs(
                                f"[{snapshot_time_str}] SELECTOR_RESULT | {s_name} | "
                                f"opened=[] | candidates={len(selector_candidates[s_name])} | "
                                f"skips={', '.join(sorted(set(reasons))) if reasons else 'NO_SLOT'}\n"
                            )

                    gc.collect()

                    # --- CONSOLE PULSE ---
                    if current_time - last_pulse_time >= 60:
                        visible = []
                        for name, book in books.items():
                            if not book["config"].silent:
                                visible.append(f"{name} {'[L]' if book['locked'] else ''}:${book['balance']:.2f}")
                        dry_bits = []
                        for name, t in dry_live.tracks.items():
                            dry_bits.append(f"{name}:{t['balance']:.2f}{'[L]' if t['locked'] else ''}")
                        print(f"✅ [{time.strftime('%H:%M:%S')}] " + " | ".join(visible[:5]) + " || DRY " + " | ".join(dry_bits))
                        last_pulse_time = current_time

                    # --- TG HOURLY PULSE ---
                    if current_time - last_tg_pulse_time >= 3600:
                        report_lines = []
                        for name, book in books.items():
                            if book["config"].silent:
                                continue
                            day_pnl = book["balance"] - book["start_balance"]
                            dd = book["peak_balance"] - book["balance"]
                            l_status = "🔒" if book["locked"] else "🟢"
                            report_lines.append(
                                f"🔹 {l_status} {name}: **${book['balance']:.2f}** "
                                f"({day_pnl:+.2f}$ day, DD -{dd:.2f}$, Active:{len(book['active'])})"
                            )

                        dry_lines = []
                        for name, t in dry_live.tracks.items():
                            dry_lines.append(
                                f"▫️ {name}: ${t['balance']:.2f} "
                                f"({t['balance'] - t['balance_start']:+.2f}$, Trds:{t['trades']}, Diff:{t['diff']:+.2f}$)"
                            )

                        await client.send_message(
                            cfg.TG_TARGET,
                            f"🤖 **SKYNET V16 MICRO-LIVE ЖИВ** 🤖\n"
                            f"⏱ Время: {time.strftime('%H:%M:%S')}\n\n"
                            + "\n".join(report_lines)
                            + "\n\n**DRY-LIVE TRACKS:**\n"
                            + "\n".join(dry_lines)
                        )
                        last_tg_pulse_time = current_time

                    # --- FILE DUMPS ---
                    date_postfix = time.strftime("%Y-%m-%d_%H-%M")
                    if current_time - last_dump_3h >= 10800:
                        await dump_log_always("3h", date_postfix, books, dry_live, skip_tracker, fade_shadow)
                        last_dump_3h = current_time
                    if current_time - last_dump_12h >= 43200:
                        await dump_log_always("12h", date_postfix, books, dry_live, skip_tracker, fade_shadow)
                        last_dump_12h = current_time
                    if current_time - last_dump_48h >= 172800:
                        await dump_log_always("48h", date_postfix, books, dry_live, skip_tracker, fade_shadow)
                        last_dump_48h = current_time

                    await asyncio.sleep(5)

            except Exception as e:
                print(f"⚠️ Ошибка: {e}")
                write_to_logs(f"[{time.strftime('%H:%M:%S')}] LOOP_EXCEPTION | {type(e).__name__}: {e}\n")
                await asyncio.sleep(10)


async def main():
    if not cfg.API_ID or not cfg.API_HASH:
        raise RuntimeError("API_ID/API_HASH missing in .env")
    init_logs()
    await client.start()
    await scan_futures()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
