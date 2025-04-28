# coding: utf-8
import re
import time

class pwmServo():
    WRITE = 0
    READ = 1
        
    AMOTOR_ACTUAL_VALUE_LOW     = 0x07
    AMOTOR_ACTUAL_VALUE_HIGH    = 0x08
    BMOTOR_ACTUAL_VALUE_LOW     = 0x09
    BMOTOR_ACTUAL_VALUE_HIGH    = 0x0A
    RGBLEDCONFIG_REG            = 0x0B
    AMOT_COMMAND_REG            = 0x0C
    BMOT_COMMAND_REG            = 0x0D
    AMOT_USER_SETPOINT_LOW      = 0x0E
    AMOT_USER_SETPOINT_HIGH     = 0x0F

    BMOT_USER_SETPOINT_LOW      = 0x10
    BMOT_USER_SETPOINT_HIGH     = 0x11

    AMOT_MIN_SETPOINT_LOW       = 0x12
    AMOT_MIN_SETPOINT_HIGH      = 0x13

    AMOT_MAX_SETPOINT_LOW       = 0x14
    AMOT_MAX_SETPOINT_HIGH      = 0x15

    BMOT_MIN_SETPOINT_LOW       = 0x16
    BMOT_MIN_SETPOINT_HIGH      = 0x17

    BMOT_MAX_SETPOINT_LOW       = 0x18
    BMOT_MAX_SETPOINT_HIGH      = 0x19

    AMOTOR_SPEED_CONTROL        = 0x1A
    BMOTOR_SPEED_CONTROL        = 0x1B

    readRegs_command = [READ, 0x53, 0x00, 36]
    writeReg_command = [WRITE, 0x53, 0x06, 0x05]   

    def __init__(self, serialHandler, I2Cadr):
        self.i2cAdr = I2Cadr
        self.serial = serialHandler

        print("Init PWM/SERVO with I2C address [%s] " % hex(self.i2cAdr))
        self.readRegs_command[1] = self.i2cAdr
        self.writeReg_command[1] = self.i2cAdr

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
       
    def setDoorState(self, doorNb, state):
        if(doorNb==0):
            MOT_COMMAND_REG = self.AMOT_COMMAND_REG
            
        if(doorNb==1):
            MOT_COMMAND_REG = self.BMOT_COMMAND_REG     
            
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        regValue = (datas[MOT_COMMAND_REG] & 0xFC)
        regValue = regValue | state     
          
        self.writeReg_command[2] = MOT_COMMAND_REG
        self.writeReg_command[3] = regValue
        self.serial.write(self.writeReg_command)