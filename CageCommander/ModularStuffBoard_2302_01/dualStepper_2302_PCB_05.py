# coding: utf-8

# 
#
#

import re
import time

class dualStepper():
    WRITE = 0
    READ = 1
        
    # Registers adress declaration
    RGBLEDCONFIG_REG             = 0x0B
    ASTEP_COMMAND_REG            = 0x0C
    BSTEP_COMMAND_REG            = 0x0D
    ASTEP_DEFAULT_STEP_LOW       = 0x0E
    ASTEP_DEFAULT_STEP_HIGH      = 0x0F

    BSTEP_DEFAULT_STEP_LOW       = 0x10
    BSTEP_DEFAULT_STEP_HIGH      = 0x11

    ASTEP_MIN_SETPOINT_LOW       = 0x12
    ASTEP_MIN_SETPOINT_HIGH      = 0x13

    ASTEP_MAX_SETPOINT_LOW       = 0x14
    ASTEP_MAX_SETPOINT_HIGH      = 0x15

    ASTEP_RAMP_REG               = 0x16
    BSTEP_RAMP_REG               = 0x17

    ASTEP_CONFIG_REG             = 0x18
    BSTEP_CONFIG_REG             = 0x19

    ASTEP_SPEED_CONTROL          = 0x1A
    BSTEP_SPEED_CONTROL          = 0x1B
  
  # Default values for data serial command read or write
    # [R/W, ModuleI2CAdr, StartRegisterToWrite, ValueToWrite, OtherValueToWriteOnStartRegisterToWrite + 1, OtherValueToWriteOnStartRegisterToWrite + 2, ...]
    readRegs_command = [READ, 0x58, 0x00, 36]
    writeReg_command = [WRITE, 0x58, 0x06, 0x05]   

    def __init__(self, serialHandler, I2Cadr):
        self.i2cAdr = I2Cadr
        self.serial = serialHandler

        print("Init STEPPERS with I2C address [%s] " % hex(self.i2cAdr))
        self.readRegs_command[1] = self.i2cAdr
        self.writeReg_command[1] = self.i2cAdr
        
        self.clearSerialBuff()
          
        #self.writeReg_command[2] = BSTEP_CONFIG_REG
        #self.writeReg_command[3] = 0x81
        #self.serial.write(self.writeReg_command)          

    def getSerialResponse(self):
        seq = []
        dataResponse = []
        dataStart = -1
        dataStop = -1
       
        tout = 0
        # Waiting for serial data..
        while self.serial.inWaiting() == 0:
            pass
        
        while (dataStart == -1 or dataStop == -1):
            for c in self.serial.read():
                seq.append(chr(c)) #convert from ANSII
                joined_seq = ''.join(str(v) for v in seq) #Make a string from array
                dataStart = joined_seq.find("\r\n#")
                dataStop = joined_seq.find("#\r\n")
               
        seq = []
        #print(joined_seq)
        dataStrResponse = joined_seq[dataStart+3 : dataStop]

        b = bytearray()
        b.extend(map(ord, dataStrResponse))

        #print(hex(dataResponse.encode()))
        #print(b)
        return b

    def clearSerialBuff(self):
        while self.serial.read():
            pass

# Set the doors state (OPEN or CLOSE)
    def setDoorState(self, doorNb, state):
        if(doorNb==0):
            STEP_COMMAND_REG = self.ASTEP_COMMAND_REG
            
        if(doorNb==1):
            STEP_COMMAND_REG = self.BSTEP_COMMAND_REG     

        if(state==0):
            regValue = 0x82
        else:
            regValue = 0x83
            
        self.clearSerialBuff()
          
        self.writeReg_command[2] = STEP_COMMAND_REG
        self.writeReg_command[3] = regValue
        print(self.writeReg_command)
        self.serial.write(self.writeReg_command)

# Set the opening speed of the door
# doorNb 0/1 and speed 0..100 [%]
    def setDoorSpeed(self, doorNb, speed):
        if(doorNb==0):
            STEP_SPEED_CONTROL = self.ASTEP_SPEED_CONTROL
            
        if(doorNb==1):
            STEP_SPEED_CONTROL = self.BSTEP_SPEED_CONTROL
        
        if(speed > 100):
            speed = 100
        if(speed < 10):
            speed = 10
            
        self.clearSerialBuff()
          
        self.writeReg_command[2] = STEP_SPEED_CONTROL
        self.writeReg_command[3] = speed
        print(self.writeReg_command)
        self.serial.write(self.writeReg_command)            