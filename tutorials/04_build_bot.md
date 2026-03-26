# Tutorial 04: Building a Trading Bot

This guide walks through building an automated trading bot using pumpAPI.

## What You'll Build

A simple trading bot that:
- Monitors new tokens
- Applies filters
- Executes trades automatically

## Step 1: Define Your Strategy

First, decide what your bot will do:

```python
FILTERS = {
    "min_market_cap": 100,      # Minimum MC in SOL
    "max_market_cap": 10000,    # Maximum MC
    "min_liquidity": 10,        # Minimum liquidity
    "max_position": 0.1,        # Max SOL per trade
    "slippage_bps": 100,        # Slippage tolerance
}
```

## Step 2: Create the Bot Class

```python
import asyncio
from pumpapi import PumpApiClient, PumpApiStream
from pumpapi_strategies import TradingSignal, SignalType

class SimpleBot:
    def __init__(self, client: PumpApiClient, config: dict):
        self.client = client
        self.config = config
        self.stream = None
        self.positions = {}

    def should_trade(self, token) -> bool:
        if token.market_cap < self.config["min_market_cap"]:
            return False
        if token.market_cap > self.config["max_market_cap"]:
            return False
        if token.liquidity < self.config["min_liquidity"]:
            return False
        return True

    async def on_new_token(self, token):
        print(f"New token: {token.symbol}")

        if not self.should_trade(token):
            print(f"  Skipped: doesn't meet filters")
            return

        print(f"  >>> TRADING OPPORTUNITY <<<")

        result = self.client.execute_buy(
            mint=token.mint,
            sol_amount=self.config["max_position"],
            slippage_bps=self.config["slippage_bps"],
            priority_fee=5000,
        )

        if result.success:
            self.positions[token.mint] = token.symbol
            print(f"  BOUGHT! TX: {result.tx_hash}")
        else:
            print(f"  FAILED: {result.error}")

    async def run(self):
        self.stream = PumpApiStream(api_key=self.client.config.api_key)
        await self.stream.connect()
        
        await self.stream.subscribe_new_tokens(self.on_new_token)
        
        print("Bot running... Press Ctrl+C to stop")
        await self.stream.listen()
```

## Step 3: Run the Bot

```python
def main():
    client = PumpApiClient(wallet_private_key="YOUR_PRIVATE_KEY")

    config = {
        "min_market_cap": 500,
        "max_market_cap": 5000,
        "min_liquidity": 50,
        "max_position": 0.1,
        "slippage_bps": 100,
    }

    bot = SimpleBot(client, config)
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()
```

## Step 4: Add More Features

### Position Management

```python
class ManagedBot(SimpleBot):
    async def on_new_token(self, token):
        await super().on_new_token(token)

    async def check_exit(self, token):
        if token.mint in self.positions:
            mc = self.client.get_market_cap(token.mint)
            
            if mc.market_cap >= self.config["max_market_cap"]:
                result = self.client.execute_sell(
                    mint=token.mint,
                    token_amount=self.config["max_position"] * 1000000,
                    decimals=6,
                )
                print(f"Exit: {result.tx_hash}")
```

### Multiple Strategies

```python
class MultiStrategyBot:
    def __init__(self):
        self.strategies = []

    def add_strategy(self, strategy):
        self.strategies.append(strategy)

    async def run(self):
        while True:
            for strategy in self.strategies:
                await strategy.execute()
            await asyncio.sleep(60)
```

## Step 5: Add Risk Management

```python
class RiskManagedBot(SimpleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daily_pnl = 0.0
        self.max_daily_loss = 1.0
        self.max_open_positions = 5

    def can_trade(self) -> bool:
        if self.daily_pnl <= -self.max_daily_loss:
            print("Daily loss limit reached")
            return False
        
        if len(self.positions) >= self.max_open_positions:
            print("Max positions reached")
            return False
        
        return True

    async def on_new_token(self, token):
        if not self.can_trade():
            return

        await super().on_new_token(token)
```

## Step 6: Logging and Monitoring

```python
import logging
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class LoggingBot(SimpleBot):
    async def on_new_token(self, token):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "new_token",
            "symbol": token.symbol,
            "mint": token.mint,
            "market_cap": token.market_cap,
        }

        with open("bot.log", "a") as f:
            f.write(json.dumps(entry) + "\n")

        await super().on_new_token(token)
```

## Step 7: Bot Lifecycle Management

```python
class ControlledBot(SimpleBot):
    async def start(self):
        await self.stream.connect()
        await self.stream.subscribe_new_tokens(self.on_new_token)

    async def stop(self):
        self.stream.stop()
        await self.stream.disconnect()

    async def run(self):
        import signal
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.stop())
            )
        
        await self.start()
```

## Complete Example

```python
import asyncio
from pumpapi import PumpApiClient, PumpApiStream

class TradingBot:
    def __init__(self):
        self.client = PumpApiClient(
            wallet_private_key="YOUR_WALLET_PRIVATE_KEY"
        )
        self.config = {
            "min_mc": 1000,
            "max_mc": 10000,
            "position_size": 0.1,
            "max_positions": 5,
        }
        self.positions = {}

    async def on_new_token(self, token):
        if token.market_cap < self.config["min_mc"]:
            return
        if token.market_cap > self.config["max_mc"]:
            return

        if len(self.positions) >= self.config["max_positions"]:
            return

        result = self.client.execute_buy(
            mint=token.mint,
            sol_amount=self.config["position_size"],
            slippage_bps=100,
        )

        if result.success:
            self.positions[token.mint] = result.tx_hash
            print(f"Bought {token.symbol}")

    async def run(self):
        stream = PumpApiStream()
        await stream.connect()
        await stream.subscribe_new_tokens(self.on_new_token)
        await stream.listen()

    def main(self):
        asyncio.run(self.run())

if __name__ == "__main__":
    TradingBot().main()
```

## Next Steps

- [Tutorial 05: Production](05_production.md) - Production deployment
- Explore [Strategies](../strategies/) - Implement more strategies
