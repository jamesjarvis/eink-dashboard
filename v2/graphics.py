from PIL import Image, ImageDraw
from datatypes import WeatherData, TrainData

SIZE_X, SIZE_Y = 448, 600

def draw_overlay(
  image: Image.Image,
  weather: WeatherData,
  train: TrainData,
):
  draw = ImageDraw.Draw(image)

  # Consistent weather box 298 x 120 px
  draw.rectangle(
    (0, SIZE_Y, 280, SIZE_Y-120), fill=(255,255,255)
  )


  image.show()