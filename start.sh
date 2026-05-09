#!/bin/bash
# SSH into the Raspberry Pi and run the chess app inside the smartenv virtualenv.
#
# Usage:
#   ./start.sh                              # runs StartChessGame.py
#   ./start.sh StartChessGameStockfish.py   # runs a different entry script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/deploy/config.sh"

if ! command -v sshpass >/dev/null 2>&1; then
    echo "Error: sshpass is not installed. Install it with: brew install sshpass"
    exit 1
fi

ENTRY_SCRIPT="${1:-StartChessGame.py}"

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $PI_PORT"

REMOTE_CMD="cd $PI_REMOTE_PATH && source smartenv/bin/activate && python $ENTRY_SCRIPT"

echo "Connecting to $PI_USER@$PI_HOST and running: $ENTRY_SCRIPT"
sshpass -p "$PI_PASSWORD" ssh -t $SSH_OPTS "$PI_USER@$PI_HOST" "$REMOTE_CMD"
