import datetime
import json
import logging
import math
from typing import List, Tuple

import pytz
import requests

from .utils import get_current_time, parse_datetime


def get_dad_joke():
    r = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "text/plain"})
    if r.status_code != 200:
        logging.error("Bad response from dad joke service")
    return r.text


def get_cowsay(text):
    payload = {"msg": text, "f": "default"}
    r = requests.get("https://helloacm.com/api/cowsay/", params=payload)
    if r.status_code != 200:
        logging.error("Bad response from cowsay service")
    t = r.text
    t = json.loads(t)
    return t


def get_iss_passtime(lat, lon, alt=50):
    """Returns the iss pass times at this location"""
    payload = {"lat": lat, "lon": lon, "alt": alt}

    r = requests.get("http://api.open-notify.org/iss-pass.json", params=payload)
    if r.status_code != 200:
        logging.error("Bad response from weather forecasting service", r.status_code)
    return r.json()


def get_forecast(lat, lon, api_key):
    """
    Gets forecast from climacell, example response as follows:
    [{
        "lat": 0.1,
        "lon": 0.1,
        "temp": {"value": 12.97, "units": "C"},
        "precipitation": {"value": 4.0469, "units": "mm/hr"},
        "sunrise": {"value": "2020-06-06T03:44:36.443Z"},
        "sunset": {"value": "2020-06-06T20:11:48.212Z"},
        "epa_aqi": {"value": 25},
        "china_aqi": {"value": 14},
        "pm25": {"value": 2, "units": "µg/m3"},
        "pm10": {"value": 4, "units": "µg/m3"},
        "o3": {"value": 28, "units": "ppb"},
        "no2": {"value": 3, "units": "ppb"},
        "observation_time": {"value": "2020-06-06T17:14:41.972Z"},
        "weather_code": {"value": "rain"},
    }]
    """
    current_time = get_current_time(pytz.utc)
    end_date = current_time + datetime.timedelta(hours=3)
    end_date.replace(microsecond=0).isoformat()

    payload = {
        "lat": lat,
        "lon": lon,
        "apikey": api_key,
        "unit_system": "si",
        "timestep": 2,
        "start_time": "now",
        "end_time": end_date,
        "fields": [
            "temp",
            "precipitation",
            "sunrise",
            "sunset",
            "weather_code",
            "pm25",
            "pm10",
            "o3",
            "no2",
            "epa_aqi",
        ],
    }

    r = requests.get("https://api.climacell.co/v3/weather/nowcast", params=payload)
    if r.status_code != 200:
        logging.error("Bad response from weather forecasting service", r.status_code)
    return r.json()


# The following are just to get information from the fat payload delivered by climacell:


def get_sunrise_and_sunset(payload) -> Tuple[datetime.datetime, datetime.datetime]:
    sunrise = parse_datetime(payload[0]["sunrise"]["value"])
    sunset = parse_datetime(payload[0]["sunset"]["value"])
    return (sunrise, sunset)


def get_max_aqi(payload) -> int:
    aqi = 0
    for i in payload:
        temp = i["epa_aqi"]["value"] or -1
        if temp > aqi:
            aqi = temp
    return aqi


def get_weather_icon(payload) -> float:
    return payload[0]["weather_code"]["value"]


def get_current_temp(payload) -> int:
    return payload[0]["temp"]["value"]


def get_opinionated_aqi_status(n: int) -> str:
    if n < 0:
        return "unknown"
    if n < 25:
        return "healthy"
    elif n < 50:
        return "alright"
    elif n < 100:
        return "not great"
    elif n < 150:
        return "unhealthy"
    return "very unhealthy"


def get_precipitation_data(payload) -> Tuple[list, list]:
    x = list()
    y = list()
    for e in payload:
        temp_date = parse_datetime(e["observation_time"]["value"], tz_to=pytz.utc)
        x.append(temp_date)
        temp_precip = e["precipitation"]["value"]
        temp_precip = (
            # 0 if temp_precip is None else float(math.ceil(temp_precip * 2)) / 2
            0
            if temp_precip is None
            else float(temp_precip)
        )
        y.append(temp_precip)
    return (x, y)

def get_web_graph_count_pages() -> int:
    r = requests.get("https://api.jamesjarvis.io/countPages")
    if r.status_code != 200:
        return 0
    return r.json()["countPages"]

def get_birthdays(birthdays) -> List[str]:
    current_time = get_current_time()
    current_month = current_time.month
    current_day = current_time.day
    if current_month in birthdays["month"]:
        month_birthdays = birthdays["month"][current_month]
        if current_day in month_birthdays["day"]:
            whose_birthday_is_it = month_birthdays["day"][current_day]
            return whose_birthday_is_it
    return []
