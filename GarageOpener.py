
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import atexit

from interface import implements, Interface
import GarageMonitorSubscriber
from GarageMonitor import GarageMonitor
import argparse

import RPi.GPIO as GPIO
import time

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

    def notifyVehicleDetected(self, image):
        print("Vehicle Detected...time to open the door")

    def closeGarageDoor(self):
       print("Opening Garage Door")
       garageCloser.start(7.5)
       garageCloser.ChangeDutyCycle(6.0)
       time.sleep(0.5)
       print("6.0")
       garageCloser.ChangeDutyCycle(4.5)
       print("4.5")
       time.sleep(0.5)
       garageCloser.ChangeDutyCycle(3.5)
       print("3.5")
       time.sleep(0.5)
       garageCloser.ChangeDutyCycle(2.5)
       print("2.5")
       time.sleep(0.5)
       garageCloser.ChangeDutyCycle(2.5)
       #print("2.5")
       time.sleep(2)
       garageCloser.ChangeDutyCycle(12.5)
       print("12.5")
       time.sleep(2)
     
    def openGarageDoor(self):
       print("Closing Garage Door")
       cnt=0
       while (cnt<4):
           cnt = cnt + 1
           garageOpener.step(100, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
       cnt=0
       while (cnt<3):
           cnt = cnt + 1
           garageOpener.step(100, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)


    def testLimitSwitch(self):
       print("Testing Limit Switch")

       try:
          pushedDown = 0
          releasedUp = 1
          prev_input = 0
          while True:
             input = GPIO.input(4)
             print("Input="+str(input))
             if ((not pushedDown) and input):
                 print("Button Pressed Down rotating 90 degrees")
                 print("Input="+str(input))
                 time.sleep(1)
                 self.openGarageDoor()
                 pushedDown = 1
                 releasedUp = 1
             elif ((releasedUp) and not input):
                 print("Button Released rotating -90 degrees")
                 print("Input="+str(input))
                 self.closeGarageDoor()
                 time.sleep(1)
                 releasedUp = 0
                 pushedDown = 0

             #p.ChangeDutyCycle(7.5) #0
             #time.sleep(1)
             #p.ChangeDutyCycle(14.5) #-90
             #time.sleep(1)
             #p.ChangeDutyCycle(2.5) #90
             #time.sleep(1)
       except KeyboardInterrupt:
          GPIO.cleanup()


    def __del__(self):
       print("Releasing GarageOpener") 
       GPIO.cleanup()


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
       garageOpener.testLimitSwitch()
    elif args.get("record"):
       garageMonitor.startRecording(args["record"])
    else:
       garageMonitor.run()


if __name__ == '__main__':
    main()

