# reads data from json file before refreshing the gui
# however, questionable... will review it later

import sys
import os
import time
import paho.mqtt.client as mqtt
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

global tempNow
global setTemp
global setProg

import json

class updatedData:
    def __init__(updated):
    # read initial vars from json file
        with open(os.path.join(basedir, 'temp.json'), 'r') as tempdata:
            Tdata = json.load(tempdata)
            updated.tempNow = Tdata['cur_temp']
            print(Tdata)

        time.sleep(1)

        with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
            data = json.load(thermodata)
            updated.setTemp = data['set_temp']
            updated.setProg = data['set_prog']
            print(data)

def returnData():
    return updatedData()