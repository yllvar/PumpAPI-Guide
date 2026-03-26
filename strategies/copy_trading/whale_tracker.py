#!/usr/bin/env python3
"""
Whale Tracker

Track large traders (whales) and get notified of their activity.

This strategy:
1. Monitors specific wallet addresses for trades
2. Alerts when large trades occur
3. Optionally copies trades automatically
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta

from pumpapi_strategies import BaseStrategy, TradingSignal, SignalType
from pumpapi import PumpApiClient, PumpApiStream


@dataclass
class WhaleActivity:
    wallet: str
    mint: str
    is_buy: bool
    amount_sol: float
    timestamp: datetime


class WhaleTracker(BaseStrategy):
    def __init__(
        self,
        client: PumpApiClient,
        stream: Optional[PumpApiStream] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("WhaleTracker", config)

        self.client = client
        self.stream = stream
        self.whale_addresses = self.config.get("whales", [])
        self.min_whale_size = self.config.get("min_size_sol", 10.0)
        self.auto_copy = self.config.get("auto_copy", False)
        self.position_size = self.config.get("position_size", 0.1)

        self.activities: deque = deque(maxlen=1000)
        self.whale_balances: Dict[str, float] = {}

    async def analyze(self, data: Dict[str, Any]) -> Optional[TradingSignal]:
        activity = data.get("activity")
        if not activity:
            return None

        if activity.amount_sol < self.min_whale_size:
            return None

        self.activities.append(activity)

        signal_type = SignalType.BUY if activity.is_buy else SignalType.SELL
        strength = min(activity.amount_sol / 100, 1.0)

        return TradingSignal(
            mint=activity.mint,
            signal_type=signal_type,
            strength=strength,
            confidence=min(activity.amount_sol / 50, 1.0),
            reason=f"Whale {activity.wallet[:8]}... {activity.amount_sol:.2f} SOL {activity.is_buy and 'BUY' or 'SELL'}",
            metadata={
                "whale": activity.wallet,
                "amount_sol": activity.amount_sol,
            },
        )

    async def on_signal(self, signal: TradingSignal) -> None:
        print(f"[Whale Alert] {signal.reason}")

        if self.auto_copy and signal.is_buy():
            result = self.client.execute_buy(
                mint=signal.mint,
                sol_amount=self.position_size,
                slippage_bps=100,
                priority_fee=5000,
            )
            print(f"Copied buy: {result.success}, tx: {result.tx_hash}")

    async def run(self, client: PumpApiClient, stream: PumpApiStream):
        self.stream = stream

        async def on_trade(trade):
            wallet = trade.user.lower()
            if wallet in [w.lower() for w in self.whale_addresses]:
                activity = WhaleActivity(
                    wallet=wallet,
                    mint=trade.mint,
                    is_buy=trade.is_buy,
                    amount_sol=trade.sol_amount / 1e9,
                    timestamp=datetime.now(),
                )
                signal = await self.analyze({"activity": activity})
                if signal:
                    await self.on_signal(signal)

        await stream.connect()

        for mint in self.config.get("watch_tokens", []):
            await stream.subscribe_trades(mint, on_trade)

        print(f"Tracking {len(self.whale_addresses)} whales")
        await stream.listen()

    def get_whale_activity(
        self,
        mint: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> List[WhaleActivity]:
        activities = list(self.activities)

        if mint:
            activities = [a for a in activities if a.mint == mint]

        if since:
            activities = [a for a in activities if a.timestamp >= since]

        return activities

    def get_total_whale_buys(self, mint: str) -> float:
        return sum(
            a.amount_sol
            for a in self.activities
            if a.mint == mint and a.is_buy
        )

    def get_total_whale_sells(self, mint: str) -> float:
        return sum(
            a.amount_sol
            for a in self.activities
            if a.mint == mint and not a.is_buy
        )


async def main():
    client = PumpApiClient(wallet_private_key="YOUR_PRIVATE_KEY")
    stream = PumpApiStream(api_key="YOUR_API_KEY")

    config = {
        "whales": [
            "WALLET_ADDRESS_1",
            "WALLET_ADDRESS_2",
        ],
        "min_size_sol": 10.0,
        "auto_copy": False,
        "position_size": 0.1,
        "watch_tokens": ["TOKEN_MINT"],
    }

    strategy = WhaleTracker(client, stream, config)
    await strategy.start()
    await strategy.run(client, stream)


if __name__ == "__main__":
    asyncio.run(main())
