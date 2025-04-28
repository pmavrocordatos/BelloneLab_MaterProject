#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 08:37:17 2023

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
    time.sleep(0.03)
    
    # Create a new feeder module in the box with I2C adress
    feeder1 = ModularStuffBoard_2302_01.feeder(myBox, 0x51)
    time.sleep(0.03)
    
    # Create a new weight sensor module in the box with I2C adress
    weight1 = ModularStuffBoard_2302_01.weightMeasurement(myBox, 0x52)
    time.sleep(0.03)
    
    # Create a new servomotor module in the box with I2C adress
    doors1 = ModularStuffBoard_2302_01.pwmServo(myBox, 0x53)
    time.sleep(0.03)
    
######################## MOUSE INFO: ######################## 
# MouseID = input("\nMouse ID: ")
# MouseDoB = input("Date of birth (YYYYMMDD): ")
# isKO = input("Is it a LgDel mouse (1 = yes / 0 = no): ")
# stimSide = int(input("The stim mouse is placed left (0) or right (1): "))
# socialRewardStim = int(input("The visual stimulus associated with the social reward is the grid (0) or the lines (1): "))
# Start_date = time.strftime('%d-%m-%Y %H:%M:%S')

MouseID = 1
MouseDoB = 1
isKO = 1
stimSide = 0
socialRewardStim = 1
Start_date = time.strftime('%d-%m-%Y %H:%M:%S')

######################## DATA FOLDER ######################## 
Data_folder = 'Data/' + time.strftime('%Y-%m-%d') + '_Mouse-' + str(MouseID)
if not os.path.exists(Data_folder):
    os.makedirs(Data_folder)

######################## CAMERA ZONES ######################## 
LeftDoorZone = lambda: cams.getZoneStates(0)[0] #call the function with LeftDoorZone()
time.sleep(0.03)
RightDoorZone = lambda: cams.getZoneStates(0)[1]
time.sleep(0.03)
JuvDoorZone = lambda: cams.getZoneStates(0)[stimSide]
time.sleep(0.03)
ObjDoorZone = lambda: cams.getZoneStates(0)[abs(stimSide-1)]
time.sleep(0.03)
FeedDoorZone = lambda: cams.getZoneStates(0)[2]
time.sleep(0.03)
BeddingZone = lambda: cams.getZoneStates(0)[3]
time.sleep(0.03)

JuvDoorStimZone = lambda: cams.getZoneStates(1)[0] # Carefull if we have a camera in each stim side! (correct with stim side etc...)
ObjDoorStimZone = True # We dont have a second camera for the stim object side (to transform into function if a second camera is installed -> check call into tasks)

time.sleep(0.03)
weight1.startTare(1) #taring balance before 
#weight1.startTare(0) # Taring has to be made "manually" before: just take bottle out and back in when white led stops blinking
time.sleep(15)
print("Tare done")

#time.sleep(10) #the time to put the plastic mouse in the bedding

weight1.startWeightMeasure(0) # to avoid automatic measure
print("measure 0 started")

time.sleep(1)
weight1.startWeightMeasure(1)
print("measure 1 started")

Task_start = int(time.time())
print("Task start: ",Task_start)
# threads = []
# event = threading.Event()

class perf(): # master structure for some variables
    pass
p = perf() 

# # Gestion du feeding en //
dark = 0

class Feeder(threading.Thread): # monitoring
    #def __init__(self, event):
    def __init__(self):   
        threading.Thread.__init__(self)
        # self.daemon = True
        #self.event = event
        self.flag = False
        self.lock = threading.Lock()
        self.stop_control = False
        self.bedding_zone = False
        
        #self.start()
    def reset_flag(self):
       with self.lock:
           self.flag = True
           
    def blocker(self):
        self.stop_control = True
    
    def run(self):
        # Names columns
        headerM = ['Timestamp', 'Mouse_weight', 'Mouse_weight_since', 'Bottle_weight', 'Bottle_weight_since','Pellets_consumed']
        Mouse_weight = 0
        first_measure = True
        Mouse_weight_since = 0
        Bottle_weight = 0
        previous_bedding = 0
        #previous = 0
        Pellets_consumed = 0
        Mouse_weight_array = []
        Bottle_weight_array = []
        
        # Creates rows of information about the mouse (ID, DoB, isKO) and position of the stim mice.
        with open(Data_folder + '/Monitoring.csv', 'w') as fileM:
            writerM = csv.writer(fileM)
            writerM.writerow([Start_date])
            writerM.writerow('')
            writerM.writerow(['Mouse ID: ', MouseID])
            writerM.writerow(['DoB: ', MouseDoB])
            writerM.writerow(['isKO (1 = LgDel): ', isKO])
            writerM.writerow(['Stim side (1 = right): ', stimSide])    
            writerM.writerow('')
            #Creates all the columns of the monitoring csv. The columns will be filled with values at every timestamp
            writerM.writerow(headerM)
           
        while True:
            if self.stop_control:
                break
            
            now = datetime.now()
            
            time.sleep(0.25)
            if BeddingZone():
                TimestampBedding = int(time.time())-Task_start
                if TimestampBedding - previous_bedding > 5: # when the mouse is in the bedding, if weight was taken 
                    previous_bedding = TimestampBedding
                    weight1.startWeightMeasure(1) # SHOULD WORK HERE
                    time.sleep(0.01)
                    Mouse_weight_array.append(weight1.getWeight(1)[0])
                    time.sleep(0.01)
                    weight1.startWeightMeasure(0)
                    time.sleep(0.01)
                    Bottle_weight_array.append(weight1.getWeight(0)[0])
                    time.sleep(0.01)
                    first_measure = False
                    print("mouse weight measure taken: ", Mouse_weight_array[-1])
                    print("bottle weight measure taken: ", Bottle_weight_array[-1])
                    print(now)
            else:
                weight1.startTare(1) #tare mouse bedding
            
            time.sleep(0.25)
            
            if feeder1.getPelletSensorState() == 0:
                time.sleep(0.01)
                if feeder1.getPelletRemaining() == 0:
                    feeder1.setPellet(1)
                
            with self.lock:
                if self.flag:
                    if len(Mouse_weight_array) != 0:
                        
                        TimestampBis = time.time()-Task_start
                        
                        ### Pellet consumed ###
                        Pellets_consumed = feeder1.getTotalFeed()
                        print("pellets consumed: ", Pellets_consumed)
                        
                        ### Mouse Weight ###
                        Mouse_weight = sum(Mouse_weight_array)/len(Mouse_weight_array)
                        print("mean of mouse weight measures taken: ", Mouse_weight, "from: ",Mouse_weight_array)
                        
                        ### Bottle Weight ###
                        Bottle_weight = sum(Bottle_weight_array)/len(Bottle_weight_array)
                        print("mean of bottle weight measures taken: ", Bottle_weight, "from: ", Bottle_weight_array) 
                        
                        print(now)
                        
                        ### time since last measure ###
                        Mouse_weight_since = weight1.getWeight(1)[1] # Gets the time since last weight measurement (when the last function "weight1.startWeightMeasure(0)" was called)
                        time.sleep(0.01)
                        Bottle_weight_since = weight1.getWeight(0)[1]
                        
                        
                        dataM = [TimestampBis, Mouse_weight, Mouse_weight_since, Bottle_weight, Bottle_weight_since, Pellets_consumed]
                        feeder1.initTotalFeed(0)
                        Mouse_weight_array = []
                        Bottle_weight_array = []
                        self.flag = False
                        
                    elif len(Mouse_weight_array) == 0 and first_measure == False:
                        Mouse_weight = None # we take the previous weight computed (mean of weight array)
                        # we keep the previous mouse weight
                        TimestampBis = time.time()-Task_start
                        Mouse_weight_since = weight1.getWeight(1)[1] # Gets the time since last weight measurement in  minutes
                        time.sleep(0.01)
                        Bottle_weight = weight1.getWeight(0)[0]
                        time.sleep(0.01)
                        Pellets_consumed = feeder1.getTotalFeed()
                         #to replace with function
                        dataM = [TimestampBis, Mouse_weight, Mouse_weight_since, Bottle_weight, Bottle_weight_since, Pellets_consumed]
                        feeder1.initTotalFeed(0)
                        Mouse_weight_array = []
                        self.flag = False
                    
                    if first_measure == False:    
                        with open(Data_folder + '/Monitoring.csv', 'a') as fileM: # write the actual csv
                            writerM = csv.writer(fileM)
                            writerM.writerow(dataM)

myFeeder = Feeder()

myFeeder.start()
 
# now = datetime.now()

# if now.hour < 8  or now.hour > 20:
#     if dark == 0:
#         myFeeder.reset_flag()
time.sleep(10)
myFeeder.reset_flag()
time.sleep(20)
myFeeder.reset_flag()
time.sleep(20)
myFeeder.reset_flag()
time.sleep(20)
myFeeder.reset_flag()
time.sleep(0.5)
myFeeder.blocker()
#myFeeder.join() #ne marche pas pour arrêter les mesures de poids

print("monitoring test finished")

