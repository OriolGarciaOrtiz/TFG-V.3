import random
import threading
import time
import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
from djitellopy import Tello

from fingerDetector import FingerDetector
from poseDetector import PoseDetector
from faceDetector import FaceDetector
from PIL import ImageTk
from PIL import Image as Img
from tkinter import messagebox
from VideoStreamer import VideoStreamer

class MovementGenerator:
    '''Esta clase es para controlar que el dron no se salga de los límites establecidos.
    Asumimos que volará en un recinto de dimensiones indicadas por los tres parametros del constructor.
    Incinialmente estará en el centro del rectangulo que constituye el suelo del recinto.
    Al despegar se quedará a 1 metro de altura.
    '''
    def __init__(self, anchura, altura, profundidad):
        self.up_limit = altura -1   # al despegar se queda a 1 metro de altura. No puede ir más arriba del limite superior
        self.down_limit =1 # no puede bajar mas de un metro de donde está al despegar
        self.left_limit = -anchura//2
        self.right_limit = anchura//2
        self.forward_limit = profundidad//2
        self.back_limit = -profundidad//2
        # las siguientes variables nos indica cuánto se ha desplazado respecto al punto inicial
        self.up_down = 0
        self.left_right = 0
        self.forward_back = 0
        #solo le dejaremos hacer flip una vez
        self.fliped = True
    def GetPosition (self):
        # para saber cuanto se ha desplazado en el plano. Se necesitará para hacerle regresar al punto inicial
        return self.left_right, self.forward_back
    def Reset (self):
        self.up_down = 0
        self.left_right = 0
        self.forward_back = 0
        self.fliped = False
    def forward (self):
        self.forward_back = self.forward_back + 1
    def back(self):
        self.forward_back = self.forward_back - 1
    def left(self):
        self.left_right = self.left_right - 1
    def right(self):
        self.left_right = self.left_right + 1

    def up(self):
        self.up_down = self.up_down + 1
    def down(self):
        self.up_down = self.up_down - 1

    def NewMovement (self, battery_level):
        # genera un nuevo desplazamiento aleatorio, pero siempre que no nos salgamos de los límites
        # Si sale un flip solo lo hará si no lo ha hecho aun (para no gastar mucha bateria) y si
        # el nivel de bateria es superior al 50%

        success = False
        while not success:
            n = random.randint(0, 6)

            if n == 0: #forward
                if  self.forward_back < self.forward_limit:
                    success = True
            if n == 1:  # back
                if self.forward_back > self.back_limit:
                    success = True
            if n == 2:  # left
                if self.left_right > self.left_limit:
                    success = True
            if n == 3:  # right
                if self.left_right < self.right_limit:
                    success = True

            if n == 4:  # up
                if self.up_down < self.up_limit:
                    success = True
            if n == 5:  # down
                if self.up_down > self.down_limit:
                    success = True
            if n == 6:  # flip
                if not self.fliped and battery_level > 50:
                    self.fliped = True
                    success = True

        return n

'''
class Scene:
    def Open(self, master, callback):
        # abre un formulario para que el usuario introduzca los datos del escenario
        # cuando los haya introducido se llamará a la función callback que se recibe
        # para que el que llama haga lo que tenga que hacer con los datos introducidos
        # por el usuario
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
        self.anchuraEntry.insert (0,'4')

        alturaLbl = tk.Label(self.mainFrame, text="Altura")
        alturaLbl.grid(row=2, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.alturaEntry = tk.Entry(self.mainFrame)
        self.alturaEntry.grid(row=2, column=1, padx=5, pady=25, sticky=N + S + E + W)
        self.alturaEntry.insert (0,'4')

        profundidadLbl = tk.Label(self.mainFrame, text="Profundidad")
        profundidadLbl.grid(row=3, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.profundidadEntry = tk.Entry(self.mainFrame)
        self.profundidadEntry.grid(row=3, column=1, padx=5, pady=25, sticky=N + S + E + W)
        self.profundidadEntry.insert (0,'4')
        # alarma es el tiempo que tiene el jugador para acertar la pose. A mitad de ese tiempo
        # la indicación se pondrá en rojo.
        alarmaLbl = tk.Label(self.mainFrame, text="Alarma")
        alarmaLbl.grid(row=4, column=0, padx=5, pady=25, sticky=N + S + E + W)
        self.alarmaEntry = tk.Entry(self.mainFrame)
        self.alarmaEntry.insert(0, '8')
        self.alarmaEntry.grid(row=4, column=1, padx=5, pady=25, sticky=N + S + E + W)



        self.image = Image.open("assets/escenario.png")
        self.image = self.image.resize((300, 300), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas = Canvas(self.mainFrame, width=300, height=300)
        canvas.grid(row=1, column=2, rowspan=4, padx=20, pady=20, sticky=N + S + E + W)

        canvas.create_image(0, 0, image=self.bg, anchor="nw")

        closeBtn = tk.Button(self.mainFrame, text="Cerrar", bg='#F57328', fg="white",
                                  command=self.closeScenario)
        closeBtn.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)

    def closeScenario (self):
        #enviamos los datos a la función que nos hayan indicado
        self.callback(int(self.anchuraEntry.get()), \
                int(self.alturaEntry.get()), \
                int(self.profundidadEntry.get()), \
                int(self.alarmaEntry.get())
        )
        self.newWindow.destroy()
'''
class DetectorClass:
    def __init__(self, drone, escenario, imageSource, broker, poseList, photos):
        self.imageSource = imageSource
        self.broker = broker
        self.poseList = poseList
        self.photos = photos
        self.direction = None
        self.returning = None
        self.RTL = False
        self.connected = False
        self.armed = None
        self.taken_off = None
        self.at_home = None

        self.takeoff_state = None

        #guardamos el dron y los datos del escenario
        self.drone = drone

        self.anchura = escenario[0]
        self.altura = escenario[1]
        self.profundidad = escenario[2]
        self.alarma = escenario[3]


        self.atras = "EXT mled g 000000000000000000000000000bb000000bb000000000000000000000000000"
        self.adelante = "EXT mled g 0000000000bbbb000bbbbbb00bbbbbb00bbbbbb00bbbbbb000bbbb0000000000"
        self.arriba = "EXT mled g 000bb00000bbbb000bbbbbb0bb0bb0bbb00bb00b000bb000000bb000000bb000"
        self.abajo = "EXT mled g 000bb000000bb000000bb000b00bb00bbb0bb0bb0bbbbbb000bbbb00000bb000"
        self.izquierda = "EXT mled g 000bb00000bb00000bb00000bbbbbbbbbbbbbbbb0bb0000000bb0000000bb000"
        self.derecha = "EXT mled g 000bb0000000bb0000000bb0bbbbbbbbbbbbbbbb00000bb00000bb00000bb000"
        self.flip = "EXT mled g 00bbbb000b000000b00bbb00b00b00b00b00b0b000b000b0000bbb0000000000"
        self.aterriza = "EXT mled g 0000000000000000000000000bbbbbb000000000000000000000000000000000"
        self.corazon = "EXT mled g 000000000rr00rr0rrrrrrrrrrrrrrrr0rrrrrr000rrrr00000rr00000000000"
        self.corazon_roto = "EXT mled g 000000000rr000r0rrrr0rrrrrrr0rrr0rrr0rr000r0rr00000rr00000000000"
        self.ole = "EXT mled l r 2.5 OLE...."
        self.preparado = "EXT mled g 00rrr0000r000r000r0000r000000r000000r0000000r000000000000000r000"

        self.level = 'easy'
        self.videoStreamer = VideoStreamer(self.imageSource, self.broker)

    def easy (self):

        self.fatherFrame.geometry("200x650")

        self.level = 'easy'
        self.bottomFrame['text'] = 'Fácil'
        self.easyBtn['bg'] ='#367E18'
        self.easyBtn['fg'] = 'white'
        self.difficultBtn['bg'] = '#FFE9A0'
        self.difficultBtn['fg'] = 'black'
        if self.mode == 'fingers':
            self.image = Image.open("assets/dedos_faciles_v.png")
        elif self.mode == 'pose':
            self.image = Image.open("assets/poses_faciles_v.png")
        else:
            self.image = Image.open("assets/caras_faciles_v.png")

        self.image = self.image.resize((160, 450), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        if self.canvasFrame != None:
            self.canvasFrame.pack_forget()

        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")
        self.canvas.pack(fill="both", expand=True)

    def resizeImage(self, img, newWidth, newHeight):
        oldWidth = img.width()
        oldHeight = img.height()
        newPhotoImage = PhotoImage(width=newWidth, height=newHeight)
        for x in range(newWidth):
            for y in range(newHeight):
                xOld = int(x * oldWidth / newWidth)
                yOld = int(y * oldHeight / newHeight)
                rgb = '#%02x%02x%02x' % img.get(xOld, yOld)
                newPhotoImage.put(rgb, (x, y))
        return newPhotoImage
    def difficult(self):
        if self.poseList == None:
            messagebox.showwarning("Error", "No has definido tus poses", parent=self.master)
        else:
            self.level = 'difficult'
            self.bottomFrame['text'] = 'Tus poses'
            self.easyBtn['bg'] = '#FFE9A0'
            self.easyBtn['fg'] = 'black'
            self.difficultBtn['bg'] = '#367E18'
            self.difficultBtn['fg'] = 'white'

            if self.mode == 'fingers':
                self.image = Image.open("assets/dedos_faciles_v.png")
            elif self.mode == 'pose':
                self.image = Image.open("assets/poses_dificiles_v.png")
            else:
                self.image = Image.open("assets/caras_faciles_v.png")

            self.image = self.image.resize((160, 450), Image.ANTIALIAS)
            self.bg = ImageTk.PhotoImage(self.image)

            self.canvas.create_image(0, 0, image=self.bg, anchor="nw")




            self.canvas.pack_forget()
            #self.fatherFrame.geometry("150x650")
            self.fatherFrame.geometry("360x650")


            self.canvasFrame = Frame (self.bottomFrame)
            self.canvasFrame.columnconfigure(0, weight=1)
            self.canvasFrame.columnconfigure(1, weight=1)

            self.canvasFrame.rowconfigure(0, weight=1)
            self.canvasFrame.rowconfigure(1, weight=1)
            self.canvasFrame.rowconfigure(2, weight=1)

            self.canvasFrame.rowconfigure(3, weight=1)
            self.canvasFrame.rowconfigure(4, weight=1)
            self.canvasFrame.rowconfigure(5, weight=1)

            if self.imageSource == 0:
                sizeW = 134
                sizeH = 100
            else:
                sizeW = 80
                sizeH = 100


            self.images = []
            for image in self.photos:
                img = cv2.resize(image, (sizeW, sizeH))
                self.images.append(ImageTk.PhotoImage(image=Img.fromarray(img)))

            self.imageAdelante = Image.open("assets/adelante.png")
            self.imageAdelante = self.imageAdelante.resize((100, 40), Image.ANTIALIAS)
            self.bgAdelante = ImageTk.PhotoImage(self.imageAdelante)
            self.canvas1F = Canvas(self.canvasFrame, width=100, height=40)
            self.canvas1F.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
            self.canvas1F.create_image(0, 0, image=self.bgAdelante, anchor=tk.NW)

            self.canvas1 = Canvas(self.canvasFrame, width=sizeW, height=sizeH, bg='white')
            self.canvas1.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
            self.canvas1.create_image(0, 0, image=self.images[0], anchor=tk.NW)


            self.imageAtras = Image.open("assets/atras.png")
            self.imageAtras = self.imageAtras.resize((100, 40), Image.ANTIALIAS)
            self.bgAtras = ImageTk.PhotoImage(self.imageAtras)
            self.canvas2F = Canvas(self.canvasFrame, width=100, height=40)
            self.canvas2F.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
            self.canvas2F.create_image(0, 0, image=self.bgAtras, anchor=tk.NW)

            self.canvas2 = Canvas(self.canvasFrame, width=sizeW, height=sizeH, bg='white')
            self.canvas2.grid(row=1, column=1,  padx=5, pady=5, sticky=N + S + E + W)
            self.canvas2.create_image(0, 0,  image=self.images[1], anchor=tk.NW)

            self.imageIzquierda = Image.open("assets/izquierda.png")
            self.imageIzquierda = self.imageIzquierda.resize((100, 40), Image.ANTIALIAS)
            self.bgIzquierda = ImageTk.PhotoImage(self.imageIzquierda)
            self.canvas3F = Canvas(self.canvasFrame, width=100, height=40)
            self.canvas3F.grid(row=2, column=0, padx=5, pady=(5,0), sticky=N + S + E + W)
            self.canvas3F.create_image(0, 0, image=self.bgIzquierda, anchor=tk.NW)

            self.canvas3 = Canvas(self.canvasFrame, width=sizeW, height=sizeH, bg='white')
            self.canvas3.grid(row=3, column=0,  padx=5, pady=(0,5), sticky=N + S + E + W)
            self.canvas3.create_image(0, 0,  image=self.images[2], anchor=tk.NW)

            self.imageDerecha = Image.open("assets/derecha.png")
            self.imageDerecha = self.imageDerecha.resize((100, 40), Image.ANTIALIAS)
            self.bgDerecha = ImageTk.PhotoImage(self.imageDerecha)
            self.canvas4F = Canvas(self.canvasFrame, width=100, height=40)
            self.canvas4F.grid(row=2, column=1, padx=5, pady=(5,0) , sticky=N + S + E + W)
            self.canvas4F.create_image(0, 0, image=self.bgDerecha, anchor=tk.NW)

            self.canvas4 = Canvas(self.canvasFrame, width=sizeW, height=sizeH, bg='white')
            self.canvas4.grid(row=3, column=1,  padx=5, pady=(0,5), sticky=N + S + E + W)
            self.canvas4.create_image(0, 0, image=self.images[3], anchor=tk.NW)

            self.imageArriba = Image.open("assets/arriba.png")
            self.imageArriba = self.imageArriba.resize((100, 40), Image.ANTIALIAS)
            self.bgArriba = ImageTk.PhotoImage(self.imageArriba)
            self.canvas5F = Canvas(self.canvasFrame, width=100, height=40)
            self.canvas5F.grid(row=4, column=0, padx=5, pady=(5, 0), sticky=N + S + E + W)
            self.canvas5F.create_image(0, 0, image=self.bgArriba, anchor=tk.NW)

            self.canvas5 = Canvas(self.canvasFrame, width=sizeW, height=sizeH, bg='white')
            self.canvas5.grid(row=5, column=0, padx=5, pady=(0,5), sticky=N + S + E + W)
            self.canvas5.create_image(0, 0,  image=self.images[4], anchor=tk.NW)

            self.imageAbajo = Image.open("assets/abajo.png")
            self.imageAbajo = self.imageAbajo.resize((100, 40), Image.ANTIALIAS)
            self.bgAbajo = ImageTk.PhotoImage(self.imageAbajo)
            self.canvas6F = Canvas(self.canvasFrame, width=100, height=40)
            self.canvas6F.grid(row=4, column=1, padx=5, pady=(5, 0), sticky=N + S + E + W)
            self.canvas6F.create_image(0, 0, image=self.bgAbajo, anchor=tk.NW)

            self.canvas6 = Canvas(self.canvasFrame, width=sizeW, height=sizeH, bg='white')
            self.canvas6.grid(row=5, column=1, padx=5, pady=(0,5), sticky=N + S + E + W)
            self.canvas6.create_image(0, 0,  image=self.images[5], anchor=tk.NW)

            self.canvasFrame.pack(fill="both", expand=True)






    def buildFrame(self, fatherFrame, mode):
        # mode can be: fingers, face or pose
        self.fatherFrame = fatherFrame
        self.mode = mode

        #self.cap = cv2.VideoCapture(0)

        if self.mode == 'fingers':
            self.detector = FingerDetector(self.poseList)
        elif self.mode == 'pose':
            self.detector = PoseDetector(self.poseList)
        else:
            self.detector = FaceDetector()

        self.master = tk.Frame(self.fatherFrame)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        self.topFrame = tk.LabelFrame(self.master, text="Control")
        self.topFrame.columnconfigure(0, weight=1)
        self.topFrame.columnconfigure(1, weight=1)
        self.topFrame.rowconfigure(0, weight=1)
        self.topFrame.rowconfigure(1, weight=1)
        self.topFrame.rowconfigure(2, weight=1)


        # state can be: initial, practising, flying, closed
        self.state = 'initial'
        self.easyBtn = tk.Button(self.topFrame, text="Fácil", bg='#367E18', fg="white",
                                  command=self.easy)
        self.easyBtn.grid(row=0, column=0, padx=5, pady=2, sticky=N + S + E + W)
        self.difficultBtn = tk.Button(self.topFrame, text="Tus poses", bg='#FFE9A0', fg="black",
                                     command=self.difficult)
        self.difficultBtn.grid(row=0, column=1, padx=5, pady=2, sticky=N + S + E + W)

        self.practice = tk.Button(self.topFrame, text="Practica", bg='#F57328', fg="white",
                                  command=self.practice)
        self.practice.grid(row=1, column=0, padx=5, pady=2, sticky=N + S + E + W)
        self.closeButton = tk.Button(self.topFrame, text="Salir", bg='#FFE9A0', fg="black",
                                     command=self.close)
        self.closeButton.grid(row=1, column=1, padx=5, pady=2, sticky=N + S + E + W)


        # frame to be shown when practise is finish and user wants to fly
        self.buttonFrame = tk.Frame(self.topFrame)
        self.buttonFrame.rowconfigure(0, weight=1)
        self.buttonFrame.rowconfigure(1, weight=1)
        self.buttonFrame.columnconfigure(0, weight=1)
        self.buttonFrame.columnconfigure(1, weight=1)



        self.connectButton = tk.Button(self.buttonFrame, text= 'Connect', bg='#CC3636', fg="white", command=self.connect)
        self.connectButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.takeOffButton = tk.Button(self.buttonFrame, text="Take Off", bg='#CC3636', fg="white",
                                       command=self.takeOff)
        self.takeOffButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        # button to be shown when flying
        self.landButton = tk.Button(self.buttonFrame, text="Aterriza", bg='#CC3636', fg="white",
                                    command=self.returnHome)

        # button to be shown when the dron is back home
        self.closeButton2 = tk.Button(self.buttonFrame, text="Salir", bg='#FFE9A0', fg="black", command=self.close)
        self.closeButton2.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.topFrame.grid(row=1, column=0, padx=5, pady=0, sticky=N + S + E + W)

        # by defaulf, easy mode is selected
        self.bottomFrame = tk.LabelFrame(self.master, text="Facil")


        if self.mode == 'fingers':
            self.image = Image.open("assets/dedos_faciles_v.png")
        elif self.mode == 'pose':
            self.image = Image.open("assets/poses_faciles_v.png")
        else:
            self.image = Image.open("assets/caras_faciles_v.png")

        self.image = self.image.resize((160, 450), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas = Canvas(self.bottomFrame, width=160, height=450)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

        self.bottomFrame.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.canvasFrame = None

        return self.master

    #esta es la función que le pasaremos cuando configuremos el escenario para guardarnos los datos
    def guardar (self, anchura, altura, profundidad, alarma):
        self.anchura = anchura
        self.altura = altura
        self.profundidad = profundidad
        self.alarma = alarma
    '''
    def configureScenario (self):
        scenario = Scene()
        scenario.Open (self.master, self.guardar)
    '''
    def connect(self):
        self.closeButton2.grid_forget()
        self.connected = True
        self.drone.send_control_command(self.preparado)
        # muestro el nivel de bateria
        self.connectButton['text'] = str(self.drone.get_battery())
        self.connectButton['bg'] = '#367E18'



    def takeOff(self):
        # do not allow taking off if not armed
        if self.connected:
            self.drone.takeoff()
            time.sleep(2)
            self.taken_off = True
            self.takeOffButton['text'] = 'flying'
            self.takeOffButton['bg'] = '#367E18'
            self.state = 'flying'
            # this thread will start taking images and detecting patterns to guide the drone
            x = threading.Thread(target=self.flying)
            x.start()
            self.landButton.grid(row=1, column=0, padx=5, columnspan=3, pady=5, sticky=N + S + E + W)
            #self.action()
        else:
            messagebox.showwarning("Error", "Antes de despegar debes conectarte al dron", parent=self.master)

    def close(self):
        # this will stop the video stream thread
        self.state = 'closed'
        self.videoStreamer.disconnect()
        #self.cap.release()
        self.fatherFrame.destroy()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def practice(self):
        if self.state == 'initial':
            # start practising
            self.practice['bg'] = '#367E18'
            self.practice['text'] = 'Quiero volar'
            self.state = 'practising'
            # startvideo stream to practice
            x = threading.Thread(target=self.practising)
            x.start()

        elif self.state == 'practising':
            # stop the video stream thread for practice
            self.state = 'closed'

            self.practice.grid_forget()

            # show buttons for connect, arm and takeOff
            self.buttonFrame.grid(row=2, column=0, columnspan=2, padx=5, pady=0, sticky=N + S + E + W)

            self.closeButton.grid_forget()

    def __setDirection(self, code):
        if code == 1:
            return 'Adelante'
        elif code == 2:
            return 'Atras'
        elif code == 3:
            return 'Izquierda'
        elif code == 4:
            return 'Derecha'
        elif code == 5:
            return 'Arriba'
        elif code == 6:
            return 'Abajo'
        elif code == 7:
            return 'Flip'
        else:
            return ''

    def practising(self):
        # when the user changes the pattern (new face, new pose or new fingers) the system
        # waits some time (ignore 8 video frames) for the user to stabilize the new pattern
        # we need the following variables to control this
        prevCode = -1
        cont = 0

        while self.state == 'practising':
            '''success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue'''
            success,image = self.videoStreamer.getFrame()
            if success:

                code, img = self.detector.detect(image, self.level)
                print ('tengo')
                if (code != ''):
                    print ('estoy detectando ', code)
                #img = cv2.resize(img, (800, 600))
                #img = cv2.flip(img, 1)

                # if user changed the pattern we will ignore the next 8 video frames
                if (code != prevCode):
                    cont = 1
                    prevCode = code
                else:
                    cont = cont - 1
                    if cont < 0:
                        # the first 8 video frames of the new pattern (to be ignored) are done
                        # we can start showing new results
                        direction = self.__setDirection(code)
                        cv2.putText(
                            img,
                            direction,
                            (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2,
                            (0, 0, 255),
                            4,
                        )

                cv2.imshow('video', img)
                cv2.waitKey(1)
        cv2.destroyWindow('video')
        cv2.waitKey(1)


    def avisar (self):
        #a la mitad del tiempo establecido se activa esta alarma que pone en rojo la indicación
        # pero si es la segunda vez que se dispara entonces ya no hace nada. Simplemente toma nota de
        # que es el segundo aviso
        self.aviso = self.aviso +1
        if self.aviso == 1:
            comando_rojo = self.comando.replace("b", "r")
            self.drone.send_control_command(comando_rojo)
            start_time = threading.Timer(self.alarma//2, self.avisar)
            start_time.start()



    def flying(self):

        self.movementGenerator = MovementGenerator(self.anchura, self.altura, self.profundidad)
        comandos = [self.adelante, self.atras, self.izquierda, self.derecha, self.arriba, self.abajo, self.flip]

        # we need to know if the dron is returning to lunch to show an apropriate message
        self.returning = False

        self.direction = ''
        # numero de ordenes que debe superar el jugador para triunfar
        numberOfOperations = 8
        next = 0

        while next < numberOfOperations:
                #genero la siguiente orden
                n = self.movementGenerator.NewMovement(self.drone.get_battery())
                self.comando = comandos[n]
                time.sleep(3)
                print ('comando ', self.comando)
                self.drone.send_control_command(self.comando)
                cont = 0
                detected = False
                self.aviso = 0
                # pongo en marcha el timer para avisar cuando haya pasado la mitad del tiempo de alarma
                start_time = threading.Timer(self.alarma//2, self.avisar)
                start_time.start()
                # tomo imágenes mientras no se acierte y no se acabe el tiempo de alarma
                while not detected and self.aviso != 2:
                    ''' success, image = self.cap.read()
                    if not success:
                        print("Ignoring empty camera frame.")
                        # If loading a video, use 'break' instead of 'continue'.
                        continue'''
                    success, image = self.videoStreamer.getFrame()
                    if success:
                        code, img = self.detector.detect(image, self.level)
                        #img = cv2.resize(img, (800, 600))
                        #img = cv2.flip(img, 1)
                        self.direction = self.__setDirection(code)
                        cv2.putText(
                            img,
                            self.direction,
                            (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2,
                            (0, 0, 255),
                            4,
                        )
                        cv2.imshow('video', img)
                        cv2.waitKey(1)
                        if code == n+1:
                            cont = cont +1
                            if cont == 4:
                                # tenemos 8 frames con la pose correcta. El jugador ha acertado
                                detected = True
                                print ('detectado ', code)
                        else:
                            #ha cambiado de pose
                            cont = 0


                if self.aviso == 2:
                    # se acabo el tiempo
                    self.drone.send_control_command(self.corazon_roto)
                    next = numberOfOperations +1

                else:
                    # acerto
                    start_time.cancel()
                    self.drone.send_control_command(self.corazon)
                    time.sleep(2)
                    # muevo el dron y tomo nota de su movimiento
                    if code == 1: # adelante
                        self.drone.go_xyz_speed(50, 0, 0, 100)
                        self.movementGenerator.forward()
                    elif code == 2:  # atras
                        self.drone.go_xyz_speed(-50, 0, 0, 100)
                        self.movementGenerator.back()
                    elif code == 3:  # izquierda
                        self.drone.go_xyz_speed(0, -50, 0, 100)
                        self.movementGenerator.left()
                    elif code == 4:  # derecha
                        self.drone.go_xyz_speed(0, 50, 0, 100)
                        self.movementGenerator.right()
                    elif code == 5:  # arriba
                        self.drone.go_xyz_speed(0, 0, 50, 100)
                        self.movementGenerator.up()
                    elif code == 6:  # abajo
                        self.drone.go_xyz_speed(0, 0, -50, 100)
                        self.movementGenerator.down()
                    elif code == 7:  # flip
                        self.drone.send_control_command("flip l")
                    self.connectButton['text'] = str(self.drone.get_battery())
                    next = next + 1

        if (next == numberOfOperations):
            self.drone.send_control_command(self.ole)
        # miro el desplazamiento que ha tenido en el plano para hacerle volver al punto inicial y aterrizar
        left_right,forward_back = self.movementGenerator.GetPosition()
        print ('fin ', left_right,forward_back)
        if (left_right < 0):
            for n in range (abs(left_right)):
                self.drone.go_xyz_speed(0, 50, 0, 100)
                time.sleep(2)
        else:
            for n in range(abs(left_right)):
                self.drone.go_xyz_speed(0, -50, 0, 100)
                time.sleep(2)
        if (forward_back < 0):
            for n in range(abs(forward_back)):
                self.drone.go_xyz_speed(50, 0, 0, 100)
                time.sleep(2)
        else:
            for n in range(abs(forward_back)):
                self.drone.go_xyz_speed(-50, 0, 0, 100)
                time.sleep(2)

        self.drone.land()
        messagebox.showwarning("Success", "Ya estamos en casa", parent=self.master)
        self.landButton.grid_forget()
        self.closeButton2.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
        self.movementGenerator.Reset()

        # return to the initial situation
        self.connectButton['bg'] = '#CC3636'
        self.connectButton['text'] = 'Connect'
        self.takeOffButton['bg'] = '#CC3636'
        self.takeOffButton['text'] = 'TakeOff'
        self.connected = False
        self.taken_off = False
        self.state = 'initial'
        cv2.destroyWindow('video')
        cv2.waitKey(1)


    def returnHome(self):

        self.state= 'initial'
        self.returning = True
        self.direction = 'Aterrizando'
        self.drone.land()
        self.at_home = True
        self.connected = False
        self.taken_off = False
        messagebox.showwarning("Success", "Ya estamos en casa", parent=self.master)
        self.landButton.grid_forget()
        self.closeButton2.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
        self.movementGenerator.Reset()
        # return to the initial situation
        self.connectButton['bg'] = '#CC3636'
        self.connectButton['text'] = 'Connect'
        self.takeOffButton['bg'] = '#CC3636'
        self.takeOffButton['text'] = 'TakeOff'
        self.state = 'initial'


