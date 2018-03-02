from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import picamera
import numpy as np
import imutils
import cv2
import argparse

# open a pointer to the video stream and start the FPS timer

#object_cascade = cv2.CascadeClassifier('data/model-1/cascade.xml')
vehicle_cascade = cv2.CascadeClassifier('data/rs622/model-1/cascade.xml')

# define standard colors for circle around the object
colors = {'red':(0,0,255), 'green':(0,255,0), 'blue':(255,0,0), 'yellow':(0, 255, 217), 'orange':(0,140,255)}

#
# Manages detecting of the Robomow as it approaches or leaves the garage
#    the opening / closing of the garage door
#    the notification of events surrounding the garage
class GarageMonitor():
    def __init__(self,videoSource):
       print("Initialize Garage Monitor")
       self.subscriberList = []
       self.stream = cv2.VideoCapture(videoSource)
       
    def addSubscriber(self, subscriber):
       self.subscriberList.append(subscriber)

    def notifyVehicleDetected(self,frame):
       for subscriber in self.subscriberList:
           subscriber.notifyVehicleDetected(self)

    def drawDriveway(self,frame):
       cv2.line(frame,(0,0),(511,511),(255,0,0),5)
       cv2.line(frame,(100,100),(511,511),(255,0,0),5)


    def startRecording(self,duration):
       with picamera.PiCamera() as camera:
          camera.resolution = (800, 600)
          camera.start_recording('garage-opener.h264')
          while True:
             camera.wait_recording(1)
             cv2.waitKey(1)
             key = cv2.waitKey(1) & 0xFF
             # if the 'q' key is pressed, stop the loop
             if key == ord("q"):
                camera.stop_recording()
                break


    def detectObject(self, frame):
       #resize the frame and convert it to grayscale (while still
       # retaining 3 channels)
       frame = imutils.resize(frame, width=450)
       frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
       frame = np.dstack([frame, frame, frame])
           
       # display a piece of text to the frame (so we can benchmark
       # fairly against the fast method)
       cv2.putText(frame, "Slow Method", (10, 30),
       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

       self.drawDriveway(frame)
       watches = vehicle_cascade.detectMultiScale(gray,minNeighbors=10,minSize=(125,125),maxSize=(150,150))
       i = 1
       for (x,y,w,h) in watches:
          if i == 1:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0),2)
            posStr = "i=" + str(i)
            cv2.putText(frame,posStr, (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['blue'],2)
            self.notifyVehicleDetected(frame)
          i=i+1
       cv2.imshow("Frame", frame)
    
    # monitors the video camera for activity
    def run(self):
     try:
       print("Monitoring video camera for activity")
       while True:
           (grabbed, frame) = self.stream.read()

           # if the frame was not grabbed, then we have reached the end
           # of the stream
           if not grabbed:
                print("Video Camera could NOT be accessed!!  Exiting")
                break
           self.detectObject(frame)

           # show the frame and update the FPS counter
           cv2.waitKey(1)
           key = cv2.waitKey(1) & 0xFF
           # if the 'q' key is pressed, stop the loop
           if key == ord("q"):
              break

     except KeyboardInterrupt:
      pass
     finally:
      print("Cleaning up")
      self.stream.release()
      cv2.destroyAllWindows() 

 
    def inspectFrame(self):
       print("Inspect frame...")


