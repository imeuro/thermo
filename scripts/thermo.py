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
humiNow = ''
setTemp = ''
setProg = ''


import time
from time import localtime, strftime
os.environ['TZ'] = 'Europe/Rome'
time.tzset()

from waveshare_epd import rpi_epd2in7
from PIL import Image,ImageDraw,ImageFont
import traceback # ?

from gpiozero import Button
import board
import Adafruit_DHT
from thermo_FNs import *

from threading import Event, Thread

# TODO:
# x buttons [done]
# x MQTT sync [done]
# x refresh [done]
# x relay [done]
# x final wiring [done]
# - final case
# - web gui (connect to MQTT)
# - partial screen refresh
# ...


### INIT
syncProgs()
time.sleep(5)

manageHeater()
time.sleep(5)

PrintGUI('main')


### LOOP
call_repeatedly(300, manageHeater)
call_repeatedly(300, syncProgs)
call_repeatedly(3600,PrintGUI,'main_repeatedly')


btn1 = Button(5)    # cycleModes: auto/t2/t3/man
btn2 = Button(6)    # increase temp
btn3 = Button(13)   # decrease temp
btn4 = Button(19)   # straight to AUTO!

btn1.when_pressed = cycleModes
btn2.when_pressed = incTemp
btn3.when_pressed = decTemp
btn4.when_pressed = setAuto


from signal import pause
pause()