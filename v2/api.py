from io import BytesIO
from PIL import Image
from datatypes import WeatherData, PointForecast, TrainData, Departure
import requests
import datetime
import logging
import pytz


# Utility functions
def parse_datetime(
    datetime_string, tz_from=pytz.utc, tz_to=pytz.timezone("Europe/London")
) -> datetime:
    """Simply takes a datetime string in utc format, and returns it in the timezone specified"""
    dt = datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S%z")
    return dt.astimezone(tz_to)


# deprecated: This will no longer be maintained.
def xkcd() -> Image.Image:
    """
    xkcd will fetch a random XKCD comic, and return as a PIL.Image.
    """
    URL = "https://pimoroni.github.io/feed2image/xkcd-daily.jpg"
    r = requests.get(URL)
    if r.status_code != 200:
        logging.error("failed download of xkcd!!")
        return None
    image = Image.open(BytesIO(r.content))
    return image


def get_forecast(lat: float, lon: float, api_key: str) -> WeatherData:
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
    current_time = datetime.datetime.utcnow()
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

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    r = requests.post(
        "https://api.tomorrow.io/v4/timelines",
        headers=headers,
        params=querystring,
        json=payload,
    )
    if r.status_code != 200:
        logging.error("Bad response from weather forecasting service", r.status_code)
        return None

    response_json = r.json()

    code_to_human = {
        1000: "clear",
        1001: "cloudy",
        1100: "mostly_clear",
        1101: "partly_cloudy",
        1102: "mostly_cloudy",
        2000: "fog",
        2100: "fog_light",
        3000: "light_wind",
        3001: "wind",
        3002: "strong_wind",
        4000: "drizzle",
        4001: "rain",
        4200: "rain_light",
        4201: "rain_heavy",
        5000: "snow",
        5001: "flurries",
        5100: "snow_light",
        5101: "snow_heavy",
        6000: "freezing_drizzle",
        6001: "freezing_rain",
        6200: "freezing_rain_light",
        6201: "freezing_rain_heavy",
        7000: "ice_pellets",
        7101: "ice_pellets_heavy",
        7102: "ice_pellets_light",
        8000: "thunderstorm",
    }

    forecasts = []
    for interval in response_json["data"]["timelines"][0]["intervals"]:
        weather_code = (
            code_to_human[interval["values"]["weatherCode"]]
            if interval["values"]["weatherCode"] in code_to_human
            else "unknown"
        )

        forecasts.append(
            PointForecast(
                start_time=parse_datetime(interval["startTime"]),
                temperature=interval["values"]["temperature"],
                precipitation_intensity=interval["values"]["precipitationIntensity"],
                weather_code=weather_code,
            ),
        )

    return WeatherData(
        last_updated=current_time,
        forecasts=forecasts,
        sunrise=None,
        sunset=None,
    )


def get_sunrise_and_sunset(
    lat: float, lon: float
) -> tuple[datetime.datetime, datetime.datetime]:
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
    try:
        r = requests.get(url, headers=headers, params=querystring)
    except Exception as e:
        return (None, None)
    if r.status_code != 200:
        logging.error("Bad response from sunrise-sunset service", r.status_code)
        return (None, None)
    payload = r.json()
    sunrise = parse_datetime(payload["results"]["sunrise"])
    sunset = parse_datetime(payload["results"]["sunset"])
    return (sunrise, sunset)


def beautify_time_string(time: str) -> str:
    """Changes 1210 to 12:10"""
    return f"{time[:2]}:{time[2:]}"


def beautify_station_name(name: str) -> str:
    """
    This simply returns a prettier / shorter name if it is known
    """
    if name == "London Charing Cross":
        return "LDN Charing X"
    elif name == "London Cannon Street":
        return "LDN Cannon St"
    return name


def get_train_departure_times(
    username: str, password: str, station_code: str
) -> TrainData:
    url = f"https://api.rtt.io/api/v1/json/search/{station_code}"
    try:
        r = requests.get(url, auth=(username, password))
    except Exception as e:
        return None
    if r.status_code != 200:
        return None
    departures = []
    try:
        services = r.json()["services"]
        if not services:
            return None
        for service in services:
            if "locationDetail" not in service:
                continue
            location_detail = service["locationDetail"]
            departure = Departure(
                booked_arrival=beautify_time_string(
                    location_detail["gbttBookedArrival"]
                ),
                booked_departure=beautify_time_string(
                    location_detail["gbttBookedDeparture"]
                ),
                realtime_arrival=beautify_time_string(
                    location_detail["realtimeArrival"]
                    if "realtimeArrival" in location_detail
                    else location_detail["gbttBookedArrival"]
                ),
                realtime_departure=beautify_time_string(
                    location_detail["realtimeDeparture"]
                    if "realtimeDeparture" in location_detail
                    else location_detail["gbttBookedDeparture"]
                ),
                station_origin=beautify_station_name(
                    location_detail["origin"][0]["description"]
                ),
                station_destination=beautify_station_name(
                    location_detail["destination"][0]["description"]
                ),
                display_as=location_detail["displayAs"],
            )
            departures.append(departure)
    except Exception as e:
        logging.warn("Failed to parse train times", e)
        return None
    return TrainData(
        last_updated=datetime.datetime.utcnow(),
        departures=departures,
    )
