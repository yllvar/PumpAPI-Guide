# Tutorial 02: Your First Trade

This guide walks you through executing your first trade with pumpAPI.

## Prerequisites

- Completed [Tutorial 01: Setup](01_setup.md)
- API key configured in `.env`
- Wallet with SOL balance (for trading)

## Step 1: Understand the Token Mint

For this tutorial, we'll use a Pump.fun token mint address. You can:
- Use an existing token's mint address
- Create a new token on pump.fun

Example mint: `EPjFWdd5AufqSSCwM2XcPw9yqWQ1HqmZdL2FT9HZmwJD`

## Step 2: Create the Trade Script

Create a file `my_first_trade.py`:

```python
from pumpapi import PumpApiClient

def main():
    client = PumpApiClient(
        wallet_private_key="YOUR_WALLET_PRIVATE_KEY"
    )

    mint = "YOUR_TOKEN_MINT"

    print(f"Trading token: {mint}")

    # Get current state
    token = client.get_token(mint)
    print(f"Token: {token.name} ({token.symbol})")

    mc = client.get_market_cap(mint)
    print(f"Market Cap: {mc.market_cap_sol:.2f} SOL")

    # Execute buy
    print("\nExecuting buy...")
    result = client.execute_buy(
        mint=mint,
        sol_amount=0.01,  # 0.01 SOL
        slippage_bps=100,  # 1% slippage
    )

    if result.success:
        print(f"SUCCESS! TX: {result.tx_hash}")
    else:
        print(f"FAILED: {result.error}")

    # Execute sell (optional)
    print("\nExecuting sell...")
    result = client.execute_sell(
        mint=mint,
        token_amount=1000000,  # Adjust for token decimals
        decimals=6,
    )

    if result.success:
        print(f"SUCCESS! TX: {result.tx_hash}")
    else:
        print(f"FAILED: {result.error}")

if __name__ == "__main__":
    main()
```

## Step 3: Run the Script

```bash
python my_first_trade.py
```

## Step 4: Verify the Transaction

1. Copy the transaction hash from the output
2. Visit Solscan: https://solscan.io
3. Paste the hash to view transaction details

## Understanding the Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `mint` | Token mint address | `EPjFWdd5...` |
| `sol_amount` | Amount in SOL | `0.01` |
| `token_amount` | Amount in tokens | `1000000` |
| `decimals` | Token decimals | `6` |
| `slippage_bps` | Slippage (1% = 100) | `100` |
| `priority_fee` | Priority fee in micro-lamports | `5000` |

## Step 5: Experiment

### Try Different Amounts

```python
result = client.execute_buy(
    mint=mint,
    sol_amount=0.1,  # More SOL
)
```

### Adjust Slippage

```python
result = client.execute_buy(
    mint=mint,
    sol_amount=0.01,
    slippage_bps=500,  # 5% for illiquid tokens
)
```

### Add Priority Fee

```python
result = client.execute_buy(
    mint=mint,
    sol_amount=0.01,
    priority_fee=10000,  # Higher priority for faster execution
)
```

## Common Issues

### Insufficient Funds

```
Error: Transaction failed
```

Make sure your wallet has enough SOL for:
- Trade amount
- Priority fees (~0.01 SOL per trade)
- Rent exempt balance

### Slippage Too Low

```
Error: Transaction failed: slippage exceeded
```

Increase slippage for illiquid tokens.

### Invalid Mint

```
Error: Invalid token
```

Verify the mint address is correct.

## Next Steps

- [Tutorial 03: Real-time Streaming](03_real_time_streaming.md) - Learn WebSocket streaming
- [Tutorial 04: Build a Bot](04_build_bot.md) - Create an automated trading bot
