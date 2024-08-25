from dataclasses import dataclass
import datetime
import enum

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
    weather_code: WeatherCode


@dataclass
class WeatherData:
    last_updated: datetime.datetime
    forecasts: list[PointForecast]


class WeatherCode(enum.Enum):
    CLEAR = 1000
    CLOUDY = 1001
    MOSTLY_CLEAR = 1100
    PARTLY_CLOUDY = 1101
    MOSTLY_CLOUDY = 1102
    FOG = 2000
    FOG_LIGHT = 2100
    LIGHT_WIND = 3000
    WIND = 3001
    STRONG_WIND = 3002
    DRIZZLE = 4000
    RAIN = 4001
    RAIN_LIGHT = 4200
    RAIN_HEAVY = 4201
    SNOW = 5000
    FLURRIES = 5001
    SNOW_LIGHT = 5100
    SNOW_HEAVY = 5101
    FREEZING_DRIZZLE = 6000
    FREEZING_RAIN = 6001
    FREEZING_RAIN_LIGHT = 6200
    FREEZING_RAIN_HEAVY = 6201
    ICE_PELLETS = 7000
    ICE_PELLETS_HEAVY = 7101
    ICE_PELLETS_LIGHT = 7102
    TSTORM = 8000
