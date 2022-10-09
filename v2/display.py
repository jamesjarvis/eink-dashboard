
import inky.inky_uc8159 as inky
from inkydev import InkyDev
from time import sleep

import camera
import api

SIZE_X, SIZE_Y = 600, 448
SATURATION = 0.5

class Display():
  """
  Display contains all logic for driving the InkyDev display.
  """
  def __init__(self):
    self.inky_display = inky.Inky((SIZE_X, SIZE_Y))
    self.inky_dev = InkyDev()
    
    self.setup_leds()

  def setup_leds(self):
    """
    setup_leds will set all LEDs to their default colours.
    """
    # Initialise all LEDs to basically off
    self.set_all_leds(0, 5, 0)

  def set_all_leds(self, r, g, b, update=True):
    """
    set_all_leds sets all LED's to the given colour.
    """
    self.inky_dev.set_led(0, r, g, b)
    self.inky_dev.set_led(1, r, g, b)
    self.inky_dev.set_led(2, r, g, b)
    self.inky_dev.set_led(3, r, g, b)
    if update:
      self.inky_dev.update()

  def take_picture(self, delay:int):
    """
    take_picture takes a picture with the onboard camera,
    after the given delay (in seconds).
    Then it will update the onboard display with the picture.
    """
    print("Taking a picture...")

    # Start the countdown
    for i in range(delay, 0, -1):
      self.set_all_leds(0, 0, 0, update=False)
      if i > 0:
        self.inky_dev.set_led(0, 255, 255, 255)
      if i > 1:
        self.inky_dev.set_led(1, 255, 255, 255)
      if i > 2:
        self.inky_dev.set_led(2, 255, 255, 255)
      if i > 3:
        self.inky_dev.set_led(3, 255, 255, 255)
      self.inky_dev.update()
      sleep(1)

    # Now we want to try and take a pic? I guess...

    self.set_all_leds(255, 255, 255)

    try:
      image = camera.take_picture()

      self.set_all_leds(0, 0, 50)

      print("Picture taken, displaying...")

      self.inky_display.set_image(image, saturation=SATURATION)
      self.inky_display.show()
    except Exception as e:
      print("Failed to set the image...")
      print(e)
      self.set_all_leds(255, 0, 0)
      return

    print("Picture displayed...")

  def xkcd(self):
    """
    xkcd will display a random XKCD comic every day.
    """
    print("Fetching XKCD...")
    
    try:
      image = api.xkcd()

      self.set_all_leds(0, 0, 50)

      print("Comic fetched, displaying...")

      self.inky_display.set_image(image, saturation=SATURATION)
      self.inky_display.show()
    except Exception as e:
      print("Failed to set the image...")
      print(e)
      self.set_all_leds(255, 0, 0)
      return
  