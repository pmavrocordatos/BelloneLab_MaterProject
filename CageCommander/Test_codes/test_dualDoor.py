# coding: utf-8
#   PACKAGE IMPORT #
import ModularStuffBoard_2302_01
import time
          
# USER INPUT FOR MODULES I2C ADRESS (IN HEX)
# BY DEFAULT, THE I2C ADR. START WITH 5 LIKE 0x56

step_i2cAdr = input("Set DUAL DOORS device I2C address (hex) 0x58 by default: 0x")

 
# CREATE A "BOX" OBJECT AND OPEN THE COMMUNICATION PORT #
# BAUDRATE IS 115200 BY DEFAULT
import glob

# Ports handler

my_ports = glob.glob ('/dev/tty[A-Za-z]*')
myBox = ModularStuffBoard_2302_01.netBox(my_ports[0], 115200)


# COM PORT ERROR, ENDING #
if myBox is None:
    print("ABORT, device not connected")

# COM PORT OPENED
else:

    # CONFIGURE THE BOX WITH THE USED MODULES   #
    # Create a new weight sensor module in the box with I2C adress
    doors = ModularStuffBoard_2302_01.dualStepper(myBox, int(step_i2cAdr, 16))


    
    while True:
    
        function = int(input("\n\rSelect function to test: \n\r 00: close door (0)\n\r 01: open door(0)\n\r 02: door speed(0)\n\r 10: close door (1)\n\r 11: open door(1)\n\r 12: door speed(1)\n\r --> "))
        
        if (function==0):
            print("\r\n --> Closing door 0")
            doors.setDoorState(0,0)
        if (function == 1):
            print("\r\n --> Opening door 0")
            doors.setDoorState(0,1)
        if (function == 2):
            usr_speed = input("\r\n --> Enter speed (0..100) [%]: ")
            doors.setDoorSpeed(0, int(usr_speed, 10))
            
        if (function==10):
            print("\r\n --> Closing door 1")
            doors.setDoorState(1,0)
        if (function == 11):
            print("\r\n --> Opening door 1")
            doors.setDoorState(1,1)
        if (function == 12):
            usr_speed = input("\r\n --> Enter speed (0..100) [%]: ")
            doors.setDoorSpeed(1, int(usr_speed, 10))
        time.sleep(0.02)