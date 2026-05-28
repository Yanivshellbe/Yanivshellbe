# Yaniv Money Machine — Operator Brief (CLAUDE.md)

Auto-loaded by Claude Code. This file is the single source of truth for operating the
live system. Read it fully before acting on the server.

## What this is

An algorithmic trading system on an **Alpaca paper account ($100k)**. Two tracks:
a calm "core chassis" (multi-factor long/short + macro regime rotation) and a spiky
"alpha turbo" (political-tweet butterfly cascade, Polymarket CLOB-latency scalper,
earnings IV, insider-follow). A static dashboard ("Control Tower") visualizes account,
strategies, ideas (with red-team), backtests, and nightly "dream scans". A nightly
multi-analyst scan runs 22 prompt personas (Goldman/MS/Bridgewater/JPM/BlackRock/
Citadel/Harvard/Bain/RenTech/McKinsey + 12 Quant Lab templates).

## Division of labor

- A **cloud Claude Code session** authors code and pushes to branch
  `claude/algo-trading-system-t3MC0`. It CANNOT reach the server (egress-blocked).
- **You (local Claude Code on the Mac)** operate the live server: `git pull`, run,
  monitor, fix, and drive the browser when needed.
- Loop: cloud Claude pushes → you `git pull` on the droplet → restart services.

## Live deployment (confirmed 2026-05-28)

- **Server:** DigitalOcean droplet `money-machine-01`, NYC3, Ubuntu 24.04, 2GB/1vCPU.
- **Public IP:** `64.225.10.165`  ·  Dashboard: http://64.225.10.165/
- **SSH:** `ssh root@64.225.10.165` (owner has the root password).
- **App dir:** `/opt/money-machine`  ·  **venv:** `/opt/money-machine/.venv`
- **Run user:** `money` (non-root, system user).
- **Secrets:** `/opt/money-machine/backend/config/settings.env` (chmod 600, gitignored).
- **Status:** Alpaca handshake CONFIRMED — real paper account, $100k equity / $200k
  buying power. `money-machine-orchestrator` service is **active**, rewriting
  `dashboard/state.json` every 30s. Live trading is **OFF**.

## Server operations

```bash
# Update code to latest
cd /opt/money-machine && git pull && systemctl restart money-machine-orchestrator

# CLI (always as the 'money' user)
cd /opt/money-machine/backend
sudo -u money /opt/money-machine/.venv/bin/python -m money_machine.cli status        # account snapshot
sudo -u money /opt/money-machine/.venv/bin/python -m money_machine.cli strategies    # registered strategies
sudo -u money /opt/money-machine/.venv/bin/python -m money_machine.cli personas      # 22 analyst personas
sudo -u money /opt/money-machine/.venv/bin/python -m money_machine.cli dream         # nightly multi-analyst scan
sudo -u money /opt/money-machine/.venv/bin/python -m money_machine.cli analyst <id> k=v ...

# Services
systemctl status money-machine-orchestrator --no-pager
journalctl -u money-machine-orchestrator -f          # live logs
systemctl list-timers money-machine-dream.timer       # nightly dream schedule

# Tests
cd /opt/money-machine/backend && /opt/money-machine/.venv/bin/python -m pytest tests/ -q
```

## Known issues & fixes

- **cloud-init `&>` bashism** (FIXED in `deploy/cloud-init.yaml`): cloud-init runs runcmd
  with `/bin/sh`, where `&>` backgrounds instead of redirecting, so the `money` user was
  never created → orchestrator failed `217/USER`. On the running box the user was created
  manually. Any rebuild uses the fixed line.

## Security TODO (do soon — credentials were exposed in a chat transcript)

1. **Rotate root password:** `passwd` on the server; save in a password manager. It's
   currently weak and was pasted in chat.
2. **Rotate Alpaca keys:** regenerate in Alpaca dashboard, then
   `nano /opt/money-machine/backend/config/settings.env` (update ALPACA_KEY/SECRET) →
   `systemctl restart money-machine-orchestrator`. Old keys were in chat + DO user-data.
3. **Harden SSH:** add an SSH key, then disable password auth.
4. **Repo visibility:** currently PUBLIC (no secrets committed — verified). Consider
   switching back to private with a read-only deploy key on the droplet.

## Roadmap (strategies are SKELETONS — they return no signals yet)

Build order (recommended):
1. **Simple Alpaca-only momentum/trend strategy** → prove the full loop
   (data → signal → RiskManager → paper order) with zero external feeds. Fastest win.
2. `macro_regime_rotation` → needs FRED adapter.
3. `multifactor_long_short` → needs point-in-time fundamentals + price history.
4. `news_butterfly` → needs X/news stream + LLM classifier (X API ≈ $100/mo).
5. `pol_clob_latency` → needs Polymarket CLOB WS + Binance spot WS + NTP sync.

Also: `ANTHROPIC_API_KEY` is blank → analyst/dream layer is dry-run only. Add a key to
enable real analyst output.

## Safety rules (do not violate)

- `LIVE_TRADING_ENABLED=false` and `DRY_RUN=true` MUST stay until the owner explicitly
  approves going live. No order reaches Alpaca without both flags flipped.
- `RiskManager` enforces: daily-loss 2%, drawdown 8%, position 10% of equity, PDT count.
  Do not weaken these without owner sign-off.
- Never commit `settings.env` or any secret. Never paste Live (real-money) keys anywhere.
- Confirm with the owner before paid, destructive, or irreversible actions.

## Repo map

```
dashboard/            static Control Tower (served by nginx on :80)
  data/{analysts,ideas,prompts}.json
backend/money_machine/
  orchestrator.py     glue + writes dashboard/state.json
  adapters/alpaca.py  account/positions/orders (dry-run by default)
  strategies/         base, registry, 4 skeleton strategies
  risk/manager.py     hard caps + position sizing
  analysts/runner.py  renders 22 templates, calls Anthropic
  dream/nightly.py    nightly multi-analyst scan
  cli.py
deploy/               cloud-init.yaml, deploy.sh, systemd units, nginx conf
docs/                 ARCHITECTURE, IDEAS_RED_TEAM, BROWSER_CONTROL
```
