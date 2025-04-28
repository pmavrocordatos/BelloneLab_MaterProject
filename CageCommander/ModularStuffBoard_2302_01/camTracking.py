# coding: utf-8
import re
import time

class camTracking():
    WRITE = 0
    READ = 1
        
    GPIOCONFIG_REG        = 0x06
    ACAM_FIRMWARE_VERSION = 0x07
    ACAM_STATUS_REG       = 0x08
    BCAM_FIRMWARE_VERSION = 0x09
    BCAM_STATUS_REG       = 0x0A
    RGBLEDCONFIG_REG      = 0x0B

    ACAM_ACTIVES_ZONES    = 0x0C
    ACAM_RESERVED         = 0x0D

    ACAM_BLOB_XPOS_LOW    = 0x0E
    ACAM_BLOB_XPOS_HIGH   = 0x0F

    ACAM_BLOB_YPOS_LOW    = 0x10
    ACAM_BLOB_YPOS_HIGH   = 0x11

    BCAM_ACTIVES_ZONES    = 0x12
    BCAM_RESERVED         = 0x13

    BCAM_BLOB_XPOS_LOW    = 0x14
    BCAM_BLOB_XPOS_HIGH   = 0x15

    BCAM_BLOB_YPOS_LOW    = 0x16
    BCAM_BLOB_YPOS_HIGH   = 0x17    

    readRegs_command = [READ, 0x56, 0x00, 36]
    writeReg_command = [WRITE, 0x56, 0x06, 0x05]   

    def __init__(self, serialHandler, I2Cadr):
        self.i2cAdr = I2Cadr
        self.serial = serialHandler

        print("Init Camera with I2C address [%s] " % hex(self.i2cAdr))
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


    def getPosition(self, camNb):
    
        if(camNb==0):
            CAM_POS_X_L = self.ACAM_BLOB_XPOS_LOW
            CAM_POS_X_H = self.ACAM_BLOB_XPOS_HIGH
            CAM_POS_Y_L = self.ACAM_BLOB_YPOS_LOW
            CAM_POS_Y_H = self.ACAM_BLOB_YPOS_HIGH
            
        if(camNb==1):
            CAM_POS_X_L = self.BCAM_BLOB_XPOS_LOW
            CAM_POS_X_H = self.BCAM_BLOB_XPOS_HIGH
            CAM_POS_Y_L = self.BCAM_BLOB_YPOS_LOW
            CAM_POS_Y_H = self.BCAM_BLOB_YPOS_HIGH            
            
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        xPos = ((datas[CAM_POS_X_H]<<8) + datas[CAM_POS_X_L])
        yPos = ((datas[CAM_POS_Y_H]<<8) + datas[CAM_POS_Y_L])
        return(xPos, yPos)

    def setLight(self, GPIO, state):
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        GpioCfgVal = self.getSerialResponse()[self.GPIOCONFIG_REG]
        if GPIO == 0:
            GpioCfgVal = GpioCfgVal & 0xFC
            GpioCfgVal += state
        if GPIO == 1:
                GpioCfgVal = GpioCfgVal & 0xCF
                GpioCfgVal += (state<<4)
                
        self.writeReg_command[2] = self.GPIOCONFIG_REG
        self.writeReg_command[3] = GpioCfgVal
        
        self.serial.write(self.writeReg_command)
        return(0)
        
    def setIRLight(self, GPIO, state):
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        GpioCfgVal = self.getSerialResponse()[self.GPIOCONFIG_REG]
        if GPIO == 0:
            GpioCfgVal = GpioCfgVal & 0xCF
            GpioCfgVal += state
        if GPIO == 1:
                GpioCfgVal = GpioCfgVal & 0xFC
                GpioCfgVal += (state<<4)
                
        self.writeReg_command[2] = self.GPIOCONFIG_REG
        self.writeReg_command[3] = GpioCfgVal
        
        self.serial.write(self.writeReg_command)
        return(0)         

    def getZoneStates(self, camSelect):
        if(camSelect == 0):
            CAM_ACTIVES_ZONES = self.ACAM_ACTIVES_ZONES
        else:
            CAM_ACTIVES_ZONES = self.BCAM_ACTIVES_ZONES
            
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        
        zoneStates = [bool((datas[CAM_ACTIVES_ZONES]&0x04)), bool((datas[CAM_ACTIVES_ZONES]&0x08)), bool((datas[CAM_ACTIVES_ZONES]&0x01)), bool((datas[CAM_ACTIVES_ZONES]&0x02))]
        return(zoneStates)