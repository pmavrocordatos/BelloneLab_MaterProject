# coding: utf-8
#   PACKAGE IMPORT #
import ModularStuffBoard_2302_01
import time
import glob

# USER INPUT FOR MODULES I2C ADRESS (IN HEX)
# BY DEFAULT, THE I2C ADR. START WITH 5 LIKE 0x56

fdr_i2cAdr = input("Set FEEDER device I2C address (hex) 0x51 by default: 0x")


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
    feeder1 = ModularStuffBoard_2302_01.feeder(myBox, int(fdr_i2cAdr, 16))
    
    while True:
    
        function = int(input("\n\rSelect function to test: \n\r 00: setPellet\n\r 01: getPelletRemaining\n\r 02: getTotalFeed\n\r 03: initTotalFeed \n\r 04: getPelletSensorState\n\r--> "))
        
        if (function==0):
            howMany = input("How many pellet do you want to feed ? :")
            feeder1.setPellet(int(howMany))
            print("\r\n --> Start feed ! ()", howMany)

        if (function == 1):
            print("Number of pellet to feed remaining: ", feeder1.getPelletRemaining())

        if (function == 2):
            print("Total of pellet feeded: ", feeder1.getTotalFeed())

        if (function == 3):
            howMany = input("How many pellet feeded will initialize the counter:")
            feeder1.initTotalFeed(int(howMany))

        if (function == 4):
            print("Pellet sensor state: ", feeder1.getPelletSensorState())  
        time.sleep(0.02)