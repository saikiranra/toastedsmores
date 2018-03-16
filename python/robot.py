import time
import serial
import json
from collections import defaultdict


class robot():
    def __init__(self , com):
        self.com = com
        self.extPos = "stable"
        self.clawPos = "open"
        self.wristPos = "stable"
        self.controlLoopEnabled = False
        self.angle = 0
        self.enabled = False

    def connect(self):
        try:
            self.serial = serial.Serial(self.com, 9600)
            self.enabled = True
            print("Connected to Arduino!")
        except:
            pass

    def getDataPacket(self):
        out = {}
        out["ext"] = self.extPos
        out["claw"] = self.clawPos
        out["wrist"] = self.wristPos
        out["controlLoop"] = self.controlLoopEnabled
        out["base"] = self.angle
        out["enabled"] = self.enabled

        return json.dumps(out)


    def writeCommand(self, command):
        if not self.enabled:
            self.connect()
        if not self.enabled:
            raise Exception("Couldn't connect!")
        self.serial.write((command + " ").encode())

    def baseAngle(self, angle):
        """
        Tells arduino to go to angle
        """
        message = "BASE{:03d}".format(angle)
        self.writeCommand(message)
        self.angle = angle
        self.controlLoopEnabled = True

    def outPosition(self):
        self.writeCommand("FEXT")
        self.extPos = "forward"

    def stablePosition(self):
        self.writeCommand("EXTS")
        self.extPos = "stable"

    def stowePosition(self):
        self.writeCommand("BEXT")
        self.extPos = "back"

    def wristDown(self):
        """
        """
        self.writeCommand("POUR")
        self.wristPos = "down"

    def wristUp(self):
        self.writeCommand("SPOUR")
        self.wristPos = "stable"

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
        self.controlLoopEnabled = False

    def close(self):
        self.serial.close()
