from __future__ import annotations

from .base import Signal, Strategy, StrategyMeta
from .registry import register


# Each event class maps to a list of (symbol, side, magnitude_hint).
# Magnitude is a *hint* fed to the position-sizer, never an execution amount.
CASCADE_MAP: dict[str, list[tuple[str, str, float]]] = {
    "war_escalation": [
        ("USO", "long", 1.0),   # oil
        ("GLD", "long", 0.8),   # gold
        ("VIXY", "long", 0.6),  # vol proxy
        ("SPY", "short", 0.5),
        ("JETS", "short", 0.4),
        ("ITA", "long", 0.7),   # defense
    ],
    "tariff_announcement": [
        ("FXI", "short", 0.7),
        ("EWZ", "short", 0.4),
        ("CAT", "short", 0.5),
        ("STLD", "long", 0.5),  # domestic steel
    ],
    "fed_dovish_surprise": [
        ("QQQ", "long", 0.8),
        ("IWM", "long", 0.6),
        ("TLT", "long", 0.7),
        ("DXY_PROXY", "short", 0.4),
    ],
    "fed_hawkish_surprise": [
        ("QQQ", "short", 0.7),
        ("XLF", "long", 0.5),
        ("TLT", "short", 0.7),
    ],
}


@register
class NewsButterflyCascade(Strategy):
    """Stream high-signal political/macro accounts → classify → fan out preset asset cascade.

    Status: skeleton. Requires:
      - news/social stream adapter (X API, Truth Social, news wire)
      - LLM classifier with confidence + ensemble agreement
      - Latency budget < 250ms from headline to order
    """

    meta = StrategyMeta(
        id="news_butterfly",
        title="Political Tweet Butterfly Cascade",
        category="News-Driven",
        description="Classify high-signal posts and fan out to a preset asset cascade.",
        universe=list({sym for cascade in CASCADE_MAP.values() for sym, _, _ in cascade}),
        timeframe="event",
        risk_per_trade_pct=0.5,
        needs_data=["news_stream", "social_stream", "llm_classifier"],
    )

    def classify(self, headline: str) -> tuple[str | None, float]:
        """Return (event_class, confidence). Placeholder heuristic — replaced by an LLM ensemble in production.

        Confidence ramps with the number of category keywords hit, so a clear statement like
        "war with X will happen" scores higher than a casual mention.
        """
        lowered = headline.lower()
        categories: dict[str, list[str]] = {
            "war_escalation": ["war", "strike", "invasion", "missile", "attack", "happen", "will"],
            "tariff_announcement": ["tariff", "duty", "import tax", "trade war"],
            "fed_dovish_surprise": ["rate cut", "dovish", "ease", "pivot"],
            "fed_hawkish_surprise": ["rate hike", "hawkish", "tighten", "restrictive"],
        }
        scored = {
            cat: sum(1 for kw in kws if kw in lowered)
            for cat, kws in categories.items()
        }
        cat, hits = max(scored.items(), key=lambda kv: kv[1])
        if hits == 0:
            return (None, 0.0)
        confidence = min(0.55 + 0.1 * hits, 0.95)
        return (cat, confidence)

    def generate_signals(self, context: dict) -> list[Signal]:
        headline = context.get("latest_headline")
        if not headline:
            return []
        event_class, confidence = self.classify(headline)
        if not event_class or confidence < 0.75:
            return []
        signals: list[Signal] = []
        for symbol, side, magnitude in CASCADE_MAP[event_class]:
            signals.append(
                Signal(
                    symbol=symbol,
                    side=side,  # type: ignore
                    confidence=confidence * magnitude,
                    horizon_minutes=30,
                    rationale=f"{event_class} → {symbol} {side} per cascade map",
                    source=self.meta.id,
                    suggested_stop_pct=0.6,
                    suggested_take_profit_pct=1.5,
                    meta={"event_class": event_class, "headline": headline},
                )
            )
        return signals
