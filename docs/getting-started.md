# Getting Started with pumpAPI

This guide will walk you through setting up your environment and making your first API calls.

## Prerequisites

- Python 3.10 or higher
- A Solana wallet (optional for read-only operations)
- pumpAPI API key (for authenticated endpoints)

## Installation

### Using pip

```bash
pip install pumpapi-guide
```

### From source

```bash
git clone https://github.com/yourusername/pumpAPI-guide.git
cd pumpAPI-guide
pip install -e .
```

## Environment Setup

### 1. Get an API Key

Sign up at pumpportal.fun to get your API key.

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
PUMPAPI_API_KEY=your_api_key_here
PUMPAPI_RPC_URL=https://api.mainnet-beta.solana.com
```

### 3. (Optional) Wallet Setup

For trading operations, add your wallet:

```env
PUMPAPI_WALLET_PRIVATE_KEY=your_base58_private_key
```

**Warning**: Never commit your private key to version control!

## Your First API Call

### Initialize the Client

```python
from pumpapi import PumpApiClient

# Using API key authentication
client = PumpApiClient(api_key="your_api_key")

# Or using wallet-based authentication
client = PumpApiClient(
    wallet_private_key="your_base58_private_key"
)
```

### Query Token Data

```python
# Get token information by mint address
token = client.get_token("YOUR_TOKEN_MINT")
print(f"Name: {token.name}")
print(f"Symbol: {token.symbol}")
print(f"Decimals: {token.decimals}")

# Get recent tokens
recent = client.get_recent_tokens(limit=10)
for t in recent:
    print(f"{t.symbol}: {t.name}")
```

### Get Market Data

```python
# Get bonding curve state
curve = client.get_bonding_curve("YOUR_TOKEN_MINT")
print(f"Virtual SOL reserves: {curve.virtual_sol_reserves}")
print(f"Virtual Token reserves: {curve.virtual_token_reserves}")

# Get market cap
market_cap = client.get_market_cap("YOUR_TOKEN_MINT")
print(f"Market Cap: {market_cap.market_cap_sol} SOL")
print(f"Liquidity: {market_cap.liquidity_sol} SOL")
```

### Execute a Trade

```python
# Buy tokens
result = client.execute_buy(
    mint="YOUR_TOKEN_MINT",
    sol_amount=0.1,  # 0.1 SOL
    slippage_bps=100,  # 1% slippage
)

if result.success:
    print(f"Transaction successful: {result.tx_hash}")
else:
    print(f"Transaction failed: {result.error}")

# Sell tokens
result = client.execute_sell(
    mint="YOUR_TOKEN_MINT",
    token_amount=1000,  # Amount in tokens
    decimals=6,  # Token decimals
)
```

## Using WebSocket Streams

```python
import asyncio
from pumpapi import PumpApiStream

async def on_new_token(token):
    print(f"New token: {token.name} ({token.symbol})")
    print(f"Mint: {token.mint}")

async def on_trade(trade):
    print(f"Trade: {'BUY' if trade.is_buy else 'SELL'} {trade.token_amount} tokens")

async def main():
    stream = PumpApiStream(api_key="your_api_key")
    
    await stream.connect()
    await stream.subscribe_new_tokens(on_new_token)
    await stream.subscribe_trades("YOUR_TOKEN_MINT", on_trade)
    
    await stream.listen()

asyncio.run(main())
```

## Next Steps

- Check out [Examples](../examples/) for more code samples
- Read the [API Reference](./api-reference.md) for all available endpoints
- Explore [Tutorials](../tutorials/) for step-by-step guides
- Review [Security](./security.md) best practices
