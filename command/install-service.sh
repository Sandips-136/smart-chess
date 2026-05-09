#!/bin/bash
# Install (or refresh) the chessDIYM systemd unit on the Pi so the chess
# program autostarts on boot using the smartenv virtualenv.
#
# Usage:
#   ./install-service.sh           # install + enable + start
#   ./install-service.sh --status  # just show current status / recent logs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../deploy/config.sh"

if ! command -v sshpass >/dev/null 2>&1; then
    echo "Error: sshpass is not installed. Install it with: brew install sshpass"
    exit 1
fi

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $PI_PORT"
SSH="sshpass -p $PI_PASSWORD ssh $SSH_OPTS $PI_USER@$PI_HOST"

if [[ "${1:-}" == "--status" ]]; then
    $SSH "sudo systemctl status chessDIYM --no-pager; echo; echo '--- last 30 journal lines ---'; sudo journalctl -u chessDIYM -n 30 --no-pager"
    exit 0
fi

REMOTE_UNIT="$PI_REMOTE_PATH/chessDIYM.service"

echo "Installing chessDIYM.service from $REMOTE_UNIT ..."
$SSH bash -s <<EOF
set -e
if [ ! -f "$REMOTE_UNIT" ]; then
    echo "Unit file not found at $REMOTE_UNIT — run ./deploy/push-to-pi.sh first."
    exit 1
fi
sudo cp "$REMOTE_UNIT" /etc/systemd/system/chessDIYM.service
sudo systemctl daemon-reload
sudo systemctl enable chessDIYM.service
sudo systemctl restart chessDIYM.service
sleep 1
sudo systemctl status chessDIYM --no-pager || true
EOF

echo
echo "Done. Tail logs with:  ./command/install-service.sh --status"
echo "Or live:               ./command/ssh-pi.sh 'sudo journalctl -u chessDIYM -f'"
