import time
import serial
import json
from collections import defaultdict
import robot
import environment


class routines():
    def __init__(self , rob , env):
        self.rob = rob
        self.env = env
        self.baseRange = 60
        self.hasScanned = False

    def getJSONFrame(self , fname = "bottle.txt"):
        return json.load(open(fname))

    def scan(self):
        self.hasScanned = True
        time.sleep(2)
        self.rob.stowePosition()
        time.sleep(1)
        for i in range(int(self.baseRange/self.env.scanResolution) + 1):
            degrees = i * self.env.scanResolution
            self.rob.baseAngle(degrees) #send robot arm to base angle
            time.sleep(3)
            self.rob.stop()
            time.sleep(2)
            for i in range(100):
                jsonFrame = self.getJSONFrame() #get JSON frame from camera
                self.env.addFrame(degrees , jsonFrame)
                time.sleep(0.02)

    def customRoutine(self , ingredients , output):
        if not self.hasScanned:
            self.scan()

        for item in ingredients:
            setDownAngle = self.goToItem(item)
            time.sleep(0.5)
            self.rob.outPosition()
            time.sleep(1)
            #self.rob.grab()
            self.rob.stablePosition()
            time.sleep(1)
            self.rob.goToItem(output)
            time.sleep(0.5)
            self.rob.outPosition()
            time.sleep(1)
            self.rob.wristDown()
            time.sleep(0.5)
            self.rob.wristUp()
            self.rob.stablePosition()
            time.sleep(1)
            self.goToItem(item)
            time.sleep(0.5)
            self.rob.outPosition()
            time.sleep(1)
            #self.rob.release()
            time.sleep(0.5)
            self.rob.stowePosition()
            time.sleep(1)
            

    def goToItem(self , item):
        angle = self.env.getItemAngle(item)
        self.rob.baseAngle(angle)
        time.sleep(1)
        self.rob.stop()
        return angle

    def grabAndGo(self, item):
        print("ITEMS")
        print(self.env.objLookup.keys())
        self.goToItem(item)
        time.sleep(0.5)
        self.rob.outPosition()
        time.sleep(2)
        self.rob.stablePosition()
        time.sleep(1)
        self.goToItem("cup")
        self.rob.outPosition()
        time.sleep(2)
        self.rob.pour()
        time.sleep(0.5)
        self.rob.stowePosition()
