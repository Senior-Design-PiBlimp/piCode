#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time

# ===========================================================================
# Example Code
# ===========================================================================



# Initialise the PWM device using the default address

pwm = PWM(0x40, debug=False)

pwm.setAllPWM(0,0)


