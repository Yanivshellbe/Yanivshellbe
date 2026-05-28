# Deploy — Money Machine on a fresh Ubuntu 24.04 server

Target: Hetzner CCX13, Ashburn VA (closest metro to Alpaca / Polymarket on AWS us-east-1).

## One-shot provision

SSH into the box, then:

```bash
curl -fsSL https://raw.githubusercontent.com/yanivshellbe/yanivshellbe/claude/algo-trading-system-t3MC0/deploy/deploy.sh | sudo bash
```

This installs Python + nginx + chrony (NTP) + ufw + fail2ban, clones the repo to
`/opt/money-machine`, builds the venv, installs systemd units, and serves the
dashboard on port 80. It does **not** write secrets.

## After provisioning

```bash
# 1. secrets
sudo nano /opt/money-machine/backend/config/settings.env
#    fill ALPACA_KEY / ALPACA_SECRET / ANTHROPIC_API_KEY

# 2. verify Alpaca handshake (mock if unset, real account if set)
cd /opt/money-machine/backend
sudo -u money /opt/money-machine/.venv/bin/python -m money_machine.cli status

# 3. start the state-refresh loop (writes dashboard/state.json every 30s)
sudo systemctl enable --now money-machine-orchestrator

# 4. open the dashboard
#    http://<server-ip>/

# 5. nightly dream scan is on a timer (03:00 server time)
systemctl list-timers money-machine-dream.timer
```

## Safety

`LIVE_TRADING_ENABLED=false` and `DRY_RUN=true` ship by default. No order
reaches Alpaca until both are flipped in `settings.env` and the service is
restarted. The `RiskManager` still enforces daily-loss / drawdown / PDT /
position caps even when live.

## Files

| File | Purpose |
|---|---|
| `deploy.sh` | idempotent provisioner |
| `money-machine-orchestrator.service` | 30s state-refresh loop |
| `money-machine-dream.service` + `.timer` | nightly multi-analyst scan |
| `nginx-dashboard.conf` | serves `/opt/money-machine/dashboard` on :80 |
