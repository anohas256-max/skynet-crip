import asyncio
import hashlib
import hmac
import json
import math
import os
import time
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, Optional, Tuple

import aiohttp

import skynet_config as cfg


class MexcFuturesClient:
    """Minimal official MEXC Futures OPEN-API client.

    Uses official futures API signing: Signature = HMAC_SHA256(secret, accessKey + timestamp + parameterString)
    For POST parameterString is compact JSON body; for GET it is sorted query string.
    """

    def __init__(self, access_key: str, secret_key: str, base_url: Optional[str] = None, recv_window: int = 10000):
        self.access_key = access_key or ""
        self.secret_key = secret_key or ""
        self.base_url = (base_url or getattr(cfg, "MEXC_FUTURES_BASE_URL", "https://api.mexc.com")).rstrip("/")
        self.recv_window = int(recv_window)
        self._contract_cache: Dict[str, Dict[str, Any]] = {}

    def ready(self) -> bool:
        return bool(self.access_key and self.secret_key)

    @staticmethod
    def _compact_json(body: Dict[str, Any]) -> str:
        clean = {k: v for k, v in (body or {}).items() if v is not None}
        return json.dumps(clean, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def _query_string(params: Dict[str, Any]) -> str:
        items = []
        for k in sorted((params or {}).keys()):
            v = params[k]
            if v is None:
                continue
            items.append(f"{k}={v}")
        return "&".join(items)

    def _sign(self, parameter_string: str, ts: str) -> str:
        target = f"{self.access_key}{ts}{parameter_string}"
        return hmac.new(self.secret_key.encode("utf-8"), target.encode("utf-8"), hashlib.sha256).hexdigest()

    def _headers(self, parameter_string: str, ts: str) -> Dict[str, str]:
        return {
            "ApiKey": self.access_key,
            "Request-Time": ts,
            "Signature": self._sign(parameter_string, ts),
            "Recv-Window": str(self.recv_window),
            "Content-Type": "application/json",
        }

    async def public_get(self, session: aiohttp.ClientSession, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = self.base_url + path
        async with session.get(url, params=params or {}, timeout=8) as res:
            try:
                return await res.json()
            except Exception:
                return {"success": False, "code": res.status, "message": await res.text()}

    async def private_get(self, session: aiohttp.ClientSession, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        qs = self._query_string(params)
        ts = str(int(time.time() * 1000))
        headers = self._headers(qs, ts)
        url = self.base_url + path
        async with session.get(url, params=params, headers=headers, timeout=8) as res:
            try:
                return await res.json()
            except Exception:
                return {"success": False, "code": res.status, "message": await res.text()}

    async def private_post(self, session: aiohttp.ClientSession, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = self._compact_json(body or {})
        ts = str(int(time.time() * 1000))
        headers = self._headers(payload, ts)
        url = self.base_url + path
        async with session.post(url, data=payload.encode("utf-8"), headers=headers, timeout=8) as res:
            try:
                return await res.json()
            except Exception:
                return {"success": False, "code": res.status, "message": await res.text()}

    async def get_contract_info(self, session: aiohttp.ClientSession, symbol: str) -> Optional[Dict[str, Any]]:
        if symbol in self._contract_cache:
            return self._contract_cache[symbol]
        # Official docs endpoint. Some deployments also support /api/v1/contract/detail?symbol=...
        payload = await self.public_get(session, "/api/v1/contract/detail/country", {"symbol": symbol})
        if not payload.get("success"):
            payload = await self.public_get(session, "/api/v1/contract/detail", {"symbol": symbol})
        data = payload.get("data")
        if isinstance(data, list):
            data = next((x for x in data if x.get("symbol") == symbol), None)
        if isinstance(data, dict) and data.get("symbol") == symbol:
            self._contract_cache[symbol] = data
            return data
        return None

    async def get_open_positions(self, session: aiohttp.ClientSession, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {"symbol": symbol} if symbol else {}
        return await self.private_get(session, "/api/v1/private/position/open_positions", params)

    async def get_order(self, session: aiohttp.ClientSession, order_id: str) -> Dict[str, Any]:
        return await self.private_get(session, f"/api/v1/private/order/get/{order_id}")

    async def place_order(self, session: aiohttp.ClientSession, body: Dict[str, Any]) -> Dict[str, Any]:
        return await self.private_post(session, "/api/v1/private/order/create", body)


def _dec_floor(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=ROUND_DOWN) * step


def calc_contract_vol(info: Dict[str, Any], price: float, margin_usdt: float, leverage: int) -> Tuple[int, Dict[str, Any]]:
    contract_size = Decimal(str(info.get("contractSize", "0")))
    vol_unit = Decimal(str(info.get("volUnit", "1")))
    min_vol = Decimal(str(info.get("minVol", "1")))
    max_vol = Decimal(str(info.get("maxVol", "999999999")))
    p = Decimal(str(price))
    notional = Decimal(str(margin_usdt)) * Decimal(str(leverage))

    if contract_size <= 0 or p <= 0:
        raise ValueError("BAD_CONTRACT_SIZE_OR_PRICE")

    raw_vol = notional / (p * contract_size)
    vol = _dec_floor(raw_vol, vol_unit)
    if vol < min_vol:
        vol = min_vol
    if vol > max_vol:
        vol = max_vol

    # MEXC vol is contracts; all examples use integer contracts for common USDT perpetuals.
    vol_int = int(vol)
    actual_notional = p * contract_size * Decimal(str(vol_int))
    actual_margin = actual_notional / Decimal(str(leverage))
    return vol_int, {
        "contract_size": float(contract_size),
        "vol_unit": float(vol_unit),
        "min_vol": float(min_vol),
        "max_vol": float(max_vol),
        "raw_vol": float(raw_vol),
        "vol": vol_int,
        "target_notional": float(notional),
        "actual_notional": float(actual_notional),
        "actual_margin": float(actual_margin),
    }


class MicroLiveState:
    def __init__(self):
        self.day_start = int(time.time() // 86400)
        self.trades_today = 0
        self.realized_pnl_today = 0.0
        self.open_trade: Optional[Dict[str, Any]] = None
        self.hard_locked = False
        self.lock_reason = ""

    def roll_day(self):
        d = int(time.time() // 86400)
        if d != self.day_start and self.open_trade is None:
            self.day_start = d
            self.trades_today = 0
            self.realized_pnl_today = 0.0
            self.hard_locked = False
            self.lock_reason = ""


class MexcMicroLiveExecutor:
    """Ultra conservative real micro-live bridge.

    Real trading is OFF unless all toggles are true:
      REAL_TRADING_ENABLED=true
      REAL_TRADING_ARMED=true
      LIVE_DRY_RUN=false
    """

    def __init__(self):
        self.client = MexcFuturesClient(
            access_key=getattr(cfg, "MEXC_API_KEY", ""),
            secret_key=getattr(cfg, "MEXC_API_SECRET", ""),
            recv_window=getattr(cfg, "MEXC_RECV_WINDOW", 10000),
        )
        self.state = MicroLiveState()

    def enabled(self) -> bool:
        return bool(
            getattr(cfg, "REAL_TRADING_ENABLED", False)
            and getattr(cfg, "REAL_TRADING_ARMED", False)
            and not getattr(cfg, "LIVE_DRY_RUN", True)
        )

    def status_line(self) -> str:
        return (
            f"REAL_ENABLED={getattr(cfg,'REAL_TRADING_ENABLED',False)} "
            f"ARMED={getattr(cfg,'REAL_TRADING_ARMED',False)} "
            f"LIVE_DRY_RUN={getattr(cfg,'LIVE_DRY_RUN',True)} "
            f"strategy={getattr(cfg,'REAL_STRATEGY','-')} "
            f"trades_today={self.state.trades_today} pnl_today={self.state.realized_pnl_today:+.2f} "
            f"locked={self.state.hard_locked}:{self.state.lock_reason}"
        )

    def should_open(self, strategy_name: str, candidate: Dict[str, Any], track: Dict[str, Any]) -> Tuple[bool, str]:
        self.state.roll_day()
        if not self.enabled():
            return False, "REAL_DISABLED"
        if not self.client.ready():
            return False, "API_KEYS_MISSING"
        if strategy_name != getattr(cfg, "REAL_STRATEGY", "META_V12_EXEC_SAFE_MO1"):
            return False, "NOT_REAL_STRATEGY"
        if self.state.hard_locked:
            return False, f"REAL_LOCKED_{self.state.lock_reason}"
        if self.state.open_trade is not None:
            return False, "REAL_MAX_OPEN"
        if self.state.trades_today >= int(getattr(cfg, "REAL_MAX_TRADES_PER_DAY", 1)):
            return False, "REAL_DAILY_TRADE_LIMIT"
        if self.state.realized_pnl_today <= -abs(float(getattr(cfg, "REAL_DAILY_MAX_LOSS_USDT", 0.35))):
            return False, "REAL_DAILY_LOSS_LIMIT"
        if float(getattr(cfg, "REAL_MARGIN_USDT", 3.0)) > float(getattr(cfg, "REAL_MAX_MARGIN_USDT", 3.0)):
            return False, "REAL_MARGIN_GT_MAX"
        if candidate.get("depth_thin", False):
            return False, "REAL_BLOCK_DEPTH_THIN"
        if float(candidate.get("spread_bps", 999.0)) > float(getattr(cfg, "REAL_MAX_SPREAD_BPS", 3.0)):
            return False, "REAL_SPREAD_TOO_WIDE"
        return True, "OK"

    async def open_long(self, session: aiohttp.ClientSession, strategy_name: str, candidate: Dict[str, Any], time_str: str) -> Dict[str, Any]:
        ok, why = self.should_open(strategy_name, candidate, {})
        if not ok:
            return {"ok": False, "reason": why}

        symbol = candidate["symbol"]
        price = float(candidate["price"])
        leverage = int(getattr(cfg, "REAL_LEVERAGE", 4))
        margin = float(getattr(cfg, "REAL_MARGIN_USDT", 3.0))
        info = await self.client.get_contract_info(session, symbol)
        if not info:
            return {"ok": False, "reason": "CONTRACT_INFO_FAIL"}
        if not info.get("apiAllowed", True):
            return {"ok": False, "reason": "API_NOT_ALLOWED_FOR_SYMBOL"}

        vol, meta = calc_contract_vol(info, price, margin, leverage)
        max_actual_margin = float(getattr(cfg, "REAL_MAX_ACTUAL_MARGIN_USDT", margin * 1.35))
        if meta["actual_margin"] > max_actual_margin:
            return {"ok": False, "reason": f"ACTUAL_MARGIN_TOO_HIGH_{meta['actual_margin']:.2f}"}

        oid = f"skynet_{int(time.time()*1000)}_{symbol}_open"
        body = {
            "symbol": symbol,
            "price": 0,
            "vol": vol,
            "leverage": leverage,
            "side": 1,       # open long
            "type": 5,       # market
            "openType": 1,   # isolated
            "externalOid": oid,
            "positionMode": int(getattr(cfg, "REAL_POSITION_MODE", 1)),
        }
        payload = await self.client.place_order(session, body)
        if not payload.get("success"):
            return {"ok": False, "reason": "ORDER_OPEN_FAIL", "payload": payload, "body": body, "meta": meta}

        order_id = str((payload.get("data") or {}).get("orderId", ""))
        self.state.open_trade = {
            "strategy": strategy_name,
            "symbol": symbol,
            "clean_symbol": candidate.get("clean_symbol", symbol),
            "order_id": order_id,
            "vol": vol,
            "remaining_vol": vol,
            "entry_price_ref": price,
            "leverage": leverage,
            "margin_ref": margin,
            "opened_at": time.time(),
            "meta": meta,
        }
        self.state.trades_today += 1
        return {"ok": True, "order_id": order_id, "body": body, "payload": payload, "meta": meta}

    async def close_long(self, session: aiohttp.ClientSession, strategy_name: str, symbol: str, fraction: float, reason: str) -> Dict[str, Any]:
        if not self.enabled():
            return {"ok": False, "reason": "REAL_DISABLED"}
        tr = self.state.open_trade
        if not tr or tr.get("symbol") != symbol or tr.get("strategy") != strategy_name:
            return {"ok": False, "reason": "NO_MATCHING_REAL_POSITION"}
        remain = int(tr.get("remaining_vol", 0))
        if remain <= 0:
            return {"ok": False, "reason": "NO_REMAINING_VOL"}
        close_vol = max(1, int(math.floor(remain * max(0.0, min(1.0, float(fraction))))))
        close_vol = min(close_vol, remain)
        oid = f"skynet_{int(time.time()*1000)}_{symbol}_close"
        body = {
            "symbol": symbol,
            "price": 0,
            "vol": close_vol,
            "side": 4,       # close long
            "type": 5,       # market
            "openType": 1,
            "externalOid": oid,
            "positionMode": int(getattr(cfg, "REAL_POSITION_MODE", 1)),
        }
        payload = await self.client.place_order(session, body)
        if not payload.get("success"):
            return {"ok": False, "reason": "ORDER_CLOSE_FAIL", "payload": payload, "body": body}
        tr["remaining_vol"] = remain - close_vol
        if tr["remaining_vol"] <= 0:
            self.state.open_trade = None
        return {"ok": True, "body": body, "payload": payload, "remaining_vol": tr.get("remaining_vol", 0), "close_reason": reason}
