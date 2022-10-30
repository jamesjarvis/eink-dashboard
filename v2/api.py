import requests
from io import BytesIO
from PIL import Image

def xkcd() -> Image.Image:
    """
    xkcd will fetch a random XKCD comic, and return as a PIL.Image.
    """
    URL = "https://pimoroni.github.io/feed2image/xkcd-daily.jpg"
    r = requests.get(URL)
    if r.status_code != 200:
      print("failed download of xkcd!!")
      return None
    image = Image.open(BytesIO(r.content))
    return image
