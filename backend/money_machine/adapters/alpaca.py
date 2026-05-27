from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..settings import settings


@dataclass
class AccountSnapshot:
    equity: float
    buying_power: float
    cash: float
    daytrade_count: int
    pattern_day_trader: bool
    multiplier: float


class AlpacaAdapter:
    """Thin wrapper around alpaca-py. Lazy-imported so the module loads even without the SDK."""

    def __init__(self) -> None:
        if not settings.alpaca_configured:
            self._client = None
            return
        from alpaca.trading.client import TradingClient  # type: ignore

        self._client = TradingClient(
            api_key=settings.alpaca_key,
            secret_key=settings.alpaca_secret,
            paper="paper-api" in settings.alpaca_base_url,
        )

    @property
    def ready(self) -> bool:
        return self._client is not None

    def account(self) -> AccountSnapshot:
        if not self.ready:
            return AccountSnapshot(
                equity=100_000.0,
                buying_power=400_000.0,
                cash=100_000.0,
                daytrade_count=0,
                pattern_day_trader=True,
                multiplier=4.0,
            )
        a = self._client.get_account()
        return AccountSnapshot(
            equity=float(a.equity),
            buying_power=float(a.buying_power),
            cash=float(a.cash),
            daytrade_count=int(a.daytrade_count or 0),
            pattern_day_trader=bool(a.pattern_day_trader),
            multiplier=float(a.multiplier or 1),
        )

    def positions(self) -> list[dict]:
        if not self.ready:
            return []
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "side": p.side,
                "avg_entry": float(p.avg_entry_price),
                "market_value": float(p.market_value),
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_plpc": float(p.unrealized_plpc),
            }
            for p in self._client.get_all_positions()
        ]

    def submit_order(
        self,
        *,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = "market",
        time_in_force: str = "day",
        bracket_stop: float | None = None,
        bracket_take_profit: float | None = None,
    ) -> dict:
        if settings.dry_run:
            return {
                "dry_run": True,
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "type": order_type,
                "tif": time_in_force,
                "bracket_stop": bracket_stop,
                "bracket_take_profit": bracket_take_profit,
            }
        if not self.ready:
            raise RuntimeError("Alpaca not configured. Set ALPACA_KEY / ALPACA_SECRET.")
        if not settings.live_trading_enabled:
            raise RuntimeError("LIVE_TRADING_ENABLED is false. Refusing to submit.")
        from alpaca.trading.requests import MarketOrderRequest  # type: ignore
        from alpaca.trading.enums import OrderSide, TimeInForce  # type: ignore

        req = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side.lower()),
            time_in_force=TimeInForce(time_in_force.lower()),
        )
        order = self._client.submit_order(req)
        return {"id": order.id, "symbol": symbol, "qty": qty, "side": side}
