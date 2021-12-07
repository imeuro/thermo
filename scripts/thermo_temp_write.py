# this reads bmp280 sensor data and publish it to a json file and an mqtt chan

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

class readDHT22Data(mode):
    def __init__(upd):
        if mode == "full":
            DHT_SENSOR = Adafruit_DHT.DHT22
            DHT_PIN = 4

            calibration = -1.5
            #calibration = 0

            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            upd.tempNow = round(temperature + calibration, 1)
            upd.humiNow = round(humidity)

            print("\nTemperature: %0.1f C" % upd.tempNow)
            print("\nHumidity: %0.1f " % upd.humiNow +"%")

            time.sleep(3)

            # ---------------------------------------
            # ---------------- JSON -----------------
            # ---------------------------------------

            Tdata = {
                "cur_temp": upd.tempNow, 
                "cur_humi": upd.humiNow, 
                "last_mod": time.strftime("%d-%m-%Y %H:%M")
            }
            try:
                with open(os.path.join(basedir, 'temp.json'), "w") as jsonFile:
                    json.dump(Tdata, jsonFile, indent=4)

                time.sleep(3)
            except Exception as e:
                print(e)

        else:
            try:
                with open(os.path.join(basedir, 'temp.json'), "r") as jsonFile:
                    data = json.load(thermodata)
                    upd.cur_temp = data['cur_temp']
                    upd.cur_humi = data['cur_humi']
                    print(data)
            except Exception as e:
                print(e)

        try:
            with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
                data = json.load(thermodata)
                upd.setTemp = data['set_temp']
                upd.setProg = data['set_prog']
                print(data)
        except Exception as e:
            print(e)



        # ---------------------------------------
        # ---------------- MQTT -----------------
        # ---------------------------------------

        publishToMQTT(Tdata,"brtt6/temp")

def returnDHT22Data(mode):
    return readDHT22Data(mode)

#returnDHT22Data()