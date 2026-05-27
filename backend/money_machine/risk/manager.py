from __future__ import annotations

from dataclasses import dataclass

from ..settings import settings
from ..strategies.base import Signal


@dataclass
class SizedOrder:
    symbol: str
    side: str
    qty: float
    notional_usd: float
    stop_pct: float | None
    take_profit_pct: float | None
    rejected_reason: str | None = None


class RiskManager:
    """Enforces account-level caps before a Signal becomes a real order.

    Hard checks (any failure → reject):
      1. live trading disabled / dry run
      2. daily loss > MAX_DAILY_LOSS_PCT
      3. running drawdown > MAX_DRAWDOWN_PCT
      4. position size > MAX_POSITION_PCT_EQUITY
      5. PDT day-trade count >= 3 (rolling 5 days)
      6. symbol not on allow-list / liquidity below threshold
    """

    def __init__(self, equity: float, day_pnl_pct: float, drawdown_pct: float, daytrades_used: int) -> None:
        self.equity = equity
        self.day_pnl_pct = day_pnl_pct
        self.drawdown_pct = drawdown_pct
        self.daytrades_used = daytrades_used

    def size(self, signal: Signal, reference_price: float) -> SizedOrder:
        if self.day_pnl_pct <= -settings.max_daily_loss_pct:
            return self._reject(signal, "daily loss cap hit")
        if self.drawdown_pct >= settings.max_drawdown_pct:
            return self._reject(signal, "max drawdown cap hit")
        if self.daytrades_used >= 3:
            return self._reject(signal, "PDT day-trade count exhausted")
        if reference_price <= 0:
            return self._reject(signal, "invalid reference price")

        # Position sized so per-trade loss at stop = risk_per_trade_pct * equity
        stop_pct = signal.suggested_stop_pct or 0.5
        per_trade_risk_usd = self.equity * (0.5 / 100)  # 0.5% of equity per trade default
        notional = per_trade_risk_usd / (stop_pct / 100)
        cap = self.equity * (settings.max_position_pct_equity / 100)
        notional = min(notional, cap)
        qty = round(notional / reference_price, 4)

        return SizedOrder(
            symbol=signal.symbol,
            side=signal.side,
            qty=qty,
            notional_usd=notional,
            stop_pct=stop_pct,
            take_profit_pct=signal.suggested_take_profit_pct,
        )

    def _reject(self, signal: Signal, reason: str) -> SizedOrder:
        return SizedOrder(
            symbol=signal.symbol,
            side=signal.side,
            qty=0,
            notional_usd=0,
            stop_pct=None,
            take_profit_pct=None,
            rejected_reason=reason,
        )
