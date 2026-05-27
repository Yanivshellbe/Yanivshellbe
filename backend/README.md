# backend/

Python orchestrator for the Money Machine.

## Quick start

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# fill in secrets
cp config/settings.example.env config/settings.env
# edit ALPACA_KEY / ALPACA_SECRET / ANTHROPIC_API_KEY

# sanity checks
python -m money_machine.cli personas
python -m money_machine.cli strategies
python -m money_machine.cli status              # account snapshot (mock if Alpaca not set)
python -m money_machine.cli refresh-state       # writes /dashboard/state.json

# fire a single analyst persona
python -m money_machine.cli analyst goldman_screener \
  risk_tolerance=medium amount_usd=100000 horizon=6m sectors="tech,energy"

# full nightly dream scan
python -m money_machine.cli dream
```

## Module map

```
money_machine/
├── settings.py            # env-driven config + risk caps
├── adapters/alpaca.py     # account, positions, orders (dry-run by default)
├── strategies/
│   ├── base.py            # Strategy ABC + Signal dataclass
│   ├── registry.py
│   ├── multi_factor.py        # ✓ approved
│   ├── news_butterfly.py      # ✓ approved (Trump tweet cascade)
│   ├── pol_latency.py         # ✓ approved (Polymarket CLOB lag)
│   └── macro_regime.py        # ✓ approved (sector rotation)
├── risk/manager.py        # hard caps + position sizing
├── analysts/runner.py     # renders the 22 prompt templates, calls Claude
├── dream/nightly.py       # multi-analyst overnight scan
├── orchestrator.py        # glues it all together + writes state.json
└── cli.py
```

## Safety

- `LIVE_TRADING_ENABLED=false` and `DRY_RUN=true` by default.
- `RiskManager` rejects any order that breaches daily-loss, drawdown, PDT, or position-cap.
- No order is submitted to Alpaca without **both** flags flipped explicitly.
