#!/usr/bin/python
# -*- coding:utf-8 -*-

# I am far too lazy to actually write my own cowsay generator, so I'm just gonna use an API for now
import logging

from src.cowsay import CowSay

logging.basicConfig(
    filename="cowsay.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

try:
    logging.info("Cowsay")

    cowsay = CowSay()

    black_white, red_white = cowsay.build_images()

    black_white.show()
    red_white.show()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    exit()
