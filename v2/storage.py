from .datatypes import WeatherData
import json
from PIL import Image
import os


class Storage:
    """
    Storage controls read and write access to the following data required for the display to function:
    (Background)
    - XKCD image
    - Photo
    (Overlay)
    - Weather Data
    - Train Arrival Data
    - Important Days
    """

    def __init__(
        self,
        settings_filename: str = "settings.json",
        latest_image_filename: str = "latest_photo.png",
        weather_data_filename: str = "weather_data.json",
    ):
        self.setting_filename = settings_filename
        self.latest_image_filename = latest_image_filename
        self.weather_data_filename = weather_data_filename

    def get_settings(self) -> dict:
        settings = {}
        with open(self.setting_filename, "r") as f:
            settings = json.load(f)
        return settings

    def get_weather_data(self) -> WeatherData:
        # TODO
        return None

    def set_weather_data(self, data: WeatherData):
        # TODO
        return None

    def get_latest_image(self) -> Image.Image:
        # If no latest image found, return a black image.
        if not os.path.isfile(self.latest_image_filename):
            return Image.new("RGB", (448, 600), "black")
        return Image.open(self.latest_image_filename)

    def set_latest_image(self, image: Image.Image):
        image.save(self.latest_image_filename, format="PNG")
        return None
