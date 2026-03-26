#!/usr/bin/env python3
"""
Migration Strategy

Trade in anticipation of Pump.fun token migration to Raydium.

This strategy:
1. Monitors tokens approaching migration threshold
2. Positions before migration events
3. Exits after migration completes
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from pumpapi_strategies import BaseStrategy, TradingSignal, SignalType
from pumpapi import PumpApiClient, PumpApiStream


@dataclass
class MigrationState:
    mint: str
    market_cap: float
    bond_complete: bool
    last_update: datetime


class MigrationStrategy(BaseStrategy):
    def __init__(
        self,
        client: PumpApiClient,
        stream: Optional[PumpApiStream] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("Migration", config)

        self.client = client
        self.stream = stream

        self.migration_cap = self.config.get("migration_cap", 25000.0)
        self.pre_migration_cap = self.config.get("pre_migration_cap", 20000.0)
        self.position_size = self.config.get("position_size", 0.2)
        self.check_interval = self.config.get("check_interval", 30.0)

        self.monitored_tokens: Dict[str, MigrationState] = {}
        self.positions: Dict[str, bool] = {}

    async def analyze(self, data: Dict[str, Any]) -> Optional[TradingSignal]:
        mint = data.get("mint")
        state = data.get("state")

        if not mint or not state:
            return None

        self.monitored_tokens[mint] = state

        if not state.bond_complete and not self.positions.get(mint, False):
            if state.market_cap >= self.pre_migration_cap:
                return TradingSignal(
                    mint=mint,
                    signal_type=SignalType.BUY,
                    strength=0.8,
                    price=state.market_cap,
                    confidence=0.7,
                    reason=f"Pre-migration setup: MC {state.market_cap:.0f} SOL",
                    metadata={"market_cap": state.market_cap},
                )

        elif state.bond_complete and self.positions.get(mint, False):
            if state.market_cap >= self.migration_cap:
                return TradingSignal(
                    mint=mint,
                    signal_type=SignalType.SELL,
                    strength=1.0,
                    price=state.market_cap,
                    confidence=0.9,
                    reason=f"Migration complete: MC {state.market_cap:.0f} SOL",
                    metadata={"market_cap": state.market_cap},
                )

        return None

    async def on_signal(self, signal: TradingSignal) -> None:
        print(f"[Migration Signal] {signal.reason}")

        if signal.is_buy():
            result = self.client.execute_buy(
                mint=signal.mint,
                sol_amount=self.position_size,
                slippage_bps=200,
                priority_fee=5000,
            )

            if result.success:
                self.positions[signal.mint] = True
                print(f"Bought position: {result.tx_hash}")

        elif signal.is_sell():
            result = self.client.execute_sell(
                mint=signal.mint,
                token_amount=self.position_size * 1000000,
                decimals=6,
                slippage_bps=200,
                priority_fee=5000,
            )

            if result.success:
                self.positions[signal.mint] = False
                print(f"Sold position: {result.tx_hash}")

    async def check_token(self, mint: str) -> Optional[MigrationState]:
        try:
            mc = self.client.get_market_cap(mint)
            curve = self.client.get_bonding_curve(mint)

            return MigrationState(
                mint=mint,
                market_cap=mc.market_cap_sol,
                bond_complete=curve.complete,
                last_update=datetime.now(),
            )
        except Exception as e:
            print(f"Error checking {mint}: {e}")
            return None

    async def run_loop(self, tokens: List[str]):
        while self.is_running:
            for mint in tokens:
                state = await self.check_token(mint)
                if state:
                    signal = await self.analyze({"mint": mint, "state": state})
                    if signal:
                        await self.on_signal(signal)

            await asyncio.sleep(self.check_interval)

    async def run_stream(self, tokens: List[str]):
        if not self.stream:
            self.stream = PumpApiStream()
            await self.stream.connect()

        async def on_bonding_curve(curve):
            mint = curve.mint
            if mint in self.monitored_tokens:
                state = self.monitored_tokens[mint]
                state.bond_complete = curve.complete
                state.last_update = datetime.now()

                signal = await self.analyze({"mint": mint, "state": state})
                if signal:
                    await self.on_signal(signal)

        for mint in tokens:
            await self.stream.subscribe_bonding_curve(mint, on_bonding_curve)

        await self.stream.listen()


async def main():
    client = PumpApiClient(wallet_private_key="YOUR_PRIVATE_KEY")

    config = {
        "migration_cap": 25000.0,
        "pre_migration_cap": 20000.0,
        "position_size": 0.2,
        "check_interval": 30.0,
    }

    strategy = MigrationStrategy(client, config)

    tokens = ["TOKEN_MINT_1", "TOKEN_MINT_2"]

    await strategy.start()
    await strategy.run_loop(tokens)


if __name__ == "__main__":
    asyncio.run(main())
