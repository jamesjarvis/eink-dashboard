import inky.inky_uc8159 as inky
from inkydev import InkyDev
from time import sleep
import logging
import datetime

import camera
import api

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

    def led_reset_to_default(self):
        """
        setup_leds will set all LEDs to their default colours.
        """
        # Initialise LEDs for their program function
        # 0: Photo  (blue)
        # 1: Photo  (blue)
        # 2: Photo  (blue)
        # 3: Photo with 3 sec delay (green)
        self.inky_dev.set_led(0, 0, 0, 5)
        self.inky_dev.set_led(1, 0, 0, 5)
        self.inky_dev.set_led(2, 0, 0, 5)
        self.inky_dev.set_led(3, 0, 5, 0)
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
            sleep(countdown_seconds/4)

        # Camera flash, set to bright white
        self.led_set_all(255, 255, 255)

    def redraw(self):
        """
        redraw redraws the display with the latest available information.
        """
        # Set all LEDs to a low blue colour to indicate a refresh is happening.
        logging.debug("Redrawing display")
        self.led_set_all(0, 0, 50)
        
        # TODO: Draw display.

        self.last_redraw_time = datetime.datetime.utcnow()
        logging.debug("Redraw complete")
