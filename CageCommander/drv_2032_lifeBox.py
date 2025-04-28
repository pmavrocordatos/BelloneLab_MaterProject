## drv_2032_lifeBox.py
## Python driver for Arduino board 2032
## Version 1.0 29.06.2022 / Rth
##

import threading
import json
import sys
import os
import time
import serial
import numpy as np

Pellets_consumed = 0


class myThread (threading.Thread):
    def __init__(self, name, comPort, event):
        threading.Thread.__init__(self)
        # self.daemon = True
        self.event = event
        
        class door:
            state = -1
            usr_command = -1
        class mouse:
            weight = -1
            oldTime = -1
            posX = -1
            posY = -1

        class feeder:
            sensorState = -1

        class bottle:
            state = -1
            weight = -1

        class scale:
            weight = -1

        class camera:
            activeZones = [-1, -1, -1, -1]
            activeZonesLast = [-2, -2, -2, -2]

        class camera0:
            activeZones = [-1, -1, -1, -1]
            activeZonesLast = [-2, -2, -2, -2]
            
        self.doors= [door(),door()]
                
        self.mices =[mouse(), mouse()]
        self.cams = [camera(),camera0()]
        
        self.feeders = [feeder()]                       # pellet sensor state of feeder
        self.waterBottle = [bottle()]
        self.scales = [scale()]                         # weight actually measured on the scale       
        
        self.name = name
        self.comPort = comPort
        self.serialComStatus = -1
                
        self.dataDateTime = time.time()
        try:
            self.ser = serial.Serial(comPort, 57600, timeout=0.1)  # open serial port
            self.serialComStatus = 1
        except:
            print("[ERROR] IMPOSSIBLE TO OPEN \"" + comPort + "\"")
            self.serialComStatus = -1
                
    def run(self):
        print ("\n-> Starting communication thread with " + self.name)
        # Get lock to synchronize threads
        threadLock.acquire()
        while(self.serialComStatus > 0):
            # check for stop
            if self.event.is_set():
                return
            sline=self.ser.readline()
            try:    
                #print(sline)
                if(sline != ""):
                    parsed = json.loads(sline)
                    # print(json.dumps(parsed, sort_keys=True, indent=4))
                    self.doors[0].state = parsed["data"]["main_door_state"]
                    self.doors[1].state = parsed["data"]["fake_door_state"]
                    
                    self.mices[0].weight = parsed["data"]["main_room"]["mouse"]["weight"]
                    self.mices[0].oldTime = parsed["data"]["main_room"]["mouse"]["weight_data_old_time"]
                    self.mices[0].posX = parsed["data"]["main_room"]["mouse"]["pos_X"]
                    self.mices[0].posY = parsed["data"]["main_room"]["mouse"]["pos_Y"]
                    
                    self.feeders[0].sensorState = parsed["data"]["main_room"]["feeder"]["pellet_state"]
                    
                    self.waterBottle[0].state = parsed["data"]["main_room"]["bottle"]["state"]
                    self.waterBottle[0].weight = parsed["data"]["main_room"]["bottle"]["weight"]
                    
                    self.scales[0].weight = parsed["data"]["main_room"]["weight_plate"]["value"]
                    
                    self.cams[0].activeZones[0] = parsed["data"]["main_room"]["doors"]["leftIsActive"]
                    self.cams[0].activeZones[1] = parsed["data"]["main_room"]["doors"]["rightIsActive"]
                    self.cams[0].activeZones[2] = parsed["data"]["main_room"]["feeder"]["isActive"]
                    self.cams[0].activeZones[3] = parsed["data"]["main_room"]["weight_plate"]["isActive"]
                    
                    self.mices[1].posX = parsed["data"]["stim_room"]["mouse"]["pos_X"]
                    self.mices[1].posY = parsed["data"]["stim_room"]["mouse"]["pos_Y"]
                    
                    self.cams[1].activeZones[0] = parsed["data"]["stim_room"]["doors"]["leftIsActive"]
                    self.cams[1].activeZones[1] = parsed["data"]["stim_room"]["doors"]["rightIsActive"]
            except:
                pass
                # print("JSON READ ERROR")
                #print(" DATA: " + str(sline))
            #if(self.doors[0].usr_command != self.doors[0].state):
             #   print("force update TO DOOR ------------------")
                #setDoorState(0,usr_command)
            #if(self.doors[1].usr_command != self.doors[1].state):
             #   print("force update TO DOOR ------------------")
                #setDoorState(1,usr_command)
            time.sleep(0.05)
      
        # Free lock to release next thread
        print ("\n-> Exiting serial thread -> "  + self.name)
        threadLock.release()

    def camZonesHasChanged(self, zoneNb):
        zoneChange = 0
        for x in range(4):
            actualState = self.cams[zoneNb].activeZones[x]
            lastState = self.cams[zoneNb].activeZonesLast[x]
                
            if(lastState != actualState):
                zoneChange += 1
 
        if(zoneChange > 0):
            for x in range(4):
                self.cams[zoneNb].activeZonesLast[x] = self.cams[zoneNb].activeZones[x]
                #return self.cams[zoneNb].activeZones.all()
                return True
        else :
            return None
            
    def getCamZones(self, zoneNb):
            return self.cams[zoneNb].activeZones

        
    def getScaleValue(self, sensorNb):
        return self.scales[sensorNb].weight

    def getPelletSensor(self, sensorNb):
        return self.feeders[sensorNb].sensorState  

    def getMouseData(self, mouseNb):
        return self.mices[mouseNb]
    
    def getBottleData(self, bottleNb):
        return self.waterBottle[bottleNb]        
        
    def getDoorState(self, doorNb):
        return self.doors[doorNb].state
    
    def setPellet(self, zoneNb):
        global Pellets_consumed
        self.ser.write(("{\"msgFrom\":\"" + str(self.name) + "\",\"msgId\":97640,\"msgType\":\"command\",\"data\":{\"main_room\":{\"feeder\":{\"pellet_set\": 1}}}}").encode())
        Pellets_consumed += 1
        time.sleep(0.1)
    
    def setDoorState(self, doorNb, state):
        self.doors[doorNb].usr_command = state
        if(self.doors[doorNb].state != state):
            doorName = "main_door"
            if(doorNb == 0):
                doorName ="main_door"
            else:
                doorName ="fake_door"
                
            if(self.serialComStatus >0):
                self.doorState = state
                if(state):
                    self.ser.write(("{\"msgFrom\":\"" + str(self.name) + "\",\"msgId\":97640,\"msgType\":\"command\",\"data\":{\"" + str(doorName) + "\":1}}").encode())
                else:
                    self.ser.write(("{\"msgFrom\":\"" + str(self.name) + "\",\"msgId\":97640,\"msgType\":\"command\",\"data\":{\"" + str(doorName) + "\":0}}").encode())
                time.sleep(0.1)
                #print("--- DOOR ACTION ----")
            else:
                print("[ERROR] COM PORT IS NOT OPEN")
    def getDataTimeStamp(self):
        timeStamp = "[" + self.name + "] " + str(time.ctime(time.time()))
        return timeStamp
        
    def close_serial(self):
        self.ser.close()  
        self.serialComStatus = 0
        return
        
def print_time(threadName):
      print ("%s: %s" % (threadName, time.ctime(time.time())))

threadLock = threading.Lock()
