#!/usr/bin/env python3
"""
Example 05: Advanced Patterns

Advanced usage patterns combining multiple features.

Usage:
    python 05_advanced_patterns.py
"""

import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


async def async_example():
    from pumpapi import PumpApiClient, PumpApiStream

    client = PumpApiClient()
    stream = PumpApiStream()

    print("=== Advanced Async Patterns ===\n")

    print("1. Batch Token Queries")
    print("-" * 40)

    async def fetch_token_data(mints):
        results = []
        for mint in mints:
            try:
                token = await asyncio.to_thread(client.get_token, mint)
                mc = await asyncio.to_thread(client.get_market_cap, mint)
                results.append((token, mc))
            except Exception as e:
                print(f"Error fetching {mint}: {e}")
        return results

    mints = ["MINT1", "MINT2", "MINT3"]
    results = await fetch_token_data(mints)

    for token, mc in results:
        if token:
            print(f"{token.symbol}: {mc.market_cap_sol:.2f} SOL")

    print("\n2. Concurrent Streaming")
    print("-" * 40)

    async def handle_new_token(token):
        print(f"New: {token.symbol}")

    async def handle_trade(trade):
        print(f"Trade: {trade.is_buy}")

    await stream.connect()
    await stream.subscribe_new_tokens(handle_new_token)

    task = asyncio.create_task(stream.listen())

    await asyncio.sleep(5)
    stream.stop()
    await task

    print("\n3. Error Recovery")
    print("-" * 40)

    async def robust_fetch(mint, retries=3):
        for attempt in range(retries):
            try:
                return await asyncio.to_thread(client.get_token, mint)
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt)
                else:
                    raise
        return None

    try:
        token = await robust_fetch("TOKEN_MINT")
        print(f"Fetched: {token.name if token else 'Failed'}")
    except Exception as e:
        print(f"All retries failed: {e}")

    print("\n4. Rate Limiting")
    print("-" * 40)

    import time

    class RateLimiter:
        def __init__(self, max_calls, period):
            self.max_calls = max_calls
            self.period = period
            self.calls = []

        async def acquire(self):
            now = time.time()
            self.calls = [t for t in self.calls if t > now - self.period]

            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    self.calls = self.calls[1:]

            self.calls.append(time.time())

    limiter = RateLimiter(max_calls=10, period=1.0)

    print("Making 10 rate-limited requests...")
    for i in range(10):
        async with limiter:
            print(f"Request {i+1} at {time.time():.2f}")

    print("\n=== Complete ===")


def sync_example():
    from pumpapi import PumpApiClient, lamports_to_sol, sol_to_lamports
    from pumpapi.types import BuyRequest, SellRequest

    client = PumpApiClient()

    print("=== Advanced Sync Patterns ===\n")

    print("1. Utility Functions")
    print("-" * 40)

    lamports = 1_000_000_000
    print(f"{lamports} lamports = {lamports_to_sol(lamports)} SOL")

    sol = 0.5
    print(f"{sol} SOL = {sol_to_lamports(sol)} lamports")

    print("\n2. Request Models")
    print("-" * 40)

    buy_request = BuyRequest(
        mint="TOKEN_MINT",
        amount=sol_to_lamports(0.1),
        slippage_bps=100,
        priority_fee=1000,
    )
    print(f"Buy Request: {buy_request.model_dump_json(indent=2)}")

    print("\n3. Pagination")
    print("-" * 40)

    page = 0
    limit = 10
    while True:
        tokens = client.get_recent_tokens(limit=limit, offset=page * limit)
        if not tokens:
            break

        print(f"Page {page + 1}:")
        for t in tokens:
            print(f"  {t.symbol}: {t.market_cap:.2f} SOL")

        if len(tokens) < limit:
            break
        page += 1

        if page >= 3:
            print("  ... (limiting to 3 pages)")
            break

    print("\n4. Wallet Info")
    print("-" * 40)

    if client.wallet_address:
        print(f"Wallet: {client.wallet_address}")
    else:
        print("No wallet configured")

    print("\n=== Complete ===")


def main():
    import sys

    print("Select mode:")
    print("1. Async (recommended)")
    print("2. Sync")

    choice = input("> ").strip() or "1"

    if choice == "1":
        asyncio.run(async_example())
    else:
        sync_example()


if __name__ == "__main__":
    main()
