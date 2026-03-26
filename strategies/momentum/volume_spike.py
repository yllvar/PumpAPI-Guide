#!/usr/bin/env python3
"""
Volume Spike Strategy

Trade based on sudden volume increases.

This strategy:
1. Monitors token volumes in real-time
2. Detects unusual volume spikes
3. Generates signals for momentum trades
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import deque, defaultdict
from datetime import datetime

from pumpapi_strategies import BaseStrategy, TradingSignal, SignalType
from pumpapi import PumpApiClient, PumpApiStream


@dataclass
class VolumeData:
    mint: str
    volume_sol: float
    buy_volume_sol: float
    sell_volume_sol: float
    trade_count: int
    timestamp: datetime


class VolumeSpikeStrategy(BaseStrategy):
    def __init__(
        self,
        client: PumpApiClient,
        stream: Optional[PumpApiStream] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__("VolumeSpike", config)

        self.client = client
        self.stream = stream

        self.spike_threshold = self.config.get("spike_threshold", 5.0)
        self.lookback_minutes = self.config.get("lookback", 5)
        self.min_volume = self.config.get("min_volume", 10.0)
        self.position_size = self.config.get("position_size", 0.1)

        self.volume_history: deque = deque(maxlen=1000)
        self.token_volumes: Dict[str, List[float]] = defaultdict(list)
        self.current_volumes: Dict[str, VolumeData] = {}

    async def analyze(self, data: Dict[str, Any]) -> Optional[TradingSignal]:
        volume_data = data.get("volume_data")
        if not volume_data:
            return None

        mint = volume_data.mint
        current_volume = volume_data.volume_sol

        if current_volume < self.min_volume:
            return None

        avg_volume = self.get_average_volume(mint)
        if avg_volume == 0:
            return None

        spike_ratio = current_volume / avg_volume

        if spike_ratio >= self.spike_threshold:
            signal_type = SignalType.BUY if volume_data.buy_volume_sol > volume_data.sell_volume_sol else SignalType.HOLD

            if signal_type == SignalType.BUY:
                return TradingSignal(
                    mint=mint,
                    signal_type=signal_type,
                    strength=min(spike_ratio / 10, 1.0),
                    price=volume_data.volume_sol / volume_data.trade_count if volume_data.trade_count > 0 else 0,
                    volume=current_volume,
                    confidence=min(spike_ratio / 5, 1.0),
                    reason=f"Volume spike: {spike_ratio:.1f}x average (current: {current_volume:.1f}, avg: {avg_volume:.1f})",
                    metadata={
                        "spike_ratio": spike_ratio,
                        "current_volume": current_volume,
                        "avg_volume": avg_volume,
                        "buy_volume": volume_data.buy_volume_sol,
                        "sell_volume": volume_data.sell_volume_sol,
                    },
                )

        return None

    def get_average_volume(self, mint: str) -> float:
        volumes = self.token_volumes.get(mint, [])
        if not volumes:
            return 0.0
        return sum(volumes) / len(volumes)

    async def on_signal(self, signal: TradingSignal) -> None:
        print(f"[Volume Spike] {signal.reason}")

        result = self.client.execute_buy(
            mint=signal.mint,
            sol_amount=self.position_size,
            slippage_bps=100,
            priority_fee=5000,
        )
        print(f"Buy result: {result.success}, tx: {result.tx_hash}")

    def process_trade(self, trade) -> VolumeData:
        mint = trade.mint
        sol_amount = trade.sol_amount / 1e9

        if mint not in self.current_volumes:
            self.current_volumes[mint] = VolumeData(
                mint=mint,
                volume_sol=0,
                buy_volume_sol=0,
                sell_volume_sol=0,
                trade_count=0,
                timestamp=datetime.now(),
            )

        vol = self.current_volumes[mint]
        vol.volume_sol += sol_amount
        vol.trade_count += 1

        if trade.is_buy:
            vol.buy_volume_sol += sol_amount
        else:
            vol.sell_volume_sol += sol_amount

        self.token_volumes[mint].append(sol_amount)
        self.volume_history.append(vol)

        return vol

    async def run(self, tokens: List[str]):
        if not self.stream:
            self.stream = PumpApiStream()
            await self.stream.connect()

        async def on_trade(trade):
            vol_data = self.process_trade(trade)
            signal = await self.analyze({"volume_data": vol_data})
            if signal:
                await self.on_signal(signal)

        for mint in tokens:
            await self.stream.subscribe_trades(mint, on_trade)

        print(f"Monitoring {len(tokens)} tokens for volume spikes")
        await self.stream.listen()


async def main():
    client = PumpApiClient(wallet_private_key="YOUR_PRIVATE_KEY")
    stream = PumpApiStream()

    config = {
        "spike_threshold": 5.0,
        "lookback": 5,
        "min_volume": 10.0,
        "position_size": 0.1,
    }

    strategy = VolumeSpikeStrategy(client, stream, config)

    tokens = ["TOKEN_MINT_1", "TOKEN_MINT_2"]
    await strategy.start()
    await strategy.run(tokens)


if __name__ == "__main__":
    asyncio.run(main())
