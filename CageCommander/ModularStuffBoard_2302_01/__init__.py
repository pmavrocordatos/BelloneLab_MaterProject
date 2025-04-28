import serial
from .camTracking import *
from .feeder import *
from .weightMeasurement import *
from .pwmServo import *
from .dualStepper_2302_PCB_05 import *

class netBox():
    def __new__(self, comPort, baudRate):
        gateway_verbose_mute =[0x00, 0x50, 0x04, 0x00]
        self.serialComStatus = -1
        self.baudRate = baudRate
        self.comPort = comPort
        ser = -1
        try:
            # self.ser = serial.Serial(comPort, 115200)  # open serial port

            # ser = serial.Serial(comPort, baudRate, timeout=0.1)  # open serial port
            ser = serial.Serial(self.comPort, self.baudRate, timeout=0.1)  # open serial port
            # ser.set_buffer_size(rx_size = 12800, tx_size = 12800)
            self.serialComStatus = 1
            print("Serial opened on " + comPort)
            print("-> Set Gateway verbose to OFF !")
            ser.write(gateway_verbose_mute);
            return ser
        except:
            print("[ERROR] IMPOSSIBLE TO OPEN \"" + comPort + "\"")
            self.serialComStatus = -1
 

            