# Trading Strategies

This directory contains implemented trading strategies for use with pumpAPI.

## Strategy Categories

- **Arbitrage**: Exploit price differences between pools
- **Copy Trading**: Follow successful traders
- **Momentum**: Trade based on volume and trend
- **Mean Reversion**: Trade based on price reversion

## Usage

```python
from strategies.arbitrage.cross_pool import CrossPoolArbitrage

strategy = CrossPoolArbitrage(client, config)
await strategy.start()
```

## Configuration

Each strategy accepts a configuration dict:

```python
config = {
    "min_profit_bps": 50,      # Minimum profit threshold
    "max_position": 1.0,         # Max SOL per trade
    "check_interval": 1.0,       # Seconds between checks
}
```
