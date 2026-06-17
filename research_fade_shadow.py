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


def calc_net_pnl(margin, leverage, move_pct):
    notional = margin * leverage
    gross = notional * (move_pct / 100.0)

    commission_cost = notional * cfg.COMMISSION_RATE * 2
    spread_cost = notional * (cfg.SPREAD_BPS / 10000.0)
    slippage_cost = notional * (cfg.SLIPPAGE_BPS / 10000.0) * 2
    costs = commission_cost + spread_cost + slippage_cost

    net = gross - costs
    return gross, net, costs


class ResearchFadeV1Shadow:
    """
    Research-only live shadow tracker.

    It does NOT send real orders.
    It does NOT affect dry-live.
    It only logs hypothetical SHORT fade trades from live candidates.
    """

    NAME = "RESEARCH_FADE_V1_SHADOW"

    def __init__(self, log_fn):
        self.log = log_fn
        self.active = {}
        self.last_open = {}
        self.stats = {
            "opened": 0,
            "closed": 0,
            "wins": 0,
            "losses": 0,
            "gross": 0.0,
            "net": 0.0,
            "costs": 0.0,
            "reasons": Counter(),
            "symbols": Counter(),
            "sym_net": defaultdict(float),
        }

    def enabled(self):
        return bool(getattr(cfg, "RESEARCH_FADE_V1_ENABLED", False))

    def _matches(self, cand):
        if not self.enabled():
            return False, "DISABLED"

        symbol = cand.get("symbol", "")
        clean = cand.get("clean_symbol", symbol)

        if symbol in self.active:
            return False, "ALREADY_OPEN"

        if len(self.active) >= int(getattr(cfg, "RESEARCH_FADE_V1_MAX_OPEN", 3)):
            return False, "MAX_OPEN"

        now = sf(cand.get("_current_time"), time.time())
        cooldown = sf(getattr(cfg, "RESEARCH_FADE_V1_COOLDOWN_SECONDS", 600))
        last = self.last_open.get(symbol, 0.0)
        if now - last < cooldown:
            return False, "COOLDOWN"

        if not cand.get("depth_available", False):
            return False, cand.get("depth_reason", "NO_DEPTH")

        if cand.get("depth_thin", False):
            return False, "DEPTH_THIN"

        pc = sf(cand.get("price_change"))
        spread = sf(cand.get("spread_bps"), 999.0)
        rank = int(sf(cand.get("current_turnover_rank"), 999999))
        vol = sf(cand.get("vol_ratio"))
        imb5 = sf(cand.get("imb_5"), 0.0)

        if abs(pc) < sf(getattr(cfg, "RESEARCH_FADE_V1_MIN_ABS_PC", 0.30)):
            return False, "PC_TOO_SMALL"

        if spread > sf(getattr(cfg, "RESEARCH_FADE_V1_MAX_SPREAD_BPS", 3.0)):
            return False, f"SPREAD_WIDE_{spread:.2f}"

        if rank > int(getattr(cfg, "RESEARCH_FADE_V1_MAX_RANK", 150)):
            return False, f"RANK_HIGH_{rank}"

        if vol < sf(getattr(cfg, "RESEARCH_FADE_V1_MIN_VOL_RATIO", 5.0)):
            return False, f"VOL_LOW_{vol:.1f}"

        # Robust rule from v17: IMB_ASK means top5 ask liquidity dominates.
        if imb5 > sf(getattr(cfg, "RESEARCH_FADE_V1_IMB5_MAX", -0.20)):
            return False, f"IMB_NOT_ASK_{imb5:+.2f}"

        return True, "MATCH"

    def maybe_open(self, cand, current_time, time_str):
        ok, reason = self._matches(cand)
        if not ok:
            return False, reason

        symbol = cand["symbol"]
        clean = cand.get("clean_symbol", symbol)
        price = sf(cand.get("price"))
        if price <= 0:
            return False, "BAD_PRICE"

        self.active[symbol] = {
            "symbol": symbol,
            "clean_symbol": clean,
            "entry": price,
            "time": current_time,
            "side": "SHORT",
            "max_profit_pct": 0.0,
            "max_loss_pct": 0.0,
            "price_change": sf(cand.get("price_change")),
            "vol_ratio": sf(cand.get("vol_ratio")),
            "spread_bps": sf(cand.get("spread_bps"), 999.0),
            "rank": int(sf(cand.get("current_turnover_rank"), 999999)),
            "imb_5": sf(cand.get("imb_5"), 0.0),
            "score": cand.get("score", 0),
        }
        self.last_open[symbol] = current_time
        self.stats["opened"] += 1
        self.stats["symbols"][clean] += 1

        self.log(
            f"[{time_str}] RESEARCH_FADE_V1_OPEN | SHORT | {clean} | "
            f"Entry:{price:.8f} | pc={sf(cand.get('price_change')):+.2f}% "
            f"vol=x{sf(cand.get('vol_ratio')):.1f} spread={sf(cand.get('spread_bps'),999):.2f}bps "
            f"rank={int(sf(cand.get('current_turnover_rank'),999999))} "
            f"imb5={sf(cand.get('imb_5')):+.2f} score={cand.get('score',0)}\n"
        )
        return True, "OPENED"

    def update_price(self, symbol, clean_symbol, price, current_time, time_str):
        if not self.enabled():
            return

        w = self.active.get(symbol)
        if not w:
            return

        entry = sf(w.get("entry"))
        if entry <= 0 or price <= 0:
            return

        long_move_pct = ((price - entry) / entry) * 100.0

        # SHORT profit is opposite of price move.
        short_profit_pct = -long_move_pct
        w["max_profit_pct"] = max(sf(w.get("max_profit_pct")), short_profit_pct)
        w["max_loss_pct"] = min(sf(w.get("max_loss_pct")), short_profit_pct)

        ttl = sf(getattr(cfg, "RESEARCH_FADE_V1_TTL_SECONDS", 300))
        age = current_time - sf(w.get("time"))

        if age < ttl:
            return

        gross, net, costs = calc_net_pnl(
            sf(getattr(cfg, "RESEARCH_FADE_V1_MARGIN", 3.0)),
            int(getattr(cfg, "RESEARCH_FADE_V1_LEVERAGE", 4)),
            short_profit_pct,
        )

        reason = "TIME_5M"
        self.stats["closed"] += 1
        self.stats["wins"] += int(net > 0)
        self.stats["losses"] += int(net <= 0)
        self.stats["gross"] += gross
        self.stats["net"] += net
        self.stats["costs"] += costs
        self.stats["reasons"][reason] += 1
        self.stats["sym_net"][w["clean_symbol"]] += net

        self.log(
            f"[{time_str}] RESEARCH_FADE_V1_CLOSE | SHORT | {w['clean_symbol']} | {reason} | "
            f"Entry:{entry:.8f} Exit:{price:.8f} | Move:{short_profit_pct:+.2f}% | "
            f"Gross:{gross:+.2f}$ Net:{net:+.2f}$ Costs:{costs:.2f}$ | "
            f"MFE:{sf(w.get('max_profit_pct')):+.2f}% MAE:{sf(w.get('max_loss_pct')):+.2f}% | "
            f"pc={sf(w.get('price_change')):+.2f}% vol=x{sf(w.get('vol_ratio')):.1f} "
            f"spread={sf(w.get('spread_bps'),999):.2f}bps rank={w.get('rank')} imb5={sf(w.get('imb_5')):+.2f}\n"
        )

        self.active.pop(symbol, None)

    def format_report(self):
        closed = self.stats["closed"]
        wr = (self.stats["wins"] / closed * 100.0) if closed else 0.0

        best = sorted(self.stats["sym_net"].items(), key=lambda x: x[1], reverse=True)[:5]
        worst = sorted(self.stats["sym_net"].items(), key=lambda x: x[1])[:5]

        return (
            "=== RESEARCH_FADE_V1_SHADOW REPORT ===\n"
            f"Opened:{self.stats['opened']} | Closed:{closed} | Active:{len(self.active)} | "
            f"Net:{self.stats['net']:+.2f}$ | Costs:-${self.stats['costs']:.2f} | "
            f"WR:{wr:.1f}% | Reasons:{dict(self.stats['reasons'])}\n"
            f"Best:{best} | Worst:{worst}\n"
        )
