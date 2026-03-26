# pumpAPI Architecture

This document describes the system architecture for building trading systems with pumpAPI.

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Trading Bot                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │  Strategy   │───▶│  Signal     │───▶│    Execution        │ │
│  │  Engine     │    │  Generator  │    │    Engine           │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      pumpAPI Guide Library                       │
│  ┌────────────────┐          ┌──────────────────────────────┐   │
│  │  HTTP Client   │          │     WebSocket Stream         │   │
│  │  (REST API)    │          │     (Real-time Data)         │   │
│  └────────────────┘          └──────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                         pumpAPI                                  │
│                    (External Service)                           │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. HTTP Client (`PumpApiClient`)

Handles all REST API interactions with pumpAPI:

- Token queries (info, price, market cap)
- Bonding curve state
- Trade history
- Transaction creation and execution

**Key Features**:
- Automatic retry with exponential backoff
- API key and wallet-based authentication
- Connection pooling
- Request/response logging

### 2. WebSocket Stream (`PumpApiStream`)

Provides real-time data streaming:

- New token notifications
- Trade events
- Market cap updates
- Bonding curve state changes

**Key Features**:
- Automatic reconnection
- Multiple concurrent subscriptions
- Callback-based event handling

### 3. Strategy Framework (`pumpapi_strategies`)

Base classes for building trading strategies:

- `BaseStrategy`: Abstract base for custom strategies
- `TradingSignal`: Signal model with confidence scores
- `SignalExecutor`: Order execution engine

## Data Flow

### Read Path (Market Data)

```
WebSocket/REST API
        │
        ▼
┌───────────────┐
│  Data Parser  │
└───────────────┘
        │
        ▼
┌───────────────┐
│  Strategy     │
│  Analysis     │
└───────────────┘
        │
        ▼
┌───────────────┐
│  Signal       │
│  Generation   │
└───────────────┘
```

### Write Path (Trading)

```
Signal + Amount
        │
        ▼
┌───────────────┐
│  Transaction  │
│  Builder      │
└───────────────┘
        │
        ▼
┌───────────────┐
│  Wallet       │
│  Signing      │
└───────────────┘
        │
        ▼
┌───────────────┐
│  Broadcast    │
│  to Network   │
└───────────────┘
```

## Authentication

The library supports two authentication methods:

### 1. API Key Authentication

For read-only operations and server-side transactions:

```python
client = PumpApiClient(api_key="your_api_key")
```

### 2. Wallet-Based Authentication

For client-side transaction signing:

```python
client = PumpApiClient(wallet_private_key="your_private_key")
```

## Design Patterns

### Connection Management

- Lazy initialization: Connections created on first request
- Connection pooling: Reuse HTTP connections
- Automatic reconnection: WebSocket auto-reconnect on disconnect

### Error Handling

- Retry with exponential backoff for transient errors
- Detailed error messages with context
- Graceful degradation

### Type Safety

- Pydantic models for all data types
- Full type hints throughout
- Dataclass for internal state

## Scaling Considerations

### Horizontal Scaling

- Multiple instances of trading bots
- Shared Redis for state
- Load-balanced RPC endpoints

### Vertical Scaling

- Async I/O for concurrent operations
- Batch operations where supported
- Efficient WebSocket handling

## Security

- Never log private keys
- Environment variable configuration
- Wallet signing kept local
- API key rotation support

## Extension Points

Custom strategies can extend:

```python
from pumpapi_strategies import BaseStrategy, TradingSignal, SignalType

class MyStrategy(BaseStrategy):
    async def analyze(self, data) -> Optional[TradingSignal]:
        # Custom logic
        pass

    async def on_signal(self, signal):
        # Handle signal
        pass
```
