from interface import implements, Interface
import GarageMonitorSubscriber
from GarageMonitor import GarageMonitor
import argparse

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_UP)

servoMotor = GPIO.PWM(17,50)
servoMotor.start(7.5)

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

    def openGarageDoor(self):
       print("Opening Garage Door")
       servoMotor.ChangeDutyCycle(6.0)
       time.sleep(1)
       print("6.0")
       servoMotor.ChangeDutyCycle(4.5)
       print("4.5")
       time.sleep(1)
       servoMotor.ChangeDutyCycle(3.5)
       print("3.5")
       time.sleep(1)
       servoMotor.ChangeDutyCycle(2.5)
       print("2.5")
       time.sleep(1)
       #servoMotor.ChangeDutyCycle(2.5)
       #print("2.5")
       time.sleep(2)
       servoMotor.ChangeDutyCycle(12.5)
       print("12.5")
       time.sleep(2)
     
    def closeGarageDoor(self):
       print("Closing Garage Door")
       servoMotor.ChangeDutyCycle(12.5)
       time.sleep(4)
       servoMotor.ChangeDutyCycle(6.0)
       time.sleep(3)

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

