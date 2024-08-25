from datatypes import WeatherData, PointForecast, TrainData, Departure
import json
from PIL import Image
import os
from utils import parse_datetime


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
        train_data_filename: str = "train_data.json",
    ):
        self.setting_filename = settings_filename
        self.latest_image_filename = latest_image_filename
        self.weather_data_filename = weather_data_filename
        self.train_data_filename = train_data_filename

    def get_settings(self) -> dict:
        settings = {}
        with open(self.setting_filename, "r") as f:
            settings = json.load(f)
        return settings

    def get_weather_data(self) -> WeatherData:
        weather_data = WeatherData()
        with open(self.weather_data_filename, "r") as f:
            weather_data_json = json.load(f)
            forecasts = []
            for forecast_json in weather_data_json["forecasts"]:
                forecasts.append(
                    PointForecast(
                        start_time=parse_datetime(forecast_json["start_time"]),
                        temperature=forecast_json["temperature"],
                        precipitation_intensity=forecast_json[
                            "precipitation_intensity"
                        ],
                        weather_code=forecast_json["weather_code"],
                    ),
                )
            weather_data = WeatherData(
                last_updated=parse_datetime(weather_data_json["last_updated"]),
                forecasts=forecasts,
            )
        return weather_data

    def set_weather_data(self, data: WeatherData):
        """
        Store as:
        {
            "last_updated": "",
            "forecasts": [
                {
                    "start_time": "",
                    "temperature": 0,
                    "precipitation_intensity": 0,
                    "weather_code": 0,
                },
            ]
        }
        """
        forecasts = []
        for forecast in data.forecasts:
            forecasts.append(
                {
                    "start_time": forecast.start_time.isoformat(),
                    "temperature": forecast.temperature,
                    "precipitation_intensity": forecast.precipitation_intensity,
                    "weather_code": forecast.weather_code,
                },
            )
        weather_data_json = {
            "last_updated": data.last_updated.isoformat(),
            "forecasts": forecasts,
        }
        with open(self.weather_data_filename, "w") as f:
            json.dump(weather_data_json, f, indent=2)
        return None

    def get_train_data(self) -> TrainData:
        train_data = TrainData()
        with open(self.train_data_filename, "r") as f:
            train_data_json = json.load(f)
            departures = []
            for departure_json in train_data_json["departures"]:
                departures.append(
                    Departure(
                        booked_arrival=departure_json["booked_arrival"],
                        booked_departure=departure_json["booked_departure"],
                        realtime_arrival=departure_json["realtime_arrival"],
                        realtime_departure=departure_json["realtime_departure"],
                        station_origin=departure_json["station_origin"],
                        station_departure=departure_json["station_departure"],
                        display_as=departure_json["display_as"],
                    ),
                )
            train_data = TrainData(
                last_updated=parse_datetime(departure_json["last_updated"]),
                departures=departures,
            )
        return train_data

    def set_train_data(self, train_data: TrainData):
        """
        Store as:
        {
            "last_updated": "",
            "departures": [
                {
                    "booked_arrival": "",
                    "booked_departure": "",
                    "realtime_arrival": "",
                    "realtime_departure": "",
                    "station_origin": "",
                    "station_departure": "",
                    "display_as": "",
                },
            ]
        }
        """
        departures = []
        for departure in train_data.departures:
            departures.append(
                {
                    "booked_arrival": departure.booked_arrival,
                    "booked_departure": departure.booked_departure,
                    "realtime_arrival": departure.realtime_arrival,
                    "realtime_departure": departure.realtime_departure,
                    "station_origin": departure.station_origin,
                    "station_departure": departure.station_departure,
                    "display_as": departure.display_as,
                },
            )
        train_data_json = {
            "last_updated": train_data.last_updated.isoformat(),
            "departures": departures,
        }
        with open(self.train_data_filename, "w") as f:
            json.dump(train_data_json, f, indent=2)
        return None

    def get_latest_image(self) -> Image.Image:
        # If no latest image found, return a black image.
        if not os.path.isfile(self.latest_image_filename):
            return Image.new("RGB", (448, 600), "black")
        return Image.open(self.latest_image_filename)

    def set_latest_image(self, image: Image.Image):
        image.save(self.latest_image_filename, format="PNG")
        return None
