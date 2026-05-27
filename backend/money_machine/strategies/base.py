from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal


Side = Literal["long", "short"]


@dataclass
class Signal:
    symbol: str
    side: Side
    confidence: float  # 0..1
    horizon_minutes: int
    rationale: str
    source: str
    suggested_stop_pct: float | None = None
    suggested_take_profit_pct: float | None = None
    meta: dict = field(default_factory=dict)


@dataclass
class StrategyMeta:
    id: str
    title: str
    category: str
    description: str
    universe: list[str]
    timeframe: str
    risk_per_trade_pct: float
    needs_data: list[str]  # e.g. ["bars_1m", "news", "polymarket_ws"]


class Strategy(ABC):
    meta: StrategyMeta

    @abstractmethod
    def generate_signals(self, context: dict) -> list[Signal]: ...

    def describe(self) -> dict:
        return {
            "id": self.meta.id,
            "title": self.meta.title,
            "category": self.meta.category,
            "description": self.meta.description,
            "universe": self.meta.universe,
            "timeframe": self.meta.timeframe,
            "needs_data": self.meta.needs_data,
        }
