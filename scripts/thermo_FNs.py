import os
import json
import time
from time import localtime, strftime
from datetime import datetime

os.environ['TZ'] = 'Europe/Rome'
time.tzset()
from gpiozero import Button
import board
import Adafruit_DHT
import RPi.GPIO as GPIO

from threading import Event, Thread

from waveshare_epd import rpi_epd2in7
from PIL import Image,ImageDraw,ImageFont

import paho.mqtt.client as mqtt

global tempNow
global setTemp
global setProg

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assetsdir = os.path.join(basedir, 'assets')


# --------------------------------------- #
# ---------------- GUI ------------------ #
# --------------------------------------- #

def PrintGUI(caller):

    #from thermo_read import returnData
    #d=returnData()
    from thermo_temp_write import returnDHT22Data
    d=returnDHT22Data()

    epd = rpi_epd2in7.EPD()
    epd.init()

    fontXS = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 11)
    fontS = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 16)
    fontM = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 18)
    fontL = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 19)
    #fontXL = ImageFont.truetype(os.path.join(assetsdir, 'Rubik-Light.ttf'), 48)
    fontTempInt = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 72)
    fontTempUnit = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 19)
    fontTempDec = ImageFont.truetype(os.path.join(assetsdir, 'retro_gaming.ttf'), 36)

    datenow = strftime("%d %b %Y", localtime())
    timenow = strftime("%H:%M", localtime())
    timeW,timeH = fontM.getsize(timenow)
    timeX = (epd.width) - timeW - 5
    bigtemp = str(d.tempNow).split('.')[0]
    bighumi = str(d.humiNow).split('.')[0]

    tempW,tempH = fontTempInt.getsize(bigtemp)
    tempoffset = 5+tempW
    humiW,humiH = fontTempDec.getsize(bighumi)
    humioffset = 5+humiW

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    if caller == 'main_repeatedly':
        print('----------------------> main_repeatedly')
    #if caller == 'main':
    if caller != 'null':
        print('[GUI] init...')
        # screen size: 176wx264h
        draw.text((5, 9), datenow, font = fontXS, fill = 0)
        draw.text((timeX, 4), timenow, font = fontM, fill = 0)
        # ---------------------------------------

        draw.rectangle((0, 30, epd.width, 242), fill= 0)
        draw.text((5, 50), 'TEMP:', font = fontXS, fill = 1)
        draw.text((5, 50), str(d.tempNow).split('.')[0], font = fontTempInt, fill = 1)
        draw.text((tempoffset, 63), 'o', font = fontXS, fill = 1)
        draw.text((tempoffset+10, 63), 'C', font = fontTempUnit, fill = 1)
        draw.text((tempoffset, 85),'.'+ str(d.tempNow).split('.')[1], font = fontTempDec, fill = 1)

        draw.text((5, 145), 'Humidity:', font = fontXS, fill = 1)
        draw.text((5, 155), str(d.humiNow), font = fontTempDec, fill = 1)
        draw.text((humioffset+10, 170), '%', font = fontTempUnit, fill = 1)

        fire = Image.open(os.path.join(assetsdir, 'fire-solid-16.png'))
        Himage.paste(fire, ((epd.width - 16 - 10), 40))

        # ---------------------------------- -----

        draw.line([5,215, 171,215], fill = 1)
        draw.text((5, 220), 'SET:', font = fontXS, fill = 1)
        draw.text((45, 217), str(d.setProg)+' - '+ str(d.setTemp), font = fontL, fill = 1)

        # ---------------------------------------
        draw.text((5, 246), 'PROG ', font = fontXS, fill = 0)
        draw.text((70, 244), '+ ', font = fontS, fill = 0)
        draw.text((133, 244), '- ', font = fontS, fill = 0)

        #epd.display_frame(Himage)
        epd.smart_update(Himage)

    # if caller == "temp":
    #     t=returnData()
    #     print('[GUI] refresh temp...')
    #     #epd.init()
    #     draw.rectangle((0, 45, epd.width, 80), fill= 0)
    #     draw.text((5, 45), str(t.tempNow).split('.')[0], font = fontTempInt, fill = 1)
    #     draw.text((tempoffset, 58), 'o', font = fontXS, fill = 1)
    #     draw.text((tempoffset+10, 58), 'C', font = fontTempUnit, fill = 1)
    #     draw.text((tempoffset, 80),'.'+ str(t.tempNow).split('.')[1], font = fontTempDec, fill = 1)
    #     epd.display_partial_frame(Himage, 0, 45, 80, epd.width)

    # if caller == "prog":
    #     p=returnData()
    #     #epd.init()
    #     print('[GUI] refresh program...')
    #     draw.rectangle((0, 125, epd.width, 145), fill= 0)
    #     draw.text((5, 125), 'SET:', font = fontXS, fill = 1)
    #     draw.text((45, 125), str(p.setTemp)+' - '+ str(p.setProg) + ')', font = fontXS, fill = 1)
    #     epd.display_partial_frame(Himage, 0, 125, 20, epd.width)

    #     draw.rectangle((0, 246, 45, epd.height), fill= 1)
    #     draw.text((5, 246), p.setProg+' ', font = fontXS, fill = 0)
    #     epd.display_partial_frame(Himage, 0, 246, 30, 45)
    #     #epd.smart_update(Himage)

    print('[GUI] done')
    epd.sleep()


# --------------------------------------- #
# ------------- BUTTONS ----------------- #
# --------------------------------------- #

def cycleModes():
    try:
        with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
            data = json.load(thermodata)
            curMode = data['set_prog']
            modeList = {
                'AUTO':5,
                'T1':17.5,
                'T2':20.5,
                'MAN':data['set_temp']
            }
            #print(modeList[0])
            key_list = list(modeList.keys())
            val_list = list(modeList.values())
            position = key_list.index(curMode)
            if position < 3 :
                newMode = key_list[position + 1]
                newTemp = val_list[position + 1]
            else :
                newMode = key_list[0]
                newTemp = val_list[0]

            print(newMode)
            print(newTemp)
            data['set_prog'] = newMode
            data['set_temp'] = newTemp
            data['last_mod'] = time.strftime("%d-%m-%Y %H:%M")
            
        with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
    except Exception as e:
        print('Cyclemodes:')
        print(e)

    PrintGUI('prog')
    manageHeater()
    publishToMQTT(data,"brtt6/thermo")

def incTemp():
    try:
        with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
            data = json.load(thermodata)
            newT = data['set_temp']
            newT = float(newT)
            if newT < 30.5 :
                newT += 0.5
            data['set_temp'] = newT
            data['set_prog'] = 'MAN'
            data['last_mod'] = time.strftime("%d-%m-%Y %H:%M")
            print(data)

        with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
    except Exception as e:
        print('incTemp:')
        print(e)

    PrintGUI('prog')
    manageHeater()
    publishToMQTT(data,"brtt6/thermo")

def decTemp():
    try:
        with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
            data = json.load(thermodata)
            newT = data['set_temp']
            newT = float(newT)
            if newT > 5 :
                newT -= 0.5
            data['set_temp'] = newT
            data['set_prog'] = 'MAN'
            data['last_mod'] = time.strftime("%d-%m-%Y %H:%M")
            print(data)

        with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
    except Exception as e:
        print('decTemp')
        print(e)
 
    PrintGUI('prog')
    manageHeater()
    publishToMQTT(data,"brtt6/thermo")
   
def setAuto():
    try:
        with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
            data = json.load(thermodata)
            data['set_prog'] = 'AUTO'
            data['set_temp'] = 5
            data['last_mod'] = time.strftime("%d-%m-%Y %H:%M")
            
        with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
    except Exception as e:
        print('setAuto:')
        print(e)

    PrintGUI('prog')
    manageHeater()
    publishToMQTT(data,"brtt6/thermo")

# --------------------------------------- #
# ---------- SYNC PROGRAMMING ----------- #
# --------------------------------------- #

# ogni tot leggi mqtt e vedi data['last_mod'].
# se più recente di data['last_mod'] in json, allora sovrascrivi
data_mqtt = ''
lastmod_mqtt = ''
data_json = ''
lastmod_json = ''

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
    global data_mqtt
    global lastmod_mqtt
    global data_json
    global lastmod_json

    client = mqtt.Client()
    client.on_connect = on_sync_connect
    client.on_message = on_sync_message
    client.connect("meuro.dev", 1883, 60)
    client.loop_forever()  # Start networking daemon

    ### JSON
    try:
        with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
            data_json = json.load(thermodata)
            lastmod_json = str(data_json['last_mod'])
    except Exception as e:
        print('syncProgs/read json:')
        print(e)
   

    # print('lastmod_mqtt: ')
    # print(lastmod_mqtt)
    # print('lastmod_json: ')
    # print(lastmod_json)

    ### compare MQTT <-> JSON
    element = datetime.strptime(lastmod_mqtt,"%d-%m-%Y %H:%M")
    timestamp_mqtt = datetime.timestamp(element)
    # print(timestamp_mqtt)

    element = datetime.strptime(lastmod_json,"%d-%m-%Y %H:%M")
    timestamp_json = datetime.timestamp(element)
    # print(timestamp_json)

    if timestamp_json < timestamp_mqtt:
        ### aggiorno json:
        newJSONdata = {
            "set_prog": data_mqtt['set_prog'],
            "set_temp": data_mqtt['set_temp'], 
            "last_mod": lastmod_mqtt
        }
        try:
            with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
                json.dump(newJSONdata, jsonFile, indent=4)
            print('aggiornato json')
        except Exception as e:
            print('syncProgs/write json:')
            print(e)

        PrintGUI('prog')
        manageHeater()
        
    elif timestamp_json > timestamp_mqtt :
        ### aggiorno mqtt
        newMQTTdata = {
            "set_prog": data_json['set_prog'],
            "set_temp": data_json['set_temp'], 
            "last_mod": lastmod_json
        }
        client = mqtt.Client()
        client.connect("meuro.dev", 1883, 60)
        client.loop_start()
        infotd = client.publish("brtt6/thermo", payload=json.dumps(newMQTTdata), qos=1, retain=True)
        infotd.wait_for_publish()
        time.sleep(1)
        client.disconnect()
        print('aggiornato mqtt')

    else :
        print('no updates.')

# --------------------------------------- #
# --------------- Relay ---------------- #
# --------------------------------------- #

def manageHeater():
    try:

        in1 = 23

        #GPIO.setmode(GPIO.BOARD)
        GPIO.setup(in1, GPIO.OUT)

        #from thermo_read import returnData
        #d=returnData()
        from thermo_temp_write import returnDHT22Data
        d=returnDHT22Data()

        print('current temp: '+str(d.tempNow))
        print('desired temp:'+str(d.setTemp))

        if (d.tempNow < d.setTemp):
            #print('better switch heating on.')
            GPIO.output(in1, False)
            # todo: make "fire" icon appear in gui
            
        else:
            #print('that\'s ok i can turn off now')
            GPIO.output(in1, True)
            # todo: make "fire" icon disappear in gui

    except KeyboardInterrupt:
        GPIO.cleanup()


# --------------------------------------- #
# --------------- OUTILS ---------------- #
# --------------------------------------- #

def call_repeatedly(interval, func, *args):
    stopped = Event()
    def loop():
        while not stopped.wait(interval): # the first call is in `interval` secs
            func(*args)
    Thread(target=loop).start()    
    return stopped.set


def publishToMQTT(what,where):
    time.sleep(3)
    client = mqtt.Client()
    client.connect("meuro.dev", 1883, 60)
    client.loop_start()
    infotd = client.publish(where, payload=json.dumps(what), qos=1, retain=True)
    infotd.wait_for_publish()
    time.sleep(1)
    client.disconnect()