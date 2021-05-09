import logging

from PIL import Image, ImageDraw, ImageFont

from src.tools.apis import get_cowsay, get_dad_joke
from src.tools.fonts import opensans, robotomono
from src.tools.images import subtract_top_from_bottom, x_width, y_height
from src.tools.utils import get_current_time

from .dashboard import Dashboard


class CowSay(Dashboard):
    """
    CowSay is a display mode for retrieving a random dad joke from the internet, and displaying it in
    cowsay format (horizontal).
    """

    @staticmethod
    def display_text(text: str) -> Image.Image:
        img = Image.new("RGB", (x_width, y_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(robotomono, 26)

        splitted = text.splitlines()

        distance = 40
        for i, s in enumerate(splitted):
            draw.text((90, i * distance), s, (0, 0, 0), font=font)

        return img

    @staticmethod
    def display_text_red(text: str) -> Image.Image:
        img = Image.new("RGB", (x_width, y_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(robotomono, 26)

        splitted = text.splitlines()
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

    @staticmethod
    def add_time(img: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(opensans, 16)

        current_time = get_current_time()

        # draw.text((x, y),"Sample Text",(r,g,b))
        draw.text(
            (x_width - 75, y_height - 30),
            current_time.strftime("%a, %H:%M"),
            (0, 0, 0),
            font=font,
        )
        return img

    def build_images(self) -> tuple[Image.Image, Image.Image]:
        """
        Builds two bitmap images, one for black/white and another for red/white.
        For best results, make sure that there is no black/red overlap between the
        two images.
        """
        logging.info("Getting quote...")

        quote = get_dad_joke()

        logging.info("Getting cowsay...")

        cowsay_text = get_cowsay(quote)

        __black_white_image = CowSay.display_text(cowsay_text)
        __black_white_image = CowSay.add_time(__black_white_image)

        __red_white_image = CowSay.display_text_red(cowsay_text)

        __black_white_image = subtract_top_from_bottom(
            __black_white_image, __red_white_image
        )

        return __black_white_image, __red_white_image
