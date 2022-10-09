#!/usr/bin/env python3

# Welcome to eink-display-v2!
# 
# This is a script that is designed to load on boot on a Raspberry Pi Zero connected to a
# Pimoroni Inky display (600 X 448) 7 Colour with a Pi camera attached.
# 
# Current features (mapped to each of the 4 buttons):
# 0 [Landscape]:    XKCD Daily cartoon, updates every 12 hours.
# 1 [Any]:          Photo Mode, takes a pic and displays.
# 2 [Any]:          Photo Mode, takes a pic and displays.
# 3 [Any]:          Photo Mode with 3 second delay, takes a pic and displays.

import signal
from inkydev import PIN_INTERRUPT
import RPi.GPIO as GPIO

from .display import Display

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up the display logic.
display = Display(inky_display)

def handle_interrupt(pin):
    button_a, button_b, button_c, button_d, changed = inkydev.read_buttons()

    if not changed:
        return

    if button_a:
        return
    if button_b or button_c:
        display.take_picture(0)
        return
    if button_d:
        display.take_picture(4)
        return


GPIO.add_event_detect(PIN_INTERRUPT, GPIO.FALLING, callback=handle_interrupt)

signal.pause()
