#!/bin/bash
# Raspberry Pi connection credentials
# Sourced by other deploy scripts. Do NOT commit this file to a public repo.

PI_HOST="192.168.29.6"
PI_USER="pi"
PI_PASSWORD="pi"
PI_PORT="22"

# Remote path on the Pi where code will be pushed
PI_REMOTE_PATH="/home/pi/SmartChess/RaspberryPiCode"

# Local path on the Mac to push from
LOCAL_PATH="/Users/sandipsingh/smart-chess/RaspberryPiCode"

# Files / folders to exclude when syncing
RSYNC_EXCLUDES=(
    "--exclude=chessenv/"
    "--exclude=smartenv/"
    "--exclude=__pycache__/"
    "--exclude=*.pyc"
    "--exclude=.git/"
    "--exclude=.DS_Store"
)
