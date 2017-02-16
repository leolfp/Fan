#!/usr/bin/env python

import RPi.GPIO as GPIO
import sys

channel=18 #PWM BCM channel

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel,GPIO.OUT)
p=GPIO.PWM(channel,100) #frequency
p.start(0)

try:
    while True:
        dc = int(raw_input("PWM (0-100): "))
        p.ChangeDutyCycle(dc)

except KeyboardInterrupt:
    pass

p.stop()
GPIO.cleanup()
