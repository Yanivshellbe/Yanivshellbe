from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .adapters.alpaca import AlpacaAdapter
from .risk.manager import RiskManager
from .settings import settings
from .strategies import registry  # noqa: F401  (registers strategies)
# Import strategy modules so their @register decorators run.
from .strategies import multi_factor, news_butterfly, pol_latency, macro_regime  # noqa: F401


STATE_PATH = Path(__file__).resolve().parents[2] / "dashboard" / "state.json"


class Orchestrator:
    def __init__(self) -> None:
        self.alpaca = AlpacaAdapter()

    def snapshot(self) -> dict:
        acc = self.alpaca.account()
        return {
            "account": {
                "broker": "Alpaca Paper",
                "current_equity_usd": acc.equity,
                "starting_equity_usd": 100_000,
                "buying_power_usd": acc.buying_power,
                "dtbp_status": "PDT · 4× DTBP" if acc.pattern_day_trader else "Cash",
                "live_trading_enabled": settings.live_trading_enabled,
            },
            "open_positions": self.alpaca.positions(),
            "strategies": [s.meta.id for s in registry.all_strategies()],
        }

    def write_state(self, extra_log: list[dict] | None = None) -> None:
        snap = self.snapshot()
        try:
            with STATE_PATH.open() as f:
                state = json.load(f)
        except FileNotFoundError:
            state = {}
        state.update({
            "version": "0.3.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "account": snap["account"],
            "open_positions": snap["open_positions"],
        })
        if extra_log:
            state.setdefault("log", []).extend(extra_log)
        STATE_PATH.write_text(json.dumps(state, indent=2))

    def evaluate_signal(self, signal, reference_price: float):
        risk = RiskManager(
            equity=self.snapshot()["account"]["current_equity_usd"],
            day_pnl_pct=0.0,        # TODO: track from session start
            drawdown_pct=0.0,       # TODO: track high-water mark
            daytrades_used=0,       # TODO: read from Alpaca account
        )
        return risk.size(signal, reference_price)
