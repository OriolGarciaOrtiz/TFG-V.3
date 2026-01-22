import random
import threading
import time
import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import tellopy

from fingerDetector import FingerDetector
from poseDetector import PoseDetector
from faceDetector import FaceDetector
from PIL import ImageTk
from tkinter import messagebox

class MovementGenerator:
    def __init__(self, up_limit,down_limit,right_limit, left_limit,forward_limit,back_limit):
        self.up_limit = up_limit
        self.down_limit =down_limit
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.forward_limit = forward_limit
        self.back_limit = back_limit

        self.up_down = 0
        self.left_right = 0
        self.forward_back = 0

    def NewMovement (self):
        success = False
        while not success:
            n = random.randint(0, 3)
            print ('next ', n)


            if n == 0: #forward
                if  self.forward_back < self.forward_limit:
                    self.forward_back = self.forward_back+1
                    success = True
            if n == 1:  # back
                if self.forward_back > self.back_limit:
                    self.forward_back = self.forward_back - 1
                    success = True
            if n == 2:  # right
                if self.left_right < self.right_limit:
                    self.left_right = self.left_right + 1
                    success = True
            if n == 3:  # left
                if self.left_right > self.left_limit:
                    self.left_right = self.left_right + 1
                    success = True
        return n




class DetectorClass:
    def __init__(self):
        self.direction = None
        self.returning = None
        self.RTL = False
        self.connected = False
        self.armed = None
        self.taken_off = None
        self.at_home = None

        self.takeoff_state = None
        self.drone = tellopy.Tello()
        self.battery = None

        self.atras = "EXT mled g 000000000000000000000000000bb000000bb000000000000000000000000000"
        self.adelante = "EXT mled g 0000000000bbbb000bbbbbb00bbbbbb00bbbbbb00bbbbbb000bbbb0000000000"
        self.arriba = "EXT mled g 000bb00000bbbb000bbbbbb0bb0bb0bbb00bb00b000bb000000bb000000bb000"
        self.abajo = "EXT mled g 000bb000000bb000000bb000b00bb00bbb0bb0bb0bbbbbb000bbbb00000bb000"
        self.izquierda = "EXT mled g 000bb00000bb00000bb00000bbbbbbbbbbbbbbbb0bb0000000bb0000000bb000"
        self.derecha = "EXT mled g 000bb00000bb00000bb00000bbbbbbbbbbbbbbbb0bb0000000bb0000000bb000"
        self.flip = "EXT mled g 00bbbb000b000000b00bbb00b00b00b00b00b0b000b000b0000bbb0000000000"
        self.aterriza = "EXT mled g 0000000000000000000000000bbbbbb000000000000000000000000000000000"
        self.corazon = "EXT mled g 000000000rr00rr0rrrrrrrrrrrrrrrr0rrrrrr000rrrr00000rr00000000000"
        self.corazon_roto = "EXT mled g 000000000rr000r0rrrr0rrrrrrr0rrr0rrr00rr000r0rr00000rr00000000000"
        self.ole = "EXT mled l r 2.5 OLE"
    def buildFrame(self, fatherFrame, mode):
        # mode can be: fingers, face or pose
        self.fatherFrame = fatherFrame
        self.mode = mode

        self.cap = cv2.VideoCapture(0)

        if self.mode == 'fingers':
            self.detector = FingerDetector()
        elif self.mode == 'pose':
            self.detector = PoseDetector()
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

        # state can be: initial, practising, flying, closed
        self.state = 'initial'

        self.practice = tk.Button(self.topFrame, text="Practica los movimientos", bg='#F57328', fg="white",
                                  command=self.practice)
        self.practice.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.closeButton = tk.Button(self.topFrame, text="Salir", bg='#FFE9A0', fg="black",
                                     command=self.close)
        self.closeButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        # frame to be shown when practise is finish and user wants to fly
        self.buttonFrame = tk.Frame(self.topFrame)
        self.buttonFrame.rowconfigure(0, weight=1)
        self.buttonFrame.rowconfigure(1, weight=1)
        self.buttonFrame.columnconfigure(0, weight=1)
        self.buttonFrame.columnconfigure(1, weight=1)

        self.connectButton = tk.Button(self.buttonFrame, text="Connect", bg='#CC3636', fg="white", command=self.connect)
        self.connectButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.takeOffButton = tk.Button(self.buttonFrame, text="Take Off", bg='#CC3636', fg="white",
                                       command=self.takeOff)
        self.takeOffButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        # button to be shown when flying
        self.landButton = tk.Button(self.buttonFrame, text="Aterriza", bg='#CC3636', fg="white",
                                    command=self.returnHome)

        # button to be shown when the dron is back home
        self.closeButton2 = tk.Button(self.buttonFrame, text="Salir", bg='#FFE9A0', fg="black", command=self.close)

        self.topFrame.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        # by defaulf, easy mode is selected
        self.bottomFrame = tk.LabelFrame(self.master, text="Indicaciones")

        if self.mode == 'fingers':
            self.image = Image.open("assets/dedos_faciles.png")
        elif self.mode == 'pose':
            self.image = Image.open("assets/poses_faciles.png")
        else:
            self.image = Image.open("assets/caras_faciles.png")

        self.image = self.image.resize((400, 550), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = Canvas(self.bottomFrame, width=400, height=550)
        canvas1.pack(fill="both", expand=True)
        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        self.bottomFrame.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

        return self.master

    def action(self):
        if self.connected:
            time.sleep(4)
            self.connectButton['text'] = 'connected'
            self.connectButton['bg'] = '#367E18'

        if self.taken_off:
            self.takeOffButton['text'] = 'flying'
            self.takeOffButton['bg'] = '#367E18'
            self.state = 'flying'
            # this thread will start taking images and detecting patterns to guide the drone
            x = threading.Thread(target=self.flying)
            x.start()
            self.landButton.grid(row=2, column=0, padx=5, columnspan=3, pady=5, sticky=N + S + E + W)

        if self.at_home:
            # the dron completed the RTL
            messagebox.showwarning("Success", "Ya estamos en casa", parent=self.master)
            self.landButton.grid_forget()

            # return to the initial situation
            self.connectButton['bg'] = '#CC3636'
            self.connectButton['text'] = 'Connect'
            self.takeOffButton['bg'] = '#CC3636'
            self.takeOffButton['text'] = 'TakeOff'
            self.state = 'initial'

    def connect(self):
        print('voy a conectar')
        # do not allow connection if level of difficulty is not fixed
        self.closeButton2.grid_forget()
        self.init_drone()

    def init_drone(self):
        # Connect to the drone, start streaming and subscribe to events
        self.drone.connect()
        self.drone.wait_for_connection(10.0)
        self.drone.send_packet_data("mon")
        self.drone.send_packet_data("mdirection 2")
        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA,
                             self.flight_data_handler)
        self.connected = True
        self.action()

    def flight_data_handler(self, event, sender, data):
        self.battery = data.battery_percentage

    def takeOff(self):
        # do not allow taking off if not armed
        if self.connectButton['bg'] == '#367E18':
            self.drone.takeoff()
            self.taken_off = True
            self.action()
        else:
            messagebox.showwarning("Error", "Antes de despegar debes conectarte al dron", parent=self.master)

    def close(self):
        # this will stop the video stream thread
        self.state = 'closed'
        self.cap.release()
        self.drone.sock.close()
        self.drone.quit()
        self.fatherFrame.destroy()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def practice(self):
        if self.state == 'initial':
            # start practising
            self.practice['bg'] = '#367E18'
            self.practice['text'] = 'Estoy preparado. Quiero volar'
            self.state = 'practising'
            # startvideo stream to practice
            x = threading.Thread(target=self.practising)
            x.start()

        elif self.state == 'practising':
            # stop the video stream thread for practice
            self.state = 'closed'

            self.practice.grid_forget()

            # show buttons for connect, arm and takeOff
            self.buttonFrame.grid(row=1, column=0, columnspan=2, padx=5, pady=0, sticky=N + S + E + W)

            self.closeButton.grid_forget()
            self.closeButton.grid(row=0, column=0, columnspan=2, padx=7.5, pady=0, sticky=N + S + E + W)

    def __setDirection(self, code):
        if code == 1:
            return 'Adelante'
        elif code == 2:
            return 'Atras'
        elif code == 3:
            return 'Derecha'
        elif code == 4:
            return 'Izquierda'
        elif code == 5:
            return 'Flip'
        elif code == 6:
            return 'Aterriza'
        elif code == 0:
            return 'Stop'
        else:
            return ''

    def practising(self):
        # when the user changes the pattern (new face, new pose or new fingers) the system
        # waits some time (ignore 8 video frames) for the user to stabilize the new pattern
        # we need the following variables to control this
        prevCode = -1
        cont = 0

        while self.state == 'practising':
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            code, img = self.detector.detect(image)
            img = cv2.resize(img, (800, 600))
            img = cv2.flip(img, 1)

            # if user changed the pattern we will ignore the next 8 video frames
            if (code != prevCode):
                cont = 4
                prevCode = code
            else:
                cont = cont - 1
                if cont < 0:
                    # the first 8 video frames of the new pattern (to be ignored) are done
                    # we can start showing new results
                    direction = self.__setDirection(code)
                    cv2.putText(img, direction, (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 10)

            cv2.imshow('video', img)
            cv2.waitKey(1)
        cv2.destroyWindow('video')
        cv2.waitKey(1)

    def avisar (self):
        self.aviso = self.aviso +1
        if self.aviso == 1:
            comando_rojo = self.comando.replace("b", "r")
            self.drone.send_packet_data(comando_rojo)
            start_time = threading.Timer(5, self.avisar)
            start_time.start()



    def flying(self):

        movementGenerator = MovementGenerator(1,-1,2,-2,2,-2)
        comandos = [self.adelante, self.atras, self.derecha, self.izquierda]

        # see comments for practising function
        prevCode = -1
        cont = 0
        # we need to know if the dron is returning to lunch to show an apropriate message
        self.returning = False

        self.direction = ''
        numberOfOperations = 5
        next = 0

        while next < numberOfOperations:
                n = movementGenerator.NewMovement()
                self.comando = comandos[n]
                self.drone.send_packet_data(self.comando)
                time.sleep(2)
                cont = 0
                detected = False
                self.aviso = 0
                start_time = threading.Timer(5, self.avisar)
                start_time.start()
                while not detected and self.aviso != 2:
                    success, image = self.cap.read()
                    if not success:
                        print("Ignoring empty camera frame.")
                        # If loading a video, use 'break' instead of 'continue'.
                        continue
                    code, img = self.detector.detect(image)
                    img = cv2.resize(img, (800, 600))
                    img = cv2.flip(img, 1)
                    self.direction = self.__setDirection(code)
                    cv2.putText(img, self.direction, (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 10)
                    cv2.imshow('video', img)
                    cv2.waitKey(1)
                    if code == n+1:
                        cont = cont +1
                        if cont == 8:
                            detected = True
                    else:
                        cont = 0
                    if code == 6:
                        detected = True

                if self.aviso == 2:
                    self.drone.send_packet_data(self.corazon_roto)
                    next = numberOfOperations +1

                else:
                    start_time.cancel()
                    self.drone.send_packet_data(self.corazon)
                    time.sleep(2)

                    if code == 1:
                        self.drone.forward(30)
                        time.sleep(2)
                        self.drone.forward(0)
                    elif code == 2:  # south
                        self.drone.backward(30)
                        time.sleep(2)
                        self.drone.backward(0)

                    elif code == 3:  # east
                        self.drone.right(30)
                        time.sleep(2)
                        self.drone.right(0)
                    elif code == 4:  # west
                        self.drone.left(30)
                        time.sleep(2)
                        self.drone.left(0)
                    elif code == 5:
                        self.drone.send_packet_data("flip b")
                        self.drone.send_packet_data("flip b")
                    elif code == 6:
                        self.returnHome()
                    elif code == 0:
                        pass
                        #self.drone.forward(0)
                        #self.drone.backward(0)
                        #self.drone.right(0)
                        #self.drone.left(0)

                    #cv2.putText(img, self.direction, (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 10)
                    #cv2.imshow('video', img)
                    #cv2.waitKey(1)
                    next = next + 1

        if (next == numberOfOperations):
            self.drone.send_packet_data(self.ole)
        self.drone.land()
        cv2.destroyWindow('video')
        cv2.waitKey(1)


    def returnHome(self):

        self.state= 'initial'
        self.returning = True
        self.direction = 'Aterrizando'
        #now = time.time()  # get the time
        self.drone.land()
        #elapsed = time.time() - now
        #time.sleep(3. - elapsed)

        self.at_home = True
        self.action()

