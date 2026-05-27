from __future__ import annotations

from .base import Signal, Strategy, StrategyMeta
from .registry import register


@register
class PolymarketCLOBLatency(Strategy):
    """Polymarket UP/DOWN 5MIN reprice lag scalper.

    Status: skeleton. Requires:
      - Polymarket CLOB WebSocket
      - Binance spot WS for BTC reference price
      - NTP-synced timestamps; reject signals where t_polymarket - t_binance < 50ms
      - Auto-flatten on disconnect
      - Strict per-trade, daily, and hard-stop risk caps
    """

    meta = StrategyMeta(
        id="pol_clob_latency",
        title="Polymarket CLOB Latency Scalper",
        category="Latency Arb",
        description="Exploit ~100ms CLOB reprice lag vs Binance spot on 5MIN UP/DOWN contracts.",
        universe=["POLY:BTC-UP-5MIN", "POLY:BTC-DOWN-5MIN"],
        timeframe="tick",
        risk_per_trade_pct=0.5,
        needs_data=["polymarket_clob_ws", "binance_spot_ws", "ntp_sync"],
    )

    def generate_signals(self, context: dict) -> list[Signal]:
        # Placeholder. Real impl would read context["polymarket_book"], context["binance_spot"],
        # compute implied probability, compare, and emit a directional signal if drift > threshold.
        return []
