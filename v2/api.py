from io import BytesIO
from PIL import Image
from datatypes import WeatherData, PointForecast
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
