#!/usr/bin/env python3

import io
import picamera
import signal
from PIL import Image, ImageDraw
from inkydev import InkyDev, PIN_INTERRUPT
import inky.inky_uc8159 as inky
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up InkyDev first to power on the display
inkydev = InkyDev()

# Set up the Inky Display
display = inky.Inky((600, 448))

# Create our drawing surface (a PIL Image)
image = Image.new("P", display.resolution)
draw = ImageDraw.Draw(image)

def handle_interrupt(pin):
    button_a, button_b, button_c, button_d, changed = inkydev.read_buttons()

    if changed and (button_a or button_b or button_c or button_d):
        print("Taking a picture...")
        # Now we want to try and take a pic? I guess...

        inkydev.set_led(0, 255, 255, 255)
        inkydev.set_led(1, 255, 255, 255)
        inkydev.set_led(2, 255, 255, 255)
        inkydev.set_led(3, 255, 255, 255)
        inkydev.update()

        # Create the in-memory stream
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            camera.capture(stream, format='jpeg')
        # "Rewind" the stream to the beginning so we can read its content
        stream.seek(0)
        image = Image.open(stream)
        image.resize(display.resolution)

        print("Picture taken, displaying...")

        display.set_image(image)
        display.show()

        inkydev.set_led(0, 0, 0, 0)
        inkydev.set_led(1, 0, 0, 0)
        inkydev.set_led(2, 0, 0, 0)
        inkydev.set_led(3, 0, 0, 0)
        inkydev.update()

        print("Picture displayed...")


GPIO.add_event_detect(PIN_INTERRUPT, GPIO.FALLING, callback=handle_interrupt)

signal.pause()