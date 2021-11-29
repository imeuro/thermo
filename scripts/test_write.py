import os
import time
import paho.mqtt.client as mqtt
import json

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
	data = json.load(thermodata)
	print(data['last_mod'])

	client = mqtt.Client()
	client.connect("meuro.dev", 1883, 60)
	client.loop_start()
	infotd = client.publish("brtt6/thermo", payload=json.dumps(data), qos=1, retain=True)

	infotd.wait_for_publish()
	time.sleep(1)
	client.disconnect()