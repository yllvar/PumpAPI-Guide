# pumpAPI Guide - Documentation

Welcome to the pumpAPI Guide documentation. This repository provides comprehensive resources for building trading bots and strategies on Solana using the pumpAPI.

## Quick Links

- [Getting Started](./getting-started.md)
- [API Reference](./api-reference.md)
- [Architecture](./architecture.md)
- [Infrastructure](./infrastructure.md)
- [Security](./security.md)

## Overview

pumpAPI is a powerful API for interacting with Pump.fun tokens on Solana. This guide covers:

- **API Client**: Python client for REST API interactions
- **WebSocket Streams**: Real-time data streaming
- **Trading Strategies**: Implemented strategies for various market conditions
- **Examples**: Progressive code examples from basic to advanced

## Installation

```bash
pip install pumpapi-guide
```

Or install from source:

```bash
git clone https://github.com/yourusername/pumpAPI-guide.git
cd pumpAPI-guide
pip install -e .
```

## Quick Start

```python
from pumpapi import PumpApiClient

# Initialize with API key
client = PumpApiClient(api_key="your_api_key")

# Get token info
token = client.get_token("YOUR_TOKEN_MINT")
print(f"Token: {token.name} ({token.symbol})")

# Execute a buy
result = client.execute_buy(
    mint="YOUR_TOKEN_MINT",
    sol_amount=0.1,  # 0.1 SOL
)
```

## Examples

See the [examples](../examples/) directory for progressive code examples:

1. `01_basic_buy_sell.py` - Your first API call
2. `02_data_stream.py` - WebSocket data streaming
3. `03_lightning_trade.py` - Fast execution
4. `04_token_monitor.py` - New token detection
5. `05_advanced_patterns.py` - Advanced patterns

## Strategies

Explore [strategies](../strategies/) for implemented trading strategies:

- **Arbitrage**: Cross-pool and triangle arbitrage
- **Copy Trading**: Whale tracking and signal execution
- **Momentum**: Volume spikes and migration plays
- **Mean Reversion**: Bonding curve reversion

## Tutorials

Follow our step-by-step [tutorials](../tutorials/):

1. [Setup](./tutorials/01_setup.md) - Environment setup
2. [First Trade](./tutorials/02_first_trade.md) - Execute your first trade
3. [Real-time Streaming](./tutorials/03_real_time_streaming.md) - WebSocket data
4. [Build a Bot](./tutorials/04_build_bot.md) - Create a trading bot
5. [Production](./tutorials/05_production.md) - Production best practices

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Check this documentation hub
