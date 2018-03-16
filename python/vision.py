# USAGE
# python3 vision.py
# will use mobile-net-ssd pretrained machine learning model for image classification

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import json
import time
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--record", type=str, action='store', default="", 
	help="record flag followed by output filename, must end with .mp4")
args = vars(ap.parse_args())

bottles = []
#vs = VideoStream(src=1)
vs = cv2.VideoCapture(1)
record = False 

if ".mp4" in args["record"]: 
    record = True

video_writer = []

class Bottle:
    bottle = dict()

    def __init__(self):
        self.writeTime = time.time()*1000
        self.writeInterval = 10 #seconds

    def update(self, x, y, w, h):
        self.bottle["x"] = np.asscalar(x)
        self.bottle["y"] = np.asscalar(y)
        self.bottle["width"] = np.asscalar(w)
        self.bottle["height"] = np.asscalar(h)

    def writeToFile(self):
        curTime = time.time()
        if(curTime*1000 - self.writeTime > self.writeInterval): 
            # write to file
            fh = open("bottle.txt", "w")
            data = self.toJSON()
            fh.writelines(data)
            fh.close()

            #reset time
            writeTime = time.time()*1000 

    def findCode(self, frame):
        #read from dict
        x = self.bottle["x"]
        y = self.bottle["y"]
        w = self.bottle["width"]
        h = self.bottle["height"]

        frame = Image.fromarray(frame)
        mw, mh = frame.size

        #make bounding box twice as big
        x1 = (x-0.5*w) if (x-0.5*w) > 0 else 0
        y1 = (y-0.5*h) if (y-0.5*h) > 0 else 0
        
        x2 = (x+1.5*w) if (x+1.5*w) < mw else mw
        y2 = (y+1.5*h) if (y+1.5*h) < mh else mh

        #crop image
        '''print("MAX W: " + str(mw) + ", H: " + str(mh)) 
        print("(" + str(x1) + "," + str(y1) + ")") 
        print("(" + str(x2) + "," + str(y2) + ")") '''
        image = frame.crop((x1, y1, x2, y2))

        codes = decode(image)
        if(len(codes) < 1):
            self.bottle["name"] = "empty"
            return 

        for c in codes: #ideally only one code will be found
            data = c.data
            #convert byte string to regular string
            self.bottle["name"] = str(data,'utf-8')
            break
    
    def toJSON(self):
        return json.dumps(self.bottle)

    def __str__(self):
        return self.toJSON()

def readBarCode(frame):
    image = Image.fromarray(frame)
    codes = decode(image)
    if(len(codes) > 0):
        print('QR codes: %s' % codes)

def classify(detections, w, h, CLASSES, COLORS, frame, record=False):
    global bottles, video_writer
    minConfidence = 0.1

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # extract the index of the class label from the
        # `detections`, then compute the (x, y)-coordinates of
        # the bounding box for the object
        idx = int(detections[0, 0, i, 1])
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        # only ouput bottle classifications
        if(CLASSES[idx] == "bottle" and confidence > minConfidence):
            bottle = Bottle()

            #create classification object
            bottle.update(startX, startY, abs(endX-startY), abs(endY-startY))
            #try to read the associated bar code
            bottle.findCode(frame)
            #test print
            #print(bottle)

            #append bottle to global bottles
            bottles.append(bottle)

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > minConfidence:
            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx],
                confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    if(record):
        video_writer.write(frame)

writeTime = time.time()
writeInterval = 1

def bottlesToFile():
    global bottles, writeTime, writeInterval
    l = []

    for bottle in bottles:
        #print(bottle)
        l.append(bottle.bottle)

    bottleDict = {"bottles":l}
    bottleJSON = json.dumps(bottleDict)

    #get current time
    curTime = time.time()

    # only write to file once every second
    if(curTime - writeTime > writeInterval):
        fh = open("bottle.txt", "w")
        fh.writelines(bottleJSON)
        fh.close()

        #reset last written time
        writeTime = time.time()

    print(bottleJSON)

def main():
    global vs, bottles, record, video_writer

	# initialize the list of class labels MobileNet SSD was trained to
	# detect, then generate a set of bounding box colors for each class
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    # load our serialized model from disk
    print("[INFO] loading model...")
    prototxt = "model/MobileNetSSD_deploy.prototxt.txt"
    model = "model/MobileNetSSD_deploy.caffemodel"
    net = cv2.dnn.readNetFromCaffe(prototxt, model)

	# initialize the video stream, allow the cammera sensor to warmup,
	# and initialize the FPS counter
    print("[INFO] starting video stream...")
    #vs.start()
    time.sleep(3.0)
    fps = FPS().start()
    width = 400
    height = 400

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if(record):
        video_writer = cv2.VideoWriter("output.mp4", fourcc, 20, (400, 225))

    # confidence in image classification
    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        val, frame = vs.read()
        frame = imutils.resize(frame, width=width)
        frame = cv2.flip(frame, -1)
        #qreadBarCode(frame)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (width, height)),
            0.007843, (width, height), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        #if(record):
        #    video_writer.write(frame)

        classify(detections, w, h, CLASSES, COLORS, frame, record)

        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            video_writer.release()
            break

        # update the FPS counter
        fps.update()

        #write bottle to file
        bottlesToFile()

        #end the bottles after frame
        #bottles[:] = []
        bottles.clear()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    video_writer.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            #video_writer.release()
            cv2.destroyAllWindows()
            sys.exit(0)
        except SystemExit:
            os._exit(0)