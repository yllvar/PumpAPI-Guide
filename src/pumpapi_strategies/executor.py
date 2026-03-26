from __future__ import annotations

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .signal import TradingSignal, SignalType


logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    order_id: str
    mint: str
    signal: TradingSignal
    amount: float
    order_type: SignalType
    status: OrderStatus = OrderStatus.PENDING
    tx_hash: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = self.created_at


class SignalExecutor:
    def __init__(
        self,
        client,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.client = client
        self.config = config or {}
        self._orders: Dict[str, Order] = {}
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._order_counter = 0

    async def execute(self, signal: TradingSignal, amount: float) -> Order:
        self._order_counter += 1
        order_id = f"order_{self._order_counter}_{signal.mint}"

        order = Order(
            order_id=order_id,
            mint=signal.mint,
            signal=signal,
            amount=amount,
            order_type=signal.signal_type,
        )

        try:
            if signal.signal_type == SignalType.BUY:
                result = await self._execute_buy(order)
            elif signal.signal_type == SignalType.SELL:
                result = await self._execute_sell(order)
            else:
                order.status = OrderStatus.FAILED
                order.error = "Unsupported order type"
                return order

            if result.get("success"):
                order.status = OrderStatus.FILLED
                order.tx_hash = result.get("tx_hash")
            else:
                order.status = OrderStatus.FAILED
                order.error = result.get("error", "Unknown error")

        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            order.status = OrderStatus.FAILED
            order.error = str(e)

        order.updated_at = datetime.now()
        self._orders[order_id] = order

        if order.status == OrderStatus.FILLED:
            await self._notify_handlers("filled", order)
        else:
            await self._notify_handlers("failed", order)

        return order

    async def _execute_buy(self, order: Order) -> Dict[str, Any]:
        try:
            result = self.client.execute_buy(
                mint=order.mint,
                sol_amount=order.amount,
                slippage_bps=self.config.get("slippage_bps", 100),
                priority_fee=self.config.get("priority_fee", 0),
            )
            return {
                "success": result.success,
                "tx_hash": result.tx_hash,
                "error": result.error,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_sell(self, order: Order) -> Dict[str, Any]:
        try:
            result = self.client.execute_sell(
                mint=order.mint,
                token_amount=order.amount,
                decimals=self.config.get("token_decimals", 6),
                slippage_bps=self.config.get("slippage_bps", 100),
                priority_fee=self.config.get("priority_fee", 0),
            )
            return {
                "success": result.success,
                "tx_hash": result.tx_hash,
                "error": result.error,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def on_event(self, event_type: str, handler: Callable):
        self._handlers[event_type] = handler

    async def _notify_handlers(self, event_type: str, order: Order):
        if event_type in self._handlers:
            try:
                await self._handlers[event_type](order)
            except Exception as e:
                logger.error(f"Handler error for {event_type}: {e}")

    def get_order(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_orders(self, status: Optional[OrderStatus] = None) -> list:
        if status is None:
            return list(self._orders.values())
        return [o for o in self._orders.values() if o.status == status]

    async def cancel_order(self, order_id: str) -> bool:
        order = self._orders.get(order_id)
        if not order:
            return False

        if order.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.now()
            return True
        return False
