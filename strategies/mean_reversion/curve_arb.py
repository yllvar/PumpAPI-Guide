#!/usr/bin/env python3
"""
Bonding Curve Reversion

Trade based on bonding curve price reversion.

This strategy:
1. Monitors the virtual reserves of a token
2. Detects when price deviates from fair value
3. Trades on reversion to mean
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from pumpapi_strategies import BaseStrategy, TradingSignal, SignalType
from pumpapi import PumpApiClient, PumpApiStream


@dataclass
class CurveState:
    mint: str
    virtual_sol: int
    virtual_tokens: int
    price: float
    timestamp: datetime


class CurveReversionStrategy(BaseStrategy):
    def __init__(
        self,
        client: PumpApiClient,
        stream: Optional[PumpApiStream] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("CurveReversion", config)

        self.client = client
        self.stream = stream

        self.reversion_threshold = self.config.get("reversion_threshold", 0.2)
        self.lookback_periods = self.config.get("lookback", 10)
        self.position_size = self.config.get("position_size", 0.1)
        self.check_interval = self.config.get("check_interval", 10.0)

        self.price_history: Dict[str, List[float]] = {}
        self.current_prices: Dict[str, float] = {}

    async def analyze(self, data: Dict[str, Any]) -> Optional[TradingSignal]:
        curve_state = data.get("curve_state")
        if not curve_state:
            return None

        mint = curve_state.mint
        current_price = curve_state.price

        if mint not in self.price_history:
            self.price_history[mint] = []

        self.price_history[mint].append(current_price)
        self.current_prices[mint] = current_price

        if len(self.price_history[mint]) < 3:
            return None

        avg_price = sum(self.price_history[mint]) / len(self.price_history[mint])
        deviation = (current_price - avg_price) / avg_price if avg_price > 0 else 0

        if abs(deviation) >= self.reversion_threshold:
            if deviation < 0:
                signal_type = SignalType.BUY
                reason = f"Price below average: {deviation*100:.1f}% deviation"
            else:
                signal_type = SignalType.SELL
                reason = f"Price above average: {deviation*100:.1f}% deviation"

            return TradingSignal(
                mint=mint,
                signal_type=signal_type,
                strength=min(abs(deviation) * 2, 1.0),
                price=current_price,
                confidence=abs(deviation),
                reason=reason,
                metadata={
                    "current_price": current_price,
                    "avg_price": avg_price,
                    "deviation": deviation,
                },
            )

        return None

    async def on_signal(self, signal: TradingSignal) -> None:
        print(f"[Curve Reversion] {signal.reason}")

        if signal.is_buy():
            result = self.client.execute_buy(
                mint=signal.mint,
                sol_amount=self.position_size,
                slippage_bps=100,
                priority_fee=5000,
            )
            print(f"Buy result: {result.success}, tx: {result.tx_hash}")

        elif signal.is_sell():
            result = self.client.execute_sell(
                mint=signal.mint,
                token_amount=self.position_size * 1000000,
                decimals=6,
                slippage_bps=100,
                priority_fee=5000,
            )
            print(f"Sell result: {result.success}, tx: {result.tx_hash}")

    async def get_curve_state(self, mint: str) -> Optional[CurveState]:
        try:
            curve = self.client.get_bonding_curve(mint)

            if curve.virtual_token_reserves == 0:
                return None

            price = curve.virtual_sol_reserves / curve.virtual_token_reserves

            return CurveState(
                mint=mint,
                virtual_sol=curve.virtual_sol_reserves,
                virtual_tokens=curve.virtual_token_reserves,
                price=price,
                timestamp=datetime.now(),
            )
        except Exception as e:
            print(f"Error getting curve state: {e}")
            return None

    async def run_loop(self, tokens: List[str]):
        while self.is_running:
            for mint in tokens:
                state = await self.get_curve_state(mint)
                if state:
                    signal = await self.analyze({"curve_state": state})
                    if signal:
                        await self.on_signal(signal)

            await asyncio.sleep(self.check_interval)

    async def run_stream(self, tokens: List[str]):
        if not self.stream:
            self.stream = PumpApiStream()
            await self.stream.connect()

        async def on_bonding_curve(curve):
            mint = curve.mint
            if curve.virtual_token_reserves > 0:
                price = curve.virtual_sol_reserves / curve.virtual_token_reserves
                state = CurveState(
                    mint=mint,
                    virtual_sol=curve.virtual_sol_reserves,
                    virtual_tokens=curve.virtual_token_reserves,
                    price=price,
                    timestamp=datetime.now(),
                )
                signal = await self.analyze({"curve_state": state})
                if signal:
                    await self.on_signal(signal)

        for mint in tokens:
            await self.stream.subscribe_bonding_curve(mint, on_bonding_curve)

        print(f"Monitoring {len(tokens)} tokens for curve reversion")
        await self.stream.listen()


async def main():
    client = PumpApiClient(wallet_private_key="YOUR_PRIVATE_KEY")

    config = {
        "reversion_threshold": 0.2,
        "lookback": 10,
        "position_size": 0.1,
        "check_interval": 10.0,
    }

    strategy = CurveReversionStrategy(client, config)

    tokens = ["TOKEN_MINT_1", "TOKEN_MINT_2"]

    await strategy.start()
    await strategy.run_loop(tokens)


if __name__ == "__main__":
    asyncio.run(main())
