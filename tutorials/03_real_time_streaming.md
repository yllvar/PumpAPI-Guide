# Tutorial 03: Real-time Data Streaming

This guide covers WebSocket streaming for real-time market data.

## What You'll Learn

- Subscribe to new token events
- Track real-time trades
- Monitor market cap changes
- Watch bonding curve updates

## Step 1: Create the Streaming Script

```python
import asyncio
from pumpapi import PumpApiStream, PumpApiClient

async def on_new_token(token):
    print(f"\n[NEW TOKEN] {token.symbol}")
    print(f"  Name: {token.name}")
    print(f"  Mint: {token.mint}")
    print(f"  MC: {token.market_cap:.4f} SOL")

async def on_trade(trade):
    side = "BUY" if trade.is_buy else "SELL"
    print(f"\n[TRADE] {side}")
    print(f"  SOL: {trade.sol_amount / 1e9:.4f}")
    print(f"  Tokens: {trade.token_amount}")
    print(f"  Trader: {trade.user[:8]}...")

async def on_market_cap(mc):
    print(f"\n[MC UPDATE] {mc.market_cap_sol:.2f} SOL")

async def on_bonding_curve(curve):
    print(f"\n[CURVE UPDATE]")
    print(f"  Complete: {curve.complete}")
    if curve.complete:
        print("  >>> MIGRATED TO DEX <<<")

async def main():
    stream = PumpApiStream(api_key="YOUR_API_KEY")

    await stream.connect()
    print("Connected!\n")

    # Subscribe to new tokens
    await stream.subscribe_new_tokens(on_new_token)

    # Subscribe to specific token events
    token_mint = "YOUR_TOKEN_MINT"
    await stream.subscribe_trades(token_mint, on_trade)
    await stream.subscribe_market_cap(token_mint, on_market_cap)
    await stream.subscribe_bonding_curve(token_mint, on_bonding_curve)

    print("Streaming... Press Ctrl+C to stop")
    await stream.listen()

asyncio.run(main())
```

## Step 2: Run the Script

```bash
python my_stream.py
```

## Step 3: Understanding Subscriptions

### New Token Subscription

```python
await stream.subscribe_new_tokens(callback)
```

Receives all new Pump.fun tokens as they're created.

### Trade Subscription

```python
await stream.subscribe_trades(mint, callback)
```

Receives every trade for a specific token.

### Market Cap Subscription

```python
await stream.subscribe_market_cap(mint, callback)
```

Receives market cap updates.

### Bonding Curve Subscription

```python
await stream.subscribe_bonding_curve(mint, callback)
```

Receives bonding curve state changes.

## Step 4: Building a Token Monitor

```python
import asyncio
from datetime import datetime
from pumpapi import PumpApiStream

class TokenMonitor:
    def __init__(self):
        self.tokens_seen = set()
        self.stream = None

    async def on_new_token(self, token):
        if token.symbol not in self.tokens_seen:
            self.tokens_seen.add(token.symbol)
            print(f"New: {token.symbol} - {token.mint}")

            # Filter for potential gems
            if token.market_cap < 500:
                print(f">>> LOW CAP ALERT: {token.symbol} <<<")

    async def run(self):
        self.stream = PumpApiStream()
        await self.stream.connect()
        await self.stream.subscribe_new_tokens(self.on_new_token)
        await self.stream.listen()

asyncio.run(TokenMonitor().run())
```

## Step 5: Building a Trade Tracker

```python
import asyncio
from collections import defaultdict
from pumpapi import PumpApiStream

class TradeTracker:
    def __init__(self):
        self.volume = defaultdict(float)

    async def on_trade(self, trade):
        self.volume[trade.mint] += trade.sol_amount / 1e9
        print(f"Total volume for {trade.mint[:8]}: {self.volume[trade.mint]:.2f} SOL")

    async def run(self, mints):
        stream = PumpApiStream()
        await stream.connect()
        
        for mint in mints:
            await stream.subscribe_trades(mint, self.on_trade)
        
        await stream.listen()

mints = ["MINT1", "MINT2"]
asyncio.run(TradeTracker().run(mints))
```

## Common Issues

### Connection Drops

The library includes auto-reconnection. For manual handling:

```python
async def listen(self):
    while True:
        try:
            await stream.listen()
        except Exception as e:
            print(f"Disconnected: {e}")
            await asyncio.sleep(5)
            await stream.connect()
```

### Rate Limits

Implement backoff:

```python
async def on_trade(self, trade):
    await asyncio.sleep(0.1)  # Rate limit
    # process trade
```

## Next Steps

- [Tutorial 04: Build a Bot](04_build_bot.md) - Create an automated trading bot
- [Tutorial 05: Production](05_production.md) - Production best practices
