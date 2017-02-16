#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import os

# Return CPU temperature as float
def getCPUtemp():
    f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    temp = f.readline()
    f.close()
    return float(temp) / 1000.0

# Log Fan speed
def logFanSpeed(speed,temp):
    f = open('/var/log/fan', 'w')
    f.write('speed=' + str(int(speed)) + '%\n')
    f.write('temp=' + str(int(temp)) + '.' + str(int(temp*10)%10) + ' C\n')
    f.close()

channel=18 #PWM BCM channel

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel,GPIO.OUT)
p=GPIO.PWM(channel,100) #frequency
p.start(0)

sup=75.0
inf=45.0
min=10.0
max=100.0
lastdc=0.0
alpha=0.2

try:
    while True:

        CPU_temp = getCPUtemp()
        dc = (CPU_temp - inf)/(sup-inf)*max
        if dc <= 0: dc = 0.0
        if dc >= max: dc = max
        if dc < min: dc = 0.0
        if dc > 0.0 and lastdc == 0.0:
            p.ChangeDutyCycle(100)
            time.sleep(0.2)
	logFanSpeed(dc,CPU_temp)
	if dc > lastdc:
		newdc = dc
	else:
		newdc = lastdc * (1-alpha) + dc * alpha
        p.ChangeDutyCycle(newdc)
        lastdc = newdc
        time.sleep(2)

except KeyboardInterrupt:
    pass

p.stop()
GPIO.cleanup()
