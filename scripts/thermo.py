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
# - MQTT sync (vedere last_mod più recente tra mqtt e json e aggiornare set_temp & set_prog)
# - refresh (partial refresh)
# - relay + final wiring
#
# ...


PrintGUI('main')


# program lasts 10 minutes 
# according to desired full refresh
# interval set in crontab
time.sleep(600) 