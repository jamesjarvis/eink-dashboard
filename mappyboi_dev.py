#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging

from src.mappyboi import MappyBoi

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

    black_white.show()
    red_white.show()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    exit()
