#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

# Return CPU temperature in Celsius as float
def getCPUtemp():
    f = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    temp = f.readline()
    f.close()
    return float(temp) / 1000.0

# Opens historical log
csv = open('/var/log/fan.csv', 'w', 1)
csv.write('speed,time,temp,state\n')

# Log Fan speed, temperature and state
def logFanSpeed(time, speed, temp, state):
    speed_s = str(int(speed))
    temp_s = str(int(temp)) + '.' + str(int(temp*10)%10)

    # Snapshot of current state
    f = open('/var/log/fan', 'w')
    f.write('speed=' + speed_s + '%\n')
    f.write('temp=' + temp_s + ' C\n')
    f.write('state=' + state + '\n')
    f.close()

    # Historical log
    csv.write(str(time) + ',' + speed_s + ',' + temp_s + ',' + state + '\n')


channel=18  # PWM BCM channel

# Starting the PWM
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel,GPIO.OUT)
p=GPIO.PWM(channel,100)  # frequency
p.start(0)

# Temperatures in Celsius
temp = 0.0
lastTemp = 0.0

# Number of measures to consider - analysis shows that 4 is optimal
sampling = 4
threshold = sampling - 1

# Initial state
state = 'idle'

# dx has a circular list of the last derivatives signs
dx = [0] * sampling
# trend accumulates the signs
trend = 0

# Speed limits
speed_min = 30.0
speed_max = 100.0

# Temp thresholds - must be a configuration
temp_down = 42.0
temp_up = 50.0

try:
    i = 0
    tm = 0
    while True:
        temp = getCPUtemp()

        # Calculating trend
        trend -= dx[i]
        dx[i] = cmp(temp - lastTemp, 0)
        trend += dx[i]

        # state transition
        if state != 'warm':
            if trend >= threshold:
                state = 'warm'
            elif state == 'idle' and temp > temp_up:
                state = 'cool'
            elif temp < temp_down:  # and state == 'cool'
                state = 'idle'
        else:  # state == 'warm'
            if trend <= -threshold:
                state = 'cool'

        # Temperature calculation - two linear formulas that optimizes noise and efficacy
        if state == 'warm':
            speed = (temp - temp_up) * 2.0 + speed_min
            # speed[temp] = {50: 30, 55: 40, 60: 50, ...}
        elif state == 'cool':
            speed = (temp - temp_down) * 0.6 + speed_min
            # speed[temp] = {75: 50, 42: 30, ...}
        else:  # state == 'idle'
            speed = 0.0

        # Adjusting speed out of limits
        if speed < speed_min:
            speed = 0.0
        elif speed > speed_max:
            speed = speed_max
        p.ChangeDutyCycle(speed)

        logFanSpeed(tm, speed, temp, state)

        lastTemp = temp
        i = (i + 1) % sampling
        tm += 1
        time.sleep(1)

except KeyboardInterrupt:
    pass

p.stop()
GPIO.cleanup()
csv.close()
