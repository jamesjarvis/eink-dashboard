
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
  Fundamentally we have a "background" and a "overlay" component to the UI.
  The background is an image, that is set to the total size of the display, and the overlay
  is a section of the display roughly 1/3rd the height of the display, from the bottom.
  It will contain:
  - Weather (bottom left)
  - Train times + important days (bottom right)
  """
  def __init__(self):
    self.inky_display = inky.Inky((SIZE_X, SIZE_Y))
    self.inky_dev = InkyDev()
    
    self.setup_leds()

  def setup_leds(self):
    """
    setup_leds will set all LEDs to their default colours.
    """
    # Initialise LEDs for their program function
    # 0: XKCD   (white)
    # 1: Photo  (blue)
    # 2: Photo  (blue)
    # 3: Photo with 3 sec delay (green)
    self.inky_dev.set_led(0, 5, 5, 5)
    self.inky_dev.set_led(1, 0, 0, 5)
    self.inky_dev.set_led(2, 0, 0, 5)
    self.inky_dev.set_led(3, 0, 5, 0)
    self.inky_dev.update()

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

      image = image.resize(self.inky_display.resolution)
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

      self.inky_display.set_image(image)
      self.inky_display.show()
    except Exception as e:
      print("Failed to set the image...")
      print(e)
      self.set_all_leds(255, 0, 0)
      return

    print("Comic displayed...")
  