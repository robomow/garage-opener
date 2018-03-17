from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import picamera
import numpy as np
import imutils
import cv2
import argparse
import numpy
import csv
import pusherclient
import os

import sys
sys.path.append('..')

# Add a logging handler so we can see the raw communication data
import logging
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-p", "--preview",
    help="options open/close")
ap.add_argument("-r", "--record",
    help="record duration in sec")
args = vars(ap.parse_args())


global pusher

def garageEventCallback(data):
    print("Received an event")
    gic.startRecording(60)


# We can't subscribe until we've connected, so we use a callback handler
# to subscribe when able
def connect_handler(data):
    channel = pusher.subscribe('robomow')
    channel.bind('garage-event', garageEventCallback)

pusher = pusherclient.Pusher("dafdd16435b9b98c88fd")
#pusher = pusherclient.Pusher("cc46da1883d0ec0a6197")
pusher.connection.bind('pusher:connection_established', connect_handler)
pusher.connect()

#
# Manages detecting of the Robomow as it approaches or leaves the garage
#    the opening / closing of the garage door
#    the notification of events surrounding the garage
class GarageInternalCamera():
    #PUSHER_APP_ID = '487778'
    PUSHER_APP_ID = '489803'
    #PUSHER_KEY = 'cc46da1883d0ec0a6197'
    PUSHER_KEY = 'cc46da1883d0ec0a6197'
    #PUSHER_SECRET = 'cff575fc033daf5660a2'
    PUSHER_SECRET = 'cff575fc033daf5660a'
    PUSHER_CLUSTER = 'mt1'
    PUSHER_GARAGE_CHANNEL = 'robomow'
    PUSHER_GARAGE_EVENT = 'garage-event'
   
    recordDuration = 60
    preview = False

    def __init__(self,preview):
       print("Initialize Garage Monitor")
       #self.subscriberList = []
       #self.stream = cv2.VideoCapture(videoSource)
       
    def addSubscriber(self, subscriber):
       self.subscriberList.append(subscriber)

    def notifyVehicleDetected(self,frame):
       for subscriber in self.subscriberList:
           subscriber.notifyVehicleDetected(self)

    def notifyVehicleEntryDetected(self,frame):
       for subscriber in self.subscriberList:
           subscriber.notifyVehicleEntryDetected(self)

    def startRecording(self,duration):
       with picamera.PiCamera() as camera:
          camera.resolution = (800, 600)
          camera.hflip = True
          camera.vflip = True
          camera.start_preview()
          camera.start_recording('/home/pi/data/videos/garage-opener-internal.h264')
          camera.wait_recording(duration)
          camera.stop_recording()
          time.sleep(1)
          os.system("scp /home/pi/data/vidos/garage-opener-internal.h264 pi@192.168.1.32:/home/pi/data/videos/garage-opener-internal.h264")


    def cleanup(self):
        self.stream.release()
        cv2.destroyAllWindows() 
        
    # monitors the video camera for activity
    def run(self):
        print("Garage Internal Camera is active...")
        while True:
            time.sleep(1) 
            print("Waiting for record event")

global gic
gic = GarageInternalCamera(True)

def main():

    preview = False
    if args.get("record"):
      duration = args["record"]
      gic.recordDuration = duration
      print("Recording for duration "+duration)
      gic.startRecording(int(duration))
    else:
      if args.get("preview",True):
         gic.preview = True
      gic.run()

if __name__ == '__main__':
    main()
