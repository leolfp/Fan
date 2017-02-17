#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

# Return CPU temperature as float
def getCPUtemp():
    f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    temp = f.readline()
    f.close()
    return float(temp) / 1000.0

# Log Fan speed
def logFanSpeed(speed, temp, state):
    f = open('/var/log/fan', 'w')
    f.write('speed=' + str(int(speed)) + '%\n')
    f.write('temp=' + str(int(temp)) + '.' + str(int(temp*10)%10) + ' C\n')
    f.write('state=' + state + '\n')
    f.close()

channel=18 #PWM BCM channel

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel,GPIO.OUT)
p=GPIO.PWM(channel,100) #frequency
p.start(0)

temp = 0.0
lastTemp = 0.0

sampling = 4
threshold = sampling - 1

state = 'idle'
# dx has a circular list of the last derivatives signs
dx = [0] * sampling
# trend accumulates the signs
trend = 0

speed_min = 30.0
speed_max = 100.0

temp_down = 46.0
temp_up = 50.0

try:
    i = 0
    while True:
        temp = getCPUtemp()

        trend -= dx[i]
        dx[i] = cmp(temp - lastTemp, 0)
        trend += dx[i]

        # state transition
        if state != 'warm':
            if trend >= threshold:
                state = 'warm'
            elif state == 'idle' and temp > temp_up:
                state = 'cool'
        else:
            if trend <= -threshold:
                state = 'cool'

        if state == 'warm':
            speed = (temp - temp_up) * 2.0 + speed_min
            # speed[temp] = {50: 30, 55: 40, 60: 50, ...}
        elif state == 'cool':
            speed = (temp - temp_down) * 0.69 + speed_min
            # speed[temp] = {75: 50, 46: 30, ...}
        else:
            speed = 0.0

        if speed < speed_min:
            speed = 0.0
            state = 'idle'
        elif speed > speed_max:
            speed = speed_max

        p.ChangeDutyCycle(speed)
        logFanSpeed(speed, temp, state)

        lastTemp = temp
        i = (i + 1) % sampling
        time.sleep(1)

except KeyboardInterrupt:
    pass

p.stop()
GPIO.cleanup()
