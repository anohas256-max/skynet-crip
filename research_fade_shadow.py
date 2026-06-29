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
    Aggressive research-only SHORT fade matrix.

    Never sends real orders.
    Never affects dry-live.
    Opens hypothetical SHORT positions from live candidates.
    Closes active positions by direct ticker polling, not only candidate ticks.
    """

    NAME = "RESEARCH_FADE_V1_SHADOW"

    # V3 idea:
    # Do NOT hard-block potentially good trades.
    # Split signals into lanes:
    # - CORE: stricter offline-robust fade
    # - HF_TEST: more trades, shadow-only, measured separately
    # - SPIKE: violent move fade, still controlled
    PROFILES = [
        {
            "name": "CORE_SP2_ASK10",
            "max_spread": 2.0,
            "imb5_max": -0.10,
            "min_abs_pc": 0.30,
            "min_vol": 5.0,
            "max_rank": 150,
        },
        {
            "name": "CORE_SP3_ASK20",
            "max_spread": 3.0,
            "imb5_max": -0.20,
            "min_abs_pc": 0.30,
            "min_vol": 5.0,
            "max_rank": 150,
        },
        {
            "name": "HF_SP5_ASK10",
            "max_spread": 5.0,
            "imb5_max": -0.10,
            "min_abs_pc": 0.30,
            "min_vol": 5.0,
            "max_rank": 80,
        },
        {
            "name": "SPIKE_SP7",
            "max_spread": 7.0,
            "imb5_max": -0.05,
            "min_abs_pc": 0.70,
            "min_vol": 8.0,
            "max_rank": 60,
        },
    ]

    # Soft quarantine only for reporting. We do NOT block these symbols.
    # They still open in shadow, but report can show them separately.
    QUARANTINE_SYMBOLS = {
        "FET", "XPL", "INJ", "TIA", "VVV", "BILL", "UNI"
    }

    def __init__(self, log_fn):
        self.log = log_fn
        allowed_raw = str(getattr(cfg, "RESEARCH_FADE_V1_PROFILES", "CORE_SP2_ASK10") or "")
        allowed = {x.strip() for x in allowed_raw.split(",") if x.strip()}
        self.profiles = [p for p in self.PROFILES if not allowed or p["name"] in allowed]
        self.active = {}
        self.last_open = {}
        self.stats = defaultdict(lambda: {
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
        })
        self.last_poll = 0.0

    def enabled(self):
        return bool(getattr(cfg, "RESEARCH_FADE_V1_ENABLED", True))

    def _active_key(self, profile, symbol):
        return f"{profile}:{symbol}"

    def _matches_profile(self, cand, profile):
        symbol = cand.get("symbol", "")
        if not symbol:
            return False, "NO_SYMBOL"


        key = self._active_key(profile["name"], symbol)
        if key in self.active:
            return False, "ALREADY_OPEN"

        max_open_total = si(getattr(cfg, "RESEARCH_FADE_V1_MAX_OPEN_TOTAL", 9), 9)
        if len(self.active) >= max_open_total:
            return False, "MAX_OPEN_TOTAL"

        max_open_per_profile = si(getattr(cfg, "RESEARCH_FADE_V1_MAX_OPEN_PER_PROFILE", 3), 3)
        profile_active = sum(1 for x in self.active.values() if x.get("profile") == profile["name"])
        if profile_active >= max_open_per_profile:
            return False, "MAX_OPEN_PROFILE"

        now = sf(cand.get("_current_time"), time.time())
        cooldown = sf(getattr(cfg, "RESEARCH_FADE_V1_COOLDOWN_SECONDS", 600))
        last = self.last_open.get(key, 0.0)
        if now - last < cooldown:
            return False, "COOLDOWN"

        if not cand.get("depth_available", False):
            return False, cand.get("depth_reason", "NO_DEPTH")

        if cand.get("depth_thin", False):
            return False, "DEPTH_THIN"

        pc = sf(cand.get("price_change"))
        spread = sf(cand.get("spread_bps"), 999.0)
        rank = si(cand.get("current_turnover_rank"), 999999)
        vol = sf(cand.get("vol_ratio"))
        imb5 = sf(cand.get("imb_5"), 0.0)

        if abs(pc) < profile["min_abs_pc"]:
            return False, "PC_TOO_SMALL"

        if spread > profile["max_spread"]:
            return False, f"SPREAD_WIDE_{spread:.2f}"

        if rank > profile["max_rank"]:
            return False, f"RANK_HIGH_{rank}"

        if vol < profile["min_vol"]:
            return False, f"VOL_LOW_{vol:.1f}"

        if imb5 > profile["imb5_max"]:
            return False, f"IMB_NOT_ASK_{imb5:+.2f}"

        return True, "MATCH"

    def maybe_open(self, cand, current_time, time_str):
        if not self.enabled():
            return []

        opened = []
        symbol = cand.get("symbol", "")
        clean = cand.get("clean_symbol", symbol)
        price = sf(cand.get("price"))
        if not symbol or price <= 0:
            return opened

        cand["_current_time"] = current_time

        for profile in self.profiles:
            ok, reason = self._matches_profile(cand, profile)
            if not ok:
                continue

            key = self._active_key(profile["name"], symbol)

            self.active[key] = {
                "key": key,
                "profile": profile["name"],
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
                "rank": si(cand.get("current_turnover_rank"), 999999),
                "imb_5": sf(cand.get("imb_5"), 0.0),
                "score": cand.get("score", 0),
            }

            self.last_open[key] = current_time
            st = self.stats[profile["name"]]
            st["opened"] += 1
            st["symbols"][clean] += 1

            self.log(
                f"[{time_str}] RESEARCH_FADE_V1_OPEN | {profile['name']} | SHORT | {clean} | "
                f"Entry:{price:.8f} | pc={sf(cand.get('price_change')):+.2f}% "
                f"vol=x{sf(cand.get('vol_ratio')):.1f} spread={sf(cand.get('spread_bps'),999):.2f}bps "
                f"rank={si(cand.get('current_turnover_rank'),999999)} "
                f"imb5={sf(cand.get('imb_5')):+.2f} score={cand.get('score',0)}\n"
            )
            opened.append(profile["name"])

        return opened

    def update_price(self, symbol, clean_symbol, price, current_time, time_str):
        if not self.enabled():
            return

        if price <= 0:
            return

        keys = [k for k, w in self.active.items() if w.get("symbol") == symbol]
        for key in keys:
            self._update_one(key, clean_symbol, price, current_time, time_str, source="TICK")

    async def poll_active_prices(self, session, current_time, time_str):
        """
        Direct active-position close polling.
        This prevents stuck OPEN trades when a symbol does not reappear in candidate/ticker loop.
        """
        if not self.enabled() or not self.active:
            return

        interval = sf(getattr(cfg, "RESEARCH_FADE_V1_POLL_SECONDS", 20))
        if current_time - self.last_poll < interval:
            return
        self.last_poll = current_time

        symbols = sorted({w["symbol"] for w in self.active.values()})
        for symbol in symbols:
            try:
                url = f"https://contract.mexc.com/api/v1/contract/ticker?symbol={symbol}"
                async with session.get(url, timeout=5) as res:
                    if res.status != 200:
                        self.log(f"[{time_str}] RESEARCH_FADE_V1_POLL_FAIL | {symbol} | HTTP_{res.status}\n")
                        continue
                    data = await res.json()
                    d = data.get("data") or {}
                    price = sf(d.get("lastPrice") or d.get("fairPrice") or d.get("indexPrice"))
                    if price <= 0:
                        self.log(f"[{time_str}] RESEARCH_FADE_V1_POLL_FAIL | {symbol} | BAD_PRICE\n")
                        continue
                    clean = symbol.replace("_USDT", "")
                    self.update_price(symbol, clean, price, current_time, time_str)
            except Exception as e:
                self.log(f"[{time_str}] RESEARCH_FADE_V1_POLL_FAIL | {symbol} | {type(e).__name__}: {e}\n")

    def _update_one(self, key, clean_symbol, price, current_time, time_str, source="TICK"):
        w = self.active.get(key)
        if not w:
            return

        entry = sf(w.get("entry"))
        if entry <= 0 or price <= 0:
            return

        long_move_pct = ((price - entry) / entry) * 100.0
        short_profit_pct = -long_move_pct

        w["max_profit_pct"] = max(sf(w.get("max_profit_pct")), short_profit_pct)
        w["max_loss_pct"] = min(sf(w.get("max_loss_pct")), short_profit_pct)

        ttl = sf(getattr(cfg, "RESEARCH_FADE_V1_TTL_SECONDS", 300))
        age = current_time - sf(w.get("time"))

        if age < ttl:
            return

        gross, net, costs = calc_net_pnl(
            sf(getattr(cfg, "RESEARCH_FADE_V1_MARGIN", 3.0)),
            si(getattr(cfg, "RESEARCH_FADE_V1_LEVERAGE", 4), 4),
            short_profit_pct,
        )

        reason = "TIME_5M"
        profile = w.get("profile", "UNKNOWN")
        st = self.stats[profile]

        st["closed"] += 1
        st["wins"] += int(net > 0)
        st["losses"] += int(net <= 0)
        st["gross"] += gross
        st["net"] += net
        st["costs"] += costs
        st["reasons"][reason] += 1
        st["sym_net"][w["clean_symbol"]] += net

        self.log(
            f"[{time_str}] RESEARCH_FADE_V1_CLOSE | {profile} | SHORT | {w['clean_symbol']} | {reason} | "
            f"Entry:{entry:.8f} Exit:{price:.8f} | Move:{short_profit_pct:+.2f}% | "
            f"Gross:{gross:+.2f}$ Net:{net:+.2f}$ Costs:{costs:.2f}$ | "
            f"MFE:{sf(w.get('max_profit_pct')):+.2f}% MAE:{sf(w.get('max_loss_pct')):+.2f}% | "
            f"pc={sf(w.get('price_change')):+.2f}% vol=x{sf(w.get('vol_ratio')):.1f} "
            f"spread={sf(w.get('spread_bps'),999):.2f}bps rank={w.get('rank')} "
            f"imb5={sf(w.get('imb_5')):+.2f} source={source}\n"
        )

        self.active.pop(key, None)

    def format_report(self):
        lines = ["=== RESEARCH_FADE_V1_SHADOW MATRIX REPORT ==="]
        total_opened = 0
        total_closed = 0
        total_net = 0.0

        for profile in [p["name"] for p in self.profiles]:
            st = self.stats[profile]
            closed = st["closed"]
            wr = (st["wins"] / closed * 100.0) if closed else 0.0
            best = sorted(st["sym_net"].items(), key=lambda x: x[1], reverse=True)[:5]
            worst = sorted(st["sym_net"].items(), key=lambda x: x[1])[:5]

            total_opened += st["opened"]
            total_closed += closed
            total_net += st["net"]

            lines.append(
                f"{profile}: Opened:{st['opened']} Closed:{closed} "
                f"Net:{st['net']:+.2f}$ Costs:-${st['costs']:.2f} WR:{wr:.1f}% "
                f"Active:{sum(1 for x in self.active.values() if x.get('profile') == profile)} "
                f"Reasons:{dict(st['reasons'])} Best:{best} Worst:{worst}"
            )

        lines.append(f"TOTAL: Opened:{total_opened} Closed:{total_closed} Active:{len(self.active)} Net:{total_net:+.2f}$")
        return "\n".join(lines) + "\n"
