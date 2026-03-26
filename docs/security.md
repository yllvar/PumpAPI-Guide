# Security Best Practices

Security guidance for building and operating pumpAPI trading systems.

## Wallet Security

### Private Key Management

**NEVER** commit private keys to version control:

```python
# BAD - hardcoded key
client = PumpApiClient(wallet_private_key="4xX...")

# GOOD - from environment
client = PumpApiClient(
    wallet_private_key=os.getenv("PUMPAPI_WALLET_PRIVATE_KEY")
)
```

### Recommended Setup

1. Use hardware wallets for production funds
2. Use hot/cold wallet separation
3. Set up multi-sig for large transactions
4. Implement withdrawal limits

### Key Storage Options

| Method | Security | Use Case |
|--------|----------|----------|
| Environment variables | Medium | Development |
| HashiCorp Vault | High | Production |
| AWS Secrets Manager | High | AWS deployment |
| Hardware wallet | Highest | Long-term storage |

## API Key Security

### Key Management

- Store API keys in environment variables
- Rotate keys periodically
- Use separate keys for dev/prod
- Monitor key usage

### Access Control

```python
# Limit API key permissions
# - Read-only keys for monitoring
# - Trading keys for execution
# - Admin keys for account management
```

## Transaction Security

### Slippage Protection

Always set appropriate slippage:

```python
# Conservative slippage for illiquid tokens
result = client.execute_buy(
    mint="TOKEN_MINT",
    sol_amount=0.1,
    slippage_bps=500,  # 5% for low liquidity
)

# Tighter slippage for established tokens
result = client.execute_buy(
    mint="TOKEN_MINT",
    sol_amount=0.1,
    slippage_bps=50,  # 0.5% for established tokens
)
```

### Amount Limits

Implement per-trade limits:

```python
MAX_TRADE_SOL = 1.0  # 1 SOL max per trade
MAX_TRADE_TOKENS = 1000000  # Token amount limit

def safe_execute_buy(mint, sol_amount):
    if sol_amount > MAX_TRADE_SOL:
        sol_amount = MAX_TRADE_SOL
    return client.execute_buy(mint, sol_amount)
```

## Network Security

### RPC Security

- Use HTTPS/WSS for all connections
- Validate SSL certificates
- Avoid public RPC for trading

### Firewall Rules

```bash
# Allow specific IPs only
ufw allow from <rpc_ip> to any port 443
```

## Operational Security

### Logging

Avoid logging sensitive data:

```python
# BAD - logs everything
logger.debug(f"Buying with key: {private_key}")

# GOOD - log only what you need
logger.debug(f"Buying {sol_amount} SOL")
```

### Error Handling

Don't expose sensitive information in errors:

```python
# BAD
raise ValueError(f"Invalid key: {private_key}")

# GOOD
raise ValueError("Invalid authentication")
```

## Code Security

### Dependency Management

- Pin dependency versions
- Review dependencies regularly
- Use security scanners

```bash
pip-audit        # Check for vulnerabilities
safety check     # Verify dependencies
```

### Code Review

- Require reviews for all changes
- Scan for secrets before commit
- Use pre-commit hooks

```python
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: detect-secrets
      - id: trailing-whitespace
```

## Monitoring

### Alert on Anomalies

- Large trades
- Failed transactions
- Unusual activity patterns

### Audit Trail

```python
# Log all trades with context
logger.info(f"Trade executed: {tx_hash}, amount: {amount}, mint: {mint}")
```

## Incident Response

### If Compromised

1. Revoke API keys immediately
2. Transfer funds to cold wallet
3. Rotate all secrets
4. Review access logs
5. Document incident

## Checklist

- [ ] Private keys in environment, not code
- [ ] API keys rotated regularly
- [ ] Slippage limits configured
- [ ] Trade amount limits in place
- [ ] Logging sanitized
- [ ] Dependencies audited
- [ ] Access logs monitored
- [ ] Incident response plan ready
