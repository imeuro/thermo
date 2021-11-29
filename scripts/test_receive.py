import paho.mqtt.client as mqtt
import json


def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    #print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("brtt6/thermo")  # Subscribe to the topic “digitest/test1”, receive any messages published on it


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    #print("Message received-> " + msg.topic + ":" + str(msg.payload))  # Print a received msg

    m_in=json.loads(msg.payload) #decode json data
    print(m_in)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("meuro.dev", 1883, 60)
client.loop_forever()  # Start networking daemon
