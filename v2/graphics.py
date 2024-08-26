from PIL import Image, ImageDraw, ImageFont
from datatypes import WeatherData, TrainData
from itertools import islice
import fonts
import datetime
import pytz

SIZE_X, SIZE_Y = 448, 600


def draw_overlay(
    image: Image.Image,
    weather: WeatherData,
    train: TrainData,
):
    current_time = datetime.datetime.utcnow().astimezone(
        tz=pytz.timezone("Europe/London")
    )
    draw = ImageDraw.Draw(image)

    # Consistent weather box 250 x 100 px
    CONSISTENT_BOX_HEIGHT = 110
    WEATHER_BOX_WIDTH, WEATHER_BOX_HEIGHT = 250, CONSISTENT_BOX_HEIGHT
    draw.rectangle(
        (0, SIZE_Y, WEATHER_BOX_WIDTH, SIZE_Y - WEATHER_BOX_HEIGHT),
        fill=(255, 255, 255),
        width=0,
    )
    # Draw temperature bottom left
    font = ImageFont.truetype(fonts.FONT_OPEN_SANS, 100)
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
        fonts.CELSIUS,
        (0, 255, 0),
        font=font_weather,
    )
    # Draw sunset/sunrise next to that
    font = ImageFont.truetype(fonts.FONT_OPEN_SANS, 18)
    font_weather = ImageFont.truetype(fonts.FONT_WEATHER, 18)
    # sunrise > current, then sunrise
    # current > sunrise < sunset then sunset
    # current > sunset then sunrise
    sun_glyph = fonts.SUNRISE
    sun_time = weather.sunrise
    if current_time > weather.sunrise and current_time < weather.sunset:
        sun_glyph = fonts.SUNSET
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
    font_weather = ImageFont.truetype(fonts.FONT_WEATHER, 60)
    icons = {
        "light_wind": fonts.DUST,
        "wind": fonts.WINDY,
        "strong_wind": fonts.STRONG_WIND,
        "freezing_rain_heavy": fonts.RAIN,
        "freezing_rain": fonts.SLEET,
        "freezing_rain_light": fonts.DAY_SHOWERS,
        "freezing_drizzle": fonts.DAY_SLEET,
        "ice_pellets_heavy": fonts.HAIL,
        "ice_pellets": fonts.HAIL,
        "ice_pellets_light": fonts.DAY_HAIL,
        "snow_heavy": fonts.SNOW_WIND,
        "snow": fonts.SNOW,
        "snow_light": fonts.DAY_SNOW,
        "flurries": fonts.SLEET,
        "thunderstorm": fonts.THUNDERSTORM,
        "rain_heavy": fonts.RAINDROP,
        "rain": fonts.RAIN,
        "rain_light": fonts.DAY_RAIN_MIX,
        "drizzle": fonts.DAY_SHOWERS,
        "fog_light": fonts.DAY_FOG,
        "fog": fonts.FOG,
        "cloudy": fonts.CLOUDY,
        "mostly_cloudy": fonts.CLOUD,
        "partly_cloudy": fonts.DAY_CLOUDY,
        "mostly_clear": fonts.DAY_SUNNY_OVERCAST,
        "clear": fonts.DAY_SUNNY,
    }
    w = draw.textlength(icons[weather.forecasts[0].weather_code], font=font_weather)
    draw.text(
        (WEATHER_BOX_WIDTH - w - 5, SIZE_Y - (WEATHER_BOX_HEIGHT - 5)),
        icons[weather.forecasts[0].weather_code],
        (255, 0, 0),
        font=font_weather,
    )

    # Consistent train box 198 x 100 px
    TRAIN_BOX_WIDTH, TRAIN_BOX_HEIGHT = SIZE_X - WEATHER_BOX_WIDTH, CONSISTENT_BOX_HEIGHT
    draw.rectangle(
        (WEATHER_BOX_WIDTH, SIZE_Y, SIZE_X, SIZE_Y - TRAIN_BOX_HEIGHT),
        fill=(255, 255, 255),
        width=0,
    )
    # Filter services not going to london
    departures = filter(
        lambda item: "LDN" in item.station_destination, train.departures
    )
    departures = list(islice(departures, 6))
    font = ImageFont.truetype(fonts.FONT_OPEN_SANS, 14)
    # Draw list of departures
    pos = SIZE_Y - TRAIN_BOX_HEIGHT
    for departure in departures:
        msg = f"{departure.booked_departure}: {departure.station_destination}"
        w, h = draw.textsize(msg, font=font)
        draw.text(
            (SIZE_X - TRAIN_BOX_WIDTH + 5, pos),
            msg,
            (255, 0, 0) if departure.display_as == "CANCELLED_CALL" else (0, 0, 0),
            font=font,
        )

        if departure.display_as == "CANCELLED_CALL":
            draw.text(
                (SIZE_X - TRAIN_BOX_WIDTH + w + 10, pos),
                "CANCL",
                (255, 0, 0),
                font=font,
            )
        elif departure.realtime_departure != departure.booked_departure:
            draw.text(
                (SIZE_X - TRAIN_BOX_WIDTH + w + 10, pos),
                f"({departure.realtime_departure})",
                (200, 160, 60),
                font=font,
            )
        pos = pos + h

    # Transient boxes live above the consistent boxes, and only show up if there is data to show.
    TRANSIENT_BOX_HEIGHT = 50
    RAIN_BOX_HEIGHT, RAIN_BOX_WIDTH = TRANSIENT_BOX_HEIGHT, WEATHER_BOX_WIDTH
    if sum(forecast.precipitation_intensity for forecast in weather.forecasts) > 0 :
        draw.rectangle(
            (0, SIZE_Y-WEATHER_BOX_HEIGHT, RAIN_BOX_WIDTH, SIZE_Y - WEATHER_BOX_HEIGHT - RAIN_BOX_HEIGHT),
            fill=None,
            width=0,
        )
        precip_x, precip_y = get_precipitation_data(weather)
        graph_img = plot_time_data(precip_x, precip_y)
        image.paste(graph_img, (0, SIZE_Y-WEATHER_BOX_HEIGHT-RAIN_BOX_HEIGHT), graph_img)


    image.show()



def get_precipitation_data(data: WeatherData) -> tuple[list[datetime.datetime], list[float]]:
    x = []
    y = []
    for forecast in data.forecasts:
        x.append(forecast.start_time)
        temp_precip = (
            0
            if not forecast.precipitation_intensity
            else float(forecast.precipitation_intensity)
        )
        y.append(temp_precip)
    return (x, y)

from matplotlib import dates
from matplotlib import pyplot as plt
import io
import pytz
def plot_time_data(x, y) ->  Image.Image:
    plt.figure(figsize=(2.5, 0.5), dpi=100)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0.3)
    plt.fill_between(x, 0, y, color="blue")

    axes = plt.gca()
    axes.axes.get_yaxis().set_visible(False)
    axes.axes.set_yscale('log')
    axes.set_frame_on(False)
    hfmt = dates.DateFormatter("%H:%M", tz=pytz.timezone("Europe/London"))
    axes.set_ylim([0.01, 25])
    axes.tick_params(axis='x', labelsize=6, length=2, direction='in', colors='blue')
    axes.set_xticks(axes.get_xticks()[::2])
    axes.xaxis.set_major_formatter(hfmt)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", transparent=True)
    buf.seek(0)
    img = Image.open(buf)
    return img