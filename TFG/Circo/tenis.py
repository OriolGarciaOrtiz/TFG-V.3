import cv2 as cv
from djitellopy import Tello
from ColorDetector import ColorDetector
import random

tello = Tello()
colorDetector = ColorDetector()
tello.connect()
print(tello.get_battery())


moving = False
cont = 0

tello.streamon()
n=0
while n < 100:
    img = tello.get_frame_read().frame
    cv.imshow('frame', img)
    cv.waitKey(1)
    n=n+1
while cont < 6:
    img = tello.get_frame_read().frame
    img, color = colorDetector.DetectColor(img)
    cv.imshow('frame', img)
    cv.waitKey(1)
    if color == 'green' and not moving:
        tello.takeoff()
        next = 1
        moving = True

    if color == 'blueS' and moving:
        if next == 1:
            d = random.randint(0,50)
            h = random.randint(-60, 60)
            tello.go_xyz_speed(0, 250+d, h, 100)
            next = 2
            cont = cont + 1
        else:
            d = random.randint(0, 50)
            h = random.randint(-60, 60)
            tello.go_xyz_speed(0, -(250+d), h, 100)
            next = 1
            cont = cont + 1

tello.land()

