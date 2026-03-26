#!/usr/bin/env python3
"""
Triangle Arbitrage

Exploit price differences through multiple pools in a cycle.

Example: USDC -> SOL -> TOKEN -> USDC
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from pumpapi_strategies import BaseStrategy, TradingSignal, SignalType
from pumpapi import PumpApiClient


@dataclass
class TriangleOpportunity:
    route: List[str]
    profit_bps: float
    estimated_profit: float


class TriangleArbitrage(BaseStrategy):
    def __init__(
        self,
        client: PumpApiClient,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("TriangleArbitrage", config)

        self.client = client
        self.min_profit_bps = self.config.get("min_profit_bps", 30)
        self.base_amount = self.config.get("base_amount", 10.0)
        self.check_interval = self.config.get("check_interval", 5.0)

    async def analyze(self, data: Dict[str, Any]) -> Optional[TradingSignal]:
        token = data.get("mint")
        if not token:
            return None

        try:
            opportunity = await self.find_triangle_opportunity(token)
            if opportunity and opportunity.profit_bps >= self.min_profit_bps:
                return TradingSignal(
                    mint=token,
                    signal_type=SignalType.BUY,
                    strength=min(opportunity.profit_bps / 500, 1.0),
                    confidence=opportunity.profit_bps / 100,
                    reason=f"Triangle: {opportunity.route}, profit={opportunity.profit_bps:.1f}bps",
                    metadata={
                        "route": opportunity.route,
                        "profit_bps": opportunity.profit_bps,
                    },
                )
        except Exception as e:
            print(f"Error: {e}")

        return None

    async def find_triangle_opportunity(self, mint: str) -> Optional[TriangleOpportunity]:
        try:
            pump_price = self.client.get_token_price(mint)

            usdc_price = await self.get_pool_price("USDC", "SOL")
            token_price = await self.get_pool_price(mint, "SOL")

            if not usdc_price or not token_price:
                return None

            route = ["USDC", "SOL", mint, "USDC"]

            sol_per_usdc = 1 / usdc_price
            tokens_per_sol = 1 / token_price

            if pump_price < token_price:
                profit = (token_price - pump_price) / pump_price
                profit_bps = profit * 10000
            else:
                profit_bps = 0

            if profit_bps < self.min_profit_bps:
                return None

            return TriangleOpportunity(
                route=route,
                profit_bps=profit_bps,
                estimated_profit=self.base_amount * profit,
            )

        except Exception as e:
            print(f"Triangle check error: {e}")
            return None

    async def get_pool_price(self, token_a: str, token_b: str) -> Optional[float]:
        return 1.0

    async def on_signal(self, signal: TradingSignal) -> None:
        print(f"[Triangle Signal] {signal.reason}")

    async def run_loop(self, tokens: List[str]):
        while self.is_running:
            for token in tokens:
                signal = await self.analyze({"mint": token})
                if signal:
                    await self.on_signal(signal)

            await asyncio.sleep(self.check_interval)


async def main():
    client = PumpApiClient(wallet_private_key="YOUR_PRIVATE_KEY")

    config = {
        "min_profit_bps": 30,
        "base_amount": 10.0,
        "check_interval": 5.0,
    }

    strategy = TriangleArbitrage(client, config)
    tokens = ["TOKEN1", "TOKEN2"]

    await strategy.start()
    await strategy.run_loop(tokens)


if __name__ == "__main__":
    asyncio.run(main())
