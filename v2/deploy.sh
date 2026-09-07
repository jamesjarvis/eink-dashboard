#!/usr/bin/env bash
set -euo pipefail

HOST=pi@pi-zero.local
HOST_LOCATION=/home/pi/

find . -name '*.pyc' -delete

scp api.py camera.py datatypes.py display.py fonts.py graphics.py main.py storage.py settings.json "$HOST:$HOST_LOCATION"
scp -r fonts "$HOST:$HOST_LOCATION"

ssh "$HOST" 'sudo systemctl restart display.service'

echo "******************** Deployed **********************"
