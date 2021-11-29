import os
import time
import board
import adafruit_bmp280
import json

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bmp280.sea_level_pressure = 1013.25

print("\nTemperature: %0.1f C" % bmp280.temperature)

time.sleep(1)
with open(os.path.join(basedir, 'thermo.json'), 'r') as thermodata:
    data = json.load(thermodata)
    data['thermo']['current_temp'] = round(bmp280.temperature - 1.5, 1)
    data['thermo']['current_temp_time'] = time.strftime("%d-%m-%Y %H:%M")

with open(os.path.join(basedir, 'thermo.json'), "w") as jsonFile:
    json.dump(data, jsonFile, indent=4)

time.sleep(1)
