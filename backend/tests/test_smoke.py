"""Smoke tests — verify modules import and risk manager rejects properly."""
from __future__ import annotations


def test_strategies_register():
    from money_machine.strategies import (  # noqa: F401
        macro_regime,
        multi_factor,
        news_butterfly,
        pol_latency,
        registry,
    )

    ids = {s.meta.id for s in registry.all_strategies()}
    assert {"multifactor_long_short", "news_butterfly", "pol_clob_latency", "macro_regime_rotation"}.issubset(ids)


def test_news_butterfly_classifies():
    from money_machine.strategies.news_butterfly import NewsButterflyCascade

    s = NewsButterflyCascade()
    sigs = s.generate_signals({"latest_headline": "Trump says war with Iran will happen"})
    assert len(sigs) >= 4
    assert all(0 <= sig.confidence <= 1 for sig in sigs)


def test_risk_manager_blocks_after_daily_loss():
    from money_machine.risk.manager import RiskManager
    from money_machine.strategies.base import Signal

    rm = RiskManager(equity=100_000, day_pnl_pct=-3.0, drawdown_pct=1.0, daytrades_used=0)
    sig = Signal("SPY", "long", 0.9, 60, "test", "test", 0.5, 1.0)
    sized = rm.size(sig, reference_price=500)
    assert sized.qty == 0
    assert sized.rejected_reason == "daily loss cap hit"


def test_prompt_render_replaces_placeholders():
    from money_machine.analysts.runner import render_prompt

    out = render_prompt("goldman_screener", {
        "risk_tolerance": "medium",
        "amount_usd": "100000",
        "horizon": "6m",
        "sectors": "tech,energy",
    })
    assert "medium" in out and "100000" in out and "tech,energy" in out
    assert "{{" not in out
