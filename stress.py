#!/usr/bin/env python

import RPi.GPIO as GPIO
import os
import time

channel=18 #PWM BCM channel

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel,GPIO.OUT)
p=GPIO.PWM(channel,100) #frequency

# Return CPU temperature as float
def getCPUtemp():
    f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    temp = f.readline()
    f.close()
    return float(temp) / 1000.0

def log(speed,time,temp,state):
    f.write(str(speed) + ',' + str(time) + ',' + str(int(temp)) + '.' + str(int(temp*10)%10) + ',' + state + '\n')

f = open('log.csv', 'w')
f.write('speed,time,temp,state\n')

print '2 min cooldown'
p.start(100)
time.sleep(120)

max = 100
min = 10
step = 10
temp = lastTemp = getCPUtemp()

try:
    for dc in range(max, min, -step):
        print 'Test ' + dc + '%:'
        p.ChangeDutyCycle(dc)
        tm = 0

        # run bench in background
        os.popen('sysbench --num-threads=4 --max-requests=30000 --test=cpu run >/dev/null 2>&1')

        while temp >= lastTemp:
            time.sleep(1)
            log(dc,tm,temp,'warm')

            tm += 1
            lastTemp = temp
            temp = getCPUtemp()

        print '  warm in ' + tm + 'seconds'
        limit = tm + 60 * 5

        while tm <= limit:
            time.sleep(1)
            log(dc,tm,temp,'cool')

            tm += 1
            lastTemp = temp
            temp = getCPUtemp()

        print '  cool in ' + tm + 'seconds'


except KeyboardInterrupt:
    pass

p.stop()
GPIO.cleanup()
f.close()
