"""
Master file of  what is going on

Assumes 200 degrees of range, starting 0 all the way to the left
"""

import time
import serial

BASE_RANGE = 200
E = None
R = None

class env():
    def __init__(self):
        self.raw = {}
        self.scanResolution = 20 #degrees

    def addFrame(self, angle, jsonFrame):
        self.raw[angle] = jsonFrame

    def findItme(self, item):
        pass

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

def scan():
    gotoScanPosition()
    E = env()
    R = robot()
    for i in range(int(BASE_RANGE/E.scanResolution) + 1):
        degrees = i * E.scanResolution
        R.baseAngle(degrees) #send robot arm to base angle
        time.sleep(2)
        jsonFrame = None #get JSON frame from camera
        E.addFrame(degrees , jsonFrame)



        
