### UNEDING WHILE LOOP (?) ###
# coding: utf-8
import ModularStuffBoard_2302_01
import time
import glob
          
# USER INPUT FOR MODULES I2C ADRESS (IN HEX)
# BY DEFAULT, THE I2C ADR. START WITH 5 LIKE 0x56
#cam_i2cAdr = input("Set CAMERA device I2C address (hex) 0x56 by default: 0x")
#fdr_i2cAdr = input("Set FEEDER device I2C address (hex) 0x51 by default: 0x")
#wght_i2cAdr = input("Set WEIGHT device I2C address (hex) 0x52 by default: 0x")
#servo_i2cAdr = input("Set SERVO device I2C address (hex) 0x53 by default: 0x")

# CREATE A "BOX" OBJECT AND OPEN THE COMMUNICATION PORT
# BAUDRATE IS 115200 BY DEFAULT

my_ports = glob.glob ('/dev/tty[A-Za-z]*')
myBox = ModularStuffBoard_2302_01.netBox(my_ports[0], 115200)


# COM PORT ERROR, ENDING
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
    doors1 = ModularStuffBoard_2302_01.dualStepper(myBox, 0x58)

    
    
    while True:
    
        # BLINK TEST ON THE CAMERA LIGHTS
        # White LED
        cams.setLight(0, 0)
        time.sleep(0.5)
        cams.setLight(0, 1)
        time.sleep(0.5)
        cams.setLight(0, 0)
        time.sleep(0.5)
        
        # IR LED
        cams.setLight(1, 0)
        time.sleep(0.5)
        cams.setLight(1, 1)
        time.sleep(0.5)
        cams.setLight(1, 0)
        time.sleep(0.5)
        
        # OPEN/CLOSE TEST ON THE DOORS (Values->  0:Motors disable,  1:CLOSED    3: HALF OPEN     2: FULL OPEN)
        # Open/Close the door #0 (Value = 3 = Half open)
        doors1.setDoorState(0, 3)
        time.sleep(0.5)
        doors1.setDoorState(0, 1)
        time.sleep(0.5)

        # Open/Close the door #1 (Value = 3 = Half open)
        doors1.setDoorState(1, 3)
        time.sleep(0.5)
        doors1.setDoorState(1, 1)
        time.sleep(0.5)
        
        # FEEDER TEST
        # Set 1 Pellet to feed
        feeder1.setPellet(2)
        time.sleep(0.5)
        
        # Get the Pellet remaining to feed 
        pellet = feeder1.getPelletRemaining()
        print("Remaing pellet to feed: ", pellet)
        time.sleep(0.5)
        
        # WEIGHT SENSOR TEST [Array] (Firs arg in return is the weight, second is the time in min since the last measure)
        print("Measured weight on bottle [gr]: ", weight1.getWeight(0)[0])
        #(Weight sensor-> 0: Bottle 1: Mouse plate) [0: Weight 1: since time]
        time.sleep(0.5)
        
        # CAMERA TEST (Zones & Mouse position)
        # Zones test
        print("CAM0 ZONE 1 enable ? : ", cams.getZoneStates(0)[1])
        time.sleep(0.5)
        
        print("cams Zones enable: ", cams.getZoneStates(1))
        time.sleep(0.5)
        
        # mouse position test
        print("position Mouse 1: ", cams.getPosition(0))
        time.sleep(0.5)
        print("position Mouse 2: ", cams.getPosition(1))
        time.sleep(0.5)
        
        tryAgain = input("DO YOU WANT TO START THE TEST AGAIN ? y/n : ")
        if(tryAgain == "y"):
            pass
        else:
            break
            