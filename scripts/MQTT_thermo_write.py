import os
import time
import board
import adafruit_bmp280
import paho.mqtt.client as mqtt
import json

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bmp280.sea_level_pressure = 1013.25

print("\nTemperature: %0.1f C" % bmp280.temperature)

time.sleep(1)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected...")
    # get roomba data
    client.subscribe([
        ("brtt6/thermo",0),
    ])

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    print(msg.topic)
    print(str(msg.payload,'utf8'))
    data = json.loads(msg.payload)
    cleantopic=msg.topic.replace('brtt6/','')

    data[cleantopic] = eval(msg.payload)

    print('Reading previous data... ')
    print(data[cleantopic])

    #######################
    print('Done! Disconnecting...')
    # close connection
    client.disconnect()

    #print('done loop...')

def on_publish(client, obj, mid):
    print("on_publish: ........." + str(client))
    print("mid: " + str(mid))
    print("obj: " + str(obj))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

client = mqtt.Client()

client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_publish = on_publish
client.on_message = on_message

client.connect("meuro.dev", 1883, 60)


client.loop_start()

thermodata =json.dumps({
    'cur_temp' : round(bmp280.temperature - 1.5, 1),
    'last_mod' : time.strftime("%d-%m-%Y %H:%M"),
    })
#publish.single("brtt6/thermo", thermodata, hostname="meuro.dev")
infotd = client.publish("brtt6/thermo", thermodata, qos=1, retain=True)
#msg_txt = '{"msgnum": "'+str(x)+'"}'
#print("Publishing: "+thermodata)
#infot = client.publish(args.topic, thermodata, qos=args.qos)
infotd.wait_for_publish()

time.sleep(1)

client.disconnect()



