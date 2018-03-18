
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import atexit

import subprocess

from interface import implements, Interface
import GarageMonitorSubscriber
from GarageMonitor import GarageMonitor
import argparse
import cv2
import numpy as np
import os
import threading


import RPi.GPIO as GPIO
import time

from time import sleep
import pusher

#
# Initialize limit switch
#
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_UP)

#
# Initialize servo motor that closes the door
#
garageCloser = GPIO.PWM(17,50)

#
# Initialize stepper motor that opens the garage
#
# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT()

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

garageOpener = mh.getStepper(200, 2)  # 200 steps/rev, motor port #1
garageOpener.setSpeed(100)             # 30 RPM

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-d", "--door",
    help="options open/close")
ap.add_argument("-t", "--testswitch",
    help="test limit switch")
ap.add_argument("-c", "--copy",
    help="combine video recordings")
ap.add_argument("-u", "--upload",
    help="upload vidos")
ap.add_argument("-r", "--record",
    help="starts video recording for seconds specified")
args = vars(ap.parse_args())

#
# The GarageOpener class manages all the operations that can be performed on 
# the Robomow garage.  This includes opening/closing the garage
#
# It subscribes to the GarageMonitor notifications and performs the
# appropriate action when the notification event occurs
#
# The GarageOpener also used the pusher.com technology to broadcast 
# the event to interested parties.  (i.e. a web or mobile app) after
# an action is performed
#
class GarageOpener:
    #PUSHER_APP_ID = '487778'
    PUSHER_APP_ID = '489803'
    #PUSHER_KEY = 'cc46da1883d0ec0a6197' 
    PUSHER_KEY = 'dafdd16435b9b98c88fd' 
    #PUSHER_SECRET = 'cff575fc033daf5660a2'
    PUSHER_SECRET = 'eef1bc8f97c689aea0a4'
    #PUSHER_CLUSTER = 'us2'
    PUSHER_CLUSTER = 'mt1'
    PUSHER_GARAGE_CHANNEL = 'robomow' 
    PUSHER_GARAGE_EVENT = 'garage-event'

    doorOpen = False
    # Limit Switch variables
    pushedDown = 0
    releasedUp = 1
    prev_input = 0
    pusherClient = None
    stepperThread = threading.Thread()

    def __init__(self):
        print("Initializing the GarageOpener")
        GarageOpener.pusherClient = pusher.Pusher(
           app_id=GarageOpener.PUSHER_APP_ID,
           key=GarageOpener.PUSHER_KEY,
           secret=GarageOpener.PUSHER_SECRET,
           cluster=GarageOpener.PUSHER_CLUSTER,
            ssl=True
        )


    def notifyVehicleDetected(self, image):
        a=1
        #print("Vehicle Detected...time to open the door")

    def notifyVehicleEntryDetected(self, image):
        print("Vehicle Entry Detected...time to open the door")
        if (GarageOpener.doorOpen == False):
            self.openGarageDoor()

    #
    # scp the file over
    #
    def copyInternalCameraClip(self):
        p = subprocess.Popen(["scp", "pi@192.168.1.31:/home/pi/data/videos/garage-opener-internal.h264","/home/pi/data/videos"])
        sts = os.waitpid(p.pid, 0)
        return True

    def uploadVideos(self):
        print("uploadVideos")
        #self.copyInternalCameraClip();
        #p = subprocess.Popen(["youtube-upload", "--title=\"Robomow Garage Entry\"","--description=\"vidoe of robomow entering the garage\"","--client-secrets=/home/pi/youtube/client_secrets.json","/home/pi/data/videos/garage-opener-external.avi"])
        #sts = os.waitpid(p.pid, 0)
        #p = subprocess.Popen(["youtube-upload", "--title=\"Robomow Garage Entry\"","--description=\"vidoe of robomow entering the garage\"","--client-secrets=/home/pi/youtube/client_secrets.json","/home/pi/data/videos/garage-opener-internal.h264"])
        #sts = os.waitpid(p.pid, 0)
      

       
    def closeGarageDoor(self):
       print("Closing Garage Door")
       GarageOpener.doorOpen = False
       garageCloser.start(7.5)
       garageCloser.ChangeDutyCycle(2.5)
       time.sleep(2.0)
       garageCloser.ChangeDutyCycle(7.5)
       print("7.5")

       GarageOpener.pusherClient.trigger(GarageOpener.PUSHER_GARAGE_CHANNEL, GarageOpener.PUSHER_GARAGE_EVENT, {'message': 'Robomow Garage has been successfully closed'})
       time.sleep(5)
       self.uploadVideos();
     
    def stepperOpenGarageDoor(self):
       print("Stepper Motor Opening Garage Door")
       GarageOpener.doorOpen = True
       cnt=0
       while (cnt<4):
           cnt = cnt + 1
           garageOpener.step(100, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
       cnt=0
       while (cnt<3):
           cnt = cnt + 1
           garageOpener.step(100, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)

       GarageOpener.pusherClient.trigger(GarageOpener.PUSHER_GARAGE_CHANNEL, GarageOpener.PUSHER_GARAGE_EVENT, {'message': 'Robomow Garage has been successfully opened'})
       time.sleep(3)

    def openGarageDoor(self):
       print("Opening Garage Door")
       if not self.stepperThread.isAlive():
           self.stepperThread = threading.Thread(target=self.stepperOpenGarageDoor)
           self.stepperThread.start()

    def checkLimitSwitch(self):
       #print("Testing Limit Switch")

       try:
          #while True:
             input = GPIO.input(4)
             #print("Input="+str(input))
             if ((not GarageOpener.pushedDown) and input):
                 print("Button Pressed Down rotating 90 degrees")
                 print("Input="+str(input))

                 print("Robomow has successfully parked in garage.")
                 print("   Lets wait 60 seconds and close the door")
                 time.sleep(5)

                 time.sleep(1)
                 self.closeGarageDoor()
                 GarageOpener.pushedDown = 1
                 GarageOpener.releasedUp = 1
             elif ((GarageOpener.releasedUp) and not input):
                 print("Button Released rotating -90 degrees")
                 print("Input="+str(input))

                 print("Robomow is leaving garage.")
                 print("   Lets wait 60 seconds and close the door")
                 time.sleep(30)

                 self.closeGarageDoor()
                 GarageOpener.releasedUp = 0
                 GarageOpener.pushedDown = 0

       except KeyboardInterrupt:
          GPIO.cleanup()


    def __del__(self):
       print("Releasing GarageOpener") 
       GPIO.cleanup()

    def run(self,garageMonitor):
       print("Running GarageOpener main loop")
       try:
           while True:
              if (garageMonitor.run() == False):
                 break
              self.checkLimitSwitch()
       except KeyboardInterrupt:
           pass
       finally:
           print("Cleaning up")
           GPIO.cleanup()
           garageMonitor.cleanup() 


def main():

    if not args.get("video", False):
       camera = 0
    else:
       camera = args["video"]

    garageOpener = GarageOpener()
    if args.get("upload"):
       garageMonitor = GarageMonitor(camera,None)
       garageOpener.uploadVideos()
    else:
       garageMonitor = GarageMonitor(camera,'/home/pi/data/videos/garage-opener-external.avi')

    garageMonitor.addSubscriber(garageOpener)
    
    if args.get("door",True):
       op = args["door"]
       if args["door"] == 'open':
          garageOpener.openGarageDoor()
       if args["door"] == 'close':
          garageOpener.closeGarageDoor()
    elif args.get("testswitch",True):
       garageOpener.checkLimitSwitch()
    elif args.get("record"):
       garageMonitor.startRecording(args["record"])
    else:
       garageOpener.run(garageMonitor)


if __name__ == '__main__':
    main()

