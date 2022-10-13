# V2 Eink Display

This is intended to be ran on a raspberry pi zero connected with a pi zero camer and the pimoroni InkyDev board.

Connect via ssh, then run deploy.sh.

Then copy

```bash

# Run the display boi.
sudo python3 /home/pi/picamdisplay.py & > /home/pi/logpicamdisplay.txt 2>&1

```

To `/etc/rc.local` to run the script on startup.
