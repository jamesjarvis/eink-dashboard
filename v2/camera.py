import io
import picamera
from PIL import Image


def take_picture() -> Image.Image:
    """
    take_picture actually takes the picture, returning a PIL Image.
    """
    # Create the in-memory stream
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.capture(stream, format="jpeg")
    # "Rewind" the stream to the beginning so we can read its content
    stream.seek(0)
    image = Image.open(stream)

    return image
