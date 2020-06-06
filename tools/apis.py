import datetime
import json
import logging

import requests


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


def get_forecast(lat, lon, api_key):
    end_date = datetime.datetime.now() + datetime.timedelta(hours=2)
    end_date = f"{end_date.replace(microsecond=0).isoformat()}Z"

    payload = {
        "lat": lat,
        "lon": lon,
        "apikey": api_key,
        "unit_system": "si",
        "timestep": 5,
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


def get_sunrise_and_sunset(payload) -> (datetime.datetime, datetime.datetime):
    sunrise = datetime.datetime.strptime(payload[0]["sunrise"]["value"], '%Y-%m-%dT%H:%M:%S.%fZ')
    sunrise = sunrise + datetime.timedelta(hours=1)
    sunset = datetime.datetime.strptime(payload[0]["sunset"]["value"], '%Y-%m-%dT%H:%M:%S.%fZ')
    sunset = sunset + datetime.timedelta(hours=1)
    return (sunrise, sunset)


def get_max_aqi(payload) -> int:
    aqi = 0
    for i in payload:
        temp = i["epa_aqi"]["value"]
        if temp > aqi:
            aqi = temp
    return aqi


def get_current_temp(payload) -> int:
    return payload[0]["temp"]["value"]


def get_opinionated_aqi_status(n: int) -> str:
    if n < 25:
        return "healthy"
    elif n < 50:
        return "alright"
    elif n < 100:
        return "not great"
    elif n < 150:
        return "unhealthy"
    return "very unhealthy"


def get_precipitation_data(payload) -> (list, list):
    x = list()
    y = list()
    for e in payload:
        temp_date = datetime.datetime.strptime(e["observation_time"]["value"], '%Y-%m-%dT%H:%M:%S.%fZ')
        temp_date = temp_date + datetime.timedelta(hours=1)
        x.append(temp_date)
        temp_precip = e["precipitation"]["value"]
        temp_precip = 0 if temp_precip is None else temp_precip
        y.append(temp_precip)
    return (x, y)
