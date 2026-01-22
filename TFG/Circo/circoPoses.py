import time
from tkinter import *
import tkinter as tk

import requests
from tkinter import font, simpledialog
from PIL import Image, ImageTk
from tkvideo import tkvideo
from DetectorClass import DetectorClass
from FollowClass import FollowDetector
import BodyControlClass
from djitellopy import Tello
from PoseGeneratorDetectorClass import PoseGenerarorDetector

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
        self.anchuraEntry.insert(0,'4')

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
'''
class Circo(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.make_widgets()

    def make_widgets(self):
        # don't assume that self.parent is a root window.
        # instead, call `winfo_toplevel to get the root window
        self.winfo_toplevel().title("Circo de drones")
'''


class Camera(Frame):

    selectionCamera = False
    int_camera = 0

    def Open(self, master):
        self.newWindow = Toplevel(master)
        self.selectionCamera = False
        self.selectedCamera = 0
        self.selectedBroker = 0
        self.newWindow.title("Camera")
        self.newWindow.geometry("300x300")
        self.mainFrame = tk.Frame(self.newWindow)
        self.mainFrame.pack()
        self.mainFrame.rowconfigure(0, weight=1)
        self.mainFrame.rowconfigure(1, weight=1)
        self.mainFrame.rowconfigure(2, weight=1)
        self.mainFrame.rowconfigure(3, weight=1)
        self.mainFrame.rowconfigure(4, weight=1)
        self.mainFrame.rowconfigure(5, weight=1)
        '''self.mainFrame.rowconfigure(6, weight=1)
        self.mainFrame.rowconfigure(7, weight=1)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(2, weight=1)
        self.mainFrame.columnconfigure(3, weight=1)'''

        self.cameraSelection = tk.IntVar()  # Variable de control para la seleccion de la cámara
        self.cameraSelection.set(0)  # Por defecto va estar puesto el ordendador

        self.brokerSelection = tk.IntVar()  # Variable de control para la selección del broker
        self.brokerSelection.set(0)  # Por defecto va estar puesto dronseetac

        self.phoneBtn = tk.Radiobutton(
            self.mainFrame,
            text="Cámara del Móvil",
            variable=self.cameraSelection,
            value=1,
            command=self.updateCameraSelection)

        self.computerBtn = tk.Radiobutton(
            self.mainFrame,
            text="Cámara del Ordenador",
            variable=self.cameraSelection,
            value=0,
            command=self.updateCameraSelection)

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

        self.phoneBtn.grid(row=0, column=0, padx=5, pady=5, sticky=N + S  + W )
        self.computerBtn.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + W )
        self.closeSelectBtn.grid(row=4, column=0, padx=5, pady=5, sticky=N + S + W )

    def updateCameraSelection(self):
        # Si seleccionas el radiobutton del móvil, deselecciona el radiobutton del ordenador
        # y muestra las opciones para el broker
        if self.cameraSelection.get() == 1:
            self.cameraSelection.set(1)
            self.dronseetacBtn.grid(row=2, column=0,  padx=5, pady=5, sticky=N + S + W )
            self.hivemqBtn.grid(row=3, column=0,  padx=5, pady=5, sticky=N + S + W )


        # Si seleccionas el radiobutton del ordenador, deselecciona el radiobutton del móvil
        if self.cameraSelection.get() == 0:
            self.cameraSelection.set(0)
            self.dronseetacBtn.grid_forget()
            self.hivemqBtn.grid_forget()

    def updateBrokerSelection(self):
        if self.brokerSelection.get() == 1:
            self.brokerSelection.set(1)

            # Si seleccionas el radiobutton del ordenador, deselecciona el radiobutton del móvil
        if self.brokerSelection.get() == 0:
            self.brokerSelection.set(0)


    def closeSelection(self):
        self.selectedCamera = 0
        self.selectedBroker = 0
        if self.cameraSelection.get() == 1:
            self.selectedCamera = 1
            print('Has seleccionado usar la cámara del móvil!')
            if self.brokerSelection.get() == 1:
                self.selectedBroker= 1

        self.newWindow.destroy()
        self.selectionCamera = True
        print ('camara seleccionada: ', self.selectedCamera)
        print('broker seleccionado: ', self.selectedBroker)


'''class SelectSourceDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title):
        self.selection = None
        self.opcion = tk.StringVar()
        self.opcion.set ("laptopCamera")
        super().__init__(parent, title)



    def body(self, frame):

        tk.Radiobutton(frame, text="Laptop camera", variable=self.opcion,
                    value="laptopCamera").pack()
        tk.Radiobutton(frame, text="Mobile phone camera", variable=self.opcion,
                    value= "mobileCamera").pack()


        return frame

    def ok_pressed(self):
        self.selection = self.opcion.get()
        self.destroy()

    def cancel_pressed(self):
        self.destroy()

    def buttonbox(self):
        self.ok_button = tk.Button(self, text="OK", width=5, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = tk.Button(
            self, text="Cancel", width=5, command=self.cancel_pressed
        )
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())
'''
class CircoPoses:

    def Open (self, master):
        self.drone = Tello()
        self.master = master
        self.poseList = None
        self.photos = None

        self.configure()
        '''
        self.mixer.music.load('assets/circo.mp3')
        self.mixer.music.play(10)

        self.newWindow = Toplevel(self.master)

        self.newWindow.geometry("770x525")

        self.image = Image.open("assets/entrada.png")
        self.image = self.image.resize((770, 525), Image.ANTIALIAS)

        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = Canvas(self.newWindow, width=770, height=525)
        canvas1.pack(fill="both", expand=True)
        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        myFont = font.Font(family='Arial', size=18, weight='bold')
        drone = Tello()
        configuracion_escenario = [0,0,0,0]

        enterButton = Button(self.newWindow, text="El circo de las poses", height=1, bg='#367E18', fg='#FFE9A0', width=12,
                             command=self.configure)
        enterButton['font'] = myFont
        enterButton.place(x=300, y=300, anchor="nw")
        # enterButton_canvas = canvas1.create_window(770 / 2, 525 / 2 + 50, window=enterButton)

        # Execute tkinter
        self.newWindow.mainloop()
        '''


    def follow(self):
        followWindow = Toplevel(self.circusWindow)
        followWindow.title("Sígueme")
        followWindow.geometry("450x650")
        # Presentation mode
        BodyControlClass.main()
        # detector = FollowDetector()
        # frame = detector.buildFrame(newWindow)
        # frame.pack(fill="both", expand="yes", padx=10, pady=10)
        followWindow.mainloop()


    def fingers(self):

        fingerWindow = Toplevel(self.circusWindow)
        fingerWindow.title("Dedos")
        fingerWindow.geometry("200x650")
        self.imageSource = self.camera.selectedCamera
        self.broker = self.camera.selectedBroker
        detector = DetectorClass(self.drone, self.configuracion_escenario, self.imageSource, self.broker,self.poseList, self.photos)
        frame = detector.buildFrame(fingerWindow, 'fingers')
        frame.pack(fill="both", expand="yes")
        fingerWindow.mainloop()


    def pose(self):
        poseWindow = Toplevel(self.circusWindow)
        poseWindow.title("Pose")
        poseWindow.geometry("200x700")
        self.imageSource = self.camera.selectedCamera
        self.broker = self.camera.selectedBroker
        detector = DetectorClass(self.drone, self.configuracion_escenario,self.imageSource,self.broker,self.poseList, self.photos)
        frame = detector.buildFrame(poseWindow, 'pose')
        frame.pack(fill="both", expand="yes")
        poseWindow.mainloop()


    def faces(self):


        newWindow = Toplevel(self.circusWindow)
        newWindow.title("Pose")
        newWindow.geometry("450x650")
        self.imageSource = self.camera.selectedCamera
        self.broker = self.camera.selectedBroker
        detector = DetectorClass(self.drone, self.configuracion_escenario,self.imageSource,self.broker, None, None)
        frame = detector.buildFrame(newWindow, 'face')
        frame.pack(fill="both", expand="yes", padx=10, pady=10)
        newWindow.mainloop()

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

        self.image2 = Image.open("assets/circoPoses.png")
        self.image2 = self.image2.resize((800, 520), Image.ANTIALIAS)
        self.bg2 = ImageTk.PhotoImage(self.image2)
        canvas2 = Canvas(self.circusWindow, width=800, height=520)
        canvas2.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        canvas2.create_image(0, 0, image=self.bg2, anchor="nw")
        myFont4 = font.Font(family='Arial', size=12, weight='bold')
        followmeButton = Button(self.circusWindow, text="Sígueme", height=1, bg='#367E18', fg='#FFE9A0', width=8, command=self.follow)
        followmeButton.place( x=50, y=480, anchor="nw")
        followmeButton['font'] = myFont4
        poseButton = Button(self.circusWindow, text="Poses", height=1, bg='#367E18', fg='#FFE9A0', width=8, command=self.pose)
        poseButton.place( x=450, y=480, anchor="nw")
        poseButton['font'] = myFont4
        fingersButton = Button(self.circusWindow, text="Dedos", height=1, bg='#367E18', fg='#FFE9A0', width=8,
                               command=self.fingers)
        fingersButton.place( x=300, y=480, anchor="nw")
        fingersButton['font'] = myFont4

        facesButton = Button(self.circusWindow, text="Caras", height=1, bg='#367E18', fg='#FFE9A0', width=8, command=self.faces)
        facesButton.place( x=650, y=480, anchor="nw")
        facesButton['font'] = myFont4

        byeButton = Button(self.circusWindow, text="Salir", height=1, bg='#FFE9A0', fg='#367E18', command=self.bye)
        byeButton.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        byeButton['font'] = myFont4
        self.circusWindow.mainloop()

    def guardar (self, anchura, altura, profundidad, alarma):
        self.configuracion_escenario = [anchura, altura, profundidad, alarma]

    def configureScenario (self):
        scenario = Scene()
        scenario.Open (self.configurationWindow, self.guardar)


    def selectImageSource (self):
        #dialog = SelectSourceDialog(title="Select Image Source", parent=self.configurationWindow)
        self.camera = Camera()
        self.camera.Open(self.configurationWindow)



    def storePoses (self, poseList, photos):
        print ('ya tengo las poses ')
        self.photos = photos
        self.poseList = poseList
        self.createWindow.destroy()

    def createPoses (self):
        poseGeneratorDetector = PoseGenerarorDetector()
        self.createWindow = Toplevel(self.configurationWindow)
        #self.createWindow.geometry('480x480')
        self.createWindow.geometry('480x600')
        self.imageSource = self.camera.selectedCamera
        self.broker = self.camera.selectedBroker
        print ('voy a pasar ', self.imageSource, self.broker)
        frame = poseGeneratorDetector.BuildFrame(self.createWindow, self.imageSource, self.broker,self.storePoses)
        frame.pack(fill=BOTH, expand=True)
        self.createWindow.mainloop()

    def connect(self):
        print ('aaaaaaa')
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

        escenarioButton = Button(self.configurationWindow, text="Configura escenario", height=1, bg='#367E18', fg='#FFE9A0', command=self.configureScenario)
        escenarioButton.place( x=30, y=450, anchor="nw")
        escenarioButton['font'] = myFont2

        fuenteButton = Button(self.configurationWindow, text="Elige fuente de la imagen", height=1, bg='#367E18',
                                 fg='#FFE9A0', command=self.selectImageSource)
        fuenteButton.place(x=180, y=450, anchor="nw")
        fuenteButton['font'] = myFont2

        definePosesButton = Button(self.configurationWindow, text="Crea tus poses", height=1, bg='#367E18',
                                 fg='#FFE9A0', command=self.createPoses)
        definePosesButton.place(x=360, y=450, anchor="nw")
        definePosesButton['font'] = myFont2

        connectButton = Button(self.configurationWindow, text="Conecta con el dron", height=1, bg='#367E18', fg='#FFE9A0', command=self.connect)
        connectButton.place( x=480, y=450, anchor="nw")
        connectButton['font'] = myFont2

        self.batteryLbl = Label (self.configurationWindow, text= "Nivel de bateria: ????")
        self.batteryLbl.place( x=640, y=450, anchor="nw")
        self.batteryLbl['font'] = myFont2


        empezarButton = Button(self.configurationWindow, text="Empezar expectáculo", height=1, width = 75, bg='#367E18', fg='#FFE9A0', command=self.empezar)
        empezarButton.place( x=100, y=490, anchor="nw")
        empezarButton['font'] = myFont2

        self.configurationWindow.mainloop()
