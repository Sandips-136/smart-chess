#!/bin/bash
# Push local code to the Raspberry Pi using credentials from config.sh
#
# Usage:
#   ./push-to-pi.sh                # push everything (except excluded folders)
#   ./push-to-pi.sh --dry-run      # show what would be pushed without copying
#   ./push-to-pi.sh <file/folder>  # push a single file or folder

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if ! command -v sshpass >/dev/null 2>&1; then
    echo "Error: sshpass is not installed. Install it with: brew install sshpass"
    exit 1
fi

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $PI_PORT"

if [ -n "$1" ] && [ "$1" != "--dry-run" ]; then
    # Push a specific file or folder
    SRC="$1"
    if [ ! -e "$SRC" ]; then
        echo "Error: '$SRC' does not exist"
        exit 1
    fi
    REL_PATH="${SRC#$LOCAL_PATH/}"
    echo "Pushing $SRC -> $PI_USER@$PI_HOST:$PI_REMOTE_PATH/$REL_PATH"
    sshpass -p "$PI_PASSWORD" rsync -avz \
        "${RSYNC_EXCLUDES[@]}" \
        -e "ssh $SSH_OPTS" \
        "$SRC" \
        "$PI_USER@$PI_HOST:$PI_REMOTE_PATH/$REL_PATH"
else
    DRY_RUN=""
    if [ "$1" = "--dry-run" ]; then
        DRY_RUN="--dry-run"
        echo "DRY RUN — no files will actually be copied"
    fi
    echo "Pushing $LOCAL_PATH/ -> $PI_USER@$PI_HOST:$PI_REMOTE_PATH/"
    sshpass -p "$PI_PASSWORD" rsync -avz $DRY_RUN \
        "${RSYNC_EXCLUDES[@]}" \
        -e "ssh $SSH_OPTS" \
        "$LOCAL_PATH/" \
        "$PI_USER@$PI_HOST:$PI_REMOTE_PATH/"
fi

echo "Done."
