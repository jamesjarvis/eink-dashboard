import datetime
import requests
import math
from PIL import Image
import numpy as np
import logging
from io import BytesIO

tile_dimension = 256

def get_update_time():
    current_time = datetime.datetime.utcnow().replace(microsecond=0, second=0)
    current_time = current_time - datetime.timedelta(minutes=10 + (current_time.minute % 5))
    return current_time

def generate_base_map(zoom, xtile, ytile, api_key=None) -> str:
    return f"http://a.tile.stamen.com/toner/{zoom}/{xtile}/{ytile}.png"

def generate_weather_map(zoom, xtile, ytile, api_key=None) -> str:
    return f"https://tile.openweathermap.org/map/precipitation_new/{zoom}/{xtile}/{ytile}.png?appid={api_key}"

def generate_metoffice_map(zoom, xtile, ytile, api_key=None) -> str:
    current_time = get_update_time()
    return f"https://www.metoffice.gov.uk/public/data/LayerCache/OBSERVATIONS/ItemBbox/RADAR_UK_Composite_Highres/{xtile}/{ytile}/{zoom}/png?TIME={current_time.isoformat()}Z"

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


def generate_3x5_image(xtile, ytile, zoom, generate_url, api_key=None):
    image_arr = list()

    y = -2
    while y <= 2:
        x = -1
        while x <= 1:
            # print(xtile + x, ytile + y)
            r = requests.get(generate_url(zoom, xtile + x, ytile + y, api_key))
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