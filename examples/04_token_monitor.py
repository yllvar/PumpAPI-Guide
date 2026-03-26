#!/usr/bin/env python3
"""
Example 04: Token Monitor

Monitor new tokens and detect trading opportunities.

Usage:
    python 04_token_monitor.py
"""

import asyncio
import signal
from datetime import datetime
from collections import deque
from dotenv import load_dotenv

load_dotenv()


class TokenMonitor:
    def __init__(self, history_size: int = 100):
        self.new_tokens = deque(maxlen=history_size)
        self.monitored_mints = set()
        self.running = False

    async def on_new_token(self, token):
        self.new_tokens.append(token)
        self.monitored_mints.add(token.mint)

        print(f"\n{'='*50}")
        print(f"NEW TOKEN DETECTED!")
        print(f"{'='*50}")
        print(f"Name:     {token.name}")
        print(f"Symbol:   {token.symbol}")
        print(f"Mint:     {token.mint}")
        print(f"Market Cap: {token.market_cap:.4f} SOL")
        print(f"Liquidity:  {token.liquidity:.4f} SOL")
        print(f"Timestamp:  {token.timestamp}")
        print(f"{'='*50}\n")

        await self.analyze_opportunity(token)

    async def analyze_opportunity(self, token):
        if token.market_cap < 100:
            print(f"[OPPORTUNITY] Low market cap - potential early gem")
        elif token.market_cap < 1000:
            print(f"[OPPORTUNITY] Medium market cap - established token")
        else:
            print(f"[INFO] High market cap token")

    async def on_trade(self, trade):
        mint = trade.mint
        side = "BUY" if trade.is_buy else "SELL"
        sol_amount = trade.sol_amount / 1_000_000_000

        print(f"[TRADE] {side:4} | {sol_amount:8.4f} SOL | {mint[:8]}... ")

        if sol_amount > 10:
            print(f"       ^ LARGE TRADE DETECTED!")


async def main():
    from pumpapi import PumpApiStream

    monitor = TokenMonitor()

    print("=== pumpAPI Token Monitor ===\n")
    print("Monitoring for new tokens...\n")

    stream = PumpApiStream()
    await stream.connect()

    await stream.subscribe_new_tokens(monitor.on_new_token)

    monitor.running = True

    print("Streaming... (Press Ctrl+C to stop)\n")

    try:
        await stream.listen()
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        await stream.disconnect()

    print(f"\nTotal tokens detected: {len(monitor.new_tokens)}")
    print(f"Unique mints: {len(monitor.monitored_mints)}")


def run():
    import sys
    if sys.platform != "win32":
        import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExited")


if __name__ == "__main__":
    run()
