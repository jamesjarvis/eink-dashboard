from .datatypes import WeatherData
import json
from PIL import Image


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
    ):
        self.setting_filename = settings_filename

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
        # TODO
        return None

    def set_latest_image(self, image: Image.Image):
        # TODO
        return None

    def get_xkcd_image(self) -> Image.Image:
        # TODO
        return None

    def set_xkcd_image(self, image: Image.Image):
        # TODO
        return None