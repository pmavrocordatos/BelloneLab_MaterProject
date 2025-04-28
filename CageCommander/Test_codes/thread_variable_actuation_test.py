#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 11:36:28 2023

@author: psyteam74
"""

######################## IMPORTS ######################## 
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
import pdb


######################## SYSTEM INITIATION ######################## 
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


######################## NIGHT PERF MONITORING STUFF ######################## 
def findMiddle(input_list):
    middle = float(len(input_list))/2
    if middle % 2 != 0:
        return input_list[int(middle - .5)]
    else:
        return (input_list[int(middle)]) # if the list has a pair number of elements the returned value is the one after the middle one
    
######################## PYGAME INITIATION ######################## 
#pdb.set_trace()

pygame.init() 

# Screen setting
#screen = pygame.display.set_mode((1920, 1080))
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption('EcoBox Test')
pygame.mouse.set_visible(0)

# Image importation
grid = pygame.image.load("Img/grid.png").convert()
line = pygame.image.load("Img/line.png").convert()
white = pygame.image.load("Img/white.png").convert()
black = pygame.image.load("Img/black.png").convert()

# Get image size
grid_size = grid.get_size()
line_size = line.get_size()
blink_size = white.get_size()
screen_size = screen.get_size()

# Define scale
scale = 1.8

# Put image at scale
grid = pygame.transform.scale(grid, (grid_size[0]*scale, grid_size[1]*scale))
line = pygame.transform.scale(line, (line_size[0]*scale, line_size[1]*scale))
white = pygame.transform.scale(white, (blink_size[0]*scale, blink_size[1]*scale))
black = pygame.transform.scale(black, (blink_size[0]*scale, blink_size[1]*scale))

# Get scaled image size
grid_size = grid.get_size()
line_size = line.get_size()
blink_size = white.get_size()

######################## CAMERA ZONES ######################## 
LeftDoorZone = lambda: cams.getZoneStates(0)[0] #call the function with LeftDoorZone()
time.sleep(0.03)
RightDoorZone = lambda: cams.getZoneStates(0)[1]
time.sleep(0.03)

JuvDoorZone = lambda: cams.getZoneStates(0)[stimSide]
# global JuvDoorState
JuvDoorState = JuvDoorZone()
time.sleep(0.03)

ObjDoorZone = lambda: cams.getZoneStates(0)[abs(stimSide-1)]
# global ObjDoorState
ObjDoorState = ObjDoorZone()
time.sleep(0.03)

#FeedDoorZone = lambda: cams.getZoneStates(0)[2]

BeddingZone = lambda: cams.getZoneStates(0)[3]
# global BeddingState
BeddingState = BeddingZone()
time.sleep(0.03)

JuvDoorStimZone = lambda: cams.getZoneStates(1)[0] # Carefull if we have a camera in each stim side! (correct with stim side etc...)
# global JuvDoorStimState
JuvDoorStimState = JuvDoorStimZone()
ObjDoorStimZone = True # We dont have a second camera for the stim object side (to transform into function if a second camera is installed -> check call into tasks)


######################## MONITORING/FEEDING ######################## 
# weight1.startTare(1) #taring balance before 
# #weight1.startTare(0) # fausse les mesures du nest
# time.sleep(10)
# print("Tare done")

# weight1.startWeightMeasure(0) # to avoid automatic measure (ask Raph)
# print("measure 0 started")

# time.sleep(1)
# weight1.startWeightMeasure(1)
# print("measure 1 started")

Task_start = int(time.time())
print("Task start: ",Task_start)
# threads = []
# event = threading.Event()
weight1.disableSensor(0) #turn off bottle weight measurement

time.sleep(0.03)
weight1.startTare(1)
time.sleep(10)

now = datetime.now()
if now.hour < 8  or now.hour > 20: 
   dark = 1
else:
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
        self.door_open_R = False
        self.door_closed_R = False
        self.door_open_L = False
        self.door_closed_L = False
        
        #self.start()
    def reset_flag(self):
        with self.lock:
            self.flag = True
           
    def blocker(self):
        self.stop_control = True
        
    def set_door_open_R(self):
        with self.lock:
            self.door_open_R = True
        
    def set_door_closed_R(self):
        with self.lock:
            self.door_closed_R = True
        
    def set_door_open_L(self):
        with self.lock:
            self.door_open_L = True
        
    def set_door_closed_L(self):
        with self.lock:
            self.door_closed_L = True
    
    def run(self):
        # Names columns
        headerM = ['Timestamp', 'Mouse_weight', 'Mouse_weight_since', 'Bottle_weight', 'Bottle_weight_since','Pellets_consumed'] #['Timestamp', 'Mouse_weight', 'Mouse_weight_since', 'Bottle_weight', 'Bottle_weight_since','Pellets_consumed']
        Mouse_weight = 0
        first_measure = True
        Mouse_weight_since = 0
        #Bottle_weight = 0
        previous_bedding = 0
        last_tare = 0
        #previous = 0
        Pellets_consumed = 0
        Mouse_weight_array = []
        #Bottle_weight_array = []
        
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
            time.sleep(0.1)
            global JuvDoorState
            JuvDoorState = JuvDoorZone()
            time.sleep(0.1)
            global ObjDoorState
            ObjDoorState = ObjDoorZone()
            time.sleep(0.1)
            global JuvDoorStimState
            JuvDoorStimState = JuvDoorStimZone()
            time.sleep(0.1)
            global BeddingState
            BeddingState = BeddingZone()
            time.sleep(0.1)
            
            if self.stop_control:
                break
            
            now = datetime.now()
            
            if self.door_open_R:
                doors1.setDoorState(1, 3) #doors1.setDoorState(0, 3) #door half open 
                time.sleep(0.1)
                self.door_open_R = False
            
            if self.door_closed_R:
                doors1.setDoorState(1, 1) #doors1.setDoorState(0, 3) #door closed
                time.sleep(0.1)
                self.door_closed_R = False
                
            if self.door_open_L:
                doors1.setDoorState(0, 3) #doors1.setDoorState(0, 3) #door half open 
                time.sleep(0.1) 
                self.door_open_L = False
               
            if self.door_closed_L:
                doors1.setDoorState(0, 1) #doors1.setDoorState(0, 3) #door half open 
                time.sleep(0.1)
                self.door_closed_L = False
            
            if BeddingZone():
                TimestampBedding = int(time.time())-Task_start
                if TimestampBedding - previous_bedding > 5: # when the mouse is in the bedding, if weight was taken 
                    previous_bedding = TimestampBedding
                    weight1.startWeightMeasure(1) # SHOULD WORK HERE
                    time.sleep(0.01)
                    current_weight = weight1.getWeight(1)[0]
                    Mouse_weight_array.append(current_weight)
                    time.sleep(0.01)
                    #weight1.startWeightMeasure(0)
                    time.sleep(0.01)
                    #current_bottle_weight = weight1.getWeight(0)[0]
                   # Bottle_weight_array.append(current_bottle_weight)
                    time.sleep(0.01)
                    first_measure = False
                    print("mouse weight measure taken: ", Mouse_weight_array[-1])
                   # print("bottle weight measure taken: ", Bottle_weight_array[-1])
                    print(now)
            else:
                current_tare = time.time()-Task_start
                if current_tare - last_tare > 200: # faire une tare toutes les 200 secondes
                    weight1.startTare(1) #tare mouse bedding
                    last_tare = current_tare
                
            
            time.sleep(0.25)
            
            if feeder1.getPelletSensorState() == 0:
                time.sleep(0.01)
                if feeder1.getPelletRemaining() == 0:
                    feeder1.setPellet(1)
                
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
                    # Bottle_weight = sum(Bottle_weight_array)/len(Bottle_weight_array)
                    # print("mean of bottle weight measures taken: ", Bottle_weight, "from: ", Bottle_weight_array) 
                    
                    print(now)
                    
                    ### time since last measure ###
                    Mouse_weight_since = weight1.getWeight(1)[1] # Gets the time since last weight measurement (when the last function "weight1.startWeightMeasure(0)" was called)
                    time.sleep(0.01)
                    # Bottle_weight_since = weight1.getWeight(0)[1]
                    
                    
                    dataM = [TimestampBis, Mouse_weight, Mouse_weight_since, Pellets_consumed]#[TimestampBis, Mouse_weight, Mouse_weight_since, Bottle_weight, Bottle_weight_since, Pellets_consumed]
                    feeder1.initTotalFeed(0)
                    Mouse_weight_array = []
                   #Bottle_weight_array = []
                    self.flag = False
                    
                elif len(Mouse_weight_array) == 0 and first_measure == False:
                    Mouse_weight = None # we take the previous weight computed (mean of weight array)
                    # we keep the previous mouse weight
                    TimestampBis = time.time()-Task_start
                    Mouse_weight_since = weight1.getWeight(1)[1] # Gets the time since last weight measurement in  minutes
                    time.sleep(0.01)
                    #Bottle_weight = weight1.getWeight(0)[0]
                    time.sleep(0.01)
                    Pellets_consumed = feeder1.getTotalFeed()
                      #to replace with function
                    dataM = [TimestampBis, Mouse_weight, Mouse_weight_since, Pellets_consumed]#[TimestampBis, Mouse_weight, Mouse_weight_since, Bottle_weight, Bottle_weight_since, Pellets_consumed]
                    feeder1.initTotalFeed(0)
                    Mouse_weight_array = []
                    self.flag = False
                
                if first_measure == False:    
                    with open(Data_folder + '/Monitoring.csv', 'a') as fileM: # write the actual csv
                        writerM = csv.writer(fileM)
                        writerM.writerow(dataM)

myFeeder = Feeder()

myFeeder.start()


######################## LAUNCHING THE TASK ######################## 
print("\n-> Running the task baby !!\n")
going = True
timeout = True
stage = 1      # Etape de début
consecutive_success = 3 # number of consecutive success (switch from stages 1 to 2 and 2 to 3): should be set to 10
count = 0
margin = 200
event_list = []
screen.fill(0)

class perf(): # master structure for some variables
    pass
p = perf() 
pygame.display.flip()

pygame.event.clear()

######################## GAME LOOP ########################
while going:
    
    now = datetime.now()
    key = pygame.key.get_pressed()
    print(JuvDoorState, ObjDoorState, JuvDoorStimState, BeddingState)
    time.sleep(2)
    #myFeeder.reset_flag()
    #myFeeder.set_door_open_R()

myFeeder.blocker()
