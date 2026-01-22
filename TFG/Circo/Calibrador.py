from tkinter import *
from tkinter.ttk import *
import cv2 as cv
import threading
import tkinter as tk

class Calibrador:
    def __SendVideoForCalibration (self, ):

        primera = True


        while self.markingFrameForCalibration:
            img = self.tello.get_frame_read().frame
            img = self.colorDetector.MarkFrameForCalibration(img)
            cv.imshow('frame'+str(self.cont), img)
            cv.waitKey(1)
            if primera:
                self.iniciarBtn['text'] = 'Tomar valores'
                primera = False
        self.cont = self.cont + 1


    def __TakeVideoWithColor (self, ):
        primera = True

        while self.takingVideoWithColor:
            img = self.tello.get_frame_read().frame
            img,_, color = self.colorDetector.DetectColor(img)
            cv.imshow('frame' + str(self.cont), img)
            cv.waitKey(1)
            if primera:
                self.verificarBtn['text'] = 'Parar'
                primera = False
        self.verificarBtn['text'] = 'Verificar'
        self.cont = self.cont + 1


    def Open (self, master, tello, colorDetector):
        self.newWindow = Toplevel(master)
        self.newWindow.title("Calibrador")
        self.newWindow.geometry("150x300")
        self.mainFrame = tk.Frame (self.newWindow)
        self.mainFrame.pack()
        self.mainFrame.rowconfigure(0, weight=1)
        self.mainFrame.rowconfigure(1, weight=1)
        self.mainFrame.rowconfigure(2, weight=1)
        self.mainFrame.rowconfigure(3, weight=1)

        self.tello = tello
        self.colorDetector = colorDetector


        self.iniciarBtn = tk.Button(self.mainFrame,
                            text="Iniciar calibración",
                            command=self.Iniciar)
        self.iniciarBtn.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.verificarBtn = tk.Button(self.mainFrame,
                                    text="Verificar",
                                    command=self.Verificar)
        self.verificarBtn.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.cerrarBtn = tk.Button(self.mainFrame,
                       text="Cerrar",
                       command=self.Cerrar)
        self.cerrarBtn.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.cont = 0
        valoresFrame = tk.LabelFrame (self.mainFrame, text = "Valores")
        valoresFrame.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
        valoresFrame.rowconfigure(0, weight=1)
        valoresFrame.rowconfigure(1, weight=1)
        valoresFrame.rowconfigure(2, weight=1)
        valoresFrame.rowconfigure(3, weight=1)
        valoresFrame.rowconfigure(4, weight=1)
        valoresFrame.rowconfigure(5, weight=1)
        valoresFrame.columnconfigure(0, weight=1)
        valoresFrame.columnconfigure(1, weight=1)
        valoresFrame.columnconfigure(2, weight=1)

        tk.Button(valoresFrame,text="Yellow", bg= 'Yellow').grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.defaultYellow = Label(valoresFrame, text='?')
        self.defaultYellow.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.newYellow = Label(valoresFrame, text = '?')
        self.newYellow.grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)

        tk.Button(valoresFrame, text="Green", bg= 'Green').grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.defaultGreen = Label(valoresFrame, text='?')
        self.defaultGreen.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.newGreen = Label(valoresFrame, text='?')
        self.newGreen.grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)

        tk.Button(valoresFrame, text="BlueS", bg = 'Teal').grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.defaultBlueS = Label(valoresFrame, text='?')
        self.defaultBlueS.grid(row=2, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.newBlueS = Label(valoresFrame, text='?')
        self.newBlueS.grid(row=2, column=2, padx=5, pady=5, sticky=N + S + E + W)

        tk.Button(valoresFrame, text="BlueL", bg = 'Cyan').grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.defaultBlueL = Label(valoresFrame, text='?')
        self.defaultBlueL.grid(row=3, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.newBlueL = Label(valoresFrame, text='?')
        self.newBlueL.grid(row=3, column=2, padx=5, pady=5, sticky=N + S + E + W)

        tk.Button(valoresFrame, text="Pink", bg = 'HotPink1').grid(row=4, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.defaultPink = Label(valoresFrame, text='?')
        self.defaultPink.grid(row=4, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.newPink = Label(valoresFrame, text='?')
        self.newPink.grid(row=4, column=2, padx=5, pady=5, sticky=N + S + E + W)

        tk.Button(valoresFrame, text="Purple", bg = 'MediumPurple1').grid(row=5, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.defaultPurple = Label(valoresFrame, text='?')
        self.defaultPurple.grid(row=5, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.newPurple = Label(valoresFrame, text='?')
        self.newPurple.grid(row=5, column=2, padx=5, pady=5, sticky=N + S + E + W)

        yellow, green, blueS, blueL, pink, purple = self.colorDetector.DameValores()
        self.defaultYellow['text'] = str(yellow)
        self.defaultGreen['text'] = str(green)
        self.defaultBlueS['text'] = str(blueS)
        self.defaultBlueL['text'] = str(blueL)
        self.defaultPink['text'] = str(pink)
        self.defaultPurple['text'] = str(purple)

        self.markingFrameForCalibration = False
        self.takingVideoWithColor = False

        self.tello.streamon()

    def Iniciar(self):
        if not self.markingFrameForCalibration:
            self.markingFrameForCalibration = True
            w = threading.Thread(target=self.__SendVideoForCalibration)
            w.start()
        else:
            self.colorDetector.TomaValores()
            yellow, green, blueS, blueL, pink, purple = self.colorDetector.DameValores()
            self.newYellow['text'] = str(yellow)
            self.newGreen['text'] = str(green)
            self.newBlueS['text'] = str(blueS)
            self.newBlueL['text'] = str(blueL)
            self.newPink['text'] = str(pink)
            self.newPurple['text'] = str(purple)

    def Verificar(self):
        self.markingFrameForCalibration = False
        if not self.takingVideoWithColor:
            print ('vamos a verificar')
            self.takingVideoWithColor = True
            w = threading.Thread(target=self.__TakeVideoWithColor)
            w.start()
        else:
            self.takingVideoWithColor = False


    def Cerrar (self):
        self.markingFrameForCalibration = False
        self.takingVideoWithColor = False
        self.newWindow.destroy()





