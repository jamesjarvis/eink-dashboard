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

Every redraw ends with a summary line carrying its duration, how many of its four busy
waits stalled, and the machine's temperature and throttling bitmask:

```txt
Redraw complete in 31.4s, 0/4 busy waits held high (none), soc 37.4C throttled=0x0
Redraw complete in 274.1s, 3/4 busy waits held high (power on, display refresh, power off), soc 41.2C throttled=0x0
```

A healthy redraw is about 31 seconds with no stalled waits. Anything under 10 seconds did
not finish its waveform and has left a corrupted frame on the panel — that should not
happen now, and if it does the busy wait has regressed again.

```bash
grep -oE "[0-9]/4 busy waits held high" display.log | sort | uniq -c
grep "held high" display.log | grep -oE "soc [0-9.]+C" | sort -n | uniq -c
```

Weather and train fetches are best-effort. If either fails the last known good data is kept,
the display still redraws, and the D button LED turns red until the next successful cycle.

## The busy pin stalls

The panel often fails to signal on its busy pin. The driver then has nothing to wait on and
sleeps out its 90 second timeout, so a redraw takes 90, 180 or 270 seconds instead of 31.
Analysis of 7270 redraws between 2026-07-06 and 2026-09-08:

- Each individual wait stalls about 23% of the time.
- It is not specific to one command. `display refresh` stalls at 21.5%, `power on` and
  `power off` together at 24.0%.
- It is not independent per wait. All three stalling together happened 1020 times against
  90 expected by chance, so a redraw tends to stall entirely or not at all.
- It persists. Runs reach 194 consecutive stalled redraws (about 32 hours) and 883
  consecutive clean ones (about 6 days).

That shape rules out a per-cycle timing race, which is what commit 9770813 assumed when it
replaced the busy wait with a short poll and corrupted the panel. Do not attempt another
timing fix. The cause is still unknown; under-voltage is currently ruled out, with
`throttled=0x0` across a 23 hour window that included a heavily stalling period.
