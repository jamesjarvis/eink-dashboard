#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging

from PIL import ImageDraw, ImageFont

from settings import climacell_api_key, latitude, longitude
from tools.apis import (
    get_current_temp,
    get_forecast,
    get_max_aqi,
    get_opinionated_aqi_status,
    get_precipitation_data,
    get_sunrise_and_sunset,
    get_iss_passtime,
    get_weather_icon,
)
from tools.fonts import opensans, weather
from tools.utils import get_current_time, get_time_epoch
from tools.graphing import plot_time_data
from tools.images import subtract_top_from_bottom, to_bitmap, y_height
from tools.tiles import (
    deg2num,
    generate_3x5_image,
    generate_base_map,
    generate_metoffice_map,
)
from random import random

from waveshare_epd import epd7in5b_V3

logging.basicConfig(
    filename="display.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

# config

lat = 52.98
lon = -2.28
zoom = 7


def add_time(img):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(opensans, 16)

    current_time = get_current_time()

    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text(
        (400, 0), current_time.strftime("%a, %H:%M"), (255, 255, 255), font=font,
    )
    return img


def draw_top_right_box(img, red=False):
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        (y_height - 250, 0, y_height, 350), outline=None, fill=(255, 255, 255)
    )
    return img


def add_raining_soon_graph(img, graph_img):
    img.alpha_composite(graph_img, (y_height - 250, 200))
    return img


def add_temp(img, temp):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(opensans, 120)
    weatherfont = ImageFont.truetype(weather, 150)
    draw.text(
        (y_height - 255, -30), f"{int(temp)}", (0, 0, 0), font=font,
    )
    draw.text(
        (y_height - 100, -55), "\uf03c", (0, 0, 0), font=weatherfont,
    )
    return img


def add_aqi(img, quality):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(opensans, 18)
    draw.text(
        (y_height - 240, 110), f"AQI - {quality}", (0, 0, 0), font=font,
    )
    return img


def add_sunriseset(img, sunrise_time, sunset_time):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(opensans, 18)
    current_time = get_current_time()
    weatherfont = ImageFont.truetype(weather, 18)
    sunrise = "\uf051"
    sunset = "\uf052"
    # sunrise > current, then sunrise
    # current > sunrise < sunset then sunset
    # current > sunset then sunrise
    sunthingtodraw = sunrise
    suntimetowrite = sunrise_time
    if current_time > sunrise_time and current_time < sunset_time:
        sunthingtodraw = sunset
        suntimetowrite = sunset_time
    draw.text(
        (y_height - 240, 140), sunthingtodraw, (0, 0, 0), font=weatherfont,
    )
    draw.text(
        (y_height - 203, 140),
        f"- {suntimetowrite.strftime('%H:%M')}",
        (0, 0, 0),
        font=font,
    )
    return img


def add_iss_passtime(img, passtimes):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(opensans, 18)

    text = "??"
    if passtimes and len(passtimes["response"]) > 0:
        next_pass = passtimes["response"][0]["risetime"]
        next_pass_time = get_time_epoch(next_pass)
        text = next_pass_time.strftime("%-d %b, %H:%M")

    draw.text(
        (y_height - 240, 170), f"ISS - {text}", (0, 0, 0), font=font,
    )
    return img


def add_weather_icon(img, icon):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(weather, 50)

    icons = {
        "freezing_rain_heavy": "\uf01a",
        "freezing_rain": "\uf01a",
        "freezing_rain_light": "\uf01a",
        "freezing_drizzle": "\uf01a",
        "ice_pellets_heavy": "\uf06b",
        "ice_pellets": "\uf06b",
        "ice_pellets_light": "\uf06b",
        "snow_heavy": "\uf01b",
        "snow": "\uf01b",
        "snow_light": "\uf01b",
        "flurries": "\uf064",
        "tstorm": "\uf01e",
        "rain_heavy": "\uf01a",
        "rain": "\uf01a",
        "rain_light": "\uf019",
        "drizzle": "\uf019",
        "fog_light": "\uf014",
        "fog": "\uf014",
        "cloudy": "\uf002",
        "mostly_cloudy": "\uf002",
        "partly_cloudy": "\uf002",
        "mostly_clear": "\uf00d",
        "clear": "\uf00d",
    }

    draw.text(
        (y_height - 80, 120), icons[icon], (0, 0, 0), font=font,
    )
    return img


try:
    logging.info("Weather map")

    # Do the image stuff

    logging.info("Download images...")

    xtile, ytile = deg2num(lat, lon, zoom)

    logging.info("Base image downloading...")
    base_image = generate_3x5_image(
        xtile, ytile, zoom, generate_base_map, cache="base_weather"
    )
    # base_image = add_time(base_image)

    logging.info("Weather image downloading...")
    # Old style
    # weather_image = generate_3x5_image(xtile, ytile, zoom, generate_weather_map)

    # New hotness
    weather_image = generate_3x5_image(xtile, ytile, zoom, generate_metoffice_map)

    logging.info("Generate map...")

    weather_bitmap = to_bitmap(weather_image, 20)

    # Get additional weather forecast

    logging.info("Getting additional forecast")

    # Paint an area for this info
    base_image = draw_top_right_box(base_image, red=False)
    weather_bitmap = draw_top_right_box(weather_bitmap, red=True)

    # Get additional shit
    forecast = get_forecast(latitude, longitude, climacell_api_key)
    temp = get_current_temp(forecast)
    aqi_status = get_opinionated_aqi_status(get_max_aqi(forecast))
    sunrise, sunset = get_sunrise_and_sunset(forecast)
    passtimes = get_iss_passtime(latitude, longitude)
    weather_state = get_weather_icon(forecast)

    precip_x, precip_y = get_precipitation_data(forecast)
    graph_img = plot_time_data(precip_x, precip_y)

    base_image = add_raining_soon_graph(base_image, graph_img)
    base_image = add_temp(base_image, temp)
    base_image = add_aqi(base_image, aqi_status)
    base_image = add_sunriseset(base_image, sunrise, sunset)
    base_image = add_iss_passtime(base_image, passtimes)
    weather_bitmap = add_weather_icon(weather_bitmap, weather_state)

    # Actually display it
    final_image = subtract_top_from_bottom(base_image, weather_bitmap)

    # final_image.show()
    # weather_bitmap.show()

    epd = epd7in5b_V3.EPD()
    # images
    blackimage = epd.getbuffer(final_image)
    redimage =  epd.getbuffer(weather_bitmap)



    logging.info("init and Clear")
    epd.init()
    if random() < 0.2:
        epd.Clear()

    logging.info("Displaying")
    epd.display(blackimage, redimage)

    logging.info("Go to Sleep for 10 minutes...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V3.epdconfig.module_exit()
    exit()
