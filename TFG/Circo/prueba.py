import time

import cv2 as cv
from djitellopy import Tello
from ColorDetector import ColorDetector

tello = Tello()
tello.connect()
print(tello.get_battery())
tello.takeoff()
time.sleep(5)
tello.go_xyz_speed( 50, 50, 50, 10)
time.sleep(5)
tello.go_xyz_speed( 50, 0, 0, 10)
time.sleep(5)
tello.go_xyz_speed( 0, 50, 0, 10)
time.sleep(5)
tello.go_xyz_speed( 0, 0, 50, 10)
time.sleep(5)
tello.land()
