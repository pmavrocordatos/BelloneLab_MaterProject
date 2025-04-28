# coding: utf-8
import re
import time

class weightMeasurement():
    WRITE = 0
    READ = 1
        
    GPIOCONFIG_REG              = 0x06
    ASENSMEAS_LOW_REG           = 0x07
    ASENSMEAS_HIGH_REG          = 0x08
    BSENSMEAS_LOW_REG           = 0x09
    BSENSMEAS_HIGH_REG          = 0x0A
    RGBLEDCONFIG_REG            = 0x0B
    ASCALESCOMMAND_REG          = 0x0C
    BSCALESCOMMAND_REG          = 0x0D
    ASENS_LASTMEAS_TIME_LOW     = 0x0E
    ASENS_LASTMEAS_TIME_HIGH    = 0x0F
    BSENS_LASTMEAS_TIME_LOW     = 0x10
    BSENS_LASTMEAS_TIME_HIGH    = 0x11
    MEASUREMENT_INTERVAL_LOW    = 0x12
    MEASUREMENT_INTERVAL_HIGH   = 0x13
    ASENS_CALIB_FACTOR_LOW      = 0x14
    ASENS_CALIB_FACTOR_HIGH     = 0x15
    BSENS_CALIB_FACTOR_LOW      = 0x16
    BSENS_CALIB_FACTOR_HIGH     = 0x17  

    readRegs_command = [READ, 0x52, 0x00, 36]
    writeReg_command = [WRITE, 0x52, 0x06, 0x05]   

    def __init__(self, serialHandler, I2Cadr):
        self.i2cAdr = I2Cadr
        self.serial = serialHandler

        print("Init Weight measurement with I2C address [%s] " % hex(self.i2cAdr))
        self.readRegs_command[1] = self.i2cAdr
        self.writeReg_command[1] = self.i2cAdr

    def getSerialResponse(self):
        seq = []
        dataResponse = []
        dataStart = -1
        dataStop = -1

        # Waiting for serial data..
        tout = 0
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
       
    def getWeight(self, sensorNb):   
        if(sensorNb==0):
            SENSMEAS_LOW = self.ASENSMEAS_LOW_REG
            SENSMEAS_HIGH = self.ASENSMEAS_HIGH_REG
            LASTMEAS_TIME_LOW = self.ASENS_LASTMEAS_TIME_LOW
            LASTMEAS_TIME_HIGH = self.ASENS_LASTMEAS_TIME_HIGH            
            
        if(sensorNb==1):
            SENSMEAS_LOW = self.BSENSMEAS_LOW_REG
            SENSMEAS_HIGH = self.BSENSMEAS_HIGH_REG
            LASTMEAS_TIME_LOW = self.BSENS_LASTMEAS_TIME_LOW
            LASTMEAS_TIME_HIGH = self.BSENS_LASTMEAS_TIME_HIGH    
            
        self.clearSerialBuff()
        self.serial.write(self.readRegs_command)
        datas = self.getSerialResponse()
        
        weight = ((datas[SENSMEAS_HIGH]<<8) + datas[SENSMEAS_LOW])
        time = ((datas[LASTMEAS_TIME_HIGH]<<8) + datas[LASTMEAS_TIME_LOW])        
        return(weight, time)
        
    def startWeightMeasure(self, sensorNb):   
        if(sensorNb==0):
            SCALESCOMMAND_REG = self.ASCALESCOMMAND_REG
            
            
        if(sensorNb==1):
            SCALESCOMMAND_REG = self.BSCALESCOMMAND_REG
            
        self.writeReg_command[1] = self.i2cAdr
        self.writeReg_command[2] = SCALESCOMMAND_REG
        self.writeReg_command[3] = 0x09
        
        self.clearSerialBuff()
        self.serial.write(self.writeReg_command)
        #datas = self.getSerialResponse()
        
    def startTare(self, sensorNb):   
        if(sensorNb==0):
            SCALESCOMMAND_REG = self.ASCALESCOMMAND_REG
            
        if(sensorNb==1):
            SCALESCOMMAND_REG = self.BSCALESCOMMAND_REG
            
        self.writeReg_command[1] = self.i2cAdr
        self.writeReg_command[2] = SCALESCOMMAND_REG
        self.writeReg_command[3] = 0x03
        
        self.clearSerialBuff()
        self.serial.write(self.writeReg_command)
        #datas = self.getSerialResponse()        

    def disableSensor(self, sensorNb):   
        if(sensorNb==0):
            SCALESCOMMAND_REG = self.ASCALESCOMMAND_REG
            
        if(sensorNb==1):
            SCALESCOMMAND_REG = self.BSCALESCOMMAND_REG
            
        self.writeReg_command[1] = self.i2cAdr
        self.writeReg_command[2] = SCALESCOMMAND_REG
        self.writeReg_command[3] = 0x04
        
        self.clearSerialBuff()
        self.serial.write(self.writeReg_command)
        #datas = self.getSerialResponse()