#!/usr/bin/env python3
"""
Example 02: Data Streaming

Real-time WebSocket data streaming for tokens, trades, and market data.

Usage:
    python 02_data_stream.py
"""

import asyncio
import signal
from dotenv import load_dotenv

load_dotenv()


def main():
    from pumpapi import PumpApiStream, PumpApiClient

    streaming = True

    async def handle_new_token(token):
        print(f"\n[NEW TOKEN]")
        print(f"  Name:   {token.name}")
        print(f"  Symbol: {token.symbol}")
        print(f"  Mint:   {token.mint}")
        print(f"  MC:     {token.market_cap:.2f} SOL")
        print(f"  Time:   {token.timestamp}")

    async def handle_trade(trade):
        side = "BUY" if trade.is_buy else "SELL"
        print(f"\n[TRADE] {side}")
        print(f"  Mint:       {trade.mint}")
        print(f"  SOL:        {trade.sol_amount / 1e9:.4f}")
        print(f"  Tokens:    {trade.token_amount}")
        print(f"  Trader:     {trade.user[:8]}...")
        print(f"  Tx:         {trade.tx_hash[:32]}...")

    async def handle_market_cap(mc):
        print(f"\n[MARKET CAP UPDATE]")
        print(f"  Mint:      {mc.mint}")
        print(f"  Market Cap: {mc.market_cap_sol:.2f} SOL")
        print(f"  FDV:        {mc.fdv_sol:.2f} SOL")
        print(f"  Liquidity:  {mc.liquidity_sol:.2f} SOL")

    async def handle_bonding_curve(curve):
        print(f"\n[BONDING CURVE UPDATE]")
        print(f"  Mint:     {curve.mint}")
        print(f"  Complete: {curve.complete}")
        if curve.complete:
            print(f"  >>> TOKEN MIGRATED TO DEX <<<")

    async def run_stream():
        stream = PumpApiStream()

        print("=== pumpAPI Data Streaming Example ===\n")
        print("Connecting to WebSocket...")

        await stream.connect()

        print("Connected!\n")
        print("Subscribing to events...")

        await stream.subscribe_new_tokens(handle_new_token)

        test_mint = "YOUR_TOKEN_MINT_HERE"
        if test_mint != "YOUR_TOKEN_MINT_HERE":
            await stream.subscribe_trades(test_mint, handle_trade)
            await stream.subscribe_market_cap(test_mint, handle_market_cap)
            await stream.subscribe_bonding_curve(test_mint, handle_bonding_curve)
        else:
            print("Note: Set test_mint for trade/market cap subscriptions")

        print("Listening for events... (Press Ctrl+C to stop)\n")

        try:
            await stream.listen()
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            await stream.disconnect()

    def signal_handler(sig, frame):
        print("\nReceived interrupt signal")
        streaming = False

    signal.signal(signal.SIGINT, signal_handler)

    asyncio.run(run_stream())


if __name__ == "__main__":
    main()
