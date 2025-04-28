#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 15:55:06 2023

@author: psyteam74

"""
######################## SYSTEM INITIATION ######################## 
import pygame
import time
from datetime import datetime
import csv
import os
import sys
import threading
import random
import numpy as np
from threading import Event
from random import seed
from random import randint
from numpy import isnan
import ModularStuffBoard_2302_01
import glob
import serial.tools.list_ports

print("Hope you performed a reset of all the hardware and the kernel before launching the task !!!")
# Exit = int(input("So, reset done (1) or not (0): "))
Exit = 1
if Exit == 0:
    print("\nExiting the task... Reset the hardware and the kernel !!!")
    sys.exit()

# Ports handler
my_ports = glob.glob ('/dev/tty[A-Za-z]*')
myBox = ModularStuffBoard_2302_01.netBox(my_ports[0], 115200)

if myBox is None:
    print("ABORT, device not connected")

# Modules connection
else:
    # CONFIGURE THE BOX WITH THE USED MODULES
    # Create a new camera module in the box with I2C adress
    # adresses are set for the box V1. change adresse if necessary or copy/past orginal code for inputs (more flexible)
    cams = ModularStuffBoard_2302_01.camTracking(myBox, 0x56)
    
    # Create a new feeder module in the box with I2C adress
    feeder1 = ModularStuffBoard_2302_01.feeder(myBox, 0x51)
    
    # Create a new weight sensor module in the box with I2C adress
    weight1 = ModularStuffBoard_2302_01.weightMeasurement(myBox, 0x52)
    
    # Create a new servomotor module in the box with I2C adress
    doors1 = ModularStuffBoard_2302_01.pwmServo(myBox, 0x53)


weight1.startTare(1) #taring balance before 
time.sleep(3)
print("Tare done")

time.sleep(10)
weight1.startWeightMeasure(0)
weight1.startWeightMeasure(1) # to avoid automatic measure


print("measure 1 started")
#time.sleep(5)

print(weight1.getWeight(1)[0])

    