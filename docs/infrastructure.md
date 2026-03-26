# Infrastructure Setup

Guide to setting up infrastructure for pumpAPI trading bots.

## RPC Endpoints

### Recommended RPC Providers

| Provider | Mainnet URL | Notes |
|----------|-------------|-------|
| Helius | `https://mainnet.helius-rpc.com` | Best for trading bots |
| Triton | `https://rpc.ankr.com/solana` | Good reliability |
| QuickNode | `https://api.mainnet-beta.solana.com` | Pay tier available |
| Default | `https://api.mainnet-beta.solana.com` | Rate limited |

### High-Performance Setup

For production trading bots, use dedicated RPC:

```python
client = PumpApiClient(
    rpc_url="https://mainnet.helius-rpc.com/?api-key=YOUR_KEY",
)
```

### RPC Configuration Options

```python
from pumpapi import PumpApiConfig

config = PumpApiConfig(
    rpc_url="https://mainnet.helius-rpc.com/?api-key=YOUR_KEY",
    timeout=30,
    max_retries=3,
)

client = PumpApiClient(config=config)
```

## Server Requirements

### Minimum Setup (Development)

- 2 vCPU
- 4GB RAM
- 50GB SSD
- Python 3.10+

### Recommended Setup (Production)

- 4+ vCPU
- 8GB+ RAM
- 100GB+ NVMe SSD
- Low-latency network

### Colocation

For ultra-low latency trading:
- Co-locate with Solana validators
- Use dedicated network connections
- Consider FPGA acceleration

## WebSocket Configuration

### Connection Management

```python
from pumpapi import PumpApiStream

stream = PumpApiStream(
    wss_url="wss://pumpportal.fun/api/data",
    api_key="your_api_key",
)

# Auto-reconnect is built-in
await stream.connect()
```

### Subscription Limits

- New tokens: Unlimited
- Per-token trades: Up to 10 concurrent
- Market cap: Up to 10 concurrent per token

## Database (Optional)

### PostgreSQL for Trade History

```python
import asyncpg

async def setup_db():
    conn = await asyncpg.connect(
        host="localhost",
        database="trading",
        user="user",
        password="password",
    )
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            mint TEXT NOT NULL,
            amount REAL NOT NULL,
            price REAL NOT NULL,
            side TEXT NOT NULL,
            tx_hash TEXT UNIQUE,
            timestamp TIMESTAMP DEFAULT NOW()
        )
    """)
    return conn
```

### Redis for State

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Cache token prices
r.setex(f"price:{mint}", 60, price)

# Track open positions
r.sadd(f"positions:{wallet}", mint)
```

## Monitoring

### Health Checks

```python
import asyncio

async def health_check(client):
    try:
        await client.get_global_data()
        return True
    except Exception:
        return False
```

### Metrics

Track these key metrics:

- Latency: Request to response time
- Success rate: Transaction success percentage
- PnL: Profit and loss tracking
- API usage: Rate limit proximity

## Network Optimization

### Priority Fees

Set priority fees for faster confirmations:

```python
result = client.execute_buy(
    mint="TOKEN_MINT",
    sol_amount=0.1,
    priority_fee=5000,  # micro-lamports
)
```

### Batch Requests

Where possible, batch queries:

```python
# Instead of individual calls
for mint in token_list:
    price = client.get_token_price(mint)

# Use batch endpoints when available
prices = client.get_token_prices(token_list)
```

## Environment Configuration

### Production .env

```env
PUMPAPI_API_KEY=your_production_key
PUMPAPI_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
PUMPAPI_WSS_URL=wss://pumpportal.fun/api/data
PUMPAPI_SLIPPAGE_BPS=50
PUMPAPI_PRIORITY_FEE_MICRO_LAMPORTS=5000
PUMPAPI_DEBUG=false
```

### Security

- Never commit `.env` files
- Use secret management services
- Rotate API keys regularly
