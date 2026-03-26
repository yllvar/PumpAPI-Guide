from __future__ import annotations

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    WATCH = "watch"


class SignalStrength(Enum):
    WEAK = 0.25
    LOW = 0.5
    MEDIUM = 0.75
    STRONG = 1.0


@dataclass
class TradingSignal:
    mint: str
    signal_type: SignalType
    strength: float
    price: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    confidence: float = 0.0
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def is_buy(self) -> bool:
        return self.signal_type == SignalType.BUY

    def is_sell(self) -> bool:
        return self.signal_type == SignalType.SELL

    def is_strong(self, threshold: float = 0.7) -> bool:
        return self.strength >= threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mint": self.mint,
            "type": self.signal_type.value,
            "strength": self.strength,
            "price": self.price,
            "volume": self.volume,
            "market_cap": self.market_cap,
            "confidence": self.confidence,
            "reason": self.reason,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SignalBatch:
    signals: List[TradingSignal] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def add(self, signal: TradingSignal):
        self.signals.append(signal)

    def buy_signals(self) -> List[TradingSignal]:
        return [s for s in self.signals if s.is_buy()]

    def sell_signals(self) -> List[TradingSignal]:
        return [s for s in self.signals if s.is_sell()]

    def strong_signals(self, threshold: float = 0.7) -> List[TradingSignal]:
        return [s for s in self.signals if s.is_strong(threshold)]
