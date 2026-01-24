import math

import cv2 as cv
import numpy as np

class ColorDetector:
    def __init__(self):

        #self.yellow = 25
        self.yellow =25
        #self.green = 45
        self.green = 46
        self.blueS = 108
        #self.blueL = 94
        self.blueL = 96
        self.pink = 169
        self.purple = 130


    def DameValores (self):
        return self.yellow,self.green,self.blueS,self.blueL,self.pink,self.purple

    def TomaValores (self):
        self.yellow = self.yellowtmp
        self.green = self.greentmp
        self.blueS = self.blueStmp
        self.blueL = self.blueLtmp
        self.pink = self.pinktmp
        self.purple = self.purpletmp


    def MarkFrameForCalibration (self, frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        self.yellowtmp = hsv[200, 200][0]
        self.greentmp = hsv[200, 500][0]
        self.blueStmp = hsv[200, 800][0]
        self.blueLtmp = hsv[500, 200][0]
        self.pinktmp = hsv[500, 500][0]
        self.purpletmp = hsv[500, 800][0]

        cv.circle(frame, (200, 200), 100, (0, 255, 255), 3)
        cv.putText(img=frame, text=str(self.yellowtmp), org=(150, 200), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=2,
                   color=(255,255,255), thickness=1)

        cv.circle(frame, (500, 200), 100, (0, 255, 0), 3)
        cv.putText(img=frame, text=str(self.greentmp), org=(450, 200), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=2,
                   color=(255,255,255), thickness=1)

        cv.circle(frame, (800, 200), 100, (240, 106, 23), 3)
        cv.putText(img=frame, text=str(self.blueStmp), org=(750, 200), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=2,
                   color=(255,255,255), thickness=1)

        cv.circle(frame, (200, 500), 100, (250, 240, 30), 3)
        cv.putText(img=frame, text=str(self.blueLtmp), org=(150, 500), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=2,
                   color=(255,255,255), thickness=1)

        cv.circle(frame, (500, 500), 100, (139, 1, 240), 3)
        cv.putText(img=frame, text=str(self.pinktmp), org=(450, 500), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=2,
                   color=(255,255,255), thickness=1)

        cv.circle(frame, (800, 500), 100, (240, 29, 140), 3)
        cv.putText(img=frame, text=str(self.purpletmp), org=(750, 500), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=2,
                   color=(255,255,255), thickness=1)
        return frame

    def Cerca (self, ax,ay):

        dis = math.sqrt((ax-320)*(ax-320) + (ay-240)*(ay-240))
        print ('distancia ',ax, ay, dis)
        if dis > 10:
            return False
        else:
            return True

    def DetectColor(self, frame):



        # Convert BGR to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        #print (hsv[720 // 2, 480 // 2][0], hsv[720 // 2, 480 // 2][1], hsv[720 // 2, 480 // 2][2])

        marge = 5

        # define range of colors in HSV
        lowerYellow = np.array([self.yellow-marge, 100, 100])
        upperYellow = np.array([self.yellow+marge, 255, 255])

        lowerGreen = np.array([self.green-marge, 100, 50])
        upperGreen = np.array([self.green+marge, 255, 255])

        lowerBlueS = np.array([self.blueS-marge, 100, 50])
        upperBlueS = np.array([self.blueS+marge, 255, 255])

        lowerBlueL = np.array([self.blueL-marge, 100, 50])
        upperBlueL = np.array([self.blueL+marge, 255, 255])

        lowerPink= np.array([self.pink-marge, 100, 50])
        upperPink = np.array([self.pink+marge, 255, 255])

        lowerPurple = np.array([self.purple-marge, 100, 50])
        upperPurple = np.array([self.purple+marge, 255, 255])

        detectedColour = 'none'

        # ignore selected contour with area less that this
        minimumSize = 0

        areaBiggestContour = 0
        self.cX, self.cY = 0, 0

        # for each color:
        #   find contours of this color
        #   get the biggest contour
        #   check if the contour is within the target rectangle (if area = 'small')
        #   check if the contour has the minimun area
        #   keet this contour if it is the biggest by the moment

        mask = cv.inRange(hsv, lowerYellow, upperYellow)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=5)
        mask = cv.dilate(mask, kernel, iterations=5)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            cyellow = max(contours, key=cv.contourArea)
            M = cv.moments(cyellow)

            if cv.contourArea(cyellow) > areaBiggestContour:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
                contour = cyellow
                areaBiggestContour = cv.contourArea(cyellow)
                detectedColour = 'yellow'

        mask = cv.inRange(hsv, lowerGreen, upperGreen)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=5)
        mask = cv.dilate(mask, kernel, iterations=5)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            cGreen = max(contours, key=cv.contourArea)
            M = cv.moments(cGreen)

            if cv.contourArea(cGreen) > areaBiggestContour:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
                contour = cGreen
                areaBiggestContour = cv.contourArea(cGreen)
                detectedColour = 'green'

        mask = cv.inRange(hsv, lowerBlueS, upperBlueS)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=5)
        mask = cv.dilate(mask, kernel, iterations=5)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            cBlueS = max(contours, key=cv.contourArea)
            M = cv.moments(cBlueS)

            if cv.contourArea(cBlueS) > areaBiggestContour:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
                contour = cBlueS
                areaBiggestContour = cv.contourArea(cBlueS)
                detectedColour = 'blueS'

        mask = cv.inRange(hsv, lowerBlueL, upperBlueL)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=5)
        mask = cv.dilate(mask, kernel, iterations=5)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            cBlueL = max(contours, key=cv.contourArea)
            M = cv.moments(cBlueL)


            if cv.contourArea(cBlueL) > areaBiggestContour:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
                contour = cBlueL
                areaBiggestContour = cv.contourArea(cBlueL)
                detectedColour = 'blueL'

        mask = cv.inRange(hsv, lowerPink, upperPink)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=5)
        mask = cv.dilate(mask, kernel, iterations=5)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            cPink = max(contours, key=cv.contourArea)
            M = cv.moments(cPink)
            if cv.contourArea(cPink) > areaBiggestContour:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
                contour = cPink
                areaBiggestContour = cv.contourArea(cPink)
                detectedColour = 'pink'

        mask = cv.inRange(hsv, lowerPurple, upperPurple)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=5)
        mask = cv.dilate(mask, kernel, iterations=5)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            cPurple = max(contours, key=cv.contourArea)
            M = cv.moments(cPurple)
            if cv.contourArea(cPurple) > areaBiggestContour:
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])
                contour = cPurple
                areaBiggestContour = cv.contourArea(cPurple)
                detectedColour = 'purple'

        if detectedColour != 'none' and areaBiggestContour > minimumSize:
            x,y,w,h = cv.boundingRect(contour)
            areaBiggestContour = w * h
            frame = cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.putText(img=frame, text=detectedColour, org=(50, 50), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=2,
                       color=(0, 0, 0), thickness=1)
            frame = cv.circle(frame, (self.cX, self.cY), radius=10, color=(0, 255, 0), thickness=-1)
            cv.putText(img=frame, text=detectedColour, org=(50, 50), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=1,
                       color=(255, 255, 255), thickness=1)
        #frame = cv.circle(frame, (720 // 2, 480 // 2), radius=10, color=(0, 0, 255), thickness=-1)

        return frame,[[self.cX,self.cY],areaBiggestContour], detectedColour

