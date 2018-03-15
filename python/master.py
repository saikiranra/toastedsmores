"""
Master file of  what is going on

Assumes 200 degrees of range, starting 0 all the way to the left
"""

import time
import serial
import json
import defaultdict

BASE_RANGE = 200
E = None
R = None

class env():
    def __init__(self):
        #400(x) by 225(y) 
        self.raw = {}
        self.objLookup = defaultdict(list)
        self.scanResolution = 20 #degrees

    def addFrame(self, angle, jsonFrame):
        self.raw[angle] = jsonFrame
        objects = jsonFrame["bottles"]
        for objFrame in objects:
            self.objLookup[objFrame["name"]] = (angle , objFrame)

    def frameToCenterDistance(self , frame):
        """
        400 size, middle is 200
        """
        middle = 200
        frameXMiddle = frame["x"] + (frame["width"]/2)
        return abs(middle - frameXMiddle)

    def findItem(self, item):
        """
        Find the closest item to center
        """
        out = None
        for frame in self.objLookup[item]:
            if out == None:
                out = frame
            elif self.frameToCenterDistance(frame[1]) < self.frameToCenterDistance(out[1]):
                out = frame

    def getItemAngle(self , item):
        return self.findItem[item][0]
            
class robot():
    def __init__(self):
        self.serial = serial.Serial('COM6', 9600)

    def writeCommand(self, command):
        self.serial.write((command + " ").encode())

    def baseAngle(self, angle):
        """
        Tells arduino to go to angle
        """
        message = "BASE{:03d}".format(angle)
        self.writeCommand(message)

    def pour(self):
        """
        """
        pass

    def upright(self):
        """
        """
        pass


    def scanPosition(self):
        """
        Tells arduino to go to scan config
        """
        pass

    def stop(self):
        self.writeCommand("STOP")

    def close(self):
        self.serial.close()

def getJSONFrame():
    fname = "bottle.txt"
    return json.load(open(fname))

def scan():
    gotoScanPosition()
    E = env()
    R = robot()
    for i in range(int(BASE_RANGE/E.scanResolution) + 1):
        degrees = i * E.scanResolution
        R.baseAngle(degrees) #send robot arm to base angle
        time.sleep(2)
        jsonFrame = getJSONFrame() #get JSON frame from camera
        E.addFrame(degrees , jsonFrame)

def goToItem(item):
    angle = E.getItemAngle(item)
    R.baseAngle(angle)
    time.sleep(1)
    R.stop()


    

        
