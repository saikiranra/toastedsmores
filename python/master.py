"""
Master file of  what is going on

Assumes 200 degrees of range, starting 0 all the way to the left
"""

import time
import serial
import json
from collections import defaultdict
import robot
import environment
import routines 

import http.server
import socketserver

rob = None
env = None
rout = None

class ToastedSmoresWebServer(http.server.BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type' , 'text/html')
        self.end_headers()

    def getBasePath(self):
        out = self.path
        out = out.strip("/")
        out = out.split("?")[0]
        return out

    def getData(self):
        global rob
        global env
        sc = self.path.split("?")[1]
        out = ""
        if sc == "robot":
            out = rob.getDataPacket()
        else:
            out = env.getDataPacket()
        self.wfile.write(bytes(out , 'UTF-8'))
        
    def getArgsDict(self):
        latter = self.path.split("?")[1]
        andSplit = latter.split("&")
        out = {}
        for item in andSplit:
            kvsplit = item.split("=")
            if len(kvsplit) == 1:
                out[kvsplit[0]] = None
            else:
                temp = kvsplit[1].split(",")
                if len(temp) > 1:
                    out[kvsplit[0]] = temp
                else:
                    out[kvsplit[0]] = kvsplit[1]
        return out

    def setCommand(self):
        global rob
        global env
        global rout

        argsDict = self.getArgsDict()
        if "sequence" in argsDict:
            #run drink maker
            rout.customRoutine(argsDict["order"] , argsDict["cup"])
        if "scan" in argsDict:
            rout.scan()
            

    def serveHTMLPage(self):
        out = "404 Error"
        if self.getBasePath() == "":
            fp = open("html/index.html" , "rb")
            out = fp.read()
            fp.close()
        else:
            try:
                fp = open("html" + self.path , "rb")
                out = fp.read()
                fp.close()
            except:
                print(self.path + " couldn't be opened!")
        self.wfile.write(out)

    def do_GET(self):
        self._set_headers()
        if self.getBasePath() == "data":
            #sendData
            self.getData()
            pass
        elif self.getBasePath() == "command":
            #runCommand
            self.setCommand()
            pass
        else:
            #serve pages
            self.serveHTMLPage()
        self.end_headers()
    

    def serve_forever(port):
        socketserver.TCPServer(('', port), ToastedSmoresWebServer).serve_forever()        




if __name__ == "__main__":
    global rob
    global env
    global rout
    rob = robot.robot("COM3")
    env = environment.environment()
    rout = routines.routines(rob , env)
    ToastedSmoresWebServer.serve_forever(8000)




    

        
