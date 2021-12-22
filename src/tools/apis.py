import datetime
import json
import logging
import math
from typing import List, Tuple

import pytz
import requests

from .utils import get_current_time, parse_datetime, beautify_time_string


def get_dad_joke() -> str:
    r = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "text/plain"})
    if r.status_code != 200:
        logging.error("Bad response from dad joke service")
    return r.text


def get_cowsay(text: str) -> dict:
    payload = {"msg": text, "f": "default"}
    r = requests.get("https://helloacm.com/api/cowsay/", params=payload)
    if r.status_code != 200:
        logging.error("Bad response from cowsay service")
    t = r.text
    t = json.loads(t)
    return t


def get_iss_passtime(lat: float, lon: float, alt: int=50) -> dict:
    """Returns the iss pass times at this location"""
    payload = {"lat": lat, "lon": lon, "alt": alt}

    r = requests.get("http://api.open-notify.org/iss-pass.json", params=payload)
    if r.status_code != 200:
        logging.error("Bad response from weather forecasting service", r.status_code)
    return r.json()


def get_forecast(lat: float, lon: float, api_key: str) -> dict:
    """
    Gets forecast from tomorrow.io, example response as follows:
    {
        "data":{
            "timelines":[
                {
                    "timestep":"1m",
                    "startTime":"2021-09-11T19:29:00Z",
                    "endTime":"2021-09-11T22:29:00Z",
                    "intervals":[
                        {
                            "startTime":"2021-09-11T19:29:00Z",
                            "values":{
                                "temperature":18.69,
                                "precipitationIntensity":0,
                                "weatherCode":1101
                            }
                        },
                        {
                            "startTime":"2021-09-11T19:30:00Z",
                            "values":{
                                "temperature":18.66,
                                "precipitationIntensity":0,
                                "weatherCode":1101
                            }
                        },
                    ]
                },
            ]
        }
    }
    """
    # TODO: Sunrise, Sunset and air quality metrics are fucked. Thanks climacell/tomorrow...
    current_time = get_current_time(pytz.utc)
    end_date = current_time + datetime.timedelta(hours=3)
    end_date.replace(microsecond=0).isoformat()

    querystring = {
        "apikey": api_key,
    }
    payload = {
        "location": [lat, lon],
        "units": "metric",
        "timesteps": ["1m"],
        # "startTime": "now",
        "endTime": end_date.isoformat(),
        "fields": [
            "temperature",
            "precipitationIntensity",
            # "sunriseTime",
            # "sunsetTime",
            "weatherCode",
            "particulateMatter25",
            "particulateMatter10",
            "pollutantO3",
            "pollutantNO2",
            "epaIndex",
        ],
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    r = requests.post("https://api.tomorrow.io/v4/timelines", headers=headers, params=querystring, json=payload)
    if r.status_code != 200:
        logging.error("Bad response from weather forecasting service", r.status_code)
        return None
    return r.json()


# The following are just to get information from the fat payload delivered by climacell:


def get_sunrise_and_sunset(lat: float, lon: float) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    Gets sunrise/set from an api in the following format:
    {
        "results":{
            "sunrise":"2021-12-22T08:00:00+00:00",
            "sunset":"2021-12-22T15:00:00+00:00",
            "solar_noon":"2021-12-22T11:00:00+00:00",
            "day_length":30000,
            "civil_twilight_begin":"2021-12-22T07:00:00+00:00",
            "civil_twilight_end":"2021-12-22T16:00:00+00:00",
            "nautical_twilight_begin":"2021-12-22T06:00:00+00:00",
            "nautical_twilight_end":"2021-12-22T17:00:00+00:00",
            "astronomical_twilight_begin":"2021-12-22T05:00:00+00:00",
            "astronomical_twilight_end":"2021-12-22T17:00:00+00:00"
        },
        "status":"OK"
    }
    """
    url = f"https://api.sunrise-sunset.org/json"
    querystring = {
        "date": "today",
        "formatted": 0,
        "lat": lat,
        "lng": lon,
    }
    headers = {
        "Accept": "application/json",
    }
    r = requests.get(url, headers=headers, params=querystring)
    if r.status_code != 200:
        logging.error("Bad response from sunrise-sunset service", r.status_code)
        return (None, None)
    payload = r.json()
    sunrise = parse_datetime(payload["results"]["sunrise"])
    sunset = parse_datetime(payload["results"]["sunset"])
    return (sunrise, sunset)


def get_max_aqi(payload) -> int:
    # TODO: Find a way to get aqi info again.
    return -1
    aqi = 0
    for i in payload:
        temp = i["epa_aqi"]["value"] or -1
        if temp > aqi:
            aqi = temp
    return aqi


def get_weather_icon(payload) -> float:
    if not payload:
        return 0
    return payload["data"]["timelines"][0]["intervals"][0]["values"]["weatherCode"]


def get_current_temp(payload) -> int:
    if not payload:
        return 0
    return payload["data"]["timelines"][0]["intervals"][0]["values"]["temperature"]


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
    # payload["data"]["timelines"][0]["intervals"][0]["values"]["temperature"]
    for e in payload["data"]["timelines"][0]["intervals"]:
        temp_date = parse_datetime(e["startTime"], tz_to=pytz.utc)
        x.append(temp_date)
        temp_precip = e["values"]["precipitationIntensity"]
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


def get_web_graph_count_links() -> int:
    r = requests.get("https://api.jamesjarvis.io/countLinks")
    if r.status_code != 200:
        return 0
    return r.json()["countLinks"]


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


def get_vaccinations_first_dose() -> dict:
    """
    This should return a dict with:
    date (str):   currentDateString
    value (int):  numberOfFirstDoseVaccinations
    """
    url = "https://api.coronavirus.data.gov.uk/v1/data?filters=areaName=United%2520Kingdom;areaType=overview&latestBy=cumPeopleVaccinatedFirstDoseByPublishDate&structure=%7B%22date%22:%22date%22,%22value%22:%22cumPeopleVaccinatedFirstDoseByPublishDate%22%7D&format=json&page=1"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()["data"][0]

def get_vaccinations_second_dose() -> dict:
    """
    This should return a dict with:
    date (str):   currentDateString
    value (int):  numberOfSecondDoseVaccinations
    """
    url = "https://api.coronavirus.data.gov.uk/v1/data?filters=areaName=United%2520Kingdom;areaType=overview&latestBy=cumPeopleVaccinatedSecondDoseByPublishDate&structure=%7B%22date%22:%22date%22,%22value%22:%22cumPeopleVaccinatedSecondDoseByPublishDate%22%7D&format=json&page=1"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()["data"][0]

def get_vaccinations_third_dose() -> dict:
    """
    This should return a dict with:
    date (str):   currentDateString
    value (int):  numberOfThirdDoseVaccinations
    """
    url = "https://api.coronavirus.data.gov.uk/v1/data?filters=areaName=United%2520Kingdom;areaType=overview&latestBy=cumPeopleVaccinatedThirdInjectionByPublishDate&structure=%7B%22date%22:%22date%22,%22value%22:%22cumPeopleVaccinatedThirdInjectionByPublishDate%22%7D&format=json&page=1"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()["data"][0]

class Station:
    """
    Train station
    """
    def __init__(self, description: str, public_time: str) -> None:
        self.description: str = description
        self.public_time: str = public_time

class Service:
    """
    Train service, see https://www.realtimetrains.co.uk/about/developer/pull/docs/locationlist/
    """
    def __init__(self) -> None:
        self.service_uid: str = None
        self.run_date: datetime.date = None
        self.booked_arrival: str = None
        self.booked_departure: str = None
        self.realtime_arrival: str = None
        self.realtime_departure: str = None
        self.origin: Station = None
        self.destination: Station = None
        self.display_as: str = None


def beautify_station_name(name: str) -> str:
    """
    This simply returns a prettier / shorter name if it is known
    """
    if name == "London Charing Cross":
        return "London Charing X"
    elif name == "London Cannon Street":
        return "London Cannon St"
    return name


def get_train_departure_times(username: str, password: str, station_code: str) -> List[Service]:
    url = f"https://api.rtt.io/api/v1/json/search/{station_code}"
    r = requests.get(url, auth=(username, password))
    if r.status_code != 200:
        return None
    return_services = []
    try:
        services = r.json()["services"]
        for service in services:
            temp_s = Service()
            temp_s.service_uid = service['serviceUid']
            temp_s.run_date = datetime.datetime.strptime(service['runDate'], "%Y-%m-%d").date()
            if "locationDetail" in service:
                location_detail = service["locationDetail"]
                # location = Station(service["locationDetail"][""])
                temp_s.booked_arrival = beautify_time_string(location_detail["gbttBookedArrival"])
                temp_s.booked_departure = beautify_time_string(location_detail["gbttBookedDeparture"])
                arrivalTime = location_detail["realtimeArrival"] if "realtimeArrival" in location_detail else location_detail["gbttBookedArrival"]
                temp_s.realtime_arrival = beautify_time_string(arrivalTime)
                departureTime = location_detail["realtimeDeparture"] if "realtimeDeparture" in location_detail else location_detail["gbttBookedDeparture"]
                temp_s.realtime_departure = beautify_time_string(departureTime)
                temp_s.display_as = location_detail["displayAs"]
                temp_s.origin = Station(
                    beautify_station_name(location_detail["origin"][0]["description"]),
                    beautify_time_string(location_detail["origin"][0]["publicTime"]),
                )
                temp_s.destination = Station(
                    beautify_station_name(location_detail["destination"][0]["description"]),
                    beautify_time_string(location_detail["destination"][0]["publicTime"]),
                )
            return_services.append(temp_s)
    except Exception as e:
        logging.warn("Failed to parse train times", e)
    return return_services
