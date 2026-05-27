from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).resolve().parents[1] / "config" / "settings.env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    alpaca_key: str = os.getenv("ALPACA_KEY", "")
    alpaca_secret: str = os.getenv("ALPACA_SECRET", "")
    alpaca_base_url: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    anthropic_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-7")

    max_daily_loss_pct: float = _float("MAX_DAILY_LOSS_PCT", 2.0)
    max_drawdown_pct: float = _float("MAX_DRAWDOWN_PCT", 8.0)
    max_gross_leverage: float = _float("MAX_GROSS_LEVERAGE", 3.0)
    max_position_pct_equity: float = _float("MAX_POSITION_PCT_EQUITY", 10.0)
    min_liquidity_usd: float = _float("MIN_LIQUIDITY_USD", 1_000_000)

    live_trading_enabled: bool = _bool("LIVE_TRADING_ENABLED", False)
    dry_run: bool = _bool("DRY_RUN", True)

    @property
    def alpaca_configured(self) -> bool:
        return bool(self.alpaca_key and self.alpaca_secret)


settings = Settings()
