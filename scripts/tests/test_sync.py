import os
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

import paho.mqtt.client as mqtt
import json

import time
from datetime import datetime

### MQTT
def on_sync_connect(client, userdata, flags, rc):
    client.subscribe("brtt6/thermo")
def on_sync_message(client, userdata, msg):
    m_in=json.loads(msg.payload) #decode json data
    global data_mqtt
    global lastmod_mqtt

    data_mqtt = m_in
    lastmod_mqtt = m_in['last_mod']
    client.disconnect()
def syncProgs():
    data_mqtt = ''
    lastmod_mqtt = ''
    data_json = ''
    lastmod_json = ''

    client = mqtt.Client()
    client.on_connect = on_sync_connect
    client.on_message = on_sync_message
    client.connect("meuro.dev", 1883, 60)
    client.loop_forever()  # Start networking daemon

    ### JSON
    with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
        data_json = json.load(thermodata)
        lastmod_json = str(data_json['last_mod'])
        


    print('lastmod_mqtt: ')
    print(lastmod_mqtt)
    print('lastmod_json: ')
    print(lastmod_json)
    ### compare MQTT <-> JSON
    element = datetime.strptime(lastmod_mqtt,"%d-%m-%Y %H:%M")
    timestamp_mqtt = datetime.timestamp(element)
    print(timestamp_mqtt)

    element = datetime.strptime(lastmod_json,"%d-%m-%Y %H:%M")
    timestamp_json = datetime.timestamp(element)
    print(timestamp_json)

    if timestamp_json < timestamp_mqtt:
        #aggiorno json:
        newTdata = {
            "set_prog": data_mqtt['set_prog'],
            "set_temp": data_mqtt['set_temp'], 
            "last_mod": lastmod_mqtt
        }
        with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
            json.dump(newTdata, jsonFile, indent=4)
        print('aggiornato json')

    elif timestamp_json > timestamp_mqtt :
        #aggiorno mqtt
        newTdata = {
            "set_prog": data_json['set_prog'],
            "set_temp": data_json['set_temp'], 
            "last_mod": lastmod_json
        }
        client = mqtt.Client()
        client.connect("meuro.dev", 1883, 60)
        client.loop_start()
        infotd = client.publish("brtt6/thermo", payload=json.dumps(newTdata), qos=1, retain=True)
        infotd.wait_for_publish()
        time.sleep(1)
        client.disconnect()
        print('aggiornato mqtt')

    else :
        print('burp!')