# API Reference

Complete reference for the pumpAPI client and stream classes.

## PumpApiClient

Main client for interacting with the pumpAPI REST endpoints.

### Initialization

```python
from pumpapi import PumpApiClient

# API key authentication
client = PumpApiClient(api_key="your_api_key")

# Wallet-based authentication
client = PumpApiClient(wallet_private_key="your_private_key")

# With custom config
client = PumpApiClient(
    api_key="your_api_key",
    rpc_url="https://api.mainnet-beta.solana.com",
    slippage_bps=100,
    priority_fee_micro_lamports=1000,
)
```

### Token Endpoints

#### `get_token(mint: str) -> TokenInfo`

Get token information by mint address.

```python
token = client.get_token("YOUR_TOKEN_MINT")
print(token.name)       # Token name
print(token.symbol)     # Token symbol
print(token.decimals)   # Token decimals
```

#### `get_token_by_ticker(ticker: str) -> TokenInfo`

Get token information by ticker symbol.

```python
token = client.get_token_by_ticker("PEPE")
```

#### `get_recent_tokens(limit: int = 50, offset: int = 0) -> List[TokenMetadata]`

Get recently created tokens.

```python
recent = client.get_recent_tokens(limit=20)
for token in recent:
    print(f"{token.symbol}: {token.name} - {token.market_cap} SOL")
```

### Market Data Endpoints

#### `get_bonding_curve(mint: str) -> BondingCurveState`

Get the bonding curve state for a token.

```python
curve = client.get_bonding_curve("YOUR_TOKEN_MINT")
print(curve.virtual_sol_reserves)
print(curve.virtual_token_reserves)
print(curve.complete)  # True if token has migrated to DEX
```

#### `get_market_cap(mint: str) -> MarketCapInfo`

Get market cap and liquidity information.

```python
mc = client.get_market_cap("YOUR_TOKEN_MINT")
print(f"Market Cap: {mc.market_cap_sol} SOL")
print(f"Liquidity: {mc.liquidity_sol} SOL")
print(f"Holders: {mc.holder_count}")
```

#### `get_token_price(mint: str) -> float`

Get current token price in SOL.

```python
price = client.get_token_price("YOUR_TOKEN_MINT")
print(f"Price: {price} SOL")
```

#### `get_trades(mint: str, limit: int = 50) -> List[TradeInfo]`

Get recent trades for a token.

```python
trades = client.get_trades("YOUR_TOKEN_MINT", limit=10)
for trade in trades:
    print(f"{'BUY' if trade.is_buy else 'SELL'} {trade.token_amount} at {trade.sol_amount} SOL")
```

### Transaction Endpoints

#### `create_buy_transaction(mint, sol_amount, slippage_bps, priority_fee)`

Create a buy transaction. Returns unsigned transaction data.

```python
tx_data = client.create_buy_transaction(
    mint="YOUR_TOKEN_MINT",
    sol_amount=0.1,
    slippage_bps=100,
    priority_fee=1000,
)
```

#### `create_sell_transaction(mint, token_amount, decimals, slippage_bps, priority_fee)`

Create a sell transaction.

```python
tx_data = client.create_sell_transaction(
    mint="YOUR_TOKEN_MINT",
    token_amount=1000,
    decimals=6,
    slippage_bps=100,
    priority_fee=1000,
)
```

#### `execute_buy(mint, sol_amount, slippage_bps, priority_fee) -> TradeResult`

Execute a buy transaction (creates, signs, and broadcasts).

```python
result = client.execute_buy(
    mint="YOUR_TOKEN_MINT",
    sol_amount=0.1,
)
if result.success:
    print(f"Tx: {result.tx_hash}")
```

#### `execute_sell(mint, token_amount, decimals, slippage_bps, priority_fee) -> TradeResult`

Execute a sell transaction.

```python
result = client.execute_sell(
    mint="YOUR_TOKEN_MINT",
    token_amount=1000,
    decimals=6,
)
```

### Utility Endpoints

#### `get_fees(mint: str) -> Dict`

Get fee information for a token.

```python
fees = client.get_fees("YOUR_TOKEN_MINT")
```

#### `get_global_data() -> Dict`

Get global protocol data.

```python
data = client.get_global_data()
```

### Properties

#### `wallet_address -> Optional[str]`

Returns the associated wallet address.

```python
print(client.wallet_address)
```

---

## PumpApiStream

WebSocket client for real-time data streaming.

### Initialization

```python
from pumpapi import PumpApiStream

stream = PumpApiStream(
    wss_url="wss://pumpportal.fun/api/data",
    api_key="your_api_key",
)
```

### Subscription Methods

#### `subscribe_new_tokens(callback) -> str`

Subscribe to new token events.

```python
async def handle_new_token(token):
    print(f"New: {token.symbol}")

sub_id = await stream.subscribe_new_tokens(handle_new_token)
```

#### `subscribe_trades(mint, callback) -> str`

Subscribe to trade events for a specific token.

```python
async def handle_trade(trade):
    print(f"Trade: {trade.is_buy}")

sub_id = await stream.subscribe_trades("YOUR_TOKEN_MINT", handle_trade)
```

#### `subscribe_market_cap(mint, callback) -> str`

Subscribe to market cap updates.

```python
async def handle_market_cap(mc):
    print(f"MC: {mc.market_cap_sol} SOL")

sub_id = await stream.subscribe_market_cap("YOUR_TOKEN_MINT", handle_market_cap)
```

#### `subscribe_bonding_curve(mint, callback) -> str`

Subscribe to bonding curve updates.

```python
async def handle_curve(curve):
    print(f"Curve complete: {curve.complete}")

sub_id = await stream.subscribe_bonding_curve("YOUR_TOKEN_MINT", handle_curve)
```

### Connection Management

#### `connect()`

Establish WebSocket connection.

```python
await stream.connect()
```

#### `disconnect()`

Close WebSocket connection.

```python
await stream.disconnect()
```

#### `listen()`

Start listening for messages (blocking).

```python
await stream.listen()
```

#### `stop()`

Stop the listener.

```python
stream.stop()
```

#### `unsubscribe(subscription_id)`

Unsubscribe from a subscription.

```python
await stream.unsubscribe(sub_id)
```

---

## Data Models

### TokenInfo

| Field | Type | Description |
|-------|------|-------------|
| mint | str | Token mint address |
| name | str | Token name |
| symbol | str | Token symbol |
| decimals | int | Token decimals |
| uri | Optional[str] | Metadata URI |

### TradeInfo

| Field | Type | Description |
|-------|------|-------------|
| mint | str | Token mint |
| sol_amount | int | SOL amount (lamports) |
| token_amount | int | Token amount |
| is_buy | bool | Buy or sell |
| user | str | Trader address |
| timestamp | int | Unix timestamp |
| tx_hash | str | Transaction hash |

### BondingCurveState

| Field | Type | Description |
|-------|------|-------------|
| mint | str | Token mint |
| virtual_token_reserves | int | Virtual token reserves |
| virtual_sol_reserves | int | Virtual SOL reserves |
| real_token_reserves | int | Real token reserves |
| real_sol_reserves | int | Real SOL reserves |
| token_supply | int | Total token supply |
| initialized | bool | Curve initialized |
| complete | bool | Migrated to DEX |

### TradeResult

| Field | Type | Description |
|-------|------|-------------|
| tx_hash | str | Transaction hash |
| success | bool | Success status |
| error | Optional[str] | Error message |
| timestamp | int | Unix timestamp |
