import cv2 as cv
from djitellopy import Tello
from ColorDetector import ColorDetector
import random
import tkinter as tk
from tkinter import *

class MatchBall:
    def buildFrame (self, master, drone, colorDetector):
        self.drone = drone
        self.colorDetector = colorDetector
        self.master = master
        self.matchBallFrame = tk.Frame (self.master)
        self.matchBallFrame.rowconfigure(0, weight=1)
        self.empezarButton = tk.Button(self.matchBallFrame, text="Empezar", height=1, bg='#367E18', fg='#FFE9A0', width=8, command=self.empezar)
        self.empezarButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
        return self.matchBallFrame

    def empezar (self):
        moving = False
        cont = 0
        self.empezarButton['text'] = str (self.drone.get_battery())


        self.drone.streamon()
        n=0
        while n < 100:
            img = self.drone.get_frame_read().frame
            cv.imshow('frame', img)
            cv.waitKey(1)
            n=n+1
        while cont < 8:
            img = self.drone.get_frame_read().frame
            img,_, color = self.colorDetector.DetectColor(img)
            cv.imshow('frame', img)
            cv.waitKey(1)
            if color == 'green' and not moving:
                self.drone.takeoff()
                next = 1
                moving = True

            if color == 'blueS' and moving:
                if next == 1:
                    d = random.randint(0,50)
                    h = random.randint(-60, 60)
                    self.drone.go_xyz_speed(0, 250+d, h, 100)
                    next = 2
                    cont = cont + 1
                else:
                    d = random.randint(0, 50)
                    h = random.randint(-60, 60)
                    self.drone.go_xyz_speed(0, -(250+d), h, 100)
                    next = 1
                    cont = cont + 1
            self.empezarButton['text'] = str(self.drone.get_battery())
        self.drone.land()

