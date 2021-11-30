# this reads bmp280 sensor data and publish it to a json file and an mqtt chan

import sys
import os
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(basedir, 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

import time
import board
from gpiozero import Button
import adafruit_bmp280
import paho.mqtt.client as mqtt
import json

from waveshare_epd import rpi_epd2in7
from PIL import Image,ImageDraw,ImageFont

from thermo_FNs import *

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

bmp280.sea_level_pressure = 1013.25


calibration = -1.5


calibratedTEMP = round(bmp280.temperature + calibration, 1)
print("\nTemperature: %0.1f C" % calibratedTEMP)

time.sleep(1)

# ---------------------------------------
# ---------------- JSON -----------------
# ---------------------------------------

Tdata = {
    "cur_temp": round(bmp280.temperature + calibration, 1), 
    "last_mod": time.strftime("%d-%m-%Y %H:%M")
}
try:
    with open(os.path.join(basedir, 'temp.json'), "w") as jsonFile:
        json.dump(Tdata, jsonFile, indent=4)

    time.sleep(5)
except Exception as e:
    print(e)


# ---------------------------------------
# ---------------- MQTT -----------------
# ---------------------------------------

publishToMQTT(Tdata,"brtt6/thermo")