# coding: utf-8
#   PACKAGE IMPORT #
import ModularStuffBoard_2302_01
import time
import glob
import serial.tools.list_ports
# USER INPUT FOR MODULES I2C ADRESS (IN HEX)
# BY DEFAULT, THE I2C ADR. START WITH 5 LIKE 0x56
cam_i2cAdr = input("Set CAMERA device I2C address (hex) 0x56 by default: 0x")
fdr_i2cAdr = input("Set FEEDER device I2C address (hex) 0x51 by default: 0x")
wght_i2cAdr = input("Set WEIGHT device I2C address (hex) 0x52 by default: 0x")
servo_i2cAdr = input("Set SERVO device I2C address (hex) 0x53 by default: 0x")

# CREATE A "BOX" OBJECT AND OPEN THE COMMUNICATION PORT #
# BAUDRATE IS 115200 BY DEFAULT
# Ports handler

my_ports = glob.glob ('/dev/tty[A-Za-z]*')
myBox = ModularStuffBoard_2302_01.netBox(my_ports[0], 115200)

if myBox is None:
    print("ABORT, device not connected")


# COM PORT OPENED
else:

    # CONFIGURE THE BOX WITH THE USED MODULES   #
    # Create a new camera module in the box with I2C adress
    cams = ModularStuffBoard_2302_01.camTracking(myBox, 0x56)
    
    # Create a new feeder module in the box with I2C adress
    feeder1 = ModularStuffBoard_2302_01.feeder(myBox, int(fdr_i2cAdr, 16))
    
    # Create a new weight sensor module in the box with I2C adress
    weight1 = ModularStuffBoard_2302_01.weightMeasurement(myBox, int(wght_i2cAdr, 16))
    
    # Create a new servomotor module in the box with I2C adress
    doors1 = ModularStuffBoard_2302_01.pwmServo(myBox, int(servo_i2cAdr, 16))
    

    
    while True:
    
        print("Pos on cam 0: ", cams.getPosition(0))
        time.sleep(0.02)
        z = cams.getZoneStates(0)
        time.sleep(0.02)
#        print("Zones: ", z)
        if z[0]== 1:
            cams.setLight(0, 0)
            time.sleep(0.02)
            pellet = feeder1.getPelletRemaining()
            if(pellet == 0):
                #feeder1.setPellet(0)
                print("SET PELLET!")
            else:
                print("Feeder not clear !!! ", pellet)              
        else:
            cams.setLight(0, 1)
            time.sleep(0.02)

        if z[1]== 1:
            doors1.setDoorState(1, 3)
            time.sleep(0.02)
        else:
            doors1.setDoorState(1, 1)
            
        if z[2]== 1:
            print("Bottle weight: ")
            print(weight1.getWeight(0))
            time.sleep(0.02)
            print("Mouse weight: ")
            weight1.startWeightMeasure(1)
            time.sleep(0.5)
            print(weight1.getWeight(1))
        
        if z[3]== 1:
            weight1.startTare(1)
            doors1.setDoorState(0, 1)
            time.sleep(0.02)
        else:
            doors1.setDoorState(0, 3)
            time.sleep(0.02)