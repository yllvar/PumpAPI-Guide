#!/usr/bin/env python3
"""
Example 01: Basic Buy and Sell

Your first pumpAPI calls - query token data and execute basic trades.

Usage:
    python 01_basic_buy_sell.py
"""

from dotenv import load_dotenv

load_dotenv()


def main():
    from pumpapi import PumpApiClient

    client = PumpApiClient()

    print("=== pumpAPI Basic Example ===\n")

    token_mint = "YOUR_TOKEN_MINT_HERE"

    print("1. Get Token Info")
    print("-" * 40)
    try:
        token = client.get_token(token_mint)
        print(f"Name:    {token.name}")
        print(f"Symbol:  {token.symbol}")
        print(f"Mint:    {token.mint}")
        print(f"Decimals: {token.decimals}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n2. Get Recent Tokens")
    print("-" * 40)
    try:
        recent = client.get_recent_tokens(limit=5)
        for t in recent:
            print(f"{t.symbol:10} {t.name:30} MC: {t.market_cap:.2f} SOL")
    except Exception as e:
        print(f"Error: {e}")

    print("\n3. Get Bonding Curve State")
    print("-" * 40)
    try:
        curve = client.get_bonding_curve(token_mint)
        print(f"Virtual SOL:     {curve.virtual_sol_reserves}")
        print(f"Virtual Tokens: {curve.virtual_token_reserves}")
        print(f"Complete:       {curve.complete}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n4. Get Market Cap")
    print("-" * 40)
    try:
        mc = client.get_market_cap(token_mint)
        print(f"Market Cap: {mc.market_cap_sol:.2f} SOL")
        print(f"Liquidity:  {mc.liquidity_sol:.2f} SOL")
        print(f"Holders:    {mc.holder_count}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n5. Get Token Price")
    print("-" * 40)
    try:
        price = client.get_token_price(token_mint)
        print(f"Price: {price:.10f} SOL")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== Complete ===")


if __name__ == "__main__":
    main()
