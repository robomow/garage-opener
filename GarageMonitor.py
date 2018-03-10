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
    driveWayEntryCnt = 0
    #driveWayEntry = [[11,341],[13,342],[16,343], [11,281], [16,275]
    driveWayContours = [numpy.array([[0,250],[250,200],[400,300],[550,500],[550,600],[70,600],[70,470],[0,500],[0,250]], dtype=numpy.int32)]
    driveWayExitContours = [numpy.array([[770,450],[740,250],[700,200],[670,200],[640,250],[600,450],[770,450]], dtype=numpy.int32)]

    def __init__(self,videoSource):
       print("Initialize Garage Monitor")
       self.subscriberList = []
       self.stream = cv2.VideoCapture(videoSource)
       
    def addSubscriber(self, subscriber):
       self.subscriberList.append(subscriber)

    def notifyVehicleDetected(self,frame):
       for subscriber in self.subscriberList:
           subscriber.notifyVehicleDetected(self)

    def notifyVehicleEntryDetected(self,frame):
       for subscriber in self.subscriberList:
           subscriber.notifyVehicleEntryDetected(self)

    def drawDrivewayExit(self,frame):
       posStr = "Time to"
       cv2.putText(frame,posStr, (710,410), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['blue'],2)
       posStr = "Close Garage Door"
       cv2.putText(frame,posStr, (700,480), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['blue'],2)
       for cnt in GarageMonitor.driveWayExitContours:
          cv2.drawContours(frame,[cnt],0,(255,255,255),2)

    def drawDriveway(self,frame):
       cv2.line(frame,(00,500),(70,470),(0,255,0),2)
       cv2.line(frame,(70,470),(70,600),(0,255,0),2)

       # top upper line
       cv2.line(frame,(0,250),(250,200),(0,255,0),2)
       
       # top connect line
       cv2.line(frame,(250,200),(400,300),(0,255,0),2)

       # right outer line
       cv2.line(frame,(400,300),(550,500),(0,255,0),2)

       # right outer line
       cv2.line(frame,(550,500),(550,600),(0,255,0),2)

       # Message
       posStr = "Time to"
       cv2.putText(frame,posStr, (200,325), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['blue'],2)
       posStr = "Open Garage Door"
       cv2.putText(frame,posStr, (150,350), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['blue'],2)
       for cnt in GarageMonitor.driveWayContours:
          cv2.drawContours(frame,[cnt],0,(255,255,255),2)


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


    def checkDrivewayEntry(self,x,y):
       GarageMonitor.driveWayEntryCnt = GarageMonitor.driveWayEntryCnt + 1
       if (GarageMonitor.driveWayEntryCnt > 30):
           GarageMonitor.driveWayEntryCnt = 0
           return True
       else:
           return False

    def detectObject(self, frame):
       #resize the frame and convert it to grayscale (while still
       # retaining 3 channels)
       frame = imutils.resize(frame, width=800)
       frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
       frame = np.dstack([frame, frame, frame])
           
       # display a piece of text to the frame (so we can benchmark
       # fairly against the fast method)
       #cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

       watches = vehicle_cascade.detectMultiScale(gray,minNeighbors=10,minSize=(125,125),maxSize=(150,150))
       i = 1
       for (x,y,w,h) in watches:
          if i == 1:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            #posStr = "i=" + str(i)
            posStr = "  found [" + str(x)+","+str(y)+","+str(w)+","+str(h)+"]"
            cv2.putText(frame,posStr, (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,colors['blue'],2)
            print(posStr)
             
            self.drawDrivewayExit(frame)
            for cnt in GarageMonitor.driveWayContours:
                 dist = cv2.pointPolygonTest(cnt,(x,y),False)
                 if (dist >= 0 ):
                     print(" *** In the driveway ")
                     self.drawDriveway(frame)
                     coordinates = (x,y)
                     if self.checkDrivewayEntry(x,y):
                          self.notifyVehicleEntryDetected(frame)
                     #with open("driveway-entry.csv","a") as de:
                     #   writer = csv.writer(de)
                     #   writer.writerow(coordinates)
            self.notifyVehicleDetected(frame)
          i=i+1
       cv2.imshow("Frame", frame)
    
    def cleanup(self):
        self.stream.release()
        cv2.destroyAllWindows() 
        
    # monitors the video camera for activity
    def run(self):
           #print("Monitoring video camera for activity")
           (grabbed, frame) = self.stream.read()

           # if the frame was not grabbed, then we have reached the end
           # of the stream
           if not grabbed:
                print("Video Camera could NOT be accessed!!  Exiting")
                return False
           self.detectObject(frame)

           # show the frame and update the FPS counter
           cv2.waitKey(1)
           key = cv2.waitKey(1) & 0xFF
           # if the 'q' key is pressed, stop the loop
           if key == ord("q"):
              return False
 
           return True
    def inspectFrame(self):
       print("Inspect frame...")


