
import inky.inky_uc8159 as inky
from inkydev import InkyDev
import camera

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
    display.set_all_leds(0, 5, 0)

  def set_all_leds(self, r, g, b):
    """
    set_all_leds sets all LED's to the given colour.
    """
    self.inky_dev.set_led(0, r, g, b)
    self.inky_dev.set_led(1, r, g, b)
    self.inky_dev.set_led(2, r, g, b)
    self.inky_dev.set_led(3, r, g, b)
    self.inky_dev.update()

  def take_picture(self, delay:int):
    """
    take_picture takes a picture with the onboard camera,
    after the given delay (in seconds).
    Then it will update the onboard delay with the picture.
    """
    print("Taking a picture...")
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

    self.set_all_leds(0, 5, 0)

    print("Picture displayed...")
  