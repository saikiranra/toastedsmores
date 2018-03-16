import time
import serial
import json
from collections import defaultdict


class environment():
    def __init__(self):
        #400(x) by 225(y) 
        self.raw = {}
        self.objLookup = defaultdict(list)
        self.scanResolution = 10 #degrees

    def getDataPacket(self):
        out = {"water":1}
        for obj in self.objLookup.keys():
            out[obj] = {}
            out[obj]["angle"] = self.getItemAngle(obj)

        return json.dumps(out)

    def reset(self):
        self.raw = {}
        self.objLookup = defaultdict(list)

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
        print("FindingItem")
        print(item)
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
