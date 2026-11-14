"""Takes screenshots entirely in memory (nothing is written to disk)."""
import io

import imagehash
import mss
from PIL import Image

import config


def screenshot():
    """Returns (PIL image, jpeg bytes)."""
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[config.MONITOR])
        img = Image.frombytes("RGB", shot.size, shot.rgb)
    img.thumbnail((config.IMAGE_MAX_SIZE, config.IMAGE_MAX_SIZE))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=config.JPEG_QUALITY)
    return img, buf.getvalue()


def fingerprint(img):
    return imagehash.phash(img)
