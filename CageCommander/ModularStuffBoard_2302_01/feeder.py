# coding: utf-8

#   feeder.py
#   Demo app for use the Feeder python library
#   History date:
#    - 08.07.2023 Adding getTotalFeed, initTotalFeed, getPelletSensorState

import re
import time

class feeder():
    WRITE = 0
    READ = 1

    STATUS_REG           = 0x05        
    GPIOCONFIG_REG       = 0x06
    FEEDCOUNT_REG        = 0x07
    FEEDREMAIN_REG       = 0x08
    RESERVED_REG         = 0x09
    RESERVED2_REG        = 0x0A
    RGBLEDCONFIG_REG     = 0x0B
    FEEDCOMMAND_REG      = 0x0C
    SERVO_STOP_LOW_REG   = 0x0D
    SERVO_STOP_HIGH_REG  = 0x0E
    SERVO_CW_LOW_REG     = 0x0F
    SERVO_CW_HIGH_REG    = 0x10
    SERVO_CCW_LOW_REG    = 0x11
    SERVO_CCW_HIGH_REG   = 0x12    

    readRegs_command = [READ, 0x51, 0x00, 36]
    writeReg_command = [WRITE, 0x51, 0x06, 0x05]   

    def __init__(self, serialHandler, I2Cadr):
        self.i2cAdr = I2Cadr
        self.serial = serialHandler

        print("Init Feeder with I2C address [%s] " % hex(self.i2cAdr))
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

    def setPellet(self, count):         
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        self.writeReg_command[2] = self.FEEDCOMMAND_REG
        self.writeReg_command[3] = (count << 4) + 0x01
        self.serial.write(self.writeReg_command)

    def getPelletRemaining(self):
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        
        pcount = (datas[self.FEEDREMAIN_REG]&0x07)
        return(pcount)
    
    def getTotalFeed(self):
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        
        totalFeed = (datas[self.FEEDCOUNT_REG])
        return(totalFeed)
    
    def initTotalFeed(self, count):         
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        self.writeReg_command[2] = self.FEEDCOUNT_REG
        self.writeReg_command[3] = count
        self.serial.write(self.writeReg_command)

    def getPelletSensorState(self):
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        
        IRstate = (datas[self.STATUS_REG] & 0x01)
        return(IRstate)