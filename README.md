# pumpAPI Guide

Comprehensive guide and framework for building trading bots on Solana using pumpAPI.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready Python library and guide for interacting with Pump.fun tokens on Solana. Built for quant traders, developers, and researchers building automated trading systems.

## Features

- **REST API Client** - Full wrapper for pumpAPI endpoints
- **WebSocket Streams** - Real-time data for new tokens, trades, and market data
- **Dual Auth** - API key and wallet-based authentication
- **Strategy Framework** - Base classes for building trading strategies
- **Progressive Examples** - From basic to advanced usage
- **Complete Documentation** - Getting started to production

## Installation

```bash
pip install pumpapi-guide
```

Or from source:

```bash
git clone https://github.com/yourusername/pumpAPI-guide.git
cd pumpAPI-guide
pip install -e .
```

## Quick Start

```python
from pumpapi import PumpApiClient

client = PumpApiClient(api_key="your_api_key")

# Query token data
token = client.get_token("YOUR_TOKEN_MINT")
print(f"Token: {token.name} ({token.symbol})")

# Execute a trade
result = client.execute_buy(
    mint="YOUR_TOKEN_MINT",
    sol_amount=0.1,
)
```

## Documentation

- [Getting Started](docs/getting-started.md) - Setup and first API calls
- [API Reference](docs/api-reference.md) - Complete API documentation
- [Architecture](docs/architecture.md) - System design overview
- [Infrastructure](docs/infrastructure.md) - RPC and server setup
- [Security](docs/security.md) - Best practices

## Examples

Progressive examples from basic to advanced:

| File | Description |
|------|-------------|
| `examples/01_basic_buy_sell.py` | Your first API call |
| `examples/02_data_stream.py` | WebSocket data streaming |
| `examples/03_lightning_trade.py` | Fast execution |
| `examples/04_token_monitor.py` | New token detection |
| `examples/05_advanced_patterns.py` | Advanced patterns |

## Strategies

Implemented trading strategies:

- **Arbitrage**: Cross-pool and triangle arbitrage
- **Copy Trading**: Whale tracking and signal execution
- **Momentum**: Volume spikes and migration plays
- **Mean Reversion**: Bonding curve reversion

See [strategies/](strategies/) for implementations.

## Tutorials

Step-by-step guides:

1. [Setup](tutorials/01_setup.md) - Environment configuration
2. [First Trade](tutorials/02_first_trade.md) - Execute your first trade
3. [Real-time Streaming](tutorials/03_real_time_streaming.md) - WebSocket data
4. [Build a Bot](tutorials/04_build_bot.md) - Create a trading bot
5. [Production](tutorials/05_production.md) - Production best practices

## Project Structure

```
pumpAPI-guide/
├── README.md
├── docs/                    # Documentation
├── examples/                # Code examples
├── strategies/              # Trading strategies
├── tutorials/               # Step-by-step guides
├── src/
│   ├── pumpapi/            # Core library
│   └── pumpapi_strategies/ # Strategy framework
└── tests/                  # Test suite
```

## Requirements

- Python 3.10+
- pip or uv

### Dependencies

- `httpx` - HTTP client
- `solana` - Solana SDK
- `solders` - Solana primitives
- `websockets` - WebSocket client
- `python-dotenv` - Environment variables
- `pydantic` - Data validation

## Configuration

Copy `.env.example` to `.env`:

```env
PUMPAPI_API_KEY=your_api_key_here
PUMPAPI_WALLET_PRIVATE_KEY=your_private_key  # optional
PUMPAPI_RPC_URL=https://api.mainnet-beta.solana.com
```

## Support

- GitHub Issues - Bug reports and feature requests
- Documentation - Full API docs in `/docs`

## License

MIT License - see [LICENSE](LICENSE) for details.
