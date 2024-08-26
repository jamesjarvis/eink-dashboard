# V2 Eink Display

This is intended to be ran on a raspberry pi zero connected with a pi zero camera and the pimoroni InkyDev board.

## Deploying the script

```bash
sh deploy.sh
```

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
Restart=always

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable display.service
sudo systemctl start display.service
sudo systemctl status display.service
tail -f display.log
```
