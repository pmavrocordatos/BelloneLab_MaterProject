#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:02:30 2022

@author: sfxindamix
"""

# Restart the kernel before launching the task !!

import pygame
import drv_2032_lifeBox
import time
from datetime import datetime
import csv
import os
import serial.tools.list_ports
import sys
import threading
from random import seed
from random import randint
from numpy import isnan
import ModularStuffBoard_2302_01


try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass

print("Hope you performed a reset of all the hardware and the kernel before launching the task !!!")
Exit = int(input("So, reset done (1) or not (0): "))
if Exit == 0:
    print("\nExiting the task... Reset the hardware and the kernel !!!")
    sys.exit()

## All the informations about the mouse are here:
MouseID = input("\nMouse ID: ")
MouseDoB = input("Date of birth (YYYYMMDD): ")
isKO = input("Is it a LgDel mouse (1 = yes / 0 = no): ")
stimSide = int(input("The stim mouse is placed left (0) or right (1): "))
socialRewardStim = int(input("The visual stimulus associated with the social reward is the grid (0) or the lines (1): "))
Start_date = time.strftime('%d-%m-%Y %H:%M:%S')

#Create a new folder (if don't exist already)
Data_folder = 'Data/' + time.strftime('%Y-%m-%d') + '_Mouse-' + str(MouseID)
if not os.path.exists(Data_folder):
    os.makedirs(Data_folder)

LastKey = None
going = True

Task_start = time.time()
stage = 3                     # Etape de début
consecutive_success = 5 # define the number of success (will be used to switch stages)

pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption('EcoBox Test')
pygame.mouse.set_visible(0)
grid = pygame.image.load("Img/grid.png").convert()
line = pygame.image.load("Img/line.png").convert()
white = pygame.image.load("Img/white.png").convert()
black = pygame.image.load("Img/black.png").convert()
grid_size = grid.get_size()
line_size = line.get_size()
blink_size = white.get_size()
screen_size = screen.get_size()
scale = 1.8
grid = pygame.transform.scale(grid, (grid_size[0]*scale, grid_size[1]*scale))
line = pygame.transform.scale(line, (line_size[0]*scale, line_size[1]*scale))
white = pygame.transform.scale(white, (blink_size[0]*scale, blink_size[1]*scale))
black = pygame.transform.scale(black, (blink_size[0]*scale, blink_size[1]*scale))
grid_size = grid.get_size()
line_size = line.get_size()
blink_size = white.get_size()

threads = []
event = threading.Event()



myBox = ModularStuffBoard_2302_01.netBox("/dev/ttyUSB0", 115200) # Open communication port to gateway

if myBox is None:
    print("ABORT, device not connected")

# COM PORT OPENED
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
    
    
# Démarre le driver de communication avec le Arduino de la boite de comportement
#myBox.start() ##NO NEED IN UPDATED VERSION OF THE CODE#

class perf(): # master structure for some variables
    pass
p = perf() 

# Gestion du feeding en //
class Feeder(threading.Thread): # monitoring
    def __init__(self, event):
        threading.Thread.__init__(self)
        # self.daemon = True
        self.event = event
        self.start()
    
    def run(self):
        # Names columns
        headerM = ['Timestamp', 'Mouse_weight', 'Mouse_weight_since', 'Bottle_weight', 'Pellets_consumed']
        Mouse_weight = 0
        Mouse_weight_since = 0
        Bottle_weight = 0
        previous = 0
        
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
            # check for stop
            if self.event.is_set():
                # Fill the rows with a timestamp
                TimestampBis = time.time()-Task_start
                # Fill the rows with monitoring values, for every timestamp
                Mouse_weight = weight1.getWeight(0)[0] # Verify that the sensor (0) is for the mouse weight and (1) for bottle weight
                Mouse_weight_since = weight1.getWeight(0)[1] # Gets the time since last weight measurement
                Bottle_weight = weight1.getWeight(1)[0]
                dataM = [TimestampBis, Mouse_weight, Mouse_weight_since, Bottle_weight, drv_2032_lifeBox.Pellets_consumed]
                drv_2032_lifeBox.Pellets_consumed = 0 # ?
                with open(Data_folder + '/Monitoring.csv', 'a') as fileM: # write the actual csv
                    writerM = csv.writer(fileM)
                    writerM.writerow(dataM)
                return
            time.sleep(0.25)
            if(cams.getZoneStates(0) == True and feeder1.getPelletRemaining() == 0): # If getPelletRemaining() == 0, then the mouse ate all the previous pelets. if (by chance) the mouse didn't eat the previous pellets that has been given, the function wont give any pelet 
            # if myBox.getCamZones(0)[2] == 1:
                feeder1.setPellet(1) # gives a pellet
                time.sleep(0.1)
            TimestampBis = time.time()-Task_start
            if int(TimestampBis) % 30 == 0 and int(previous) != int(TimestampBis): # Gets the monitoring data every 30 seconds
                previous = TimestampBis
                Mouse_weight = weight1.getWeight(0)[0]
                Mouse_weight_since = weight1.getWeight(0)[1]
                Bottle_weight = weight1.getWeight(1)[0]
                dataM = [TimestampBis, Mouse_weight, Mouse_weight_since, Bottle_weight, drv_2032_lifeBox.Pellets_consumed]
                drv_2032_lifeBox.Pellets_consumed = 0 # ? est-ce qu'il y a cette fonction dans le code de Raph?
                with open(Data_folder + '/Monitoring.csv', 'a') as fileM:
                    writerM = csv.writer(fileM)
                    writerM.writerow(dataM)
          
myFeeder = Feeder(event) #Is feeder the monitoring class: yes

# Add threads to thread list
threads.append(myBox) # to supress
threads.append(myFeeder)

print("\n-> Running the task baby !!\n")

screen.fill(0) 
pygame.display.flip()

# There is four zones for the cameras: two on test mouse side, two for each stim side
# myBox.getCamZones(0)[0]

# ?????? define the zone state ?? -> lambda

LeftDoorZone = myBox.getCamZones(0)[0] # Define left door zone with the camera (0) zone [0]
RightDoorZone = lambda: myBox.getCamZones(0)[1] # Define right door zone with the camera (0) zone [1]

JuvDoorZone = lambda: myBox.getCamZones(0)[stimSide] # Since stimside was defined earlier either (1) right or (0) left, JuvDoorZone == LeftDoorZone or RightDoorZone
ObjDoorZone = lambda: myBox.getCamZones(0)[abs(stimSide-1)]


## Snew variable: is stim in the write zone? ### stimzone = []...



# Where are these "LeftDoorStimZone" and "RightDoorStimZone" zones? -> in this configuration, we need only one zone.

#LeftDoorStimZone = lambda: myBox.getCamZones(1)[1] # Position [1] of the second camera (1) seems to be the left (opposit to the first camera)
#RightDoorStimZone = lambda: myBox.getCamZones(1)[0]

ObjDoorStimZone = lambda: myBox.getCamZones(1)[stimSide] # Left and right seems to be opposit between cam (0) and cam (1)...
JuvDoorStimZone = lambda: myBox.getCamZones(1)[abs(stimSide-1)]

# ActiveCamZones = myBox.getCamZones(0)
# LeftDoorZone = ActiveCamZones[0]
# RightDoorZone = ActiveCamZones[1]

# ActiveCamZonesStim = myBox.getCamZones(1)
# LeftDoorStimZone = ActiveCamZones[1]
# RightDoorStimZone = ActiveCamZones[0]


# Programme fonctionne en boucle avec attente de X ms tant que la communication avec arduino est active
while (myBox.serialComStatus > 0) and going == True:
    
    
    if stage == 1: # In this stage the mice just has to learn that when she touch the screen, it opens a door
        count = 0   
        header = ['Timestamp', 'Success', 'Elapsed_time'] # set the column names
        Timestamp = 0
        Success = 0
        Elapsed_time = 0
        with open(Data_folder + '/stage1.csv', 'w') as file: # creates csv file
            # insert all the mouse data
            writer = csv.writer(file)
            writer.writerow([Start_date])
            writer.writerow('')
            writer.writerow(['Mouse ID: ', MouseID])
            writer.writerow(['DoB: ', MouseDoB])
            writer.writerow(['isKO (1 = LgDel): ', isKO])
            writer.writerow(['Stim side (1 = right): ', stimSide])    
            writer.writerow('')
            writer.writerow(header)
    while stage == 1: 
        for e in pygame.event.get():
            if e.type == pygame.FINGERDOWN:
                # if e.key == pygame.K_h:
                start = time.time()
                Timestamp = start-Task_start # time relative to very beggining
                timeout = False
                myBox.setDoorState(0,1) # Door (0) = main_door is set to (1) = open
                time.sleep(0.05)
                myBox.setDoorState(1,1)# Door (1) = fake_door is set to (1) = open
                while timeout == False:
                    end = time.time() 
                    screen.blit(white, (0, screen_size[1]-blink_size[1])) # the screens shows white squares, the mouse has to go to the interaction zone 
                    screen.blit(white, (screen_size[0]-blink_size[0], screen_size[1]-blink_size[1]))
                    pygame.display.flip()
                    time.sleep(0.25) # not for very long... just a blincking for 15 seconds
                    screen.fill(0) # black screen
                    pygame.display.flip()
                    time.sleep(0.25)
                    if(LeftDoorZone() or RightDoorZone()): # if mouse go to an interaction zone
                        count += 1 
                        Success = 1
                        Elapsed_time = end-start # duration of the trial is registered
                        timeout = True # the mouse is the interraction zone, the door will close in 7 seconds
                        time.sleep(7) 
                        myBox.setDoorState(0,0) # close the door
                        time.sleep(0.075)
                        myBox.setDoorState(1,0) # close the door
                    elif end-start >= 15: # If the mouse didn't go to the interaction zone, the door will close
                        myBox.setDoorState(0,0)
                        time.sleep(0.075)
                        myBox.setDoorState(1,0)
                        count = 0 # also the trial count stays at zero
                        Success = 0
                        Elapsed_time = 15 
                        timeout = True
                data = [Timestamp, Success, Elapsed_time] # collect data
                with open(Data_folder + '/stage1.csv', 'a') as file: #write data in file
                    writer = csv.writer(file)
                    writer.writerow(data)
                if count == consecutive_success: # number of success is defined at the start of the code (5)
                    stage = 2 #switch to stage 2
                    screen.fill(0) # screen black
                    pygame.display.flip()
                    # going = False # If we want to interupt the task at stage 1, we can turn going = False, so the while loop stops
                    
    if stage == 2: # In this stage, the mice has to pass on the zone of the doors and then click on the screen that is turned on showing white images
        count = 0
        Timestamp = 0
        Trial = 0
        Touched = 0
        Success = 0
        Elapsed_time = 0  
        header = ['Timestamp', 'Trial', 'Touched', 'Success', 'Elapsed_time']
        with open(Data_folder + '/stage2.csv', 'w') as file: # initiate csv writing and stores mouse infos
            writer = csv.writer(file)
            writer.writerow([Start_date])
            writer.writerow('')
            writer.writerow(['Mouse ID: ', MouseID])
            writer.writerow(['DoB: ', MouseDoB])
            writer.writerow(['isKO (1 = LgDel): ', isKO])
            writer.writerow(['Stim side (1 = right): ', stimSide])    
            writer.writerow('')
            writer.writerow(header)
    while stage == 2: 
        time.sleep(0.05)
        if (LeftDoorZone() == 1 or RightDoorZone() == 1): # if mouse in the door zone:
            # print("\n-> Trial initiated !!\n")
            start = time.time() # start time as soon as the mouse is on the zone
            Timestamp = start-Task_start # time relative to very beginning
            Trial += 1 
            timeout = False
            screen.blit(white, (0, screen_size[1]-blink_size[1]))  # the screen show white images
            screen.blit(white, (screen_size[0]-blink_size[0], screen_size[1]-blink_size[1])) # the screen show white images
            pygame.display.flip()
            while timeout == False:
                end = time.time()
                if end-start >= 60: # if go beyond 60 second to touch the screen -> 
                    count = 0 # count is kept at zero (then mouse has to make 5 consecutive success)
                    Success = 0 # no success
                    Touched = 0
                    Elapsed_time = 60
                    timeout = True
                    screen.fill(0) # black screen
                    pygame.display.flip()
                else:
                    for e in pygame.event.get():
                        if e.type == pygame.FINGERDOWN:
                            coordTouch = dict((k,e.dict[k]) for k in ['x', 'y'] if k in e.dict) #register touch coordinates
                            xy = list(coordTouch.values()) # il faut extraire coordonnées du toucher pour savoir quel stim visuel choisi
                            # print (str(xy))
                            if xy[0] <= blink_size[0]/screen_size[0] or xy[0] >= (screen_size[0]-blink_size[0])/screen_size[0]: # if mouse touche the screen correctly (on stim), 
                                startbis = time.time() # start second timer 
                                Touched = 1
                                myBox.setDoorState(0,1) # doors open
                                time.sleep(0.075)
                                myBox.setDoorState(1,1)
                                while timeout == False:
                                    end = time.time() # mouse did touch the screen: end of timer
                                    screen.blit(white, (0, screen_size[1]-blink_size[1])) 
                                    screen.blit(white, (screen_size[0]-blink_size[0], screen_size[1]-blink_size[1])) 
                                    pygame.display.flip() 
                                    time.sleep(0.25) 
                                    screen.fill(0)
                                    pygame.display.flip()
                                    time.sleep(0.25)
                                    if(LeftDoorZone() or RightDoorZone()): # mouse arrive at the interaction zone
                                        count += 1
                                        Success = 1
                                        Elapsed_time = end-start # the time between mouse in the zone and mouse touch the screen (stored here in case the mouse do not go to the interactionzone)
                                        timeout = True
                                        time.sleep(7) # mouse has 7 seconds of interaction
                                        myBox.setDoorState(0,0)
                                        time.sleep(0.075)
                                        myBox.setDoorState(1,0)
                                    elif end-startbis >= 15: # if the mouse took too much time (more than 15 seconds)
                                        myBox.setDoorState(0,0) # doors close
                                        time.sleep(0.075)
                                        myBox.setDoorState(1,0)
                                        count = 0
                                        Success = 0 # no success
                                        Elapsed_time = end-start
                                        timeout = True
            data = [Timestamp, Trial, Touched, Success, Elapsed_time]
            with open(Data_folder + '/stage2.csv', 'a') as file:
                writer = csv.writer(file)
                writer.writerow(data)
            time.sleep(5)
            if count == consecutive_success:
                stage = 3
                screen.fill(0)
                pygame.display.flip()
                # going = False            
        
    if stage == 3: # In this stage, the mice has to make (I think) the association between the stimuli and their corresponding reward (social/non-social)
        seed(1)
        cycles = 0
        dark = 0
        Timestamp = 0
        Trial = 0  
        socialStimSide = []
        social = 0
        p.social = []
        p.retrieved = []
        p.optout = []
        chosenStimSide = 0
        responseLatency = 0 
        rewardRetrievalLatency = 0
        recInteractionTime = 0
        uniInteractionTime = 0
        noInteractionTime = 0
        header = ['Timestamp', 'Trial', 'SocialStimSide', 'ChosenStimSide', 'SocialChosen', 'ResponseLatency', 'RewardRetrievalLatency', 
                  'RecInteractionTime', 'UniInteractionTime', 'NoInteractionTime']
        with open(Data_folder + '/stage3.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow([Start_date])
            writer.writerow('')
            writer.writerow(['Mouse ID: ', MouseID])
            writer.writerow(['DoB: ', MouseDoB])
            writer.writerow(['isKO (1 = LgDel): ', isKO])
            writer.writerow(['Stim side (1 = right): ', stimSide])   
            writer.writerow(['Visual stim leading to social stim (0 = grid & 1 = lines): ', socialRewardStim])
            writer.writerow('')
            writer.writerow(header)
    while stage == 3:
        time.sleep(0.05)
        if (LeftDoorZone() == 1 or RightDoorZone() == 1):
            start = time.time()
            Timestamp = start-Task_start
            Trial += 1
            timeout = False
            
            if len(socialStimSide)>9:
                if (sum(socialStimSide[-3:]) == 3 or sum(socialStimSide[-3:]) == 0 or
                    sum(socialStimSide[-10:]) == 7 or sum(socialStimSide[-10:]) == 3):
                    socialStimSide.append(abs(socialStimSide[-1]-1))
            elif (len(socialStimSide)<10 and len(socialStimSide)>2):
                if (sum(socialStimSide[-3:]) == 3 or sum(socialStimSide[-3:]) == 0):
                    socialStimSide.append(abs(socialStimSide[-1]-1))
            else:
                socialStimSide.append(randint(0,1)) # The size of the social stim (on screen) is randomly assigned to left or right
                
            if (socialStimSide[-1] == 1 and socialRewardStim == 1) or (socialStimSide[-1] == 0 and socialRewardStim == 0): 
                screen.blit(grid, (0, screen_size[1]-grid_size[1]))
                screen.blit(line, (screen_size[0]-line_size[0], screen_size[1]-line_size[1]))
            elif (socialStimSide[-1] == 0 and socialRewardStim == 1) or (socialStimSide[-1] == 1 and socialRewardStim == 0):
                screen.blit(line, (0, screen_size[1]-line_size[1]))
                screen.blit(grid, (screen_size[0]-grid_size[0], screen_size[1]-grid_size[1]))                
            pygame.display.flip()
            
            while timeout == False:
                end = time.time()
                if end-start >= 30:
                    Trial -= 1
                    del socialStimSide[-1]
                    timeout = True
                    screen.fill(0)
                    pygame.display.flip()
                    optout = 1
                else:
                    for e in pygame.event.get():
                        if e.type == pygame.FINGERDOWN: 
                            coordTouch = dict((k,e.dict[k]) for k in ['x', 'y'] if k in e.dict) 
                            xy = list(coordTouch.values())                             
                            startbis = time.time()
                            responseLatency = end-start
                            optout = 0
                            if (xy[0] <= blink_size[0]/screen_size[0] and socialStimSide[-1] == 0) or\
                                (xy[0] >= (screen_size[0]-blink_size[0])/screen_size[0] and socialStimSide[-1] == 1):
                                chosenStimSide = socialStimSide[-1]
                                social=1
                                myBox.setDoorState(stimSide,1)
                                while timeout == False:
                                    end = time.time()
                                    screen.blit(white, (0, screen_size[1]-blink_size[1]))
                                    screen.blit(white, (screen_size[0]-blink_size[0], screen_size[1]-blink_size[1]))
                                    pygame.display.flip()
                                    time.sleep(0.25)
                                    screen.fill(0)
                                    pygame.display.flip()
                                    time.sleep(0.25)
                                    if JuvDoorZone(): 
                                        startInteraction = time.time()
                                        startInteracTime = 0
                                        noInterac = 0
                                        uniInterac = 0
                                        recInterac = 0
                                        startedRec = 0
                                        startedUni = 0
                                        startedNo = 0
                                        rewardRetrievalLatency = end-startbis
                                        while timeout == False:
                                            endInteraction = time.time()
                                            if endInteraction-startInteraction >= 7:
                                                timeout = True
                                                if noInterac:
                                                    noInteractionTime = noInteractionTime+(endInteraction-startInteracTime)
                                                elif uniInterac:
                                                    uniInteractionTime = uniInteractionTime+(endInteraction-startInteracTime)
                                                elif recInterac:
                                                    recInteractionTime = recInteractionTime+(endInteraction-startInteracTime)
                                            elif JuvDoorZone() and JuvDoorStimZone():
                                                recInterac = 1
                                                if noInterac:
                                                    noInteractionTime = noInteractionTime+(endInteraction-startInteracTime)
                                                    noInterac = 0
                                                    startedNo = 0
                                                elif uniInterac:
                                                    uniInteractionTime = uniInteractionTime+(endInteraction-startInteracTime)
                                                    uniInterac = 0
                                                    startedUni = 0
                                                if startedRec == 0:
                                                    startInteracTime = time.time()
                                                    startedRec = 1
                                            elif JuvDoorZone() and not JuvDoorStimZone():
                                                uniInterac = 1
                                                if noInterac:
                                                    noInteractionTime = noInteractionTime+(endInteraction-startInteracTime)
                                                    noInterac = 0
                                                    startedNo = 0
                                                elif recInterac:
                                                    recInteractionTime = recInteractionTime+(endInteraction-startInteracTime)
                                                    recInterac = 0
                                                    startedRec = 0
                                                if startedUni == 0:
                                                    startInteracTime = time.time()
                                                    startedUni = 1
                                            else:
                                                noInterac = 1
                                                if recInterac:
                                                    recInteractionTime = recInteractionTime+(endInteraction-startInteracTime)
                                                    recInterac = 0
                                                    startedRec = 0
                                                elif uniInterac:
                                                    uniInteractionTime = uniInteractionTime+(endInteraction-startInteracTime)
                                                    uniInterac = 0
                                                    startedUni = 0
                                                if startedNo == 0:
                                                    startInteracTime = time.time()
                                                    startedNo = 1
                                        myBox.setDoorState(stimSide,0)
                                    elif end-startbis >= 15:
                                        noInteractionTime = float("NaN")
                                        recInteractionTime = float("NaN")
                                        uniInteractionTime = float("NaN")
                                        rewardRetrievalLatency = float("NaN")
                                        myBox.setDoorState(stimSide,0) 
                                        timeout = True
                                data = [Timestamp, Trial, socialStimSide[-1], chosenStimSide, social, responseLatency, rewardRetrievalLatency, 
                                        recInteractionTime, uniInteractionTime, noInteractionTime]
                                with open(Data_folder + '/stage3.csv', 'a') as file:
                                    writer = csv.writer(file)
                                    writer.writerow(data)
                                noInteractionTime = 0
                                recInteractionTime = 0
                                uniInteractionTime = 0
                            elif (xy[0] <= blink_size[0]/screen_size[0] and socialStimSide[-1] == 1) or\
                                (xy[0] >= (screen_size[0]-blink_size[0])/screen_size[0] and socialStimSide[-1] == 0):
                                chosenStimSide = abs(socialStimSide[-1]-1)
                                social=0
                                myBox.setDoorState(abs(stimSide-1),1)
                                while timeout == False:
                                    end = time.time()
                                    screen.blit(white, (0, screen_size[1]-blink_size[1]))
                                    screen.blit(white, (screen_size[0]-blink_size[0], screen_size[1]-blink_size[1]))
                                    pygame.display.flip()
                                    time.sleep(0.25)
                                    screen.fill(0)
                                    pygame.display.flip()
                                    time.sleep(0.25)
                                    if ObjDoorZone(): 
                                        startInteraction = time.time()
                                        startInteracTime = 0
                                        noInterac = 0
                                        uniInterac = 0
                                        recInterac = 0
                                        startedRec = 0
                                        startedUni = 0
                                        startedNo = 0
                                        rewardRetrievalLatency = end-startbis
                                        while timeout == False:
                                            endInteraction = time.time()
                                            if endInteraction-startInteraction >= 7:
                                                timeout = True
                                                if noInterac:
                                                    noInteractionTime = noInteractionTime+(endInteraction-startInteracTime)
                                                elif uniInterac:
                                                    uniInteractionTime = uniInteractionTime+(endInteraction-startInteracTime)
                                                elif recInterac:
                                                    recInteractionTime = recInteractionTime+(endInteraction-startInteracTime)
                                            elif ObjDoorZone() and ObjDoorStimZone():
                                                recInterac = 1
                                                if noInterac:
                                                    noInteractionTime = noInteractionTime+(endInteraction-startInteracTime)
                                                    noInterac = 0
                                                    startedNo = 0
                                                elif uniInterac:
                                                    uniInteractionTime = uniInteractionTime+(endInteraction-startInteracTime)
                                                    uniInterac = 0
                                                    startedUni = 0
                                                if startedRec == 0:
                                                    startInteracTime = time.time()
                                                    startedRec = 1
                                            elif ObjDoorZone() and not ObjDoorStimZone():
                                                uniInterac = 1
                                                if noInterac:
                                                    noInteractionTime = noInteractionTime+(endInteraction-startInteracTime)
                                                    noInterac = 0
                                                    startedNo = 0
                                                elif recInterac:
                                                    recInteractionTime = recInteractionTime+(endInteraction-startInteracTime)
                                                    recInterac = 0
                                                    startedRec = 0
                                                if startedUni == 0:
                                                    startInteracTime = time.time()
                                                    startedUni = 1
                                            else:
                                                noInterac = 1
                                                if recInterac:
                                                    recInteractionTime = recInteractionTime+(endInteraction-startInteracTime)
                                                    recInterac = 0
                                                    startedRec = 0
                                                elif uniInterac:
                                                    uniInteractionTime = uniInteractionTime+(endInteraction-startInteracTime)
                                                    uniInterac = 0
                                                    startedUni = 0
                                                if startedNo == 0:
                                                    startInteracTime = time.time()
                                                    startedNo = 1
                                        myBox.setDoorState(abs(stimSide-1),0)
                                    elif end-startbis >= 15:
                                        noInteractionTime = float("NaN")
                                        recInteractionTime = float("NaN")
                                        uniInteractionTime = float("NaN")
                                        rewardRetrievalLatency = float("NaN")
                                        myBox.setDoorState(abs(stimSide-1),0) 
                                        timeout = True
                                data = [Timestamp, Trial, socialStimSide[-1], chosenStimSide, social, responseLatency, rewardRetrievalLatency, 
                                        recInteractionTime, uniInteractionTime, noInteractionTime]
                                with open(Data_folder + '/stage3.csv', 'a') as file:
                                    writer = csv.writer(file)
                                    writer.writerow(data)
                                noInteractionTime = 0
                                recInteractionTime = 0
                                uniInteractionTime = 0                       
            time.sleep(5)
            if Trial == consecutive_success: # à changer tout ça !! Remplacer 'Trial' par le track stabilité choix souris
                stage = 4 # In this stage, the effort component is implemented
                screen.fill(0)
                pygame.display.flip()
                going = False      
            now = datetime.now()
            if now.hour < 8  or now.hour > 20 and optout == 0:
                if dark == 0:
                    dark = 1
                p.social.append(social)
            
            key = pygame.key.get_pressed() #so pygame know which key is being pressed
    
            if key[pygame.K_ESCAPE]==True:
                going = False
  

#     pygame.draw.circle(screen, (255,255,255), (screen_size[0]/2,screen_size[1]*2/3), 50)
#     pygame.display.flip()
                
    time.sleep(0.05)
    
event.set()
for t in threads:
    t.join()

pygame.display.quit()
pygame.quit()
sys.exit()
                
