import datetime
import logging
import math
import os
from io import BytesIO
from typing import Tuple

import numpy as np
import requests
from PIL import Image

TILE_DIMENSION = 256


def get_update_time() -> datetime:
    current_time = datetime.datetime.utcnow().replace(microsecond=0, second=0)
    current_time = current_time - datetime.timedelta(
        minutes=10
    )
    current_time = current_time - datetime.timedelta(
        minutes=(current_time.minute % 10)
    )
    return current_time


def generate_base_map(zoom: int, xtile: int, ytile: int, api_key: str=None) -> str:
    return f"http://a.tile.stamen.com/toner/{zoom}/{xtile}/{ytile}.png"


def generate_weather_map(zoom: int, xtile: int, ytile: int, api_key: str=None) -> str:
    current_time = get_update_time()
    return f"https://sat.owm.io/maps/2.0/radar/{zoom}/{xtile}/{ytile}?appid={api_key}&day={current_time.strftime('%Y-%m-%dT%H:%M')}"


def generate_metoffice_map(zoom: int, xtile: int, ytile: int, api_key: str=None) -> str:
    current_time = get_update_time()
    return f"https://www.metoffice.gov.uk/public/data/LayerCache/OBSERVATIONS/ItemBbox/RADAR_UK_Composite_Highres/{xtile}/{ytile}/{zoom}/png?TIME={current_time.isoformat()}Z"


def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def pil_grid(images, max_horiz=np.iinfo(int).max) ->  Image.Image:
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


def generate_3x5_image(xtile: int, ytile: int, zoom: int, generate_url, api_key: str=None, cache: str=None) ->  Image.Image:
    filepath = f"temp/{cache}_{xtile}_{ytile}_{zoom}.png"
    if cache is not None and os.path.isfile(filepath):
        return Image.open(filepath, mode="r")

    image_arr = list()

    y = -2
    while y <= 2:
        x = -1
        while x <= 1:
            # print(xtile + x, ytile + y)
            r = requests.get(generate_url(zoom, xtile + x, ytile + y, api_key))
            if r.status_code != 200:
                logging.info(f"failed download!! code is {r.status_code}")
            i = Image.open(BytesIO(r.content))
            i = i.resize((176, 176), resample=Image.BICUBIC)
            image_arr.append(i)
            x += 1
        y += 1

    # we then want to combine these images in a 3 x 5 grid I guess?
    bigboi = pil_grid(image_arr, 3)

    if cache is not None and not os.path.isfile(filepath):
        os.mkdir("temp")
        bigboi.save(filepath)

    return bigboi
