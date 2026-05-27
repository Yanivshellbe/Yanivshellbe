# Idea Red-Team — Round 1

Each idea was attacked along five axes before being marked **approved for paper research** or **rejected**.

| Axis | What we check |
|---|---|
| Edge | Why this works; how long it survives |
| Execution | Latency, fills, slippage, halts |
| Risk | Tail outcomes, blow-up scenarios |
| Legal/Reg | Account type, jurisdiction, market rules |
| Capital | Sizing, scale ceiling |

Status summary:

| Idea | Status | Owner module |
|---|---|---|
| Polymarket CLOB latency scalper | ✅ approved for paper research | `strategies/pol_latency.py` |
| Trump / political tweet butterfly cascade | ✅ approved for paper research | `strategies/news_butterfly.py` |
| Earnings implied-move drift | ✅ approved for paper research | `strategies/earnings_iv.py` (TODO) |
| Macro regime sector rotation | ✅ approved for paper research | `strategies/macro_regime.py` |
| Multi-factor long/short equity | ✅ approved for paper research | `strategies/multi_factor.py` |
| VIX term-structure carry | ✅ approved for paper research | `strategies/vix_carry.py` (TODO) |
| Insider Form 4 / 13D follow | ✅ approved for paper research | `strategies/insider_follow.py` (TODO) |
| Cross-venue equity latency arb | ❌ rejected — not feasible via Alpaca retail | — |

Full per-idea attack analysis lives in `/dashboard/data/ideas.json` and is rendered in the dashboard's **Idea Book + Red-Team** card.

## Strategy combination plan

Two-track portfolio:

- **Core chassis (70% of capital)** — Multi-factor L/S + macro regime rotation. Low frequency, beta-neutral, designed to chug along without blowing up.
- **Alpha turbo (30% of capital)** — News-butterfly cascade + Polymarket latency + earnings IV + insider follow. Spiky, event-driven, harvested with tight stops.

When the alpha turbo has 2 consecutive losing weeks → drop to 15%. When it has 2 consecutive winning weeks → push back to 30% (max).
