#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging

from random import random

from src.mappyboi import MappyBoi

from waveshare_epd import epd7in5b_V3

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

    epd = epd7in5b_V3.EPD()
    # images
    blackimage = epd.getbuffer(black_white)
    redimage = epd.getbuffer(red_white)

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
