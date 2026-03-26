#!/usr/bin/env python3
"""
Example 03: Lightning Trade

Fast execution example with priority fees and optimized settings.

Usage:
    python 03_lightning_trade.py
"""

import time
from dotenv import load_dotenv

load_dotenv()


def main():
    from pumpapi import PumpApiClient, sol_to_lamports

    client = PumpApiClient()

    print("=== pumpAPI Lightning Trade Example ===\n")

    token_mint = "YOUR_TOKEN_MINT_HERE"
    trade_amount_sol = 0.1

    print(f"Preparing lightning trade...")
    print(f"  Mint: {token_mint}")
    print(f"  Amount: {trade_amount_sol} SOL")

    print("\n1. Get current state")
    print("-" * 40)
    start = time.perf_counter()

    try:
        curve = client.get_bonding_curve(token_mint)
        price = client.get_token_price(token_mint)
        mc = client.get_market_cap(token_mint)

        print(f"  Price:         {price:.8f} SOL")
        print(f"  Market Cap:   {mc.market_cap_sol:.2f} SOL")
        print(f"  Complete:     {curve.complete}")
        print(f"  Query time:   {(time.perf_counter() - start)*1000:.1f}ms")
    except Exception as e:
        print(f"Error getting state: {e}")
        return

    print("\n2. Execute with priority fee")
    print("-" * 40)

    result = client.execute_buy(
        mint=token_mint,
        sol_amount=trade_amount_sol,
        slippage_bps=50,
        priority_fee=5000,
    )

    total_time = time.perf_counter() - start

    if result.success:
        print(f"  Status:        SUCCESS")
        print(f"  Tx Hash:       {result.tx_hash}")
        print(f"  Total time:    {total_time*1000:.1f}ms")
    else:
        print(f"  Status:        FAILED")
        print(f"  Error:         {result.error}")
        print(f"  Total time:    {total_time*1000:.1f}ms")

    print("\n3. Quick sell example")
    print("-" * 40)

    result = client.execute_sell(
        mint=token_mint,
        token_amount=1000,
        decimals=6,
        slippage_bps=100,
        priority_fee=5000,
    )

    if result.success:
        print(f"  Status:        SUCCESS")
        print(f"  Tx Hash:       {result.tx_hash}")
    else:
        print(f"  Status:        FAILED")
        print(f"  Error:         {result.error}")

    print("\n=== Complete ===")


if __name__ == "__main__":
    main()
