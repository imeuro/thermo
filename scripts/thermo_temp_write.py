# cron every 5 mins:
# read bmp280 sensor data and write to a json file

import sys
import os
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libdir = os.path.join(basedir, 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

import time
import board
#from gpiozero import Button
import Adafruit_DHT
import paho.mqtt.client as mqtt
import json

from waveshare_epd import rpi_epd2in7
from PIL import Image,ImageDraw,ImageFont

from thermo_FNs import *

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

calibration = -1.5
#calibration = 0

humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
tempNow = round(temperature + calibration, 1)
humiNow = round(humidity)

print("\nTemperature: %0.1f C" % tempNow)
print("\nHumidity: %0.1f " % humiNow +"%")

time.sleep(3)

# ---------------------------------------
# ---------------- JSON -----------------
# ---------------------------------------

Tdata = {
    "cur_temp": tempNow, 
    "cur_humi": humiNow, 
    "last_mod": time.strftime("%d-%m-%Y %H:%M")
}
try:
    with open(os.path.join(basedir, 'temp.json'), "w") as jsonFile:
        json.dump(Tdata, jsonFile, indent=4)

    time.sleep(3)
except Exception as e:
    print(e)


# ---------------------------------------
# ---------------- MQTT -----------------
# ---------------------------------------

publishToMQTT(Tdata,"brtt6/temp")