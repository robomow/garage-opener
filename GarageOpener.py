
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import atexit

from interface import implements, Interface
import GarageMonitorSubscriber
from GarageMonitor import GarageMonitor
import argparse

import RPi.GPIO as GPIO
import time

from time import sleep

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
ap.add_argument("-r", "--record",
    help="starts video recording for seconds specified")
args = vars(ap.parse_args())


class GarageOpener:
    doorOpen = False
    # Limit Switch variables
    pushedDown = 0
    releasedUp = 1
    prev_input = 0

    def notifyVehicleDetected(self, image):
        a=1
        #print("Vehicle Detected...time to open the door")

    def notifyVehicleEntryDetected(self, image):
        print("Vehicle Entry Detected...time to open the door")
        if (GarageOpener.doorOpen == False):
            self.openGarageDoor()

    def closeGarageDoor(self):
       print("Closing Garage Door")
       GarageOpener.doorOpen = False
       garageCloser.start(7.5)
       garageCloser.ChangeDutyCycle(2.5)
       time.sleep(2.0)
       garageCloser.ChangeDutyCycle(7.5)
       print("7.5")
       time.sleep(2)

    def closeGarageDoor2(self):
       print("Opening Garage Door")
       garageCloser.start(7.5)
       garageCloser.ChangeDutyCycle(6.5)
       time.sleep(0.2)
       print("6.5")
       garageCloser.ChangeDutyCycle(6.0)
       time.sleep(0.2)
       print("6.0")
       garageCloser.ChangeDutyCycle(5.5)
       time.sleep(0.2)
       print("5.5")
       garageCloser.ChangeDutyCycle(5.0)
       time.sleep(0.2)
       print("5.0")
       garageCloser.ChangeDutyCycle(4.5)
       print("4.5")
       time.sleep(0.2)
       garageCloser.ChangeDutyCycle(4.0)
       print("4.0")
       time.sleep(0.2)
       garageCloser.ChangeDutyCycle(3.5)
       print("3.5")
       time.sleep(0.2)
       garageCloser.ChangeDutyCycle(3.0)
       print("3.0")
       time.sleep(0.2)
       garageCloser.ChangeDutyCycle(2.5)
       print("2.5")
       time.sleep(0.2)
       garageCloser.ChangeDutyCycle(2.0)
       print("2.0")
       time.sleep(0.2)
       garageCloser.ChangeDutyCycle(0.0)
       #print("2.5")
       time.sleep(2)
       garageCloser.ChangeDutyCycle(7.5)
       print("12.5")
       time.sleep(2)
     
    def openGarageDoor(self):
       print("Opening Garage Door")
       GarageOpener.doorOpen = True
       cnt=0
       while (cnt<4):
           cnt = cnt + 1
           garageOpener.step(100, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
       cnt=0
       while (cnt<3):
           cnt = cnt + 1
           garageOpener.step(100, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)


    def checkLimitSwitch(self):
       print("Testing Limit Switch")

       try:
          #while True:
             input = GPIO.input(4)
             print("Input="+str(input))
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
    garageMonitor = GarageMonitor(camera)
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
       garageOpener.closeGarageDoor()
       garageOpener.run(garageMonitor)


if __name__ == '__main__':
    main()

