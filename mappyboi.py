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
)
from tools.fonts import opensans
from tools.utils import get_current_time
from tools.graphing import plot_time_data
from tools.images import subtract_top_from_bottom, to_bitmap, y_height
from tools.tiles import (
    deg2num,
    generate_3x5_image,
    generate_base_map,
    generate_metoffice_map,
)

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
    img.alpha_composite(graph_img, (y_height - 250, 160))
    return img


def add_temp(img, temp):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(opensans, 120)
    draw.text(
        (y_height - 245, -20), f"{int(temp)} C", (0, 0, 0), font=font,
    )
    return img


def add_aqi(img, quality):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(opensans, 18)
    draw.text(
        (y_height - 240, 140), f"AQI - {quality}", (0, 0, 0), font=font,
    )
    return img


try:
    logging.info("Weather map")

    # Do the image stuff

    logging.info("Download images...")

    xtile, ytile = deg2num(lat, lon, zoom)

    logging.info("Base image downloading...")
    base_image = generate_3x5_image(xtile, ytile, zoom, generate_base_map)
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
    # sunrise, sunset = get_sunrise_and_sunset(forecast)

    precip_x, precip_y = get_precipitation_data(forecast)
    graph_img = plot_time_data(precip_x, precip_y)

    base_image = add_raining_soon_graph(base_image, graph_img)
    weather_bitmap = add_temp(weather_bitmap, temp)
    base_image = add_aqi(base_image, aqi_status)

    # Actually display it
    final_image = subtract_top_from_bottom(base_image, weather_bitmap)

    # final_image.show()
    # weather_bitmap.show()

    epd = epd7in5b_V3.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    logging.info("Displaying")
    blackimage = final_image
    redimage = weather_bitmap
    epd.display(epd.getbuffer(blackimage), epd.getbuffer(redimage))

    logging.info("Go to Sleep for 5 minutes...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5b_V3.epdconfig.module_exit()
    exit()
