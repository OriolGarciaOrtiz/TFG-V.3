import math
import time

import tkinter as tk
from tkinter import *
from tkinter import font
from PIL import Image, ImageTk
import threading

import cv2


class ColorPlan:
    def buildFrame (self, master, drone, colorDetector):
        self.drone = drone
        self.colorDetector = colorDetector
        self.master = master
        self.colorPlanFrame = tk.Frame (self.master)

        self.image = Image.open("assets/caso1.png")
        self.image = self.image.resize((1000, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas = Canvas(self.colorPlanFrame, width=1000, height=550)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

        myFont1 = font.Font(family='Arial', size=12, weight='bold')
        takeOffButton = Button(self.colorPlanFrame, text="Despegar", height=1, bg='#367E18', fg='#FFE9A0', width=8,
                                 command=self.start)
        takeOffButton.place(x=495, y=500, anchor="nw")
        takeOffButton['font'] = myFont1

        myFont2 = font.Font(family='Arial', size=14, weight='bold')
        landButton = Button(self.colorPlanFrame, text="Aterrizaje de \n emergencia", height=2, bg='red', fg='#FFE9A0', width=12,
                                 command=self.land)
        landButton.place(x=820, y=480, anchor="nw")
        landButton['font'] = myFont2

        self.modeFrame = LabelFrame(self.colorPlanFrame, text="Modo de vuelo")
        self.opcion = StringVar()
        self.opcion.set("sinGiro")

        Radiobutton(self.modeFrame, text="Sin giro", variable=self.opcion,
                    value="sinGiro").pack()
        Radiobutton(self.modeFrame, text="Con giro", variable=self.opcion,
                    value="conGiro").pack()
        self.modeFrame.place(x=10, y=10, anchor="nw")

        self.demoFrame = LabelFrame(self.colorPlanFrame, text="Demo")
        demoTakeOffButton = Button(self.demoFrame, text="Despega", height=2, bg='red', fg='white',
                            width=12,command=self.takeOff).pack(pady=5)
        demoForwardButton = Button(self.demoFrame, text="Adelante", height=2, bg='yellow', fg='black',
                            width=12,command=self.forward).pack(pady=5)
        demoRightButton = Button(self.demoFrame, text="Derecha", height=2, bg='green', fg='white',
                            width=12,command=self.right).pack(pady=5)
        demoLeftButton = Button(self.demoFrame, text="Izquierda", height=2, bg='Turquoise', fg='black',
                            width=12,command=self.left).pack(pady=5)
        demoBackButton = Button(self.demoFrame, text="Atrás", height=2, bg='magenta3', fg='white',
                            width=12,command=self.back).pack(pady=5)
        demoLandButton = Button(self.demoFrame, text="Aterriza", height=2, bg='DarkBlue', fg='white',
                            width=12,command=self.land).pack(pady=5)

        self.demoFrame.place(x=10, y=90, anchor="nw")

        self.casosFrame = LabelFrame(self.colorPlanFrame, text="Casos")
        self.caso1Button = tk.Button(self.casosFrame, text="Caso 1", height=2, bg='navajo white', fg='black',
                                   width=12, command=self.caso1)
        self.caso1Button.pack(pady=5)
        self.caso2Button = tk.Button(self.casosFrame, text="Caso 2", height=2, bg='blanched almond', fg='black',
                                   width=12, command=self.caso2)
        self.caso2Button.pack(pady=5)
        self.caso3Button = tk.Button(self.casosFrame, text="Caso 3", height=2, bg='blanched almond', fg='black',
                                 width=12, command=self.caso3)
        self.caso3Button.pack(pady=5)
        self.caso4Button = tk.Button(self.casosFrame, text="Caso 4", height=2, bg='blanched almond', fg='black',
                                width=12, command=self.caso4)
        self.caso4Button.pack(pady=5)



        self.casosFrame.place(x=900, y=90, anchor="nw")

        self.speed = 20
        self.caso = 'caso1'
        return self.colorPlanFrame

    def takeOff (self):
        self.drone.takeoff()
        self.drone.move_up(30)



    def forward (self):
        print ('forward: ', self.speed)
        self.drone.send_rc_control(0, self.speed, 0, 0)

    def back (self):
        if self.opcion.get() == 'sinGiro':
            self.drone.send_rc_control(0, -self.speed, 0, 0)
        else:
            self.drone.send_rc_control(0, 0, 0, 0)
            self.drone.rotate_clockwise(180)
            self.drone.send_rc_control(0, self.speed, 0, 0)

    def right (self):
        if self.opcion.get() == 'sinGiro':
            self.drone.send_rc_control(self.speed, 0, 0,0)
        else:
            self.drone.send_rc_control(0, 0, 0, 0)
            self.drone.rotate_clockwise(90)
            self.drone.send_rc_control(0, self.speed, 0, 0)

    def left (self):

        if self.opcion.get() == 'sinGiro':
            self.drone.send_rc_control(-self.speed, 0, 0, 0)
        else:
            self.drone.send_rc_control(0, 0, 0, 0)
            self.drone.rotate_counter_clockwise(90)
            self.drone.send_rc_control(0, self.speed, 0, 0)

    def land(self):
        self.drone.send_rc_control(0, 0, 0, 0)
        self.drone.land()

    def caso1(self):
        if self.caso == 'caso1':
            self.image = Image.open("assets/caso1SG.png")
            self.caso = 'caso1SG'
        elif self.caso == 'caso1SG':
            self.image = Image.open("assets/caso1CG.png")
            self.caso = 'caso1CG'
        else:
            self.caso2Button['bg'] = 'navajo white'
            self.caso2Button['bg'] = 'blanched almond'
            self.caso3Button['bg'] = 'blanched almond'
            self.caso4Button['bg'] = 'blanched almond'
            self.image = Image.open("assets/caso1.png")
            self.caso = 'caso1'

        self.image = self.image.resize((1000, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

    def caso2(self):
        if self.caso == 'caso2':
            self.image = Image.open("assets/caso2SG.png")
            self.caso = 'caso2SG'
        elif self.caso == 'caso2SG':
            self.image = Image.open("assets/caso2CG.png")
            self.caso = 'caso2CG'
        else:
            self.caso1Button['bg'] = 'blanched almond'
            self.caso2Button['bg'] = 'navajo white'
            self.caso3Button['bg'] = 'blanched almond'
            self.caso4Button['bg'] = 'blanched almond'
            self.image = Image.open("assets/caso2.png")
            self.caso = 'caso2'

        self.image = self.image.resize((1000, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")


    def caso3(self):
        if self.caso == 'caso3':
            self.image = Image.open("assets/caso3SG.png")
            self.caso = 'caso3SG'
        elif self.caso == 'caso3SG':
            self.image = Image.open("assets/caso3CG.png")
            self.caso = 'caso3CG'
        else:
            self.caso1Button['bg'] = 'blanched almond'
            self.caso2Button['bg'] = 'blanched almond'
            self.caso3Button['bg'] = 'navajo white'
            self.caso4Button['bg'] = 'blanched almond'
            self.image = Image.open("assets/caso3.png")
            self.caso = 'caso3'

        self.image = self.image.resize((1000, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")


    def caso4(self):
        if self.caso == 'caso4':
            self.image = Image.open("assets/caso4SG.png")
            self.caso = 'caso4SG'
        elif self.caso == 'caso4SG':
            self.image = Image.open("assets/caso4CG.png")
            self.caso = 'caso4CG'
        else:
            self.caso1Button['bg'] = 'blanched almond'
            self.caso2Button['bg'] = 'blanched almond'
            self.caso3Button['bg'] = 'blanched almond'
            self.caso4Button['bg'] = 'navajo white'
            self.image = Image.open("assets/caso4.png")
            self.caso = 'caso4'

        self.image = self.image.resize((1000, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

    def Cerca(self,pos):

        dis = math.sqrt((pos[0] - 320) * (pos[0] - 320) + (pos[1] - 240) * (pos[1] - 240))
        #print('distancia ', pos[0], pos[1], dis)
        if dis > 250:
            return False
        else:
            return True

    def fly (self):
        color = ""
        self.flying = True
        moving = False
        lastColor = 'none'

        while self.flying:
            telloFrame = self.drone.get_frame_read().frame

            telloFrame = cv2.resize(telloFrame, (640, 480))
            cv2.circle(telloFrame, (320, 240), 7, (0, 0, 255), -1)
            cv2.putText(img=telloFrame, text=color, org=(320, 300), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=2,
                        color=(255, 255, 255), thickness=1)

            cv2.imshow("tello", telloFrame)
            cv2.waitKey(1)

            img, data, color = self.colorDetector.DetectColor(telloFrame)
            if color != lastColor:
                    lastColor = color
                    if color == 'yellow':
                        # hacia delante
                        if not moving:
                            moving = True
                            self.forward()
                        elif self.Cerca(data[0]):
                            self.forward()

                    elif color == 'blueS':
                        print('detecto blueS')
                        # aterriza
                        if self.Cerca(data[0]):
                            self.land()
                            self.flying = False
                    elif color == 'blueL':
                        print('detecto blueL')
                        # hacia la izquierda
                        if not moving:
                            moving = True
                            self.left()
                        elif self.Cerca(data[0]):
                            self.left()

                    elif color == 'green':
                        # hacia la derecha
                        print ('green')
                        if not moving:
                            moving = True
                            self.right()

                        elif self.Cerca(data[0]):
                            self.right()
                    elif color == 'pink':
                        # hacia atras
                        if not moving:
                            moving = True
                            self.back()
                        elif self.Cerca(data[0]):
                            self.back()




    def start(self):
        self.drone.streamon()
        telloFrame = self.drone.get_frame_read().frame

        telloFrame = cv2.resize(telloFrame, (640, 480))

        cv2.imshow("tello", telloFrame)
        cv2.waitKey(1)
        self.takeOff()
        x = threading.Thread(target=self.fly)
        x.start()




