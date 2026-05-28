#!/usr/bin/env bash
#
# Money Machine — one-shot provisioner for Ubuntu 24.04 (Hetzner CCX13, Ashburn).
# Run as root on a fresh server:
#
#   curl -fsSL https://raw.githubusercontent.com/yanivshellbe/yanivshellbe/claude/algo-trading-system-t3MC0/deploy/deploy.sh | bash
#
# ...or clone the repo and run ./deploy/deploy.sh
#
# Idempotent: safe to re-run. Does NOT write secrets — you fill settings.env after.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/yanivshellbe/yanivshellbe.git}"
REPO_BRANCH="${REPO_BRANCH:-claude/algo-trading-system-t3MC0}"
APP_DIR="/opt/money-machine"
RUN_USER="money"

log() { echo -e "\n\033[1;32m==>\033[0m $*"; }

if [[ $EUID -ne 0 ]]; then
  echo "Run as root (sudo)." >&2
  exit 1
fi

log "Installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y \
  python3 python3-venv python3-pip git nginx ufw fail2ban chrony curl

log "Enabling NTP time sync (chrony) — required for latency strategies"
systemctl enable --now chrony
chronyc makestep || true

log "Creating run user: ${RUN_USER}"
id -u "${RUN_USER}" &>/dev/null || useradd --system --create-home --shell /usr/sbin/nologin "${RUN_USER}"

log "Cloning / updating repo at ${APP_DIR}"
if [[ -d "${APP_DIR}/.git" ]]; then
  git -C "${APP_DIR}" fetch origin "${REPO_BRANCH}"
  git -C "${APP_DIR}" checkout "${REPO_BRANCH}"
  git -C "${APP_DIR}" reset --hard "origin/${REPO_BRANCH}"
else
  git clone --branch "${REPO_BRANCH}" "${REPO_URL}" "${APP_DIR}"
fi

log "Setting up Python venv + dependencies"
python3 -m venv "${APP_DIR}/.venv"
"${APP_DIR}/.venv/bin/pip" install --upgrade pip
"${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/backend/requirements.txt"

log "Seeding settings.env (if absent)"
SETTINGS="${APP_DIR}/backend/config/settings.env"
if [[ ! -f "${SETTINGS}" ]]; then
  cp "${APP_DIR}/backend/config/settings.example.env" "${SETTINGS}"
  echo ">>> Fill in ${SETTINGS} with your ALPACA_KEY / ALPACA_SECRET / ANTHROPIC_API_KEY"
fi
chown -R "${RUN_USER}:${RUN_USER}" "${APP_DIR}"
chmod 600 "${SETTINGS}"

log "Installing systemd units"
cp "${APP_DIR}/deploy/money-machine-orchestrator.service" /etc/systemd/system/
cp "${APP_DIR}/deploy/money-machine-dream.service" /etc/systemd/system/
cp "${APP_DIR}/deploy/money-machine-dream.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable money-machine-dream.timer

log "Configuring nginx to serve the dashboard"
cp "${APP_DIR}/deploy/nginx-dashboard.conf" /etc/nginx/sites-available/money-machine
ln -sf /etc/nginx/sites-available/money-machine /etc/nginx/sites-enabled/money-machine
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

log "Firewall (ufw): allow SSH + HTTP"
ufw allow OpenSSH
ufw allow 80/tcp
ufw --force enable

log "Hardening fail2ban"
systemctl enable --now fail2ban

cat <<EOF

================================================================
  Money Machine provisioned.

  NEXT STEPS:
  1. Edit secrets:   nano ${SETTINGS}
  2. Verify Alpaca:  sudo -u ${RUN_USER} ${APP_DIR}/.venv/bin/python -m money_machine.cli status
                     (run from ${APP_DIR}/backend)
  3. Start orchestrator state refresh:
                     systemctl enable --now money-machine-orchestrator
  4. Dashboard:      http://<server-ip>/
  5. Dream timer:    systemctl list-timers money-machine-dream.timer

  Trading stays in DRY_RUN / paper until you flip both flags in settings.env.
================================================================
EOF
