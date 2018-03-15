"""
Master file of  what is going on

Assumes 200 degrees of range, starting 0 all the way to the left
"""

import time
import serial
import json
from collections import defaultdict

BASE_RANGE = 60
E = None
R = None

class env():
    def __init__(self):
        #400(x) by 225(y) 
        self.raw = {}
        self.objLookup = defaultdict(list)
        self.scanResolution = 10 #degrees

    def addFrame(self, angle, jsonFrame):
        self.raw[angle] = jsonFrame
        objects = jsonFrame["bottles"]
        for objFrame in objects:
            self.objLookup[objFrame["name"]].append((angle , objFrame))

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
        return out

    def getItemAngle(self , item):
        bestFrame = self.findItem(item)
        centerY = bestFrame[1]["y"] + (bestFrame[1]["width"]/2)
        deltaCenter = (225 / 2) - centerY
        mult = 0
        if deltaCenter > 0: 
            if deltaCenter  < 30:
                pass
            elif deltaCenter < 60: 
                mult = 1
            else:
                mult = 2
        else:
            if deltaCenter > 30:
                pass
            if deltaCenter > 60:
                mult = 1
            else:
                mult = 2       

        return self.findItem(item)[0] + (mult * 2)
            
class robot():
    def __init__(self):
        self.serial = serial.Serial('/dev/tty.usbmodem14421', 9600)

    def writeCommand(self, command):
        self.serial.write((command + " ").encode())

    def baseAngle(self, angle):
        """
        Tells arduino to go to angle
        """
        message = "BASE{:03d}".format(angle)
        self.writeCommand(message)

    def outPosition(self):
        self.writeCommand("FEXT")

    def stablePosition(self):
        self.writeCommand("EXTS")

    def stowePosition(self):
        self.writeCommand("BEXT")

    def pour(self):
        """
        """
        self.writeCommand("POUR")
        time.sleep(1)
        self.writeCommand("SPOUR")

    def upright(self):
        """
        """
        pass


    def scanPosition(self):
        """
        Tells arduino to go to scan config
        """
        self.outPosition()
        time.sleep(1)
        self.stowePosition()

    def stop(self):
        self.writeCommand("STOP")

    def close(self):
        self.serial.close()

def getJSONFrame():
    fname = "bottle.txt"
    return json.load(open(fname))

def scan():
    global E, R
    E = env()
    R = robot()
    time.sleep(2)
    R.stowePosition()
    time.sleep(1)
    for i in range(int(BASE_RANGE/E.scanResolution) + 1):
        degrees = i * E.scanResolution
        R.baseAngle(degrees) #send robot arm to base angle
        time.sleep(3)
        R.stop()
        time.sleep(2)
        for i in range(100):
            jsonFrame = getJSONFrame() #get JSON frame from camera
            E.addFrame(degrees , jsonFrame)
            time.sleep(0.02)

def goToItem(item):
    angle = E.getItemAngle(item)
    print(angle)
    R.baseAngle(angle)
    time.sleep(1)
    R.stop()


scan()
print("ITEMS")
print(E.objLookup.keys())
goToItem("milk")
time.sleep(0.5)
R.outPosition()
time.sleep(2)
R.stablePosition()
time.sleep(1)
goToItem("cup")
R.outPosition()
time.sleep(2)
R.pour()
time.sleep(0.5)
R.stowePosition()


    

        
