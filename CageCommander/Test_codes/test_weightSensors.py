# coding: utf-8
#   PACKAGE IMPORT #
import ModularStuffBoard_2302_01
import time
import glob
          
# USER INPUT FOR MODULES I2C ADRESS (IN HEX)
# BY DEFAULT, THE I2C ADR. START WITH 5 LIKE 0x56

wght_i2cAdr = input("Set WEIGHT device I2C address (hex) 0x52 by default: 0x")

# CREATE A "BOX" OBJECT AND OPEN THE COMMUNICATION PORT #
# BAUDRATE IS 115200 BY DEFAULT
my_ports = glob.glob ('/dev/tty[A-Za-z]*')
myBox = ModularStuffBoard_2302_01.netBox(my_ports[0], 115200)

# COM PORT ERROR, ENDING #
if myBox is None:
    print("ABORT, device not connected")

# COM PORT OPENED
else:

    # CONFIGURE THE BOX WITH THE USED MODULES   #
    # Create a new weight sensor module in the box with I2C adress
    weight1 = ModularStuffBoard_2302_01.weightMeasurement(myBox, int(wght_i2cAdr, 16))
    
    # Disable sensor x, the sensor will be automatically enable when "startTare" or "startWeightMeasure" is called
    weight1.disableSensor(0);

    
    while True:
    
        function = int(input("\n\rSelect function to test: \n\r 00: getWeight(0)\n\r 01: startTare(0)\n\r 02: startWeightMeasure(0)\n\r 10: getWeight(1)\n\r 11: startTare(1)\n\r 12: startWeightMeasure(1)\n\r --> "))
        
        if (function==0):
            print("\r\n --> Weight: ", weight1.getWeight(0))
        if (function == 1):
            weight1.startTare(0)
        if (function == 2):
            weight1.startWeightMeasure(0)
            
        if (function == 10):
            print("\r\n --> Weight: ", weight1.getWeight(1))         
        if (function == 11):
            weight1.startTare(1)
        if (function == 12):
            weight1.startWeightMeasure(1)
        time.sleep(0.02)