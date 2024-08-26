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
# D [Portrait]:     Redraw Mode, just updates the display.

import signal
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from inkydev import PIN_INTERRUPT
import RPi.GPIO as GPIO

from display import Display
from storage import Storage
import camera
import api

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up logging.
rfh = RotatingFileHandler(
    filename="display.log",
    mode="a",
    maxBytes=20 * 1024 * 1024,  # Max file size 20MB
    backupCount=2,
    encoding=None,
    delay=0,
)
logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
    handlers=[
        rfh,
    ],
)

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
    elif button_c:
        display.led_countdown_flash(countdown_seconds=0.5)
        photo = camera.take_picture()
        storage.set_latest_image(photo)
    # If Button D pressed, redraw without taking a photo.

    # In all cases, redraw the display.
    display.redraw()
    return


# handle_interrupt can be called to run a button specific event (i.e. taking a photo)
GPIO.add_event_detect(PIN_INTERRUPT, GPIO.FALLING, callback=handle_interrupt)

while True:
    time.sleep(30)
    current_time = datetime.utcnow()

    # If the last redraw time was within the last update_interval_minutes, skip redraw.
    if display.last_redraw_time and current_time < (
        display.last_redraw_time
        + timedelta(
            minutes=float(storage.get_settings()["update_interval_minutes"]),
        )
    ):
        continue

    logging.debug("Updating data from external sources")

    try:
        logging.debug("Updating weather data")
        # Update weather data
        settings = storage.get_settings()
        weather_data = api.get_forecast(
            lat=settings["latitude"],
            lon=settings["longitude"],
            api_key=settings["tomorrow_api_key"],
        )
        weather_data.sunrise, weather_data.sunset = api.get_sunrise_and_sunset(
            lat=settings["latitude"],
            lon=settings["longitude"],
        )
        storage.set_weather_data(weather_data)

        logging.debug("Updating train data")
        # Update train data
        train_data = api.get_train_departure_times(
            username=settings["realtime_trains_username"],
            password=settings["realtime_trains_password"],
            station_code=settings["train_station"],
        )
        storage.set_train_data(train_data)
    except Exception as e:
        logging.error("error encountered while updating data", exc_info=e)

    # Redraw display
    display.redraw()

signal.pause()
