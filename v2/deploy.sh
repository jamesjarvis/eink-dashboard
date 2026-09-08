#!/usr/bin/env bash
set -euo pipefail

HOST_NAME=${DISPLAY_HOST:-pi-zero.local}
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "pi@$HOST_NAME" true 2>/dev/null; then
    echo "$HOST_NAME unreachable, falling back to tailscale"
    HOST_NAME=pi-zero.tail8a37bd.ts.net
fi

HOST=pi@$HOST_NAME
HOST_LOCATION=/home/pi/

find . -name '*.pyc' -delete

scp api.py camera.py datatypes.py display.py fonts.py graphics.py main.py storage.py settings.json "$HOST:$HOST_LOCATION"
scp -r fonts "$HOST:$HOST_LOCATION"

ssh "$HOST" 'sudo systemctl restart display.service'

echo "******************** Deployed **********************"
