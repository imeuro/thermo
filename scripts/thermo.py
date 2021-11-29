#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assetsdir = os.path.join(basedir, 'assets')
libdir = os.path.join(basedir, 'lib')
scriptsdir = os.path.join(basedir, 'scripts')

if os.path.exists(libdir):
    sys.path.append(libdir)

tempNow = ''
setTemp = ''
setProg = ''

from waveshare_epd import rpi_epd2in7

import time
from time import localtime, strftime
os.environ['TZ'] = 'Europe/Rome'
time.tzset()

from PIL import Image,ImageDraw,ImageFont
import traceback

from gpiozero import Button
import board
import adafruit_bmp280

from thermo_FNs import *

# TODO:
# x buttons [done]
# x MQTT sync [done]
# - refresh (partial refresh)
# - relay + final wiring
# - web gui
# ...


set_interval(PrintGUI('main'), 60*10)
set_interval(syncProgs, 60*1)


from signal import pause
pause()