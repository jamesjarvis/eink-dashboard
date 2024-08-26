from datatypes import WeatherData, PointForecast, TrainData, Departure
import json
from PIL import Image
import os
import datetime
import pytz


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
        try:
            with open(self.setting_filename, "r") as f:
                settings = json.load(f)
        except Exception as e:
            return settings
        return settings

    def get_weather_data(self) -> WeatherData:
        try:
            with open(self.weather_data_filename, "r") as f:
                weather_data_json = json.load(f)
                forecasts = []
                for forecast_json in weather_data_json["forecasts"]:
                    forecasts.append(
                        PointForecast(
                            start_time=datetime.datetime.fromisoformat(forecast_json["start_time"]).astimezone(tz=pytz.timezone("Europe/London")),
                            temperature=forecast_json["temperature"],
                            precipitation_intensity=forecast_json[
                                "precipitation_intensity"
                            ],
                            weather_code=forecast_json["weather_code"],
                        ),
                    )
                return WeatherData(
                    last_updated=datetime.datetime.fromisoformat(weather_data_json["last_updated"]).astimezone(tz=pytz.timezone("Europe/London")),
                    forecasts=forecasts,
                    sunrise=datetime.datetime.fromisoformat(weather_data_json["sunrise"]).astimezone(tz=pytz.timezone("Europe/London")),
                    sunset=datetime.datetime.fromisoformat(weather_data_json["sunset"]).astimezone(tz=pytz.timezone("Europe/London")),
                )
        except Exception as e:
            return None
        return None

    def set_weather_data(self, data: WeatherData):
        """
        Store as:
        {
            "last_updated": "",
            "sunrise": "",
            "sunset": "",
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
            "sunrise": data.sunrise.isoformat(),
            "sunset": data.sunset.isoformat(),
        }
        with open(self.weather_data_filename, "w") as f:
            json.dump(weather_data_json, f, indent=2)
        return None

    def get_train_data(self) -> TrainData:
        try:
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
                return TrainData(
                    last_updated=datetime.datetime.fromisoformat(departure_json["last_updated"]).astimezone(tz=pytz.timezone("Europe/London")),
                    departures=departures,
                )
        except Exception as e:
            return None
        return None

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
