## 2032_lifeBoxDemo.py
## Python demo application for work with Arduino board 2032
## Version 1.0 29.06.2022 / Rth

import drv_2032_lifeBox
import threading
# import msvcrt
import time

threads = []
event = threading.Event()
# Ouvre le driver decommunication avec la boite de comportement (Arduino)
## --> myBox = a2204_nosePoke.myThread(Nom quelconque, COM port attibué par windows (CF hardware manager windows, COM port & LPT))
myBox = drv_2032_lifeBox.myThread("Behaviour BOX A", "/dev/ttyUSB0", event)

# Démarre le driver de communication avec le Arduino de la boite de comportement
myBox.start()

# Add threads to thread list
threads.append(myBox)


# Etat initial de la boite de comportement au démarage souhaité

print("Running user application...  (press any key to exit)")


# Programme fonctionne en boucle avec attente de 100mS tant que la communication avec arduino est active
while (myBox.serialComStatus > 0):
    # Détéction de touche clavier pour quitter le programme
    # if msvcrt.kbhit():
    #     print ("you pressed",msvcrt.getch(),"so now i will quit")
    #     myBox.close_serial()
    ## ----------------------  CODE APPLICATION UTILISATEUR -----------------------------    
## DISPLAY THE BOX STATUS
    print("\n" + myBox.getDataTimeStamp())

    #First methode to get the camera zones state
    #[0]LEFT DOOR, [1]RIGHT DOOR, [2]FEEDER, [3]SCALE
    ActiveCameraZones = myBox.getCamZones(0)

    LeftDoorZone = ActiveCameraZones[0]
    RightDoorZone = ActiveCameraZones[1]
    FeederZone = ActiveCameraZones[2]
    ScaleZone = ActiveCameraZones[3]

    # ROOM 1 STATUS
    print("Mouse position: X:" + str(myBox.getMouseData(0).posX) + "| Y: " + str(myBox.getMouseData(0).posY))
    print("Ldoor: " + str(LeftDoorZone) + "| Rdoor: " + str(RightDoorZone) + "| FeederZone: " + str(FeederZone)+ "| ScaleZone: " + str(ScaleZone))
    print("Mouse weight: " + str(myBox.getMouseData(0).weight) + " (since " + str(myBox.getMouseData(0).oldTime) + "min)"  + " | Bottle weight: " + str(myBox.getBottleData(0).weight) + "g (state: " + str(myBox.getBottleData(0).state) +")\n")
    print("Pellet sensor: "+ str(myBox.getPelletSensor(0)))
    
    # ROOM 2 STATUS
    print("Mouse 2 position: X:" + str(myBox.getMouseData(1).posX) + "| Y: " + str(myBox.getMouseData(1).posY))
    print("Ldoor: " + str(myBox.getCamZones(1)[0]) + "| Rdoor: " + str(myBox.getCamZones(1)[1]) + "\n")
    
##  SAMPLE OF ACTION TO DO...
    ## Make an action only if a change was occured in the zones
    ## This for prevent to send periodical command to the box
    if(myBox.camZonesHasChanged(0) != None):
        #Check if the left door zone in the mainroom is active  ---- getCamZones(main=0/stim=1)[zoneNb]
        if(myBox.getCamZones(0)[0]):
            #Send a command to open(1) the door left(0)
            #Note: The command will be send by the driver only if the actual state
            #of the door differ from the state to apply
            myBox.setDoorState(0,1)
        else:
            myBox.setDoorState(0,0)
        
        #Right door zone in the stimroom        
        if(myBox.getCamZones(1)[0]):
            myBox.setDoorState(1,1)
        else:
            myBox.setDoorState(1,0)
        
        #Feed a pellet when the mouse is in the Feederzone AND no pellet is present
        #on the pellet sensor
        if(myBox.getCamZones(0)[2] == 1 and myBox.getPelletSensor(0) == 0):
            # feed a pellet in the mainroom
            myBox.setPellet(0)
        
   ## ----------------------  FIN DU CODE APPLICATION UTILISATEUR -----------------------------
    # Attente de 100mS dans la boucle  
    time.sleep(0.1)

    
# Wait for all threads to complete
for t in threads:
    t.join()
    
print ("Exiting application, bye bye !")
