#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
from datetime import datetime
from random import random
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from settings import birthdays, climacell_api_key, latitude, longitude

from .tools.apis import (
    get_birthdays,
    get_current_temp,
    get_forecast,
    get_iss_passtime,
    get_max_aqi,
    get_opinionated_aqi_status,
    get_precipitation_data,
    get_sunrise_and_sunset,
    get_vaccinations,
    get_weather_icon,
    get_web_graph_count_links,
    get_web_graph_count_pages,
)
from .tools.fonts import opensans, weather
from .tools.graphing import plot_time_data
from .tools.images import subtract_top_from_bottom, to_bitmap, x_width, y_height
from .tools.tiles import (
    deg2num,
    generate_3x5_image,
    generate_base_map,
    generate_metoffice_map,
)
from .tools.utils import get_current_time, get_time_epoch
from .dashboard import Dashboard


class MappyBoi(Dashboard):
    """
    MappyBoi is a display mode for showing a map (and precipitation overlay) of a particular area
    and also a simple information display for fun things such as:
    - Temperature
    - Weather conditions
    - Air Quality
    - Will It Rain Graph
    - ISS overhead time
    - Sunrise/sunset
    - Birthdays
    - UK COVID-19 Vaccination ratio
    - Web-Graph link + page counts
    """

    def __init__(
        self,
        lat: float = 52.98,
        lon: float = -2.28,
        zoom: int = 7,
    ):
        self.lat = lat
        self.lon = lon
        self.zoom = zoom

    @staticmethod
    def add_time(img: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 16)

        current_time = get_current_time()

        # draw.text((x, y),"Sample Text",(r,g,b))
        draw.text(
            (400, 0),
            current_time.strftime("%a, %H:%M"),
            (255, 255, 255),
            font=font,
        )
        return img

    @staticmethod
    def draw_top_right_box(img: Image.Image, red: bool = False) -> Image.Image:
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            (y_height - 250, 0, y_height, 350), outline=None, fill=(255, 255, 255)
        )
        return img

    @staticmethod
    def add_raining_soon_graph(img: Image.Image, graph_img) -> Image.Image:
        img.alpha_composite(graph_img, (y_height - 250, 200))
        return img

    @staticmethod
    def add_temp(img: Image.Image, temp: int) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 120)
        weatherfont = ImageFont.truetype(weather, 150)
        temp_text = f"{int(temp) if temp is not None else '?'}"
        w, _ = draw.textsize(temp_text, font=font)
        draw.text(
            ((y_height - 250) + 10, -30),
            temp_text,
            (0, 0, 0),
            font=font,
        )
        draw.text(
            ((y_height - 240) + w, -55),
            "\uf03c",
            (0, 0, 0),
            font=weatherfont,
        )
        return img

    @staticmethod
    def add_aqi(img: Image.Image, quality) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 18)
        draw.text(
            (y_height - 240, 110),
            f"AQI - {quality}",
            (0, 0, 0),
            font=font,
        )
        return img

    @staticmethod
    def add_sunriseset(
        img: Image.Image, sunrise_time: datetime, sunset_time: datetime
    ) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 18)
        current_time = get_current_time()
        weatherfont = ImageFont.truetype(weather, 18)
        sunrise = "\uf051"
        sunset = "\uf052"
        # sunrise > current, then sunrise
        # current > sunrise < sunset then sunset
        # current > sunset then sunrise
        sunthingtodraw = sunrise
        suntimetowrite = sunrise_time
        if current_time > sunrise_time and current_time < sunset_time:
            sunthingtodraw = sunset
            suntimetowrite = sunset_time
        draw.text(
            (y_height - 240, 140),
            sunthingtodraw,
            (0, 0, 0),
            font=weatherfont,
        )
        draw.text(
            (y_height - 203, 140),
            f"- {suntimetowrite.strftime('%H:%M')}",
            (0, 0, 0),
            font=font,
        )
        return img

    @staticmethod
    def add_iss_passtime(img: Image.Image, passtimes) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 18)

        text = "??"
        if passtimes and len(passtimes["response"]) > 0:
            next_pass = passtimes["response"][0]["risetime"]
            next_pass_time = get_time_epoch(next_pass)
            text = next_pass_time.strftime("%-d %b, %H:%M")

        draw.text(
            (y_height - 240, 170),
            f"ISS - {text}",
            (0, 0, 0),
            font=font,
        )
        return img

    @staticmethod
    def remove_corner(img: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            (y_height - 100, x_width, y_height, x_width - 55),
            outline=None,
            fill=(255, 255, 255),
        )
        return img

    @staticmethod
    def add_weather_icon(img: Image.Image, icon: str) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(weather, 50)

        icons = {
            "freezing_rain_heavy": "\uf01a",
            "freezing_rain": "\uf01a",
            "freezing_rain_light": "\uf01a",
            "freezing_drizzle": "\uf01a",
            "ice_pellets_heavy": "\uf06b",
            "ice_pellets": "\uf06b",
            "ice_pellets_light": "\uf06b",
            "snow_heavy": "\uf01b",
            "snow": "\uf01b",
            "snow_light": "\uf01b",
            "flurries": "\uf064",
            "tstorm": "\uf01e",
            "rain_heavy": "\uf01a",
            "rain": "\uf01a",
            "rain_light": "\uf019",
            "drizzle": "\uf019",
            "fog_light": "\uf014",
            "fog": "\uf014",
            "cloudy": "\uf002",
            "mostly_cloudy": "\uf002",
            "partly_cloudy": "\uf002",
            "mostly_clear": "\uf00d",
            "clear": "\uf00d",
        }

        x_rand = int(random() * 10)
        y_rand = int(random() * 10)

        draw.text(
            (y_height - (75 + y_rand), (115 + x_rand)),
            icons[icon],
            (0, 0, 0),
            font=font,
        )
        return img

    @staticmethod
    def add_count_pages(img: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 16)

        current_num_pages = get_web_graph_count_pages()
        if current_num_pages == 0:
            return img

        current_num_links = get_web_graph_count_links()
        if current_num_links == 0:
            return img

        draw.text(
            (15, 0),
            f"{(current_num_pages / 1000000):.1f}M pages, {(current_num_links / 1000000):.1f}M links",
            (0, 0, 0),
            font=font,
        )
        return img

    @staticmethod
    def add_count_vaccinations(img: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 20)

        ukpop = 68000000
        vaccination_data = get_vaccinations()
        if not vaccination_data:
            return img

        draw.text(
            (15, 20),
            f"{(vaccination_data['value'] / 1000000):.1f}M vaccinations",
            (0, 0, 0),
            font=font,
        )
        draw.text(
            (15, 40),
            f"{(vaccination_data['value'] / ukpop * 100):.1f}% of UK",
            (0, 0, 0),
            font=font,
        )
        return img

    @staticmethod
    def add_birthday(img: Image.Image) -> Image.Image:
        current_birthdays = get_birthdays(birthdays)
        if not current_birthdays:
            # If there are no birthdays today :(
            return img

        # Draw bottom box
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 20)
        draw.rectangle(
            (0, x_width, y_height, x_width - 100), outline=None, fill=(255, 255, 255)
        )
        # Draw happy birthday
        msg = "Happy birthday!"
        w, _ = draw.textsize(msg, font=font)
        draw.text(
            ((y_height - w) / 2, x_width - 100),
            msg,
            (0, 0, 0),
            font=font,
        )

        # Draw names
        namefont = ImageFont.truetype(opensans, 45)
        names = " & ".join(current_birthdays)
        w, h = draw.textsize(names, font=namefont)
        draw.text(
            ((y_height - w) / 2, x_width - (10 + h)),
            names,
            (0, 0, 0),
            font=namefont,
        )
        return img

    def build_images(self) -> Tuple[Image.Image, Image.Image]:
        """
        Builds two bitmap images, one for black/white and another for red/white.
        For best results, make sure that there is no black/red overlap between the
        two images.
        """
        logging.info("Download images...")

        X_TILE, Y_TILE = deg2num(self.lat, self.lon, self.zoom)

        logging.info("Base image downloading...")
        __black_white_image = generate_3x5_image(
            X_TILE,
            Y_TILE,
            self.zoom,
            generate_base_map,
            cache="base_weather",
        )

        logging.info("Weather image downloading...")
        __red_white_image = to_bitmap(
            generate_3x5_image(
                X_TILE,
                Y_TILE,
                self.zoom,
                generate_metoffice_map,
            ),
            20,
        )

        logging.info("Getting additional forecast...")
        # Paint an area for this info
        __black_white_image = MappyBoi.draw_top_right_box(
            __black_white_image, red=False
        )
        __red_white_image = MappyBoi.draw_top_right_box(__red_white_image, red=True)
        __red_white_image = MappyBoi.remove_corner(__red_white_image)

        # Get additional shit
        forecast = get_forecast(latitude, longitude, climacell_api_key)
        temp = get_current_temp(forecast)
        aqi_status = get_opinionated_aqi_status(get_max_aqi(forecast))
        sunrise, sunset = get_sunrise_and_sunset(forecast)
        passtimes = get_iss_passtime(latitude, longitude)
        weather_state = get_weather_icon(forecast)

        precip_x, precip_y = get_precipitation_data(forecast)
        graph_img = plot_time_data(precip_x, precip_y)

        __black_white_image = MappyBoi.add_raining_soon_graph(
            __black_white_image, graph_img
        )
        __black_white_image = MappyBoi.add_temp(__black_white_image, temp)
        __black_white_image = MappyBoi.add_aqi(__black_white_image, aqi_status)
        __black_white_image = MappyBoi.add_sunriseset(
            __black_white_image, sunrise, sunset
        )
        __black_white_image = MappyBoi.add_iss_passtime(__black_white_image, passtimes)
        __black_white_image = MappyBoi.add_count_pages(__black_white_image)
        __black_white_image = MappyBoi.add_count_vaccinations(__black_white_image)
        __black_white_image = MappyBoi.add_birthday(__black_white_image)
        __red_white_image = MappyBoi.add_weather_icon(__red_white_image, weather_state)

        # Subtract Red from Black
        __black_white_image = subtract_top_from_bottom(
            __black_white_image, __red_white_image
        )

        return __black_white_image, __red_white_image
