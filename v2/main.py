#!/usr/bin/env python3

# Welcome to eink-display-v2!
#
# This is a script that is designed to load on boot on a Raspberry Pi Zero connected to a
# Pimoroni Inky display (600 X 448) 7 Colour with a Pi camera attached.
#
# Current features (mapped to each of the 4 buttons):
# A [Portrait]:     Photo Mode with 3 second delay, takes a pic and displays.
# B [Portrait]:     Photo Mode, takes a pic and displays.
# C [Portrait]:     Photo Mode, takes a pic and displays.
# D [Portrait]:     Photo Mode, takes a pic and displays.

import signal
import time
from datetime import datetime, timedelta
from inkydev import PIN_INTERRUPT
import RPi.GPIO as GPIO

from display import Display
from storage import Storage
import camera

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up the storage.
storage = Storage()

# Set up the display logic.
display = Display(
    storage=storage,
)


def handle_interrupt(pin):
    """
    handle_interrupt is called any time a button is pressed on the display.
    Handles user events.
    """
    button_a, button_b, button_c, button_d, changed = display.inky_dev.read_buttons()

    if not changed:
        return

    # If Button A pressed, take a photo with a 3 second delay
    if button_a:
        display.led_countdown_flash(countdown_seconds=3)
        photo = camera.take_picture()
        storage.set_latest_image(photo)
    # If Button B pressed, take a photo with a 500ms delay.
    elif button_b:
        display.led_countdown_flash(countdown_seconds=0.5)
        photo = camera.take_picture()
        storage.set_latest_image(photo)
    # If Button C pressed, take a photo with a 500ms delay.
    elif button_b:
        display.led_countdown_flash(countdown_seconds=0.5)
        photo = camera.take_picture()
        storage.set_latest_image(photo)
    # If Button D pressed, take a photo with a 500ms delay.
    elif button_d:
        display.led_countdown_flash(countdown_seconds=0.5)
        photo = camera.take_picture()
        storage.set_latest_image(photo)

    # In all cases, redraw the display.
    display.redraw()
    return

# handle_interrupt can be called to run a button specific event (i.e. taking a photo)
GPIO.add_event_detect(PIN_INTERRUPT, GPIO.FALLING, callback=handle_interrupt)

while True:
    time.sleep(30)
    current_time = datetime.utcnow()

    # Update every update_interval_minutes
    if not display.last_redraw_time or current_time > (display.last_redraw_time + timedelta(
        minutes = float(storage.get_settings()["update_interval_minutes"]),
    )):
        display.redraw()

signal.pause()
