from PIL import Image, ImageDraw, ImageFont
from datatypes import WeatherData, TrainData
import fonts
import datetime
import pytz

SIZE_X, SIZE_Y = 448, 600


def draw_overlay(
    image: Image.Image,
    weather: WeatherData,
    train: TrainData,
):
    current_time = datetime.datetime.utcnow().astimezone(tz=pytz.timezone("Europe/London"))
    draw = ImageDraw.Draw(image)

    # Consistent weather box 280 x 110 px
    WEATHER_BOX_WIDTH, WEATHER_BOX_HEIGHT = 280, 100
    draw.rectangle(
        (0, SIZE_Y, WEATHER_BOX_WIDTH, SIZE_Y - WEATHER_BOX_HEIGHT),
        fill=(255, 255, 255),
    )
    # Draw temperature bottom left
    font = ImageFont.truetype(fonts.FONT_OPEN_SANS, 90)
    temp_text = f"{int(weather.forecasts[0].temperature) if weather.forecasts else '?'}"
    w = draw.textlength(temp_text, font=font)
    draw.text(
        (-3, SIZE_Y - (WEATHER_BOX_HEIGHT + 15)),
        temp_text,
        fill=(0, 0, 255),
        font=font,
    )
    font_weather = ImageFont.truetype(fonts.FONT_WEATHER, 60)
    draw.text(
        (w, SIZE_Y - (WEATHER_BOX_HEIGHT + 10)),
        fonts.ICON_CELSIUS,
        (0, 255, 0),
        font=font_weather,
    )
    # Draw sunset/sunrise next to that
    font = ImageFont.truetype(fonts.FONT_OPEN_SANS, 18)
    font_weather = ImageFont.truetype(fonts.FONT_WEATHER, 18)
    # sunrise > current, then sunrise
    # current > sunrise < sunset then sunset
    # current > sunset then sunrise
    sun_glyph = fonts.ICON_SUNRISE
    sun_time = weather.sunrise
    if current_time > weather.sunrise and current_time < weather.sunset:
        sun_glyph = fonts.ICON_SUNSET
        sun_time = weather.sunset
    sun_text = f"- {sun_time.strftime('%H:%M')}"
    w = draw.textlength(sun_text, font=font)
    w_glyph = draw.textlength(sun_glyph, font=font_weather)
    draw.text(
        (WEATHER_BOX_WIDTH - w - w_glyph - 10, SIZE_Y - 30),
        sun_glyph,
        (255, 0, 0),
        font=font_weather,
    )
    draw.text(
        (WEATHER_BOX_WIDTH - w - 5, SIZE_Y - 30),
        sun_text,
        (255, 0, 0),
        font=font,
    )
    # Draw weather icon
    font_weather = ImageFont.truetype(fonts.FONT_WEATHER, 30)


    image.show()
