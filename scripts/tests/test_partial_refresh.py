from __future__ import print_function
import os
import sys

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assetsdir = os.path.join(basedir, 'assets')
libdir = os.path.join(basedir, 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import rpi_epd2in7
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def main():
    print("initializing", end="")
    sys.stdout.flush()
    epd = rpi_epd2in7.EPD()
    epd.init()
    print(".", end="")
    sys.stdout.flush()

    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 16)
    draw.text((0, 5), 'Partial refresh', font=font, fill=0)

    font = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 14)
    draw.line([0, 28, epd.width, 28], fill=0, width=3)
    epd.display_frame(image)
    print(".")
    loc = 30

    draw.text((0, loc), "Look!", font=font, fill=0)
    epd.smart_update(image)
    loc += 20
    print(".", end="")
    sys.stdout.flush()

    draw.text((0, loc), "No need to refresh", font=font, fill=0)
    draw.text((0, loc+20), "the entire screen.", font=font, fill=0)
    epd.smart_update(image)
    loc += 45
    print(".", end="")
    sys.stdout.flush()

    draw.text((0, loc), "It's fast", font=font, fill=0)
    draw.text((0, loc+20), "and convenient", font=font, fill=0)
    epd.smart_update(image)
    loc += 20
    print(".", end="")
    sys.stdout.flush()

    epd.sleep()
    print("!")


if __name__ == '__main__':
    main()
