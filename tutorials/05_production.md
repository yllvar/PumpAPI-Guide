# Tutorial 05: Production Best Practices

This guide covers deploying your trading bot in production.

## Overview

Production systems require:
- Reliability
- Security
- Monitoring
- Scalability

## Step 1: Security Hardening

### Environment Variables

Never commit secrets:

```bash
# .env (add to .gitignore)
PUMPAPI_API_KEY=secret_key
PUMPAPI_WALLET_PRIVATE_KEY=secret_wallet
```

Use secret management:

```python
# Production: Use HashiCorp Vault, AWS Secrets, etc.
import os
api_key = os.environ.get("PUMPAPI_API_KEY")
```

### API Key Rotation

```python
import time

class RotatingKeyClient:
    def __init__(self, keys: list[str]):
        self.keys = keys
        self.current = 0
        self.usage_count = 0
        self.rotate_every = 1000

    def get_key(self):
        if self.usage_count >= self.rotate_every:
            self.current = (self.current + 1) % len(self.keys)
            self.usage_count = 0
        self.usage_count += 1
        return self.keys[self.current]
```

## Step 2: Error Handling

### Retry Logic

```python
import asyncio
from functools import wraps

def with_retry(max_retries=3, backoff=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(backoff ** attempt)
        return wrapper
    return decorator

@with_retry(max_retries=3)
async def execute_trade(client, mint, amount):
    return client.execute_buy(mint, amount)
```

### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = 0
        self.state = "closed"

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit open")

        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise
```

## Step 3: Monitoring

### Health Checks

```python
import asyncio
from dataclasses import dataclass

@dataclass
class HealthStatus:
    healthy: bool
    last_check: float
    errors: list[str]

class HealthMonitor:
    def __init__(self, client):
        self.client = client
        self.status = HealthStatus(True, time.time(), [])

    async def check(self):
        try:
            self.client.get_global_data()
            self.status.healthy = True
            self.status.errors = []
        except Exception as e:
            self.status.healthy = False
            self.status.errors.append(str(e))
        finally:
            self.status.last_check = time.time()
        return self.status
```

### Metrics

```python
from dataclasses import dataclass
from collections import defaultdict
import time

@dataclass
class Metrics:
    trades_executed: int = 0
    trades_failed: int = 0
    total_volume: float = 0.0
    start_time: float = 0.0
    errors: list = None

    def __post_init__(self):
        self.errors = []

    def record_trade(self, success: bool, volume: float):
        if success:
            self.trades_executed += 1
        else:
            self.trades_failed += 1
        self.total_volume += volume

    def uptime(self) -> float:
        return time.time() - self.start_time
```

## Step 4: Deployment

### Process Management

Using systemd:

```ini
# /etc/systemd/system/pumpbot.service
[Unit]
Description=pumpAPI Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pumpAPI-guide
Environment="PATH=/home/ubuntu/pumpAPI-guide/venv/bin"
ExecStart=/home/ubuntu/pumpAPI-guide/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 botuser
USER botuser

CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  bot:
    build: .
    restart: always
    env_file:
      - .env
    volumes:
      - ./data:/app/data

  monitor:
    image: prom/prometheus
    ports:
      - "9090:9090"
```

## Step 5: Logging

### Structured Logging

```python
import json
import logging
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        })

handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logging.root.addHandler(handler)
```

### Log Rotation

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "bot.log",
    maxBytes=10_000_000,  # 10MB
    backupCount=5,
)
```

## Step 6: Runbooks

### Restart Procedure

```bash
sudo systemctl restart pumpbot
```

### Check Status

```bash
sudo systemctl status pumpbot
journalctl -u pumpbot -f
```

### Rollback

```bash
git checkout v1.0.0
sudo systemctl restart pumpbot
```

## Step 7: Backup and Recovery

### Wallet Backup

```bash
# Export wallet (keep secure!)
python -c "from pumpapi import parse_wallet_private_key; ..."
```

### State Backup

```python
import json
import boto3

def backup_state(state_file):
    with open(state_file) as f:
        state = json.load(f)
    
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket="bot-backups",
        Key=f"state/{datetime.now().isoformat()}.json",
        Body=json.dumps(state),
    )
```

## Checklist

Before going live:

- [ ] All secrets in environment variables
- [ ] Logging configured
- [ ] Health checks implemented
- [ ] Metrics collection setup
- [ ] Error handling with retry
- [ ] Circuit breakers in place
- [ ] Runbook documented
- [ ] Backup strategy defined
- [ ] Monitoring alerting active

## Next Steps

- Review [Security](../docs/security.md) documentation
- Explore [Infrastructure](../docs/infrastructure.md) setup
- Check out advanced [Strategies](../strategies/)
