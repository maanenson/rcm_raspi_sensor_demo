# Raspberry PI Machine Control / Sensor Demo for Murano platform
import sys
import time
import json
import datetime
import grovepi
import math
from grove_rgb_lcd import *

sensor = 7 #DHT Sensor Digital Port
blue = 0 #DHT Sensor Color
white = 1 #DHT Sensor Color

from murano import Murano
import requests

if len(sys.argv) < 3:
    print('Usage:')
    print('   python ./device_app <product_id> <device_id>');

PRODUCT_ID = sys.argv[1] # 'do5pjwoazfsf9a4i'
DEVICE_ID = sys.argv[2]  # '001'


def show_state():
    print('Product ID: {0} Device ID: {1}'.format(PRODUCT_ID, DEVICE_ID))


# create a murano object for the device
murano = Murano(PRODUCT_ID, DEVICE_ID)


# Get the device key (CIK)
try:
    cik = murano.load_cik()
    print('Loaded CIK from file {0}'.format(murano.filename))
except EnvironmentError:
    # no stored CIK, so activate
    cik = murano.activate()
    print('Activated device to obtain CIK')



#stats.update_stats()

# write current state of the lock to Murano
#writes = {'battery-percent': State.battery_percent,
#          'lock-state': State.lock_state}
#murano.write(writes)


print('Press Ctrl+C to quit')
timestamp = None

period_sensor_time = 2 #how many seconds to send Sensors
last_sensor_time = 0 # when was last time we sent sensor data

start_time = int(time.time())
run_time = int(time.time())-start_time

while True:
    #stats.update_stats()
    #meminfo = stats.get_memory_info()
    #print "total\tused\tfree\tcached"
    #print "%i\t%i\t%i\t%i"%(meminfo['total'],meminfo['used'],meminfo['free'],meminfo['cached'])
    #print "Memory Usage:\t%i%%"%(meminfo['percent'])
    #print "\n"
    #cpu_info = stats.get_cpu_info()
    #print "CPU Usage:\t%i%%"%(cpu_info['percent'])

    #State.cpu_usage = int(cpu_info['percent'])
    #State.mem_used = int(meminfo['used'])

    run_time = int(time.time())-start_time

    # TIME TO SEND PERIODIC SENSOR DATA
    if time.time() - last_sensor_time > period_sensor_time:

        now = datetime.datetime.utcnow()
        data = {}
        data['runtime'] = run_time

        light=int(grovepi.analogRead(0)/10.24)
        sound=int(grovepi.analogRead(1)/10.24)
        print("light = %.02f %% sound = %.02f %%"%(light, sound))
        data['light'] = light
        data['sound'] = sound

        analogdial=int(grovepi.analogRead(2)/10.24)
        print("analogdial = %.02f %% "%(analogdial))
        data['analogdial'] = analogdial

        temp = 0.01
        hum = 0.01
        [temp,humidity] = grovepi.dht(sensor,blue)
        if math.isnan(temp) == False and math.isnan(humidity) == False:
            print("temp = %.02f C humidity = %.02f%%"%(temp, humidity))
            data['temperature'] = temp
            data['humidity'] = humidity

        setRGB(65,196,220)
        display_string = str("Temp: %3.02f C \nHumidity: %3.01f %%"%(temp, humidity))
        setText_norefresh(display_string)

        rawdata = json.dumps(data)

        writes = {}
        writes['raw_data'] = rawdata


        # send current states up to Murano
        try:
            murano.write(writes)
            print(writes)
        except requests.exceptions.RequestException as e:
            print str(e)

        last_sensor_time = time.time()

    time.sleep(0.2);
