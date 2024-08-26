#!/usr/bin/env python3
from storage import Storage
import api
import graphics

storage = Storage()
settings = storage.get_settings()

# # Update weather data
# weather_data = api.get_forecast(
#     lat=settings["latitude"],
#     lon=settings["longitude"],
#     api_key=settings["tomorrow_api_key"],
# )
# weather_data.sunrise, weather_data.sunset = api.get_sunrise_and_sunset(
#     lat=settings["latitude"],
#     lon=settings["longitude"],
# )
# storage.set_weather_data(weather_data)

# # Update train data
# train_data = api.get_train_departure_times(
#     username=settings["realtime_trains_username"],
#     password=settings["realtime_trains_password"],
#     station_code=settings["train_station"],
# )
# storage.set_train_data(train_data)

graphics.draw_overlay(
  image=storage.get_latest_image(),
  weather=storage.get_weather_data(),
  train=storage.get_train_data(),
)
