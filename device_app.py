# Raspberry PI Machine Control / Sensor Demo for Murano platform
import sys
import time
import json
import datetime
import grovepi
from grove_rgb_lcd import *

sensor = 7

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
    if time.time() - last_sensor_time > 10:

        now = datetime.datetime.utcnow()
        temp = 0.01
        hum = 0.01
        [temp,humidity] = grovepi.dht(sensor,1)
        light=int(grovepi.analogRead(0)/10.24)
        sound=int(grovepi.analogRead(1)/10.24)

        print(temp,humidity,light,sound)


        setRGB(0,128,64)
        setRGB(0,255,0)
        setText("Temp:" + str(temp) + "C      " + "Humidity :" + str(humidity) + "%")

        data = {}

        data['runtime'] = run_time

        rawdata = json.dumps(data)
        #rawdata  = '{'
        #+ '"temperature":' + str(Sensors.temperature)
        #+ ', "sound":' + str(Sensors.sound)
        #+ ', "light":' + str(Sensors.light)
        #+ ', "humidity":'+ str(Sensors.humidity)
        #+', "runtime":'+ str(State.run_time)
        #+'}'

        writes = {}
        writes['raw_data'] = rawdata


        # send current states up to Murano
        try:
            #murano.write(writes)
            print(writes)
        except requests.exceptions.RequestException as e:
            print str(e)
            last_sensor_time = time.time()

    time.sleep(0.2);
