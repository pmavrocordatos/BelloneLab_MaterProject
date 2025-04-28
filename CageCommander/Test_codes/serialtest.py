#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 14:59:13 2023

@author: sfxindamix
"""

import serial

try:
    # self.ser = serial.Serial(comPort, 115200)  # open serial port

    ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.1)  # open serial port
    # ser = serial.Serial(self.comPort, self.baudRate, timeout=0.1)  # open serial port
    # ser.set_buffer_size(rx_size = 12800, tx_size = 12800)
    serialComStatus = 1
    print("Serial opened on ")
    # ser.write(gateway_verbose_mute);

except:
    print("[ERROR] IMPOSSIBLE TO OPEN")
    serialComStatus = -1