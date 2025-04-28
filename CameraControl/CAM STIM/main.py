# Mouse Tracking & Zones detection
#
# This program make the tracking of a black thing and send the occupation state of
# defined zones via a json message.
#
# Version 1.1 / 10.05.2023 RTh

import sensor, image, time, math, json
from pyb import UART
from pyb import Pin
from pyb import RTC

## Send the complete message with zones detection update
#CAREFULL THE CODE ALWAYS HAS TO START WHEN DAY LIGHTS ARE ON
sendFullMsg = 1

switch_sw1 = Pin('P6', Pin.IN, Pin.PULL_UP)
led_D3 = Pin('P8', Pin.OUT_PP, Pin.PULL_NONE)
led_D4 = Pin('P9', Pin.OUT_PP, Pin.PULL_NONE)
led_D1 = Pin('P2', Pin.OUT_PP, Pin.PULL_NONE)
led_D2 = Pin('P3', Pin.OUT_PP, Pin.PULL_NONE)
white_led = Pin('P7', Pin.IN, Pin.PULL_UP)

threshold_index = 2
res_factor = 2


uart = UART(1, 115200, timeout_char=150)                         # init with given baudrate
uart.init(115200, bits=8, parity=None, stop=1, timeout_char=150, read_buf_len=256) # init with given parameters

JobSequency = 0;


mySlaveCamData=''
# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green/blue things. You may wish to tune them...

thresholds = [ (15, 50, 0, 30, -65, -20),   # Blue tape
              (15, 45, 30, 60, 10, 50),     # Red tape# change with IR mouse
              (40, 55, 6, 25, -43, -23),       # Fake black mouse (day): (40, 55, 6, 25, -43, -23), fake mouse (day): (2, 14, -19, 2, 1, 11)
              (40, 50, 5, 25, -45, -20)]       # real mouse (night): (), real mouse (night):(5, 13, -9, 3, -19, 3)

pin_state = abs(white_led.value()-1)
previous_state = abs(pin_state-1)           # On définit le premier état de led mme "nuit" pour que le sensor passe en mode "jour" (et inversément si la nuit)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 500)
sensor.set_auto_gain(True) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking

## 90 DEGREES ROTATION -> https://docs.openmv.io/library/omv.sensor.html
sensor.set_vflip(False)
sensor.set_hmirror(False)
#sensor.set_transpose(True)

clock = time.clock()

BlackMouse = [-1,-1]
msgID =0
timer100ms=0
CamDesc = "MainRoom"
CamNumber = 0
binMsg = [0x23, 1,2,3,4,5,6,7,8,0x23]
camVersion = 1
## Send serial report flag
sendSerialreport = False
sendSlaveDataReport =False

# Main area
X1 = int(56/res_factor)
Y1 = int(104/res_factor)
X2 = int(580/res_factor)
Y2 = int(370/res_factor)

# Feeder distribution zone
#FEEDER_X1 = int(132/res_factor)
#FEEDER_Y1 = int(286/res_factor)
#FEEDER_X2 = int(226/res_factor)
#FEEDER_Y2 = int(366/res_factor)
#isInFeederZone = 0;
#isInFeederZone_last = 0;

# Weight plate zone
#WEIGHT_X1 = int(426/res_factor)
#WEIGHT_Y1 = int(200/res_factor)
#WEIGHT_X2 = int(500/res_factor)
#WEIGHT_Y2 = int(280/res_factor)
isInWeightZone = 0;
isInWeightZone_last = 0;

# Door left zone
#DOOR_LEFT_X1 = int(60/res_factor)
#DOOR_LEFT_Y1 = int(150/res_factor)
#DOOR_LEFT_X2 = int(132/res_factor)
#DOOR_LEFT_Y2 = int(286/res_factor)

DOOR_LEFT_X1 = int(500/res_factor)
DOOR_LEFT_X2 = int(572/res_factor)

DOOR_LEFT_Y1 = int(190/res_factor)
DOOR_LEFT_Y2 = int(326/res_factor)

isInLeftDoorZone = 0;
isInLeftDoorZone_last = 0;

## Door right zone
#DOOR_RIGHT_X1 = int(330/res_factor)
#DOOR_RIGHT_Y1 = int(20/res_factor)
#DOOR_RIGHT_X2 = int(450/res_factor)
#DOOR_RIGHT_Y2 = int(100/res_factor)
#isInRightDoorZone = 0;
#isInRightDoorZone_last = 0;

led_D1.value(1)
led_D2.value(1)
led_D3.value(1)
led_D4.value(1)

time.sleep_ms(1500)

if(switch_sw1.value() == True):
    led_D3.value(1)
    CamDesc = "MainRoom"
    CamNumber = 0
else:
    led_D4.value(0)
    CamDesc = "StimRoom"
    CamNumber = 1

led_D1.value(0)
led_D2.value(0)
led_D3.value(0)
led_D4.value(0)

time.sleep_ms(1000)

rtc = RTC()
rtc.datetime((2023, 8, 18, 5, 12, 33, 00, 0))

while(True):


    jsonEventData = ''
    img = sensor.snapshot()

    MouseDetected = False
    sendSerialreport = False



    #DRAW THE SEARCH ZONE
    img.draw_rectangle(X1, Y1, X2-X1, Y2-Y1, (255, 255, 255), 1, False)

    #DRAW THE FEEDER DISTRIBUTION ZONE
    #img.draw_rectangle(FEEDER_X1,FEEDER_Y1, FEEDER_X2-FEEDER_X1, FEEDER_Y2-FEEDER_Y1, (255, 255, 255), 1, False)

    ##DRAW THE WEIGHT DISTRIBUTION ZONE
    #img.draw_rectangle(WEIGHT_X1,WEIGHT_Y1, WEIGHT_X2-WEIGHT_X1, WEIGHT_Y2-WEIGHT_Y1, (255, 255, 255), 1, False)

    if (pin_state == 1):# Si la pin est HIGH (si le jour)
           if previous_state == 0:
               contrast_state = 1.5
               threshold_index = 2
               previous_state = pin_state


    else: # (si la nuit)
        if previous_state == 1:
            contrast_state = 1
            threshold_index = 3
            previous_state = pin_state

    img.gamma_corr(gamma = 1.0, contrast = contrast_state, brightness = 0.0)

    #DRAW THE LEFT DOOR ZONE
    img.draw_rectangle(DOOR_LEFT_X1,DOOR_LEFT_Y1, DOOR_LEFT_X2-DOOR_LEFT_X1, DOOR_LEFT_Y2-DOOR_LEFT_Y1, (255, 255, 255), 1, False)

    ##DRAW THE RIGHT DOOR ZONE
    #img.draw_rectangle(DOOR_RIGHT_X1,DOOR_RIGHT_Y1, DOOR_RIGHT_X2-DOOR_RIGHT_X1, DOOR_RIGHT_Y2-DOOR_RIGHT_Y1, (255, 255, 255), 1, False)

    for blob in img.find_blobs([thresholds[threshold_index]], pixels_threshold=200, area_threshold=200, merge=True):

        #BLACK BLOB
        if(blob.code() == 1):
            XBLOB = blob.cx()
            YBLOB = blob.cy()

            #CHECK IF MOUSE IS DETECTED IN SEARCH ZONE
            if(XBLOB>X1 and XBLOB < X2 and YBLOB>Y1 and YBLOB < Y2):
                MouseDetected = True
                BlackMouse[0] = XBLOB
                BlackMouse[1] = YBLOB
                # These values depend on the blob not being circular - otherwise they will be shaky.
                if blob.elongation() > 0.5:
                    img.draw_edges(blob.min_corners(), color=(255,0,0))
                    img.draw_line(blob.major_axis_line(), color=(0,255,0))
                    img.draw_line(blob.minor_axis_line(), color=(0,0,255))

                    # These values are stable all the time.
                    img.draw_rectangle(blob.rect())
                    img.draw_cross(blob.cx(), blob.cy())

                # Note - the blob rotation is unique to 0-180 only.
                img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)

                # FEEDER ZONE DETECTION
                #isInFeederZone_last = isInFeederZone
                #if(BlackMouse[0]>FEEDER_X1 and BlackMouse[0] < FEEDER_X2 and BlackMouse[1]>FEEDER_Y1 and BlackMouse[1] < FEEDER_Y2):
                #    isInFeederZone = 1
                #    led_D3.value(1)
                #else:
                #    isInFeederZone = 0
                #    led_D3.value(0)

                ## WEIGHT ZONE DETECTION
                isInWeightZone_last = isInWeightZone
                #if(BlackMouse[0]>WEIGHT_X1 and BlackMouse[0] < WEIGHT_X2 and BlackMouse[1]>WEIGHT_Y1 and BlackMouse[1] < WEIGHT_Y2):
                    #isInWeightZone = 1
                    #led_D2.value(1)
                #else:
                isInWeightZone = 0
                led_D2.value(0)

                # LEFT DOOR ZONE DETECTION
                isInLeftDoorZone_last = isInLeftDoorZone
                if(BlackMouse[0]>DOOR_LEFT_X1 and BlackMouse[0] < DOOR_LEFT_X2 and BlackMouse[1]>DOOR_LEFT_Y1 and BlackMouse[1] < DOOR_LEFT_Y2):
                    isInLeftDoorZone = 1
                    led_D4.value(1)
                else:
                    isInLeftDoorZone = 0
                    led_D4.value(0)

                ## RIGHT DOOR ZONE DETECTION
                #isInRightDoorZone_last = isInRightDoorZone
                #if(BlackMouse[0]>DOOR_RIGHT_X1 and BlackMouse[0] < DOOR_RIGHT_X2 and BlackMouse[1]>DOOR_RIGHT_Y1 and BlackMouse[1] < DOOR_RIGHT_Y2):
                    #isInRightDoorZone = 1
                    #led_D1.value(1)
                #else:
                    #isInRightDoorZone = 0
                    #led_D1.value(0)

                # ADD JSON DATA IF DECTECTION ZONE CHANGE
#                if(isInFeederZone_last != isInFeederZone):
#                    sendSerialreport = True

                if(isInWeightZone_last != isInWeightZone):
                    sendSerialreport = True

                if(isInLeftDoorZone_last != isInLeftDoorZone):
                    sendSerialreport = True

                #if(isInRightDoorZone_last != isInRightDoorZone):
                    #sendSerialreport = True
                break
            else:
                BlackMouse[0] = -1
                BlackMouse[1] = -1
                isInWeightZone_last = isInWeightZone
                isInWeightZone = 1
                led_D2.value(1)
                if(isInWeightZone_last != isInWeightZone):
                    sendSerialreport = True


    if(uart.any()):
        while(uart.any()):
            mySlaveCamData = uart.readline()
            #defaultMsg2 = "MOUSE SLAVE--> X: " + str(mySlaveCamData[6] + (mySlaveCamData[5]>>4)) + "  Y: " + str(mySlaveCamData[8] + (mySlaveCamData[7]>>4)) + "  Zones: " + str(mySlaveCamData[4])
            #print(defaultMsg2)   # write the data
            sendSlaveDataReport = True

    if(timer100ms>=25):
        if (MouseDetected == True):
            sendSerialreport=True
            timer100ms=0

    if(sendSerialreport == True):
        msgID+=1
        #activeZone = isInFeederZone + (isInWeightZone*2) + (isInLeftDoorZone*4) + (isInRightDoorZone*8)
        activeZone = (isInLeftDoorZone*4)

        binMsg[1] = CamNumber
        binMsg[2] = camVersion
        binMsg[3] = MouseDetected
        binMsg[4] = activeZone
        binMsg[5] = (BlackMouse[0] & 0xFF00)>>4
        binMsg[6] = (BlackMouse[0] & 0xFF)
        binMsg[7] = (BlackMouse[1] & 0xFF00)>>4
        binMsg[8] = (BlackMouse[1] & 0xFF)

        #defaultMsg = "X: " + str(BlackMouse[0]) + "  Y: " + str(BlackMouse[1]) + "  Zones: " + str(isInLeftDoorZone) + str(isInRightDoorZone) + str(isInFeederZone) + str(isInWeightZone)
        defaultMsg = "X: " + str(BlackMouse[0]) + "  Y: " + str(BlackMouse[1]) + "  Zones: " + str(isInLeftDoorZone) #+ str(isInFeederZone) + str(isInWeightZone)
        print('USB CAM PORT '+ defaultMsg + '  Mouse detected: ' + str(MouseDetected))
        byte_array = bytearray(binMsg)
        uart.write(byte_array)   # write the data
        #print(byte_array)   # write the data
        sendSerialreport=False

        if(sendSlaveDataReport == True):
            time.sleep_ms(10)


    if(sendSlaveDataReport == True):
        uart.write(mySlaveCamData)   # write the data
        #print(mySlaveCamData)   # write the data
        mySlaveCamData=""
        sendSlaveDataReport=False

    timer100ms+=1
    time.sleep_ms(1)
