from dataclasses import dataclass
import datetime

"""
This file contains datatypes used for specific purposes throughput the display
i.e. weather or important dates.
"""

# Weather Data

@dataclass
class PointForecast:
    start_time: datetime.datetime
    temperature: float
    precipitation_intensity: float
    weather_code: str


@dataclass
class WeatherData:
    last_updated: datetime.datetime
    sunrise: datetime.datetime
    sunset: datetime.datetime
    forecasts: list[PointForecast]

# Train Data

@dataclass
class Departure:
    # all arrival/departure times are in 12:45 format
    booked_arrival: str
    booked_departure: str
    realtime_arrival: str
    realtime_departure: str
    # station name, beautified
    station_origin: str
    station_departure: str
    # "" or "CANCELLED_CALL"
    display_as: str

@dataclass
class TrainData:
    last_updated: datetime.datetime
    departures: list[Departure]
