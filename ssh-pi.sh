#!/bin/bash
# SSH connection script for Raspberry Pi
# Host:     192.168.29.6
# User:     pi
# Password: pi

HOST="192.168.29.6"
USER="pi"
PASSWORD="pi"

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$USER@$HOST" "$@"
