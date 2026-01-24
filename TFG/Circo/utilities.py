import time

import numpy as np
from djitellopy import Tello
import cv2 as cv

def intializeTello(myDrone):
    # CONNECT TO TELLO
    myDrone.for_back_velocity = 0
    myDrone.left_right_velocity = 0
    myDrone.up_down_velocity = 0
    myDrone.yaw_velocity = 0
    myDrone.speed =0
    myDrone.streamon()
    return myDrone

def telloGetFrame(myDrone,w=720,h=480):
    # GET THE IMGAE FROM TELLO
    myFrame = myDrone.get_frame_read()
    myFrame = myFrame.frame
    img = cv.resize(myFrame, (w, h))
    img = cv.flip(img,1)
    time.sleep (0.1)

    return img

def findFace(img):
    faceCascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.1, 4)
    myFacesListC = []
    myFaceListArea = []
    for (x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        myFacesListC.append([cx, cy])
        myFaceListArea.append(area)
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        # index of closest face
        return img, [myFacesListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]

def findColor (img):
        w, h = 720, 480
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        print ('color ', hsv[360,240][0])

        # define range of colors in HSV
        lowerYellow = np.array([40, 50, 50])
        upperYellow = np.array([50, 255, 255])

        lowerBlue = np.array([100, 50, 50])
        upperBlue = np.array([120, 255, 255])


        detectedColour = 'none'

        # ignore selected contour with area less that this
        minimumSize = 10000

        areaBiggestContour = 0
        cX,cY = 0,0

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
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                contour = cyellow
                areaBiggestContour = cv.contourArea(cyellow)
                detectedColour = 'yellow'

        mask = cv.inRange(hsv, lowerBlue, upperBlue)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv.erode(mask, kernel, iterations=5)
        mask = cv.dilate(mask, kernel, iterations=5)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
        contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if (len(contours) > 0):
            cBlue = max(contours, key=cv.contourArea)
            M = cv.moments(cBlue)
            if cv.contourArea(cBlue) > areaBiggestContour:
                    areaBiggestContour = cv.contourArea(cBlue)
                    contour = cBlue
                    detectedColour = 'blue'
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])



        if detectedColour != 'none' and areaBiggestContour > minimumSize:
            #cv.drawContours(img, [contour], -1, (0, 255, 0), 3)
            x,y,w,h = cv.boundingRect(contour)
            areaBiggestContour = w*h
            img = cv.rectangle(img, (x,y), (x+w, y+h), (0,255,0),2)
            img = cv.circle(img, (cX, cY), radius=10, color=(0, 255, 0), thickness=-1)
            cv.putText(img=img, text=detectedColour, org=(50, 50), fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=1,
                       color=(255, 255, 255), thickness=1)
        img = cv.circle(img, (720 // 2, 480 // 2), radius=10, color=(0, 0, 255), thickness=-1)
        return img,[[cX,cY],areaBiggestContour], detectedColour

def trackColor(myDrone,info,w,h,pid,pLRError, pUDError, pFBError, mode):
    # si ha detectado color
    if info[0][0] != 0:

        # error de posicion en horizontal
        errorLR = info[0][0] - w//2
        # ajusto la velocidad horizontal
        # solo uso el termino proporcional y el derivativo
        speedLR = int(pid[0]*errorLR + pid[1] * (errorLR-pLRError))
        # limito el valor obtenido al rango válido para la velocidad
        speedLR = int (np.clip (speedLR, -100, 100))

        # repido el proceso para el error vertical
        errorUD = info[0][1] - h // 2
        speedUD = int(pid[0] * errorUD + pid[1] * (errorUD - pUDError))
        speedUD = int(np.clip(speedUD, -100, 100))

        # y para el error cerca/lejos, que se calcula en función del area de la mancha de color
        errorFB = (info[1] - 30000)//100
        speedFB = int(pid[0] * errorFB + pid[1] * (errorFB - pFBError))
        speedFB = int(np.clip(speedFB, -100, 100))

        # los siguientes ajustes en las velocidades obtenidas me dan resultados razonables
        print (-speedLR//6, -speedUD//4, speedFB//5)
        if mode == 'front':
            myDrone.left_right_velocity = -speedLR//6
            myDrone.up_down_velocity = -speedUD//4
            myDrone.for_back_velocity = -speedFB//5
        else:
            myDrone.left_right_velocity = -speedLR // 6
            #myDrone.up_down_velocity = -speedFB // 4
            myDrone.up_down_velocity = 0
            myDrone.for_back_velocity = speedUD // 5

    else:
        myDrone.left_right_velocity = 0
        myDrone.for_back_velocity = 0
        myDrone.up_down_velocity = 0
        myDrone.yaw_velocity = 0

    if myDrone.send_rc_control:
        myDrone.send_rc_control(myDrone.left_right_velocity, myDrone.for_back_velocity,
                                myDrone.up_down_velocity, myDrone.yaw_velocity)
    return errorLR, errorUD, errorFB