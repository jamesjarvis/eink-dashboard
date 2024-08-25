from io import BytesIO
from PIL import Image
from datatypes import WeatherData, PointForecast
from utils import parse_datetime
import requests
import datetime
import logging


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

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    r = requests.post("https://api.tomorrow.io/v4/timelines", headers=headers, params=querystring, json=payload)
    if r.status_code != 200:
        logging.error("Bad response from weather forecasting service", r.status_code)
        return None

    response_json = r.json()
    forecasts = []
    for interval in response_json["data"]["timelines"][0]["intervals"]:
        forecasts.append(
            PointForecast(
                start_time=interval["startTime"],
                temperature=interval["values"]["temperature"],
                precipitation_intensity=interval["values"]["precipitationIntensity"],
                weather_code=interval["values"]["weatherCode"],
            ),
        )
    
    return WeatherData(
        last_updated=current_time,
        forecasts=forecasts,
    )

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
