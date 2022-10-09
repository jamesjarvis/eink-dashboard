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

import io
import picamera
import signal
from PIL import Image, ImageDraw
from inkydev import InkyDev, PIN_INTERRUPT
import inky.inky_uc8159 as inky
import RPi.GPIO as GPIO

def take_picture() -> Image:
    """
    take_picture actually takes the picture, returning a PIL Image.
    """
    # Create the in-memory stream
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.capture(stream, format='jpeg')
    # "Rewind" the stream to the beginning so we can read its content
    stream.seek(0)
    image = Image.open(stream)
    
    # Resize and flip image for the display.
    image = image.resize(display.resolution)
    image = image.transpose(Image.FLIP_LEFT_RIGHT)

    return image

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SATURATION = 0.5

# Set up InkyDev first to power on the display
inkydev = InkyDev()

def set_all_leds(r, g, b):
    """
    set_all_leds sets all LED's to the given colour.
    """
    inkydev.set_led(0, r, g, b)
    inkydev.set_led(1, r, g, b)
    inkydev.set_led(2, r, g, b)
    inkydev.set_led(3, r, g, b)
    inkydev.update()

# Initialise all LEDs to basically off
set_all_leds(0, 5, 0)

# Set up the Inky Display
display = inky.Inky((600, 448))

def handle_interrupt(pin):
    button_a, button_b, button_c, button_d, changed = inkydev.read_buttons()

    if changed and (button_a or button_b or button_c or button_d):
        print("Taking a picture...")
        # Now we want to try and take a pic? I guess...

        set_all_leds(255, 255, 255)

        try:
            image = take_picture()

            set_all_leds(0, 0, 50)

            print("Picture taken, displaying...")

            display.set_image(image, saturation=SATURATION)
            display.show()
        except Exception as e:
            print("Failed to set the image...")
            print(e)
            set_all_leds(255, 0, 0)
            return

        set_all_leds(0, 5, 0)

        print("Picture displayed...")


GPIO.add_event_detect(PIN_INTERRUPT, GPIO.FALLING, callback=handle_interrupt)

signal.pause()
