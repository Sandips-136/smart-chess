#!/bin/bash
# Reboot the Raspberry Pi.
#
# Usage:
#   ./reboot-pi.sh           # ask for confirmation, then reboot
#   ./reboot-pi.sh --yes     # reboot without asking
#
# After running, the Pi will drop the SSH connection and take ~30-60s to come
# back. Wait until you can ping it again before running ./start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../deploy/config.sh"

if ! command -v sshpass >/dev/null 2>&1; then
    echo "Error: sshpass is not installed. Install it with: brew install sshpass"
    exit 1
fi

if [ "$1" != "--yes" ] && [ "$1" != "-y" ]; then
    read -p "Reboot Raspberry Pi at $PI_HOST? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $PI_PORT"

echo "Sending reboot to $PI_USER@$PI_HOST ..."
# Use 'echo pi' to feed the sudo password. Connection will drop — that's expected.
sshpass -p "$PI_PASSWORD" ssh $SSH_OPTS "$PI_USER@$PI_HOST" "echo $PI_PASSWORD | sudo -S reboot" || true

echo
echo "Reboot command sent. The Pi will be back in ~30-60 seconds."
echo "Tip: run    ping $PI_HOST    until it responds, then ./start.sh"
