import base64
from tkinter import Toplevel
from tkinter import *
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
from tkinter import messagebox
from djitellopy import Tello
import time
import cv2
import os
import paho.mqtt.client as mqtt
from io import BytesIO
#import requests
import random
import threading
from panoramic import escenarioPanoramica
from images import escenarioImagenes
from video import escenarioVideo

class Scene:

    configured = False

    def Open(self, master, callback):
        self.configured = False
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
        titleLbl = tk.Label(self.mainFrame, text="Configuración del escenario")
        titleLbl.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)

        anchuraLbl = tk.Label(self.mainFrame, text="Anchura")
        anchuraLbl.grid(row=1, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.anchuraEntry = tk.Entry(self.mainFrame)
        self.anchuraEntry.grid(row=1, column=1, padx=5, pady=25, sticky=N + S + E + W)
        self.anchuraEntry.insert(0, '4')

        alturaLbl = tk.Label(self.mainFrame, text="Altura")
        alturaLbl.grid(row=2, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.alturaEntry = tk.Entry(self.mainFrame)
        self.alturaEntry.grid(row=2, column=1, padx=5, pady=25, sticky=N + S + E + W)
        self.alturaEntry.insert(0, '4')

        profundidadLbl = tk.Label(self.mainFrame, text="Profundidad")
        profundidadLbl.grid(row=3, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.profundidadEntry = tk.Entry(self.mainFrame)
        self.profundidadEntry.grid(row=3, column=1, padx=5, pady=25, sticky=N + S + E + W)
        self.profundidadEntry.insert(0, '4')

        alarmaLbl = tk.Label(self.mainFrame, text="Alarma")
        alarmaLbl.grid(row=4, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.alarmaEntry = tk.Entry(self.mainFrame)
        self.alarmaEntry.grid(row=4, column=1, padx=5, pady=25, sticky=N + S + E + W)
        self.alarmaEntry.insert(0, '8')

        self.image = Image.open("assets/escenario.png")
        self.image = self.image.resize((300, 300))
        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = Canvas(self.mainFrame, width=300, height=300)
        canvas1.grid(row=1, column=2, rowspan=4, padx=20, pady=20, sticky=N + S + E + W)

        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        closeBtn = tk.Button(self.mainFrame, text="Cerrar", bg='#F57328', fg="white",
                                  command=self.closeScenario)
        closeBtn.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)

    '''
    Función closeScenario. Guarda los valores que le entramos de la configuración (anchura, altura, profundidad y alarma).
    Cambia el valor de la variable configured a True y cierra la ventana
    '''
    def closeScenario(self):
        self.configured = True
        self.callback(int(self.anchuraEntry.get()),
                int(self.alturaEntry.get()),
                int(self.profundidadEntry.get()),
                int(self.alarmaEntry.get())
        )
        self.newWindow.destroy()
        print('Escenario configurado!')



class Broker(Frame):

    def Open(self, master):
        self.newWindow = Toplevel(master)
        self.newWindow.title("Broker")
        self.newWindow.geometry("300x300")
        self.mainFrame = tk.Frame(self.newWindow)
        self.mainFrame.pack()
        self.mainFrame.rowconfigure(0, weight=1)
        self.mainFrame.rowconfigure(1, weight=1)
        self.mainFrame.rowconfigure(2, weight=1)
        self.mainFrame.rowconfigure(3, weight=1)

        self.brokerSelection = tk.IntVar()  # Variable de control para la selección del broker
        self.brokerSelection.set(0)  # Por defecto va estar puesto dronseetac

        self.dronseetacBtn = tk.Radiobutton(
            self.mainFrame,
            text="Broker en dronseetac",
            variable=self.brokerSelection,
            value=0,
            command=self.updateBrokerSelection)

        self.hivemqBtn = tk.Radiobutton(
            self.mainFrame,
            text="Broker en hivemq",
            variable=self.brokerSelection,
            value=1,
            command=self.updateBrokerSelection)

        self.closeSelectBtn = tk.Button(
            self.mainFrame,
            text="Cerrar y guardar selección",
            bg='#F57328', fg="white",
            command=self.closeSelection)

        self.dronseetacBtn.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + W)
        self.hivemqBtn.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + W)
        self.closeSelectBtn.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + W )



    def updateBrokerSelection(self):
        if self.brokerSelection.get() == 1:
            self.brokerSelection.set(1)

            # Si seleccionas el radiobutton del ordenador, deselecciona el radiobutton del móvil
        if self.brokerSelection.get() == 0:
            self.brokerSelection.set(0)


    def closeSelection(self):
        self.selectedBroker = 0
        if self.brokerSelection.get() == 1:
            self.selectedBroker= 1
        self.newWindow.destroy()





class CircoImagenes:

    def Open(self, master):

        self.scenario = Scene()
        self.drone = Tello()
        self.escenarioImagenes = escenarioImagenes()
        self.escenarioPanoramica = escenarioPanoramica()
        self.escenarioVideo = escenarioVideo()
        self.connectDrone = False
        self.brokerSelected = False

        myFont = font.Font(family='Arial', size=10, weight='bold')

        self.master = master
        self.newWindow = Toplevel(self.master)
        self.newWindow.title("circoImagenes")
        self.newWindow.geometry("800x600")
        self.newWindow.columnconfigure(0, weight=1)
        self.newWindow.columnconfigure(1, weight=1)
        self.newWindow.columnconfigure(2, weight=1)
        self.newWindow.columnconfigure(3, weight=1)
        self.newWindow.rowconfigure(0, weight=1)
        self.newWindow.rowconfigure(1, weight=1)
        self.newWindow.rowconfigure(2, weight=1)

        self.image = Image.open("assets/gallery3.png")
        self.image = self.image.resize((800, 600))
        res = ImageTk.PhotoImage(self.image)
        canvas = Canvas(self.newWindow, width=800, height=600)
        canvas.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        canvas.create_image(0, 0, image=res, anchor="nw")

        # Configurar button
        '''escenarioButton = Button(self.newWindow, text="Configura tu escenario antes de empezar!", height=1,
                                 bg='#367E18', fg='#FFE9A0', command=self.configureScenario)
        escenarioButton.place(x=270, y=250, anchor="nw")
        escenarioButton['font'] = myFont'''

        # elegir el broker
        brokerButton = Button(self.newWindow, text="Elige el broker", height=1, bg='#367E18',
                              fg='#FFE9A0',  command=self.selectBroker)
        brokerButton.place(x=100, y=550, anchor="nw")
        brokerButton['font'] = myFont


        # Conectar dron button
        connectButton = Button(self.newWindow, text="Conecta con el dron", height=1, bg='#367E18',
                               fg='#FFE9A0', command=self.connect)
        connectButton.place(x=230, y=550, anchor="nw")
        connectButton['font'] = myFont

        # Nivel bateria label
        self.batteryLbl = Label(self.newWindow, text="Nivel de bateria: ????")
        self.batteryLbl.place(x=400, y=550, anchor="nw")
        self.batteryLbl['font'] = myFont

        # Jugar button
        empezarButton = Button(self.newWindow, text="JUGAR", height=1, bg='#367E18',
                               fg='#FFE9A0', command=self.jugar)
        empezarButton.place(x=600, y=550, anchor="nw")
        empezarButton['font'] = myFont
        self.newWindow.mainloop()

    def configureScenario(self):
        self.scenario.Open(self.newWindow, self.guardar)

    def guardar(self, anchura, altura, profundidad, alarma):
        self.configuracion_escenario = [anchura, altura, profundidad, alarma]

    def selectBroker (self):
        self.brokerSelector = Broker()
        self.brokerSelector.Open(self.newWindow)
        self.brokerSelected = True

    def connect(self):
        if True:
            try:
                self.drone.connect()
                self.batteryLbl['text'] = "Nivel de batería: " + str(self.drone.get_battery())
                print('Conexión realizada correctamente!')
                print('Nivel de batería:', str(self.drone.get_battery()))
                self.connectDrone = True
            except Exception as e:
                messagebox.showerror("Error de conexión",
                                     "No se pudo conectar al dron. Por favor, inténtalo de nuevo.\nError: " + str(e),
                                     parent=self.master)
        else:
            messagebox.showwarning("Error", "Antes de nada debes configurar tu dron!", parent=self.master)

    def jugar(self):
        if True:
        #if self.scenario.configured:
        #if self.scenario.configured and self.connectDrone:
            myFont2 = font.Font(family='Arial', size=10, weight='bold')

            print('El juego ha comenzado')
            self.circusWindow = Toplevel(self.newWindow)
            self.circusWindow.title("Selecciona una actividad")
            self.circusWindow.geometry("800x600")
            self.circusWindow.columnconfigure(0, weight=1)
            self.circusWindow.columnconfigure(1, weight=1)
            self.circusWindow.columnconfigure(2, weight=1)
            self.circusWindow.columnconfigure(3, weight=1)
            self.circusWindow.rowconfigure(0, weight=1)
            self.circusWindow.rowconfigure(1, weight=1)

            self.image2 = Image.open("assets/circoImagenes.png")
            self.image2 = self.image2.resize((800, 520))
            self.bg2 = ImageTk.PhotoImage(self.image2)
            canvas2 = Canvas(self.circusWindow, width=800, height=520)
            canvas2.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
            canvas2.create_image(0, 0, image=self.bg2, anchor="nw")

            # Captura foto button
            fotoButton = Button(self.circusWindow, text="Foto", height=1, bg='#367E18',
                                   fg='#FFE9A0', command=self.foto)
            fotoButton.place(x=300, y=110, anchor="nw")
            fotoButton['font'] = myFont2

            # Captura panoramica button
            panoramicaButton = Button(self.circusWindow, text="Panoramica", height=1, bg='#367E18',
                                   fg='#FFE9A0', command=self.panoramica)
            panoramicaButton.place(x=350, y=110, anchor="nw")
            panoramicaButton['font'] = myFont2

            # Captura video button
            videoButton = Button(self.circusWindow, text="Video", height=1, bg='#367E18',
                                   fg='#FFE9A0', command=self.video)
            videoButton.place(x=450, y=110, anchor="nw")
            videoButton['font'] = myFont2

            self.circusWindow.mainloop()

        if not self.connectDrone and self.scenario.configured:
            messagebox.showwarning("Error", "Antes de empezar a jugar debes conectarte al dron!",
                                   parent=self.master)
        if not self.connectDrone and not self.scenario.configured:
            messagebox.showwarning("Error", "Antes de empezar debes configurar tu dron y conectarte al dron!",
                                   parent=self.master)

    def foto(self):
        if not self.brokerSelected:
            messagebox.showwarning("Error", "Debes seleccionar el broker",
                                   parent=self.master)
        else:
            self.escenarioImagenes.Open(self.circusWindow, self.brokerSelector.selectedBroker)

    def panoramica(self):
        if not self.brokerSelected:
            messagebox.showwarning("Error", "Debes seleccionar el broker",
                                   parent=self.master)
        else:
            self.escenarioPanoramica.Open(self.circusWindow, self.brokerSelector.selectedBroker)

    def video(self):
        self.escenarioVideo.Open(self.circusWindow, self.brokerSelector.selectedBroker)
