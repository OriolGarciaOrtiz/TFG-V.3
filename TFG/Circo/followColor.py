import cv2 as cv
from djitellopy import Tello
from ColorDetector import ColorDetector
import random
import tkinter as tk
from tkinter import *
from utilities import *
from ColorTraker import ColorTraker
from PIL import Image, ImageTk
import threading

class FollowColor:
    def buildFrame (self, master, drone, colorDetector, mode):
        self.mode = mode # 'front' camera or 'down' camera with mirror
        self.colorTracker = ColorTraker()
        self.drone = self.colorTracker.intializeTracker(drone)
        self.colorDetector = colorDetector
        self.master = master
        self.followColorFrame = tk.Frame (self.master)
        self.followColorFrame.rowconfigure(0, weight=1)

        self.followColorFrame.rowconfigure(1, weight=1)
        self.followColorFrame.rowconfigure(2, weight=1)
        self.followColorFrame.rowconfigure(3, weight=1)
        self.followColorFrame.rowconfigure(4, weight=1)

        self.followColorFrame.columnconfigure(0, weight=1)
        self.followColorFrame.columnconfigure(1, weight=1)
        self.followColorFrame.columnconfigure(2, weight=1)
        self.followColorFrame.columnconfigure(3, weight=1)
        self.followColorFrame.columnconfigure(4, weight=1)
        self.followColorFrame.columnconfigure(5, weight=1)


        self.KPLabel = tk.Label ( self.followColorFrame, text = 'KP')
        self.KPLabel.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.KP = tk.Entry ( self.followColorFrame)
        self.KP.insert (0,"1")
        self.KP.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        self.KDLabel = tk.Label(self.followColorFrame, text='KD')
        self.KDLabel.grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)
        self.KD = tk.Entry(self.followColorFrame)
        self.KD.insert(0, "1")
        self.KD.grid(row=0, column=3, padx=5, pady=5, sticky=N + S + E + W)

        self.KILabel = tk.Label(self.followColorFrame, text='KI')
        self.KILabel.grid(row=0, column=4, padx=5, pady=5, sticky=N + S + E + W)
        self.KI = tk.Entry(self.followColorFrame)
        self.KI.insert(0, "0")
        self.KI.grid(row=0, column=5, padx=5, pady=5, sticky=N + S + E + W)


        self.E1 = tk.Label(self.followColorFrame)
        self.E1['text'] = 0
        self.E1.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
        self.E2 = tk.Label(self.followColorFrame)
        self.E2['text'] = 0
        self.E2.grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
        self.E3 = tk.Label(self.followColorFrame)
        self.E3['text'] = 0
        self.E3.grid(row=1, column=4, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)



        self.empezarButton = tk.Button(self.followColorFrame, text="Empezar", height=2, bg='#367E18', fg='#FFE9A0', width=8, command=self.empezar1)
        self.empezarButton.grid(row=2, column=0, columnspan=6, padx=5, pady=5, sticky=N + S + E + W)

        self.image = Image.open("assets/follow_me.png")
        self.image = self.image.resize((800, 300), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas = Canvas(self.followColorFrame, width=800, height=350)
        self.canvas.grid(row=3, column=0, columnspan=6, padx=5, pady=5, sticky=N + S + E + W)
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        self.idCont = self.canvas.create_text(425, 420, text="0", fill="red", font=('Helvetica 75 bold'))

        self.aterrizajeButton = tk.Button(self.followColorFrame, text="Aterrizaje de emergencia", height=2, bg='red', fg='#FFE9A0',
                                       width=15, command=self.land)
        self.aterrizajeButton.grid(row=4, column=0, columnspan=6, padx=5, pady=5, sticky=N + S + E + W)
        self.error1 = 0
        self.error2 = 0
        self.error3 = 0
        return self.followColorFrame

    def land (self):
        self.drone.land()
        self.counting = False


    def empezar1 (self):
        x = threading.Thread(target=self.empezar)
        x.start()



    def count(self):
        cont = 0
        while self.counting:
            time.sleep (1)
            cont = cont + 1
            self.canvas.itemconfigure(self.idCont, text=str(cont))


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
            self.canvas.itemconfigure(self.idCont, text="0")
            self.drone.takeoff()
            print ('empezamos a contar')
            self.counting = True
            x = threading.Thread(target=self.count)
            x.start()

        flying = True
        timeAnt = time.time()

        while flying:

            # tomo imagen
            #img = telloGetFrame(self.drone)
            img = self.drone.get_frame_read().frame
            timeAhora = time.time()
            timeVuelta = timeAhora - timeAnt

            print (timeVuelta*1000)
            timeAnt = timeAhora

            # detecto el color
            # también me devuelve la imagen con el contorno de la mancha de color dibujado
            # en info tengo las coordenadas del punto central de la mancha de color y el area en el formato siguiente:
            # [[cX,cY],areaBiggestContour]
            img = cv.resize(img, (w, h))
            img = cv.flip(img, 1)
            img, info, detectedColor = self.colorDetector.DetectColor(img)
            pLRError, pUDError, pFBError = self.colorTracker.calculaError(self.drone, info, w, h, pid, pLRError, pUDError, pFBError, self.mode)
            self.error1 = self.error1 + (pLRError - self.error1) / 5
            self.error2 = self.error2 + (pUDError - self.error2) / 5
            self.error3 = self.error3 + (pFBError - self.error3) / 5

            self.E1['text'] = str(self.error1)
            self.E2['text'] = str(self.error2)
            self.E3['text'] = str(self.error3)

            cv.imshow("frame", img)
            cv.waitKey(1)
            print ('color ', detectedColor)
            #img, info, detectedColor = findColor(img)

            if detectedColor == 'blueS':
                print('detecto amarillo')
                flying = False
                self.drone.land()
                self.counting = False
            elif detectedColor == 'green':
                self.colorTracker.trackColor(self.drone, info, w, h, pid, self.error1,self.error2,self.error3,  self.mode)


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





