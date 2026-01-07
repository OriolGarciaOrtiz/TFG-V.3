import time
from tkinter import *
import tkinter as tk

import requests
from tkinter import font
from PIL import Image, ImageTk
from matchBall import MatchBall
from followCar import FollowCar
from followColor import FollowColor

from djitellopy import Tello
from ColorDetector import ColorDetector
from Calibrador import Calibrador
from ColorPlan import ColorPlan

class Scene:
    def Open(self, master, callback):
        self.callback = callback
        self.newWindow = Toplevel(master)

        self.newWindow.title("Scene")
        self.newWindow.geometry("700x500")
        self.mainFrame = tk.Frame(self.newWindow)
        self.mainFrame.pack()
        self.mainFrame.rowconfigure(0, weight=1)
        self.mainFrame.rowconfigure(1, weight=1)
        self.mainFrame.rowconfigure(2, weight=1)
        self.mainFrame.rowconfigure(3, weight=1)
        self.mainFrame.rowconfigure(4, weight=1)
        self.mainFrame.rowconfigure(5, weight=1)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(2, weight=1)
        self.mainFrame.columnconfigure(3, weight=1)
        titleLbl = tk.Label (self.mainFrame,text = "Configuración del escenario")
        titleLbl.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)

        anchuraLbl = tk.Label(self.mainFrame, text="Anchura")
        anchuraLbl.grid(row=1, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.anchuraEntry = tk.Entry(self.mainFrame)
        self.anchuraEntry.grid(row=1, column=1, padx=5, pady=25, sticky=N + S + E + W)

        alturaLbl = tk.Label(self.mainFrame, text="Altura")
        alturaLbl.grid(row=2, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.alturaEntry = tk.Entry(self.mainFrame)
        self.alturaEntry.grid(row=2, column=1, padx=5, pady=25, sticky=N + S + E + W)

        profundidadLbl = tk.Label(self.mainFrame, text="Profundidad")
        profundidadLbl.grid(row=3, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.profundidadEntry = tk.Entry(self.mainFrame)
        self.profundidadEntry.grid(row=3, column=1, padx=5, pady=25, sticky=N + S + E + W)

        alarmaLbl = tk.Label(self.mainFrame, text="Alarma")
        alarmaLbl.grid(row=4, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.alarmaEntry = tk.Entry(self.mainFrame)
        self.alarmaEntry.grid(row=4, column=1, padx=5, pady=25, sticky=N + S + E + W)


        self.image = Image.open("assets/escenario.png")
        self.image = self.image.resize((300, 300), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = Canvas(self.mainFrame, width=300, height=300)
        canvas1.grid(row=1, column=2, rowspan=4, padx=20, pady=20, sticky=N + S + E + W)

        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        closeBtn = tk.Button(self.mainFrame, text="Cerrar", bg='#F57328', fg="white",
                                  command=self.closeScenario)
        closeBtn.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)

    def closeScenario (self):
        self.callback(int(self.anchuraEntry.get()), \
                int(self.alturaEntry.get()), \
                int(self.profundidadEntry.get()), \
                int(self.alarmaEntry.get())
        )
        self.newWindow.destroy()


class CircoColores:

    def Open (self, master):
        self.drone = Tello()
        self.master = master
        self.colorDetector = ColorDetector()

        self.configure()

    def empezarMatchBall(self):
        matchBallWindow = Toplevel(self.circusWindow)
        matchBallWindow.title("Match Ball")
        matchBallWindow.geometry("450x650")
        matchBall = MatchBall()
        frame = matchBall.buildFrame(matchBallWindow,  self.drone, self.colorDetector)
        frame.pack()
        matchBallWindow.mainloop()

    def empezarFollowCar(self):
        followCarWindow = Toplevel(self.circusWindow)
        followCarWindow.title("Follow car")
        followCarWindow.geometry("450x650")
        followCar = FollowCar()
        frame = followCar.buildFrame(followCarWindow, self.drone, self.colorDetector, 'down')
        frame.pack()
        followCarWindow.mainloop()

    def empezarColorPlan (self):
        colorPlanWindow = Toplevel(self.circusWindow)
        colorPlanWindow.title("Color plan")
        colorPlanWindow.geometry("1000x550")
        colorPlan = ColorPlan()
        frame = colorPlan.buildFrame(colorPlanWindow, self.drone, self.colorDetector)
        frame.pack()
        colorPlanWindow.mainloop()

        pass
    def fingers(self):

        pass


    def pose(self):
        pass

    def empezarFollowColor (self):
        followColorWindow = Toplevel(self.circusWindow)
        followColorWindow.title("Follow color")
        followColorWindow.geometry("800x650")
        followColor = FollowColor()
        frame = followColor.buildFrame(followColorWindow, self.drone, self.colorDetector, 'front')
        frame.pack()
        followColorWindow.mainloop()
    def bye(self):
        bye = Toplevel(self.circusWindow)
        bye.geometry("770x525")

        self.image = Image.open("assets/bye.png")
        self.image = self.image.resize((770, 525), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas2 = Canvas(bye, width=770, height=525)
        canvas2.pack(fill="both", expand=True)
        canvas2.create_image(0, 0, image=self.bg, anchor="nw")

        bye.mainloop()


    def empezar(self):
        print ('voy a empezar')
        self.circusWindow = Toplevel(self.configurationWindow)
        self.circusWindow.title("Selecciona un acto")
        self.circusWindow.geometry("800x600")
        self.circusWindow.columnconfigure(0, weight=1)
        self.circusWindow.columnconfigure(1, weight=1)
        self.circusWindow.columnconfigure(2, weight=1)
        self.circusWindow.columnconfigure(3, weight=1)
        self.circusWindow.rowconfigure(0, weight=1)
        self.circusWindow.rowconfigure(1, weight=1)

        self.image2 = Image.open("assets/circoColores2.png")
        self.image2 = self.image2.resize((800, 520), Image.ANTIALIAS)
        self.bg2 = ImageTk.PhotoImage(self.image2)
        canvas2 = Canvas(self.circusWindow, width=800, height=520)
        canvas2.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        canvas2.create_image(0, 0, image=self.bg2, anchor="nw")
        myFont4 = font.Font(family='Arial', size=12, weight='bold')
        matchBallButton = Button(self.circusWindow, text="Match ball", height=1, bg='#367E18', fg='#FFE9A0', width=8, command=self.empezarMatchBall)
        matchBallButton.place( x=50, y=480, anchor="nw")
        matchBallButton['font'] = myFont4

        followCarButton = Button(self.circusWindow, text="Atrapa \nal ladrón", height=2, bg='#367E18', fg='#FFE9A0', width=10,
                               command=self.empezarFollowCar)
        followCarButton.place( x=300, y=480, anchor="nw")
        followCarButton['font'] = myFont4

        colorPlanButton = Button(self.circusWindow, text="Plan \nde colores", height=2, bg='#367E18', fg='#FFE9A0', width=10,
                               command=self.empezarColorPlan)
        colorPlanButton.place( x=450, y=480, anchor="nw")
        colorPlanButton['font'] = myFont4

        followColorButton = Button(self.circusWindow, text="Sígueme", height=1, bg='#367E18', fg='#FFE9A0', width=8, command=self.empezarFollowColor)
        followColorButton.place( x=650, y=480, anchor="nw")
        followColorButton['font'] = myFont4

        byeButton = Button(self.circusWindow, text="Salir", height=1, bg='#FFE9A0', fg='#367E18', command=self.bye)
        byeButton.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        byeButton['font'] = myFont4
        self.circusWindow.mainloop()

    def guardar (self, anchura, altura, profundidad, alarma):
        self.configuracion_escenario = [anchura, altura, profundidad, alarma]

    def calibrate (self):
        calibrador = Calibrador()

        calibrador.Open(self.configurationWindow, self.drone, self.colorDetector)



    def connect(self):
        self.drone.connect()
        self.batteryLbl['text'] = "Nivel de bateria: " + str (self.drone.get_battery())


    def configure (self):
        myFont2 = font.Font(family='Arial', size=10, weight='bold')

        self.configurationWindow = Toplevel(self.master)
        self.configurationWindow.title("Configurar y conectar")
        self.configurationWindow.geometry("800x600")
        self.configurationWindow.columnconfigure(0, weight=1)
        self.configurationWindow.columnconfigure(1, weight=1)
        self.configurationWindow.columnconfigure(2, weight=1)
        self.configurationWindow.columnconfigure(3, weight=1)

        self.configurationWindow.rowconfigure(0, weight=1)


        self.image2 = Image.open("assets/gallery3.png")
        self.image2 = self.image2.resize((800, 520), Image.ANTIALIAS)
        self.bg2 = ImageTk.PhotoImage(self.image2)
        canvas2 = Canvas(self.configurationWindow, width=800, height=520)
        canvas2.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        canvas2.create_image(0, 0, image=self.bg2, anchor="nw")



        connectButton = Button(self.configurationWindow, text="Conecta con el dron", height=1, bg='#367E18', fg='#FFE9A0', command=self.connect)
        connectButton.place( x=100, y=480, anchor="nw")
        connectButton['font'] = myFont2

        self.batteryLbl = Label (self.configurationWindow, text= "Nivel de bateria: ????")
        self.batteryLbl.place( x=260, y=480, anchor="nw")
        self.batteryLbl['font'] = myFont2

        calibrationButton = Button(self.configurationWindow, text="Calibra colores", height=1, bg='#367E18', fg='#FFE9A0',
                                 command=self.calibrate)
        calibrationButton.place(x=420, y=480, anchor="nw")
        calibrationButton['font'] = myFont2

        empezarButton = Button(self.configurationWindow, text="Empezar expectáculo", height=1, bg='#367E18', fg='#FFE9A0', command=self.empezar)
        empezarButton.place( x=580, y=480, anchor="nw")
        empezarButton['font'] = myFont2

        self.configurationWindow.mainloop()
