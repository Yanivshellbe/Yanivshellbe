from __future__ import annotations

from .base import Signal, Strategy, StrategyMeta
from .registry import register


@register
class MultiFactorLongShort(Strategy):
    """Momentum + Value + LowVol + Quality + Trend daily rank, long top decile / short bottom decile.

    Status: skeleton — needs point-in-time fundamentals & price history adapter before signals fire.
    """

    meta = StrategyMeta(
        id="multifactor_long_short",
        title="Multi-Factor Long/Short",
        category="Quant",
        description="Daily rank S&P 1500 across 5 factors, weekly rebalance, beta-neutral.",
        universe=["SPY components · S&P 1500"],
        timeframe="1D",
        risk_per_trade_pct=0.5,
        needs_data=["bars_1d", "fundamentals_pit"],
    )

    def generate_signals(self, context: dict) -> list[Signal]:
        # TODO: implement once fundamentals adapter is online.
        return []
