from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Signal:
    mint: str
    action: str
    strength: float
    price: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseStrategy(ABC):
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.is_running = False

    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Optional[Signal]:
        pass

    @abstractmethod
    async def on_signal(self, signal: Signal) -> None:
        pass

    async def start(self):
        self.is_running = True

    async def stop(self):
        self.is_running = False

    def update_config(self, config: Dict[str, Any]):
        self.config.update(config)

    @property
    def parameters(self) -> Dict[str, Any]:
        return self.config.copy()
