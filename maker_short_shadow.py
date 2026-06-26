import time
from collections import Counter, defaultdict

import skynet_config as cfg


def sf(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def si(x, default=0):
    try:
        if x is None:
            return default
        return int(float(x))
    except Exception:
        return default


def calc_shadow_pnl(margin, leverage, move_pct, cost_pct):
    notional = margin * leverage
    gross = notional * (move_pct / 100.0)
    cost = notional * (cost_pct / 100.0)
    net = gross - cost
    return gross, net, cost


class MakerShortTp3Sl03Shadow:
    """
    Research-only maker/limit SHORT shadow lane.

    Hypothesis from V18 maker offset lab:
      filter = FADE_POS_PC1_VOL8_SP8_R80
      side = SHORT
      maker offset = +0.15%
      TP = +3.0% short profit
      SL = -0.3% short loss
      cost model ~= 0.03%

    Never sends real orders.
    Never affects dry-live selectors.
    It only tracks:
      signal -> pending maker-limit -> fill/miss -> TP/SL/TIME.
    """

    NAME = "MAKER_SHORT_TP3_SL03_SHADOW"

    def __init__(self, log_fn):
        self.log = log_fn
        self.pending = {}
        self.active = {}
        self.last_open = {}
        self.stats = defaultdict(lambda: {
            "signals": 0,
            "seen": 0,
            "pending_opened": 0,
            "filled": 0,
            "missed": 0,
            "closed": 0,
            "wins": 0,
            "losses": 0,
            "gross": 0.0,
            "net": 0.0,
            "costs": 0.0,
            "reasons": Counter(),
            "rejects": Counter(),
            "symbols": Counter(),
            "sym_net": defaultdict(float),
        })
        self.last_poll = 0.0

    def enabled(self):
        return bool(getattr(cfg, "MAKER_SHORT_V1_ENABLED", True))

    def _params(self):
        return {
            "offset_pct": sf(getattr(cfg, "MAKER_SHORT_V1_OFFSET_PCT", 0.15), 0.15),
            "tp_pct": sf(getattr(cfg, "MAKER_SHORT_V1_TP_PCT", 3.0), 3.0),
            "sl_pct": sf(getattr(cfg, "MAKER_SHORT_V1_SL_PCT", 0.3), 0.3),
            "cost_pct": sf(getattr(cfg, "MAKER_SHORT_V1_COST_PCT", 0.03), 0.03),
            "wait_seconds": sf(getattr(cfg, "MAKER_SHORT_V1_WAIT_SECONDS", 300), 300),
            "ttl_seconds": sf(getattr(cfg, "MAKER_SHORT_V1_TTL_SECONDS", 300), 300),
            "margin": sf(getattr(cfg, "MAKER_SHORT_V1_MARGIN", 3.0), 3.0),
            "leverage": si(getattr(cfg, "MAKER_SHORT_V1_LEVERAGE", 4), 4),
            "max_pending": si(getattr(cfg, "MAKER_SHORT_V1_MAX_PENDING", 4), 4),
            "max_active": si(getattr(cfg, "MAKER_SHORT_V1_MAX_ACTIVE", 3), 3),
            "cooldown": sf(getattr(cfg, "MAKER_SHORT_V1_COOLDOWN_SECONDS", 900), 900),
            "min_pc": sf(getattr(cfg, "MAKER_SHORT_V1_MIN_PC", 1.0), 1.0),
            "min_vol": sf(getattr(cfg, "MAKER_SHORT_V1_MIN_VOL", 8.0), 8.0),
            "max_spread": sf(getattr(cfg, "MAKER_SHORT_V1_MAX_SPREAD_BPS", 8.0), 8.0),
            "max_rank": si(getattr(cfg, "MAKER_SHORT_V1_MAX_RANK", 80), 80),
            "poll_seconds": sf(getattr(cfg, "MAKER_SHORT_V1_POLL_SECONDS", 5.0), 5.0),
        }

    def _key(self, symbol):
        return str(symbol)

    def _match(self, cand, current_time):
        p = self._params()

        symbol = cand.get("symbol", "")
        if not symbol:
            return False, "NO_SYMBOL"

        key = self._key(symbol)
        if key in self.pending or key in self.active:
            return False, "ALREADY_TRACKED"

        if len(self.pending) >= p["max_pending"]:
            return False, "MAX_PENDING"

        if len(self.active) >= p["max_active"]:
            return False, "MAX_ACTIVE"

        last = self.last_open.get(symbol, 0.0)
        if current_time - last < p["cooldown"]:
            return False, "COOLDOWN"

        if not cand.get("depth_available", False):
            return False, cand.get("depth_reason", "NO_DEPTH")

        if cand.get("depth_thin", False):
            return False, "DEPTH_THIN"

        pc = sf(cand.get("price_change"))
        vol = sf(cand.get("vol_ratio"))
        spread = sf(cand.get("spread_bps"), 999.0)
        rank = si(cand.get("current_turnover_rank"), 999999)
        price = sf(cand.get("price"))

        if price <= 0:
            return False, "BAD_PRICE"

        if pc < p["min_pc"]:
            return False, f"PC_LOW_{pc:+.2f}"

        if vol < p["min_vol"]:
            return False, f"VOL_LOW_{vol:.1f}"

        if spread > p["max_spread"]:
            return False, f"SPREAD_WIDE_{spread:.2f}"

        if rank > p["max_rank"]:
            return False, f"RANK_HIGH_{rank}"

        return True, "MATCH"

    def maybe_open(self, cand, current_time, time_str):
        if not self.enabled():
            return []

        st = self.stats[self.NAME]
        st["seen"] += 1

        ok, reason = self._match(cand, current_time)
        if not ok:
            r = str(reason)
            # Keep diagnostics compact. Do not log every reject line.
            if not (
                r == "ALREADY_TRACKED"
                or r == "MAX_PENDING"
                or r == "MAX_ACTIVE"
                or r == "COOLDOWN"
            ):
                if r.startswith("PC_LOW"):
                    tag = "PC_LOW"
                elif r.startswith("VOL_LOW"):
                    tag = "VOL_LOW"
                elif r.startswith("SPREAD_WIDE"):
                    tag = "SPREAD_WIDE"
                elif r.startswith("RANK_HIGH"):
                    tag = "RANK_HIGH"
                elif "DEPTH" in r:
                    tag = r
                else:
                    tag = r
                st["rejects"][tag] += 1
            return []

        p = self._params()
        symbol = cand.get("symbol")
        clean = cand.get("clean_symbol", symbol.replace("_USDT", ""))
        price = sf(cand.get("price"))
        offset = p["offset_pct"]
        limit_price = price * (1.0 + offset / 100.0)
        key = self._key(symbol)

        self.pending[key] = {
            "key": key,
            "symbol": symbol,
            "clean_symbol": clean,
            "signal_price": price,
            "limit_price": limit_price,
            "signal_time": current_time,
            "created": current_time,
            "price_change": sf(cand.get("price_change")),
            "vol_ratio": sf(cand.get("vol_ratio")),
            "spread_bps": sf(cand.get("spread_bps"), 999.0),
            "rank": si(cand.get("current_turnover_rank"), 999999),
            "score": cand.get("score", 0),
            "max_seen_up_from_signal": 0.0,
        }
        self.last_open[symbol] = current_time

        st = self.stats[self.NAME]
        st["signals"] += 1
        st["pending_opened"] += 1
        st["symbols"][clean] += 1

        self.log(
            f"[{time_str}] MAKER_SHORT_PENDING | {self.NAME} | {clean} | "
            f"signal={price:.8f} limit={limit_price:.8f} offset={offset:.2f}% "
            f"pc={sf(cand.get('price_change')):+.2f}% vol=x{sf(cand.get('vol_ratio')):.1f} "
            f"spread={sf(cand.get('spread_bps'),999):.2f}bps "
            f"rank={si(cand.get('current_turnover_rank'),999999)} score={cand.get('score',0)}\n"
        )

        return [self.NAME]

    def update_price(self, symbol, clean_symbol, price, current_time, time_str):
        if not self.enabled() or price <= 0:
            return

        key = self._key(symbol)

        if key in self.pending:
            self._update_pending(key, price, current_time, time_str)

        if key in self.active:
            self._update_active(key, price, current_time, time_str, source="TICK")

    def _update_pending(self, key, price, current_time, time_str):
        p = self._params()
        w = self.pending.get(key)
        if not w:
            return

        signal_price = sf(w.get("signal_price"))
        limit_price = sf(w.get("limit_price"))
        if signal_price <= 0 or limit_price <= 0:
            self.pending.pop(key, None)
            return

        up_from_signal = ((price - signal_price) / signal_price) * 100.0
        w["max_seen_up_from_signal"] = max(sf(w.get("max_seen_up_from_signal")), up_from_signal)

        age = current_time - sf(w.get("signal_time"))
        clean = w.get("clean_symbol", key)

        if price >= limit_price:
            self.pending.pop(key, None)

            self.active[key] = {
                **w,
                "entry": limit_price,
                "fill_time": current_time,
                "max_profit_pct": 0.0,
                "max_loss_pct": 0.0,
            }

            st = self.stats[self.NAME]
            st["filled"] += 1

            self.log(
                f"[{time_str}] MAKER_SHORT_FILL | {self.NAME} | {clean} | "
                f"limit={limit_price:.8f} now={price:.8f} age={age:.1f}s "
                f"maxUpFromSignal={sf(w.get('max_seen_up_from_signal')):+.2f}%\n"
            )
            return

        if age >= p["wait_seconds"]:
            self.pending.pop(key, None)

            st = self.stats[self.NAME]
            st["missed"] += 1
            st["reasons"]["MISS_NO_FILL"] += 1

            self.log(
                f"[{time_str}] MAKER_SHORT_MISS | {self.NAME} | {clean} | "
                f"signal={signal_price:.8f} limit={limit_price:.8f} now={price:.8f} "
                f"age={age:.1f}s maxUpFromSignal={sf(w.get('max_seen_up_from_signal')):+.2f}%\n"
            )

    def _update_active(self, key, price, current_time, time_str, source="TICK"):
        p = self._params()
        w = self.active.get(key)
        if not w:
            return

        entry = sf(w.get("entry"))
        if entry <= 0 or price <= 0:
            return

        short_profit_pct = ((entry - price) / entry) * 100.0

        w["max_profit_pct"] = max(sf(w.get("max_profit_pct")), short_profit_pct)
        w["max_loss_pct"] = min(sf(w.get("max_loss_pct")), short_profit_pct)

        age_from_signal = current_time - sf(w.get("signal_time"))
        age_from_fill = current_time - sf(w.get("fill_time"))

        reason = None
        if short_profit_pct >= p["tp_pct"]:
            reason = "TP"
        elif short_profit_pct <= -p["sl_pct"]:
            reason = "SL"
        elif age_from_signal >= p["ttl_seconds"]:
            reason = "TIME"

        if reason is None:
            return

        gross, net, costs = calc_shadow_pnl(
            p["margin"],
            p["leverage"],
            short_profit_pct,
            p["cost_pct"],
        )

        clean = w.get("clean_symbol", key)
        st = self.stats[self.NAME]

        st["closed"] += 1
        st["wins"] += int(net > 0)
        st["losses"] += int(net <= 0)
        st["gross"] += gross
        st["net"] += net
        st["costs"] += costs
        st["reasons"][reason] += 1
        st["sym_net"][clean] += net

        self.log(
            f"[{time_str}] MAKER_SHORT_CLOSE | {self.NAME} | {clean} | {reason} | "
            f"Entry:{entry:.8f} Exit:{price:.8f} | Move:{short_profit_pct:+.2f}% | "
            f"Gross:{gross:+.2f}$ Net:{net:+.2f}$ Cost:{costs:.4f}$ | "
            f"MFE:{sf(w.get('max_profit_pct')):+.2f}% MAE:{sf(w.get('max_loss_pct')):+.2f}% | "
            f"signalAge={age_from_signal:.1f}s fillAge={age_from_fill:.1f}s "
            f"pc={sf(w.get('price_change')):+.2f}% vol=x{sf(w.get('vol_ratio')):.1f} "
            f"spread={sf(w.get('spread_bps'),999):.2f}bps rank={w.get('rank')} source={source}\n"
        )

        self.active.pop(key, None)

    async def poll_active_prices(self, session, current_time, time_str):
        if not self.enabled():
            return

        if not self.pending and not self.active:
            return

        p = self._params()
        if current_time - self.last_poll < p["poll_seconds"]:
            return
        self.last_poll = current_time

        symbols = sorted(set(self.pending.keys()) | set(self.active.keys()))
        for symbol in symbols:
            try:
                url = f"https://contract.mexc.com/api/v1/contract/ticker?symbol={symbol}"
                async with session.get(url, timeout=5) as res:
                    if res.status != 200:
                        self.log(f"[{time_str}] MAKER_SHORT_POLL_FAIL | {symbol} | HTTP_{res.status}\n")
                        continue
                    data = await res.json()
                    d = data.get("data") or {}
                    price = sf(d.get("lastPrice") or d.get("fairPrice") or d.get("indexPrice"))
                    if price <= 0:
                        self.log(f"[{time_str}] MAKER_SHORT_POLL_FAIL | {symbol} | BAD_PRICE\n")
                        continue
                    clean = symbol.replace("_USDT", "")
                    self.update_price(symbol, clean, price, current_time, time_str)
            except Exception as e:
                self.log(f"[{time_str}] MAKER_SHORT_POLL_FAIL | {symbol} | {type(e).__name__}: {e}\n")

    def format_report(self):
        p = self._params()
        st = self.stats[self.NAME]
        closed = st["closed"]
        wr = (st["wins"] / closed * 100.0) if closed else 0.0
        fill_base = st["pending_opened"]
        fill_rate = (st["filled"] / fill_base * 100.0) if fill_base else 0.0
        best = sorted(st["sym_net"].items(), key=lambda x: x[1], reverse=True)[:8]
        worst = sorted(st["sym_net"].items(), key=lambda x: x[1])[:8]

        lines = ["=== MAKER_SHORT_TP3_SL03_SHADOW REPORT ==="]
        lines.append(
            f"Params: pc>={p['min_pc']} vol>={p['min_vol']} spread<={p['max_spread']}bps "
            f"rank<={p['max_rank']} offset={p['offset_pct']}% TP={p['tp_pct']}% "
            f"SL={p['sl_pct']}% cost={p['cost_pct']}% wait={p['wait_seconds']}s ttl={p['ttl_seconds']}s"
        )
        lines.append(
            f"Seen:{st['seen']} Signals:{st['signals']} PendingOpened:{st['pending_opened']} "
            f"Filled:{st['filled']} Missed:{st['missed']} FillRate:{fill_rate:.1f}% "
            f"Closed:{closed} Active:{len(self.active)} Pending:{len(self.pending)}"
        )
        lines.append(
            f"Net:{st['net']:+.2f}$ Gross:{st['gross']:+.2f}$ Costs:-${st['costs']:.4f} "
            f"WR:{wr:.1f}% Reasons:{dict(st['reasons'])} Rejects:{dict(st['rejects'])} "
            f"Best:{best} Worst:{worst}"
        )
        return "\n".join(lines) + "\n"
