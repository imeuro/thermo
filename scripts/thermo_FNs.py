import os
import json
import time
from time import localtime, strftime
os.environ['TZ'] = 'Europe/Rome'
time.tzset()
from gpiozero import Button
import board
import adafruit_bmp280

from waveshare_epd import rpi_epd2in7
from PIL import Image,ImageDraw,ImageFont

import paho.mqtt.client as mqtt

global tempNow
global setTemp
global setProg
global datenow

datenow = time.strftime("%d-%m-%Y %H:%M")
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assetsdir = os.path.join(basedir, 'assets')

print(datenow)

# ---------------------------------------
# ---------------- GUI ------------------
# ---------------------------------------

def PrintGUI(caller):

    from thermo_read import returnData
    d=returnData()

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

    tempW,tempH = fontTempInt.getsize(bigtemp)
    tempoffset = 5+tempW

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    #if caller == 'main':
    if caller != 'null':
        print('[GUI] init...')
        # screen size: 176wx264h
        draw.text((5, 9), datenow, font = fontXS, fill = 0)
        draw.text((timeX, 4), timenow, font = fontM, fill = 0)
        # ---------------------------------------

        draw.rectangle((0, 30, epd.width, 242), fill= 0)
        draw.text((5, 45), 'TEMP:', font = fontXS, fill = 1)
        draw.text((5, 45), str(d.tempNow).split('.')[0], font = fontTempInt, fill = 1)
        draw.text((tempoffset, 58), 'o', font = fontXS, fill = 1)
        draw.text((tempoffset+10, 58), 'C', font = fontTempUnit, fill = 1)
        draw.text((tempoffset, 80),'.'+ str(d.tempNow).split('.')[1], font = fontTempDec, fill = 1)

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


# ---------------------------------------
# ------------- BUTTONS -----------------
# ---------------------------------------

btn1 = Button(5)    # cycleModes: auto/t2/t3/man
btn2 = Button(6)    # increase temp
btn3 = Button(13)   # decrease temp
btn4 = Button(19)   # straight to AUTO!

def cycleModes():
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
        data['last_mod'] = datenow
        
    with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

    publishToMQTT(data)

    PrintGUI('prog')

def incTemp():
    with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
        data = json.load(thermodata)
        newT = data['set_temp']
        newT = float(newT)
        if newT < 30.5 :
            newT += 0.5
        data['set_temp'] = newT
        data['set_prog'] = 'MAN'
        data['last_mod'] = datenow
        print(data)

    with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

    publishToMQTT(data)

    PrintGUI('prog')

def decTemp():
    with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
        data = json.load(thermodata)
        newT = data['set_temp']
        newT = float(newT)
        if newT > 5 :
            newT -= 0.5
        data['set_temp'] = newT
        data['set_prog'] = 'MAN'
        data['last_mod'] = datenow
        print(data)

    with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)
 
    publishToMQTT(data)

    PrintGUI('prog')
   
def setAuto():
    print("setAuto")
    with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
        data = json.load(thermodata)
        data['set_prog'] = 'AUTO'
        data['set_temp'] = 5
        data['last_mod'] = datenow
        
    with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

    publishToMQTT(data)

    PrintGUI('prog')

def publishToMQTT(what):
    time.sleep(3)
    client = mqtt.Client()
    client.connect("meuro.dev", 1883, 60)
    client.loop_start()
    infotd = client.publish("brtt6/thermo", payload=json.dumps(what), qos=1, retain=True)
    infotd.wait_for_publish()
    time.sleep(1)
    client.disconnect()

btn1.when_pressed = cycleModes
btn2.when_pressed = incTemp
btn3.when_pressed = decTemp
btn4.when_pressed = setAuto




# ---------------------------------------
# ---------- SYNC PROGRAMMING -----------
# ---------------------------------------

# ogni tot leggi mqtt e vedi data['last_mod'].
# se più recente di data['last_mod'] in json, allora sovrascrivi


