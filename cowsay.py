#!/usr/bin/python
# -*- coding:utf-8 -*-

# I am far too lazy to actually write my own cowsay generator, so I'm just gonna use an API for now

import datetime
import json
import logging

import requests

from PIL import Image, ImageDraw, ImageFont
from tools.images import subtract_top_from_bottom, x_width, y_height
from waveshare_epd import epd7in5b_V3

logging.basicConfig(
    filename="cowsay.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

# config


def get_update_time():
    current_time = datetime.datetime.utcnow().replace(microsecond=0, second=0)
    current_time = current_time - datetime.timedelta(
        minutes=10 + (current_time.minute % 5)
    )
    return current_time


def get_random_text():
    r = requests.get(
        "https://icanhazdadjoke.com/", headers={"Accept": "text/plain"}
    )
    if r.status_code != 200:
        logging.error("Bad response from cowsay service")
    return r.text


def get_cowsay(text):
    payload = {"msg": text, "f": "default"}
    r = requests.get("https://helloacm.com/api/cowsay/", params=payload)
    if r.status_code != 200:
        logging.error("Bad response from cowsay service")
    t = r.text
    t = json.loads(t)
    return t


def display_text(text):
    img = Image.new("RGB", (x_width, y_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/RobotoMono-Medium.ttf", 26)

    splitted = text.splitlines()

    distance = 40
    for i, s in enumerate(splitted):
        draw.text((90, i * distance), s, (0, 0, 0), font=font)

    return img


def display_text_red(text):
    img = Image.new("RGB", (x_width, y_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/RobotoMono-Medium.ttf", 26)

    splitted = text.split("\n")
    splitted = splitted[:-1]

    distance = 40
    for i, s in enumerate(splitted):
        # If it starts with one of limiting characters
        if s[0] == "/":
            draw.text((90, i * distance), f" {s[1:-2]}", (0, 0, 0), font=font)
        elif s[0] == "|":
            draw.text((90, i * distance), f" {s[1:-1]}", (0, 0, 0), font=font)
        elif s[0] == "\\":
            draw.text((90, i * distance), f" {s[1:-1]}", (0, 0, 0), font=font)

    return img


def add_time(img):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/OpenSans-SemiBold.ttf", 16)

    current_time = datetime.datetime.now()

    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text(
        (x_width - 75, y_height - 30),
        current_time.strftime("%a, %H:%M"),
        (0, 0, 0),
        font=font,
    )
    return img


try:
    logging.info("Cowsay")

    # Do the image stuff

    logging.info("Getting quote...")

    quote = get_random_text()

    logging.info("Getting cowsay...")

    cowsay_text = get_cowsay(quote)

    img_back = display_text(cowsay_text)
    img_back = add_time(img_back)

    img_red = display_text_red(cowsay_text)

    img_back = subtract_top_from_bottom(img_back, img_red)

    # Actually display it

    # img_back.show()
    # img_red.show()

    epd = epd7in5b_V3.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    logging.info("Displaying")
    blackimage = img_back
    redimage = img_red
    epd.display(epd.getbuffer(blackimage), epd.getbuffer(redimage))

    logging.info("Go to Sleep for 5 minutes...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5.epdconfig.module_exit()
    exit()
