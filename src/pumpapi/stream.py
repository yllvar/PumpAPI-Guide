from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass

import websockets
from websockets.client import WebSocketClientProtocol

from .types import (
    TradeInfo,
    MarketCapInfo,
    BondingCurveState,
    TokenMetadata,
    WebSocketMessage,
)


logger = logging.getLogger(__name__)


@dataclass
class SubscriptionConfig:
    type: str
    mint: Optional[str] = None
    include_raw: bool = False


class PumpApiStream:
    def __init__(
        self,
        wss_url: str = "wss://pumpportal.fun/api/data",
        api_key: Optional[str] = None,
    ):
        self.wss_url = wss_url
        self.api_key = api_key
        self._ws: Optional[WebSocketClientProtocol] = None
        self._subscriptions: Dict[str, SubscriptionConfig] = {}
        self._handlers: Dict[str, Callable] = {}
        self._running = False

    async def connect(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._ws = await websockets.connect(
            self.wss_url,
            extra_headers=headers,
        )
        self._running = True
        logger.info("WebSocket connected")

    async def disconnect(self):
        if self._ws:
            await self._ws.close()
        self._running = False
        logger.info("WebSocket disconnected")

    async def subscribe_new_tokens(
        self,
        callback: Callable[[TokenMetadata], None],
    ) -> str:
        subscription_id = "new_tokens"
        self._handlers[subscription_id] = callback

        await self._send({
            "method": "subscribeNewToken",
            "params": {
                "newTokens": True,
            },
            "id": subscription_id,
        })
        self._subscriptions[subscription_id] = SubscriptionConfig(type="new_token")
        return subscription_id

    async def subscribe_trades(
        self,
        mint: str,
        callback: Callable[[TradeInfo], None],
    ) -> str:
        subscription_id = f"trades_{mint}"
        self._handlers[subscription_id] = callback

        await self._send({
            "method": "subscribeTrade",
            "params": {
                " mint": mint,
            },
            "id": subscription_id,
        })
        self._subscriptions[subscription_id] = SubscriptionConfig(type="trade", mint=mint)
        return subscription_id

    async def subscribe_market_cap(
        self,
        mint: str,
        callback: Callable[[MarketCapInfo], None],
    ) -> str:
        subscription_id = f"market_cap_{mint}"
        self._handlers[subscription_id] = callback

        await self._send({
            "method": "subscribeMarketCap",
            "params": {
                "mint": mint,
            },
            "id": subscription_id,
        })
        self._subscriptions[subscription_id] = SubscriptionConfig(type="market_cap", mint=mint)
        return subscription_id

    async def subscribe_bonding_curve(
        self,
        mint: str,
        callback: Callable[[BondingCurveState], None],
    ) -> str:
        subscription_id = f"bonding_curve_{mint}"
        self._handlers[subscription_id] = callback

        await self._send({
            "method": "subscribeBondingCurve",
            "params": {
                "mint": mint,
            },
            "id": subscription_id,
        })
        self._subscriptions[subscription_id] = SubscriptionConfig(type="bonding_curve", mint=mint)
        return subscription_id

    async def unsubscribe(self, subscription_id: str):
        if subscription_id in self._subscriptions:
            await self._send({
                "method": "unsubscribe",
                "id": subscription_id,
            })
            del self._subscriptions[subscription_id]
            del self._handlers[subscription_id]

    async def _send(self, message: Dict[str, Any]):
        if self._ws and self._ws.open:
            await self._ws.send(json.dumps(message))

    async def listen(self):
        if not self._ws:
            await self.connect()

        while self._running:
            try:
                message = await self._ws.recv()
                await self._process_message(message)
            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed, reconnecting...")
                await self._reconnect()
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def _reconnect(self):
        await self.connect()
        for sub_id in self._subscriptions:
            sub = self._subscriptions[sub_id]
            await self._send({
                "method": "subscribe",
                "params": {"type": sub.type, "mint": sub.mint},
                "id": sub_id,
            })

    async def _process_message(self, message: str):
        try:
            data = json.loads(message)
            msg_type = data.get("method", "")

            if msg_type == "newToken":
                token_data = data.get("data", {})
                token = TokenMetadata(**token_data)
                if "new_tokens" in self._handlers:
                    self._handlers["new_tokens"](token)

            elif msg_type == "trade":
                trade_data = data.get("data", {})
                trade = TradeInfo(**trade_data)
                mint = trade.mint
                if f"trades_{mint}" in self._handlers:
                    self._handlers[f"trades_{mint}"](trade)

            elif msg_type == "marketCap":
                mc_data = data.get("data", {})
                market_cap = MarketCapInfo(**mc_data)
                mint = market_cap.mint
                if f"market_cap_{mint}" in self._handlers:
                    self._handlers[f"market_cap_{mint}"](market_cap)

            elif msg_type == "bondingCurve":
                bc_data = data.get("data", {})
                curve = BondingCurveState(**bc_data)
                mint = curve.mint
                if f"bonding_curve_{mint}" in self._handlers:
                    self._handlers[f"bonding_curve_{mint}"](curve)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def stop(self):
        self._running = False
