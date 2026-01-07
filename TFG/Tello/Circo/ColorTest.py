import math
import time

import cv2 as cv
from djitellopy import Tello
from ColorDetector import ColorDetector
from Calibrador import Calibrador
from tkinter import *
from tkinter.ttk import *
import tkinter as tk
import cv2


def Conectar():
    tello.connect()
    print(tello.get_battery())

def Calibrar():
    calibrador = Calibrador()
    calibrador.Open(main, tello, colorDetector)

def Cerca (pos):

    dis = math.sqrt((pos[0]-320)*(pos[0]-320) + (pos[1]-240)*(pos[1]-240))
    print ('distancia ',pos[0], pos[1], dis)
    if dis > 200:
        return False
    else:
        return True
def Verificar ():
    tello.streamon()


    color = ""
    colorAnterior = ""
    cont = 0
    maxCont = 1
    speed = 20
    tello.takeoff()
    tello.move_up(30)

    flying = True
    while flying:
        telloFrame = tello.get_frame_read().frame

        telloFrame = cv2.resize(telloFrame, (640, 480))
        cv2.circle(telloFrame, (320, 240), 7, (0, 0, 255), -1)
        cv2.putText(img=telloFrame, text=color, org=(320, 300), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=2,
                    color=(255, 255, 255), thickness=1)

        cv2.imshow("tello", telloFrame)
        cv2.waitKey(1)

        img, data, color = colorDetector.DetectColor(telloFrame)
        if color == colorAnterior:
            cont = cont + 1
            if cont == maxCont:

                if color == 'green':
                    # hacia delante
                    tello.send_rc_control(0,speed, 0, 0)
                    pass
                elif color == 'blueL':
                    if Cerca (data[0]):
                        tello.land()
                        flying = False
                cont = 0
        else:
            colorAnterior = color



main = Tk()
tello = Tello()
colorDetector = ColorDetector()

main.title  ("Ventana principal")
conectarBtn = tk.Button(main,
                   text="Conectar con el dron",
                     bg='red',
                   command=Conectar)
conectarBtn.pack()
calibrarBtn = tk.Button(main,
                   text="Calibrar",
                   command=Calibrar)
calibrarBtn.pack()
verificarBtn = tk.Button(main,
                   text="Verificar",
                   command=Verificar)
verificarBtn.pack()
main.mainloop()



