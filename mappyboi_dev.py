#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import traceback

from src.tools.images import to_black_and_red_image
from src.mappyboi import MappyBoi
from settings import ifttt_key
from src.tools.apis import send_error

logging.basicConfig(
    filename="display.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

# config
LAT = 52.98
LON = -2.28
ZOOM = 7

try:
    logging.info("Weather map")

    mappy_boi = MappyBoi(lat=LAT, lon=LON, zoom=ZOOM)

    black_white, red_white = mappy_boi.build_images()

    composite_img = to_black_and_red_image(black_white, red_white)

    composite_img.show()

except IOError as e:
    logging.info(e)
    send_error(ifttt_key, "Received IO Error", "mappyboi", e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    exit()

except Exception as e:
    logging.info("Failed to execute mappyboi :(")
    logging.exception(e)
    logging.error(traceback.format_exc())
    send_error(ifttt_key, "Received unknown exception", "mappyboi", e)
