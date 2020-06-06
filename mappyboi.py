#!/usr/bin/python
# -*- coding:utf-8 -*-

import datetime
import logging

from PIL import ImageDraw, ImageFont
from tools.images import subtract_top_from_bottom, to_bitmap
from tools.tiles import (deg2num, generate_3x5_image, generate_base_map,
                         generate_metoffice_map, get_update_time)
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
    font = ImageFont.truetype("fonts/OpenSans-SemiBold.ttf", 16)

    current_time = get_update_time()
    # Change to UK timezone (I know this isnt the best way of doing it but whatevs)
    current_time = current_time + datetime.timedelta(hours=1)

    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text(
        (400, 0),
        current_time.strftime("%a, %H:%M"),
        (255, 255, 255),
        font=font,
    )
    return img


try:
    logging.info("Weather map")

    # Do the image stuff

    logging.info("Download images...")

    xtile, ytile = deg2num(lat, lon, zoom)

    logging.info("Base image downloading...")
    base_image = generate_3x5_image(xtile, ytile, zoom, generate_base_map)
    base_image = add_time(base_image)

    logging.info("Weather image downloading...")
    # Old style
    # weather_image = generate_3x5_image(xtile, ytile, zoom, generate_weather_map)

    # New hotness
    weather_image = generate_3x5_image(
        xtile, ytile, zoom, generate_metoffice_map
    )

    logging.info("Generate map...")

    weather_bitmap = to_bitmap(weather_image, 20)
    final_image = subtract_top_from_bottom(base_image, weather_bitmap)

    # Actually display it

    # final_image.show()

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
    epd7in5.epdconfig.module_exit()
    exit()
