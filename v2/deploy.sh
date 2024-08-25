#!/usr/bin/bash

rm **/**/*.pyc

HOST=pi@pi-zero.local
HOST_LOCATION=/home/pi/

scp api.py $HOST:$HOST_LOCATION
scp camera.py $HOST:$HOST_LOCATION
scp datatypes.py $HOST:$HOST_LOCATION
scp display.py $HOST:$HOST_LOCATION
scp main.py $HOST:$HOST_LOCATION
scp storage.py $HOST:$HOST_LOCATION
scp settings.json $HOST:$HOST_LOCATION

echo "******************** Deployed **********************"
