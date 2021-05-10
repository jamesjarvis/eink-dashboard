from PIL import Image
from random import random

X_WIDTH = 880
Y_HEIGHT = 528


def to_bitmap(image:  Image.Image, threshold: int) ->  Image.Image:
    """This converts any PNG with alpha channels into a binary bitmap based on the transparency threshold"""
    pixels = list(image.getdata())

    # convert data list to contain only black or white
    newPixels = []
    for i, pixel in enumerate(pixels):
        # if above certain transparency, turn white
        if pixel[3] <= threshold:
            newPixel = (255, 255, 255)
        # if not transparent, convert to black
        else:
            newPixel = (0, 0, 0)
        
        newPixels.append(newPixel)

    # create a image and put data into it
    newImg = Image.new(image.mode, image.size)
    newImg.putdata(newPixels)
    return newImg


def rasterize(image: Image.Image) -> Image.Image:
    """This converts any PNG into a rasterized version of itself"""
    pixels = list(image.getdata())
    flip_this_one = False
    H_SIZE = image.size[0]

    # convert data list to contain only black or white
    newPixels = []
    for i, pixel in enumerate(pixels):
        # Our "rasterising" is literally just turning the diagonal pixels white.
        if flip_this_one:
            pixel = (255, 255, 255)
        
        newPixels.append(pixel)
        if i % H_SIZE != 0:
            flip_this_one = not flip_this_one

    # create a image and put data into it
    newImg = Image.new(image.mode, image.size)
    newImg.putdata(newPixels)
    return newImg


def subtract_top_from_bottom(bottomimg:  Image.Image, topimg:  Image.Image) ->  Image.Image:
    """Any pixels that are not white in the top layer are removed from the bottom layer"""
    bottompixels = list(bottomimg.getdata())
    toppixels = list(topimg.getdata())

    for i, pixel in enumerate(toppixels):
        if pixel[0] < 255:
            bottompixels[i] = (255, 255, 255)

    # put data back in the image
    bottomimg.putdata(bottompixels)
    return bottomimg
