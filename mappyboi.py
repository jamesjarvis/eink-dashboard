#!/usr/bin/python
# -*- coding:utf-8 -*-

import datetime
import logging
import math
from io import BytesIO
from time import sleep

import numpy as np
import requests

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd7in5b_V3

logging.basicConfig(filename="display.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

# config

lat = 52.98
lon = -2.28
zoom = 7

api_key = ""

tile_dimension = 256


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def pil_grid(images, max_horiz=np.iinfo(int).max):
    n_images = len(images)
    n_horiz = min(n_images, max_horiz)
    h_sizes, v_sizes = [0] * n_horiz, [0] * (n_images // n_horiz)
    for i, im in enumerate(images):
        h, v = i % n_horiz, i // n_horiz
        h_sizes[h] = max(h_sizes[h], im.size[0])
        v_sizes[v] = max(v_sizes[v], im.size[1])
    h_sizes, v_sizes = np.cumsum([0] + h_sizes), np.cumsum([0] + v_sizes)
    im_grid = Image.new("RGBA", (h_sizes[-1], v_sizes[-1]), (255, 255, 255, 255))
    for i, im in enumerate(images):
        im_grid.paste(im, (h_sizes[i % n_horiz], v_sizes[i // n_horiz]))
    return im_grid


def generate_3x5_image(xtile, ytile, zoom, generate_url):
    image_arr = list()

    y = -2
    while y <= 2:
        x = -1
        while x <= 1:
            # print(xtile + x, ytile + y)
            r = requests.get(generate_url(zoom, xtile + x, ytile + y))
            if r.status_code != 200:
                logging.info("failed download!!")
            i = Image.open(BytesIO(r.content))
            i = i.resize((176,176), resample=Image.BICUBIC)
            image_arr.append(i)
            x += 1
        y += 1

    # we then want to combine these images in a 3 x 5 grid I guess?
    bigboi = pil_grid(image_arr, 3)

    return bigboi

def get_update_time():
    current_time = datetime.datetime.utcnow().replace(microsecond=0, second=0)
    current_time = current_time - datetime.timedelta(minutes=10 + (current_time.minute % 5))
    return current_time


def generate_base_map(zoom, xtile, ytile) -> str:
    return f"http://a.tile.stamen.com/toner/{zoom}/{xtile}/{ytile}.png"


def generate_weather_map(zoom, xtile, ytile) -> str:
    return f"https://tile.openweathermap.org/map/precipitation_new/{zoom}/{xtile}/{ytile}.png?appid={api_key}"

def generate_metoffice_map(zoom, xtile, ytile) -> str:
    current_time = get_update_time()

    return f"https://www.metoffice.gov.uk/public/data/LayerCache/OBSERVATIONS/ItemBbox/RADAR_UK_Composite_Highres/{xtile}/{ytile}/{zoom}/png?TIME={current_time.isoformat()}Z"

def to_bitmap(image, threshold):
    pixels = list(image.getdata())
    flippy = False
    h_size = image.size[0]

    # convert data list to contain only black or white
    newPixels = []
    for i, pixel in enumerate(pixels):
        if flippy:
            # if above certain transparency, turn white
            if pixel[3] <= threshold:
                newPixel = (255, 255, 255)
            # if not transparent, convert to black
            else:
                newPixel = (0, 0, 0)
        else:
            # occasionally, just whack in a white pixel
            newPixel = (255, 255, 255)
        newPixels.append(newPixel)
        if i % h_size != 0:
            flippy = not flippy

    # create a image and put data into it
    newImg = Image.new(image.mode, image.size)
    newImg.putdata(newPixels)
    return newImg

def subtract_top_from_bottom(bottomimg, topimg):
    bottompixels = list(bottomimg.getdata())
    toppixels = list(topimg.getdata())

    for i, pixel in enumerate(toppixels):
        if pixel[0] == 0:
            bottompixels[i] = (255, 255, 255)

    # put data back in the image
    bottomimg.putdata(bottompixels)
    return bottomimg

def add_time(img):
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/OpenSans-SemiBold.ttf", 16)

    current_time = get_update_time()
    # Change to UK timezone (I know this isnt the best way of doing it but whatevs)
    current_time = current_time + datetime.timedelta(hours=1)

    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text((400, 0),current_time.strftime("%a, %H:%M"),(255,255,255),font=font)
    return img

try:
    logging.info("Weather map")

    while True:

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
        weather_image = generate_3x5_image(xtile, ytile, zoom, generate_metoffice_map)

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
        epd.display(epd.getbuffer(redimage), epd.getbuffer(blackimage))

        logging.info("Go to Sleep for 5 minutes...")
        epd.sleep()

        sleep(60*5)
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5.epdconfig.module_exit()
    exit()
