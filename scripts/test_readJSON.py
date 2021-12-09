import os
from time import localtime, strftime
from datetime import datetime

import paho.mqtt.client as mqtt
import json

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class readJSON:
    def __init__(upd,mode):
        if mode != 'thermo':
            try:
                with open(os.path.join(basedir, 'temp.json'), 'r') as tempdata:
                    data = json.load(tempdata)
                    upd.curTemp = data['cur_temp']
                    upd.curHumi = data['cur_humi']
                    upd.tempLastMod = data['last_mod']
                    # print('temp.json: ')
                    # print(data)
            except Exception as e:
                print(e)

        if mode != 'temp':
            try:
                with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
                    data = json.load(thermodata)
                    upd.setTemp = data['set_temp']
                    upd.setProg = data['set_prog']
                    upd.setLastMod = data['last_mod']
                    # print('thermo.json: ')
                    # print(data)
            except Exception as e:
                print(e)

def returnJSONData(mode):
    return readJSON(mode)

d=returnJSONData('full')
print(vars(d))

lastmod_json = d.setLastMod
element = datetime.strptime(lastmod_json,"%d-%m-%Y %H:%M")
timestamp_json = datetime.timestamp(element)

print(element)
print(timestamp_json)

