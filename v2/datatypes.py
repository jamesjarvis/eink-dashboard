from dataclasses import dataclass
import datetime

"""
This file contains datatypes used for specific purposes throughput the display
i.e. weather or important dates.
"""


@dataclass
class SunData:
    last_updated: datetime.datetime
    sunrise: datetime.datetime
    sunset: datetime.datetime


@dataclass
class PointForecast:
    start_time: datetime.datetime
    temperature: float
    precipitation_intensity: float
    weather_icon: float  # arbitrary values converted elsewhere

@dataclass
class WeatherData:
    last_updated: datetime.datetime
    forecasts: list[PointForecast]
