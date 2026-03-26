#!/usr/bin/env python3
"""
Signal Executor

Execute trades based on signals from any source.

This strategy:
1. Receives signals from various sources
2. Validates and filters signals
3. Executes trades with proper risk management
"""

import asyncio
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from pumpapi_strategies import (
    BaseStrategy,
    TradingSignal,
    SignalType,
    Order,
    OrderStatus,
)
from pumpapi import PumpApiClient


class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class RiskConfig:
    max_position_sol: float = 1.0
    max_daily_loss_sol: float = 5.0
    max_positions: int = 10
    min_signal_confidence: float = 0.5
    min_signal_strength: float = 0.3
    stop_loss_bps: int = 500
    take_profit_bps: int = 1000


class SignalExecutorStrategy(BaseStrategy):
    def __init__(
        self,
        client: PumpApiClient,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("SignalExecutor", config)

        self.client = client
        self.risk_config = RiskConfig(
            max_position_sol=self.config.get("max_position_sol", 1.0),
            max_daily_loss_sol=self.config.get("max_daily_loss_sol", 5.0),
            max_positions=self.config.get("max_positions", 10),
            min_signal_confidence=self.config.get("min_confidence", 0.5),
            min_signal_strength=self.config.get("min_strength", 0.3),
        )

        self.open_positions: Dict[str, float] = {}
        self.daily_pnl: float = 0.0
        self.signal_handlers: Dict[str, Callable] = {}
        self.last_reset = datetime.now()

    async def analyze(self, data: Dict[str, Any]) -> Optional[TradingSignal]:
        signal = data.get("signal")
        if not signal:
            return None

        if not self.validate_signal(signal):
            return None

        return signal

    def validate_signal(self, signal: TradingSignal) -> bool:
        if signal.strength < self.risk_config.min_signal_strength:
            return False

        if signal.confidence < self.risk_config.min_signal_confidence:
            return False

        if signal.is_buy():
            current_position = self.open_positions.get(signal.mint, 0.0)
            if current_position >= self.risk_config.max_position_sol:
                return False

            if len(self.open_positions) >= self.risk_config.max_positions:
                return False

        if self.daily_pnl <= -self.risk_config.max_daily_loss_sol:
            return False

        return True

    async def on_signal(self, signal: TradingSignal) -> None:
        print(f"[Executor] Signal: {signal.signal_type.value} {signal.mint} @ {signal.price}")

        try:
            if signal.is_buy():
                amount = min(
                    self.risk_config.max_position_sol,
                    self.risk_config.max_position_sol - self.open_positions.get(signal.mint, 0),
                )
                result = self.client.execute_buy(
                    mint=signal.mint,
                    sol_amount=amount,
                    slippage_bps=100,
                    priority_fee=5000,
                )

                if result.success:
                    self.open_positions[signal.mint] = self.open_positions.get(signal.mint, 0) + amount
                    print(f"[Executor] Buy success: {result.tx_hash}")
                else:
                    print(f"[Executor] Buy failed: {result.error}")

            elif signal.is_sell():
                current_position = self.open_positions.get(signal.mint, 0)
                if current_position <= 0:
                    print(f"[Executor] No position to sell")
                    return

                result = self.client.execute_sell(
                    mint=signal.mint,
                    token_amount=current_position * 1000000,
                    decimals=6,
                    slippage_bps=100,
                    priority_fee=5000,
                )

                if result.success:
                    pnl = current_position * (signal.price or 0) - current_position
                    self.daily_pnl += pnl
                    del self.open_positions[signal.mint]
                    print(f"[Executor] Sell success: {result.tx_hash}, PnL: {pnl:.4f} SOL")
                else:
                    print(f"[Executor] Sell failed: {result.error}")

        except Exception as e:
            print(f"[Executor] Error: {e}")

    def get_position(self, mint: str) -> float:
        return self.open_positions.get(mint, 0.0)

    def get_total_exposure(self) -> float:
        return sum(self.open_positions.values())

    def get_daily_pnl(self) -> float:
        return self.daily_pnl

    def reset_daily(self):
        self.daily_pnl = 0.0
        self.last_reset = datetime.now()


async def main():
    client = PumpApiClient(wallet_private_key="YOUR_PRIVATE_KEY")

    config = {
        "max_position_sol": 0.5,
        "max_daily_loss_sol": 2.0,
        "max_positions": 5,
        "min_confidence": 0.6,
        "min_strength": 0.4,
    }

    executor = SignalExecutorStrategy(client, config)

    print(f"Risk Config:")
    print(f"  Max Position: {executor.risk_config.max_position_sol} SOL")
    print(f"  Max Daily Loss: {executor.risk_config.max_daily_loss_sol} SOL")
    print(f"  Min Confidence: {executor.risk_config.min_signal_confidence}")


if __name__ == "__main__":
    asyncio.run(main())
