# eink-dashboard 📺

<https://jamesjarvis.io/projects/eink-dashboard/>

> A fun little rarely updating dashboard

![Eink-display](./images/display_angled.jpg)

## What is actually running

**[v2](./v2/) is the live system.** It runs on the Raspberry Pi Zero `pi-zero`
(`pi-zero.local`, or `pi-zero.tail8a37bd.ts.net` over Tailscale), driving a Pimoroni
InkyDev board with an Inky Impression 7-colour display, and a Pi camera. It is started by
`display.service` under systemd and shows a photo with a weather and train-times overlay.
See [the v2 README](./v2/README.md) for deploying and debugging it.

Everything below this line is **v1**, kept for reference. It targeted a Waveshare 7.5"
display driven from cron, and is no longer deployed anywhere.

## v1 views

| view                                         | script                    |
| -------------------------------------------- | ------------------------- |
| Map with precipitation radar overlaid in red | [Mappyboi](./mappyboi.py) |
| Cowsay with Dad jokes                        | [Cowsay](./cowsay.py)     |

![Cowsay mode](./images/display_cowsay.jpg)

**Disclaimer**, this is not my best work - but it's been a bit of lockdown fun :D

## v1 installation

This requires python3 installed, as well as some other additional components.

Probs worth following this stuff <https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)#Demo_code>

Then clone the repo onto the RPI, and create a new `settings.py` file from the [example provided](./settings.py.sample)

In order to run the scripts, just run

```bash
python3 mappyboi.py
```

Or whack it in a cron job to be run every 10 minutes with `crontab -e` and inputting the following:

```cron
*/10 * * * * python3 /home/pi/mappyboi.py
```
