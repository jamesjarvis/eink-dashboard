import inky.inky_uc8159 as inky
from inkydev import InkyDev
from time import sleep
from PIL import Image
import logging
import datetime

import camera
import api
import graphics

from storage import Storage

SIZE_X, SIZE_Y = 600, 448
SATURATION = 0.5


class Display:
    """
    Display contains all logic for driving the InkyDev display and LEDs.
    Fundamentally we have a "background" and a "overlay" component to the UI.
    The background is an image, that is set to the total size of the display, and the overlay
    is a section of the display roughly 1/3rd the height of the display, from the bottom.
    It will contain:
    - Weather (bottom left)
    - Train times + important days (bottom right)

    The display is in portrait mode.
    """

    def __init__(
        self,
        storage: Storage,
    ):
        self.inky_display = inky.Inky((SIZE_X, SIZE_Y))
        self.inky_dev = InkyDev()
        self.storage = storage
        self.last_redraw_time = None

        self.led_reset_to_default()

    def led_reset_to_default(self, errored=False):
        """
        setup_leds will set all LEDs to their default colours.
        """
        # Initialise LEDs for their program function
        # A: Photo with 3 sec delay (green)
        # B: Photo      (blue)
        # C: Photo      (blue)
        # D: Redraw     (error=red, no_error=blue)
        self.inky_dev.set_led(0, 0, 5, 0)
        self.inky_dev.set_led(1, 0, 0, 3)
        self.inky_dev.set_led(2, 0, 0, 3)
        if errored:
            self.inky_dev.set_led(3, 5, 0, 0)
        else:
            self.inky_dev.set_led(3, 0, 0, 2)
        self.inky_dev.update()

    def led_set_all(self, r, g, b, update=True):
        """
        set_all_leds sets all LED's to the given colour.
        """
        self.inky_dev.set_led(0, r, g, b)
        self.inky_dev.set_led(1, r, g, b)
        self.inky_dev.set_led(2, r, g, b)
        self.inky_dev.set_led(3, r, g, b)
        if update:
            self.inky_dev.update()

    def led_countdown_flash(self, countdown_seconds: float):
        """
        led_countdown_flash counts down for the provided seconds,
        then sets all LEDs to bright white as a "flash"
        """
        for i in range(4, 0, -1):
            self.led_set_all(0, 0, 0, update=False)
            if i > 0:
                self.inky_dev.set_led(0, 255, 255, 255)
            if i > 1:
                self.inky_dev.set_led(1, 255, 255, 255)
            if i > 2:
                self.inky_dev.set_led(2, 255, 255, 255)
            if i > 3:
                self.inky_dev.set_led(3, 255, 255, 255)
            self.inky_dev.update()
            sleep(countdown_seconds / 4)

        # Camera flash, set to bright white
        self.led_set_all(255, 255, 255)

    def redraw(self):
        """
        redraw redraws the display with the latest available information.
        """
        # Set all LEDs to a low blue colour to indicate a refresh is happening.
        logging.debug("Redrawing display")
        self.led_set_all(0, 0, 50)
        self.last_redraw_time = datetime.datetime.utcnow()

        # Background image.
        image = self.storage.get_latest_image()
        # Get the original dimensions
        original_width, original_height = image.size

        # Calculate the new dimensions for the 3:4 aspect ratio
        # To maintain maximum resolution, we'll match the height and crop the width
        new_height = original_height
        new_width = int(new_height * (3 / 4))

        # If the new width is greater than the original width, adjust for height instead
        if new_width > original_width:
            new_width = original_width
            new_height = int(new_width * (4 / 3))

        # Calculate the cropping box (centered)
        left = (original_width - new_width) / 2
        top = (original_height - new_height) / 2
        right = (original_width + new_width) / 2
        bottom = (original_height + new_height) / 2

        # Crop the image
        image = image.crop((left, top, right, bottom))
        # Flip image for the display.
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        # Resize for the rest of the render logic.
        image = image.resize((SIZE_Y, SIZE_X))

        # Draw overlay on top.
        image = graphics.draw_overlay(
            image=image,
            weather=self.storage.get_weather_data(),
            train=self.storage.get_train_data(),
        )

        # Rotate to set back onto the display
        image = image.rotate(90, expand=True)

        # Draw onto display.
        logging.info("Beginning Display Redraw")

        self.inky_display.set_image(image, saturation=SATURATION)
        self.inky_display.show()

        logging.debug("Redraw complete")

        self.led_reset_to_default()
