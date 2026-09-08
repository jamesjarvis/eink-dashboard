# V2 Eink Display

Runs on a Raspberry Pi Zero with a Pi camera and a Pimoroni InkyDev board driving an
Inky Impression 7-colour display (600 x 448).

The machine is `pi-zero` — `pi-zero.local` on the LAN, `pi-zero.tail8a37bd.ts.net` over
Tailscale. There is no host called `pi-zero-display`.

## Deploying the script

```bash
./deploy.sh
```

This copies the source to `/home/pi/` and restarts `display.service`. Without the restart
the running process keeps executing the old code.

## Running the script on startup

```bash
sudo nano /lib/systemd/system/display.service
```

Insert the following:

```txt
[Unit]
Description=E-ink Display
After=multi-user.target

[Service]
WorkingDirectory=/home/pi/
ExecStart=sudo /usr/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable display.service
sudo systemctl start display.service
sudo systemctl status display.service
```

## Debugging

The application log is `/home/pi/display.log`, rotated at 20MB with two backups.

```bash
ssh pi@pi-zero.local
tail -f display.log
grep -E "ERROR|WARNING" display.log | tail -40
systemctl status display.service
journalctl -u display.service -n 100   # slow on a Pi Zero, be patient
```

A healthy cycle logs `Updating data from external sources`, then `Beginning Display Redraw`,
then `Redraw complete`, and then `too soon, skipping for now` every 10 seconds until the next
`update_interval_minutes` window.

`Beginning Display Redraw` to `Redraw complete` should be about 31 seconds. A redraw that
finishes in under 10 seconds did not complete its waveform and will have left a corrupted
frame on the panel.

Each redraw performs four busy waits, logged as `Busy wait after reset`, `power on`,
`display refresh` and `power off`. A pin that reads high has no signal to wait on, so the
driver sleeps out the 90 second timeout instead and the redraw takes a multiple of that:

```bash
grep -o "Busy wait after [a-z ]*: pin held high" display.log | sort | uniq -c
```

That count over a few days tells us which command the panel fails to signal against, which
is the open question behind the slow redraws.

Weather and train fetches are best-effort. If either fails the last known good data is kept,
the display still redraws, and the D button LED turns red until the next successful cycle.
