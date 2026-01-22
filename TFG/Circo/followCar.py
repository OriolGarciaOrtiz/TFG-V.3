import cv2 as cv
from djitellopy import Tello
from ColorDetector import ColorDetector
import random
import tkinter as tk
from tkinter import *
from utilities import *
from ColorTraker import ColorTraker



class FollowCar:
    def buildFrame (self, master, drone, colorDetector, mode):
        self.mode = mode # 'front' camera or 'down' camera with mirror
        self.colorTracker = ColorTraker()
        self.drone = self.colorTracker.intializeTracker(drone)
        self.colorDetector = colorDetector
        self.master = master
        self.followCarFrame = tk.Frame (self.master)
        self.followCarFrame.rowconfigure(0, weight=1)
        self.followCarFrame.rowconfigure(1, weight=1)

        self.followCarFrame.columnconfigure(0, weight=1)
        self.followCarFrame.columnconfigure(1, weight=1)
        self.followCarFrame.columnconfigure(2, weight=1)
        self.followCarFrame.columnconfigure(3, weight=1)
        self.followCarFrame.columnconfigure(4, weight=1)
        self.followCarFrame.columnconfigure(5, weight=1)


        self.KPLabel = tk.Label ( self.followCarFrame, text = 'KP')
        self.KPLabel.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.KP = tk.Entry ( self.followCarFrame)
        self.KP.insert (0,"1")
        self.KP.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        self.KDLabel = tk.Label(self.followCarFrame, text='KD')
        self.KDLabel.grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)
        self.KD = tk.Entry(self.followCarFrame)
        self.KD.insert(0, "1")
        self.KD.grid(row=0, column=3, padx=5, pady=5, sticky=N + S + E + W)

        self.KILabel = tk.Label(self.followCarFrame, text='KI')
        self.KILabel.grid(row=0, column=4, padx=5, pady=5, sticky=N + S + E + W)
        self.KI = tk.Entry(self.followCarFrame)
        self.KP.insert(0, "0")
        self.KI.grid(row=0, column=5, padx=5, pady=5, sticky=N + S + E + W)



        self.empezarButton = tk.Button(self.followCarFrame, text="Empezar", height=1, bg='#367E18', fg='#FFE9A0', width=8, command=self.empezar)
        self.empezarButton.grid(row=1, column=0, columnspan=6, padx=5, pady=5, sticky=N + S + E + W)
        return self.followCarFrame

    def empezar (self):
        moving = False
        cont = 0
        self.empezarButton['text'] = str (self.drone.get_battery())

        # costantes propocional, derivativa e integral
        #pid = [1.0, 0.9, 0]
        pid = [float(self.KP.get()), float(self.KD.get()), float(self.KI.get())]

        # dimensiones de la imagen
        w, h = 720, 480

        # errores Left/right, up/down, forward/back
        pLRError = 0
        pUDError = 0
        pFBError = 0

        # para controlar si quiero despegar (0) o solo probar (1)
        startCounter = 0
        flying = False


        img = self.drone.get_frame_read().frame
        cv.imshow('frame', img)
        cv.waitKey(1)
        if startCounter == 0:
            self.drone.takeoff()
            #self.drone.move_up(10)
            startCounter = 1
        flying = True

        while flying:

            # tomo imagen
            #img = telloGetFrame(self.drone)
            img = self.drone.get_frame_read().frame

            # detecto el color
            # también me devuelve la imagen con el contorno de la mancha de color dibujado
            # en info tengo las coordenadas del punto central de la mancha de color y el area en el formato siguiente:
            # [[cX,cY],areaBiggestContour]
            img = cv.resize(img, (w, h))
            img = cv.flip(img, 1)
            img, info, detectedColor = self.colorDetector.DetectColor(img)
            cv.imshow("frame", img)
            cv.waitKey(1)
            print ('color ', detectedColor)
            #img, info, detectedColor = findColor(img)

            if detectedColor == 'blueS':
                print('detecto amarillo')
                flying = False
                self.drone.land()
            elif detectedColor == 'green':
                pLRError, pUDError, pFBError = self.colorTracker.trackColor(self.drone, info, w, h, pid, pLRError, pUDError, pFBError, self.mode)
            else:
                print ('quieto')
                self.drone.left_right_velocity = 0
                self.drone.for_back_velocity = 0
                self.drone.up_down_velocity = 0
                self.drone.yaw_velocity = 0

                if self.drone.send_rc_control:
                    self.drone.send_rc_control(self.drone.left_right_velocity, self.drone.for_back_velocity,
                                                self.drone.up_down_velocity, self.drone.yaw_velocity)
            # DISPLAY IMAGE





