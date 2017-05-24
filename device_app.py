# Raspberry PI Machine Control / Sensor Demo for Murano platform
import sys
import time
import json
#from pi_stats import PiStats
from sense_hat import SenseHat

from murano import Murano
import requests

if len(sys.argv) < 3:
    print('Usage:')
    print('   python ./device_app <product_id> <device_id>');

PRODUCT_ID = sys.argv[1] # 'do5pjwoazfsf9a4i'
DEVICE_ID = sys.argv[2]  # '001'

def show_state():
    print('Product ID: {0} Device ID: {1}'.format(PRODUCT_ID, DEVICE_ID))


w = [255,255,255] # White
ww = [220,220,220] # slightly grey
x = [65,196,220] #Exosite Blue
a = [92,93,96] #Exosite Grey
d = [34,39,54] #Exosite Dark Blue
xx = [44,157,182] #Exosite Medium Blue

r = [255,0,0]
o = [255,127,0]
y = [255,255,0]
g = [0,255,0]
b = [0,0,255]
i = [75,0,130]
v = [159,0,255]
e = [0,0,0]


image = [
d,d,w,d,d,x,d,d,
d,w,w,ww,x,x,xx,d,
d,w,w,ww,x,x,xx,d,
d,d,w,w,d,xx,d,d,
d,d,d,d,w,w,d,d,
d,d,d,d,w,w,ww,d,
d,d,d,d,w,w,ww,d,
d,d,d,d,d,w,d,d
]

image2 = [
e,e,w,e,e,x,e,e,
e,w,w,ww,x,x,xx,e,
e,w,w,ww,x,x,xx,e,
e,e,w,w,e,xx,e,e,
e,e,e,e,w,w,e,e,
e,e,e,e,w,w,ww,e,
e,e,e,e,w,w,ww,e,
e,e,e,e,e,w,e,e
]

# create object for getting Sense Hat sensor data
sense = SenseHat()
sense.low_light = True
#sense.show_message("Starting...", text_colour=x,back_colour=e)
#sense.set_pixels(image2)
sense.clear()

# create a murano object for the device
murano = Murano(PRODUCT_ID, DEVICE_ID)

# create object for getting local device stats
#stats = PiStats()



# Get the device key (CIK)
try:
    cik = murano.load_cik()
    print('Loaded CIK from file {0}'.format(murano.filename))
except EnvironmentError:
    # no stored CIK, so activate
    cik = murano.activate()
    print('Activated device to obtain CIK')

# initialize the device state of of Pi
class State:
    battery_percent = 100
    cpu_usage = 0
    mem_used = 0
    run_time = 0

# initialize the sensor state
class Sensors:
    temperature = 0
    humidity = 0
    pressure = 0
    x,y,z = 0,0,0


#stats.update_stats()

# write current state of the lock to Murano
#writes = {'battery-percent': State.battery_percent,
#          'lock-state': State.lock_state}
#murano.write(writes)

def print_state():
    print('---------------------------------')
    print('product id:      {0}'.format(PRODUCT_ID))
    print('device id:       {0}'.format(DEVICE_ID))
    print('run time:        {0}'.format(State.run_time))
    print('cpu usage:       {0}'.format(State.cpu_usage))
    print('mem used:        {0}'.format(State.mem_used))
    print('temperature:     {0}'.format(Sensors.temperature))
    print('humidity:        {0}'.format(Sensors.humidity))
    print('pressure:        {0}'.format(Sensors.pressure))
    print('---------------------------------')

print('Waiting for lock commands from Murano')
print('Press Ctrl+C to quit')
timestamp = None

period_sensor_time = 2 #how many seconds to send Sensors
last_sensor_time = 0 # when was last time we sent sensor data

start_time = int(time.time())

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

    State.run_time = int(time.time())-start_time

    # TIME TO SEND PERIODIC SENSOR DATA
    if time.time() - last_sensor_time > 10:
        sense.set_pixel(0,7,d) #set pixel to dark blue

        t = sense.get_temperature()
        p = sense.get_pressure()
        h = sense.get_humidity()

        Sensors.temperature = round(t, 1)
        Sensors.pressure = round(p, 1)
        Sensors.humidity = round(h, 1)

        print_state()

        rawdata  = '{"temperature":' + str(Sensors.temperature) + ', "pressure":' + str(Sensors.pressure)+ ', "humidity":'+ str(Sensors.humidity)+', "runtime":'+ str(State.run_time)+'}'

        writes = {}
        writes['raw_data'] = rawdata

        # send current states up to Murano
        try:
            murano.write(writes)
            sense.set_pixel(0,7,g) #set pixel to medium blue if ok
        except requests.exceptions.RequestException as e:
            sense.set_pixel(0,7,[255,146,30]) #set pixel to orange if having issues
            print str(e)
        last_sensor_time = time.time()


    time.sleep(0.2);
