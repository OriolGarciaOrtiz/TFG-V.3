import ssl
from tkinter import *
import tkinter as tk
from tkinter import font
import os
from djitellopy import Tello
import time
import cv2
import paho.mqtt.client as mqtt
import threading
from PIL import Image, ImageTk
from tkinter import messagebox
import base64
from clipper import clipper
#from clipper_back import clipper
import glob

flying = False


class escenarioPanoramica:


    def Open(self, master, selectedBroker):
        self.drone = Tello()
        self.flying = False

        self.clipper = clipper()


        self.windowPanoramic = Toplevel(master)

        # Variables
        self.detectingBool = False
        self.take_off = False
        self.connected = False
        self.panoramic = False

        '''# MQTT conexión
        self.global_broker_address = "broker.hivemq.com"
        self.global_broker_port = 8000  # 8883

        self.client = mqtt.Client("VideoService", transport="websockets")
        # self.client.username_pw_set("dronsEETAC", "mimara1456.")
        self.client.connect(self.global_broker_address, self.global_broker_port)
        self.client.loop_start()'''


        # Configuration NUEVA INTERFAZ
        self.windowPanoramic.geometry("300x600")
        self.windowPanoramic.rowconfigure(0, weight=1)
        self.windowPanoramic.rowconfigure(1, weight=1)
        self.windowPanoramic.rowconfigure(2, weight=1)
        self.windowPanoramic.rowconfigure(3, weight=1)
        self.windowPanoramic.rowconfigure(4, weight=1)
        self.windowPanoramic.rowconfigure(5, weight=1)
        self.windowPanoramic.rowconfigure(6, weight=1)
        self.windowPanoramic.rowconfigure(7, weight=1)
        self.windowPanoramic.rowconfigure(8, weight=1)
        self.windowPanoramic.rowconfigure(9, weight=1)
        self.windowPanoramic.rowconfigure(10, weight=1)
        self.windowPanoramic.rowconfigure(11, weight=1)
        self.windowPanoramic.rowconfigure(12, weight=1)
        self.windowPanoramic.rowconfigure(13, weight=1)

        self.windowPanoramic.columnconfigure(0, weight=1)
        self.windowPanoramic.columnconfigure(1, weight=1)
        self.color1 = '#38726C'
        self.color2 = '#D34E24'
        self.color3 = '#F28123'
        self.color4 = '#F7F052'

        tk.Label(self.windowPanoramic, text="Distance (m)").grid(row=0, column=0, columnspan=2,  padx=5, pady=5, sticky=N + S + E + W )
        self.distanceSlider = tk.Scale(
            self.windowPanoramic,
            from_=1,
            to=4,
            length=100,
            orient="horizontal",
            activebackground="green",
            tickinterval=0.5,
            resolution=0.5,
            #command=self.newValues,
        )
        self.distanceSlider.grid(
            column=0,
            row=1,
            columnspan=2,
            pady=5,
            padx=5,
            sticky=N + S + E + W
        )
        self.distanceSlider.set (2)
        tk.Label(self.windowPanoramic, text="Overlap (%)").grid(row=2, column=0, columnspan=2, padx=5, pady=5,
                                                                 sticky=N + S + E + W)
        self.overlapSlider = tk.Scale(
            self.windowPanoramic,
            from_=0.1,
            to=0.9,
            length=100,
            orient="horizontal",
            activebackground="green",
            tickinterval=0.1,
            resolution=0.1,
            # command=self.newValues,
        )
        self.overlapSlider.grid(
            column=0,
            row=3,
            columnspan=2,
            pady=5,
            padx=5,
            sticky=N + S + E + W
        )
        self.overlapSlider.set(0.8)





        self.connectButton = Button(self.windowPanoramic, text="Connect",bg=self.color2,
                                 fg='white', command=self.connect)
        self.connectButton.grid (row=4, column = 0, columnspan=2,  padx=5, pady=5, sticky=N + S + E + W)

        self.takeOffButton = Button(self.windowPanoramic, text="TakeOff", bg=self.color2,
                                    fg='white', command=self.takeoff)
        self.takeOffButton.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.upButton = Button(self.windowPanoramic, text="Up", bg=self.color4,
                                    fg='white', command=self.up)
        self.upButton.grid(row=6, column=0,padx=5, pady=5, sticky=N + S + E + W)

        self.downButton = Button(self.windowPanoramic, text="Down", bg=self.color4,
                                    fg='black', command=self.down)
        self.downButton.grid(row=6, column=1,padx=5, pady=5, sticky=N + S + E + W)

        self.startButton = Button(self.windowPanoramic, text="Start taking pictures", bg=self.color2,
                                    fg='white', command=self.start_taking_pictures)
        self.startButton.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.forwButton = Button(self.windowPanoramic, text="Forward", bg=self.color4,
                              fg='white', command=self.forward)
        self.forwButton.grid(row=8, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.backButton = Button(self.windowPanoramic, text="Back", bg=self.color4,
                                 fg='black', command=self.backward)
        self.backButton.grid(row=8, column=1, padx=5, pady=5, sticky=N + S + E + W)


        self.landButton = Button(self.windowPanoramic, text="Land", bg=self.color2,
                                  fg='white', command=self.land)
        self.landButton.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.buildButton = Button(self.windowPanoramic, text="Build panorama", bg=self.color2,
                                 fg='white', command=self.makePano)
        self.buildButton.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.clipButton = Button(self.windowPanoramic, text="Clip", bg=self.color2,
                                  fg='white', command=self.callSlider)
        self.clipButton.grid(row=11, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        ''' self.clipButton = Button(self.windowPanoramic, text="Clip", bg='red',
                                  fg='white', command=self.connect)
        self.clipButton.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)'''

        self.sendButton = Button(self.windowPanoramic, text="Send", bg=self.color2,
                                  fg='white', command=self.sendPanorama)
        self.sendButton.grid(row=12, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.closeButton = Button(self.windowPanoramic, text="Close", bg=self.color1,
                                 fg='white', command=self.closePan)
        self.closeButton.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.client = mqtt.Client("VideoService", transport="websockets")
        self.client.tls_set(
            ca_certs=None,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None,
        )

        if selectedBroker == 0:
            self.client.username_pw_set(
                "dronsEETAC", "mimara1456."
            )
            self.client.connect("dronseetac.upc.edu", 8883)
        else:
            print('hivemq')
            self.client.connect("broker.hivemq.com", 8884)

        self.client.max_queued_messages_set(1)
        self.client.max_inflight_messages_set(1)
        self.client.subscribe('videoFrameAnna')
        print('Waiting connection')
        self.client.loop_start()


    def connect(self):
        try:
            self.connected = True
            # muestro el nivel de bateria
            self.connectButton['text'] = str(self.drone.get_battery())
            #self.panoramic = True
            #self.connectDButton.place(x=650, y=155, anchor="nw")
            self.connectButton['bg'] = self.color1
            print("Te has conectado correctamente al dron!")

            if not self.detectingBool:
                self.detectingBool = True
                x = threading.Thread(target=self.detecting)
                x.start()
            print("Se estan transmitiendo las imágenes de la cámara del dron")

        except Exception as e:
            messagebox.showerror("Error de conexión", "No se pudo conectar al dron. Por favor, inténtalo de nuevo.\nError: " + str(e), parent=self.windowPanoramic)

    def detecting(self):
        self.drone.streamon()
        cv2.namedWindow("Tello Camera", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Tello Camera", 160,120)

        while self.detectingBool and self.connected:
            frame = self.drone.get_frame_read().frame  # Captura un frame desde la cámara del Tello
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow("Tello Camera", frame_rgb)  # Muestra el frame en una ventana
            cv2.waitKey(1)


    def takeoff(self):
        if self.connected:
            self.drone.takeoff()
            self.take_off = True
            self.panoramic = True
            self.takeOffButton['text'] = 'flying'
            self.takeOffButton['bg'] = self.color1
            self.state = 'flying'
        else:
            messagebox.showwarning("Error", "Antes de despegar debes conectarte al dron", parent=self.windowPanoramic)

    def land(self):
        self.flying = False
        self.drone.land()
        self.landButton['text'] = 'landed'
        self.takeOffButton['bg'] = self.color1
        #messagebox.showwarning("Success", "Ya estamos en casa", parent=self.windowPanoramic)

    def forward(self):
       self.adelante = True

    def backward(self):
        self.atras = True

    def up(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 0, 25, 100)
            time.sleep(0.25)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowPanoramic)

    def down(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 0, -25, 100)
            time.sleep(0.5)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowPanoramic)

    def start_taking_pictures(self):
        #self.panoramic = True
        if self.take_off and self.connected and self.panoramic:
            self.record_pano(self.drone)
            self.startButton['text'] = 'Ready to build panorama'
            self.startButton['bg'] = self.color1
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowPanoramic)

    def sendPanorama(self):
        image_path = "pano/res.jpg"
        quality = 50
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        with open(image_path, "rb") as image_file:
            image_data = cv2.imread(image_path)
            _, frameComp = cv2.imencode(".jpg", image_data, encode_param)
            image_base64 = base64.b64encode(frameComp)
            print('size: ', frameComp.shape[0])
            self.client.publish("PanoramicaAnna", payload=image_base64, qos=2)

        self.sendButton['text'] = 'Panorama sent'
        self.sendButton['bg'] = self.color1

    def closePan(self):
        self.detectingBool = False
        cv2.destroyAllWindows()
        self.windowPanoramic.destroy()


    def record_pano_thread (self, mydrone):
        for filename in glob.glob('pano/*'):
            os.remove(filename)

        d = self.distanceSlider.get()*100
        s = self.overlapSlider.get()
        t = d*(1-s)/30
        images = []
        folder_path = 'pano/'
        self.flying = True
        self.atras = False
        self.adelante = False
        interval = 0
        mydrone.send_rc_control(30, 0, 0, 0)
        time.sleep(1)

        print ('empezamos')
        while self.flying:
            # if self.panoramicBool:
            name = str(interval//10) + str(interval%10)
            filename = os.path.join(folder_path, 'image_'+name+'.jpg')

            image = mydrone.get_frame_read().frame
            if image is not None:
                #image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filename, image)
                images.append(image)
                # print('images', images)

            if self.adelante:
                self.adelante = False
                mydrone.send_rc_control(0, 30, 0, 0)
                time.sleep(0.5)
            elif self.atras:
                self.atras = False
                mydrone.send_rc_control(0, -30, 0, 0)
                time.sleep(0.5)


            mydrone.send_rc_control(30, 0, 0, 0)  # left_right_velocity: 30 (escala -100:100)
            # velocidad_actual = mydrone.get_speed_x()
            # print('velocidad',velocidad_actual)
            interval = interval + 1
            # time.sleep(t)
            time.sleep(t)

        print('images', len(images))
        # stitcher = cv2.Stitcher_create()
        # self.result = stitcher.stitch((tuple(images)))
        # cv2.imwrite('assets/telloPanoramic/result.jpg', self.result[1])
        # self.panoramicBool = False
        print('iresult')

        #mydrone.land()
        '''self.makePano()
        self.callSlider()'''

    def record_pano(self, mydrone):

        y = threading.Thread (target = self.record_pano_thread, args = [mydrone, ])
        y.start()


    def makePano(self):

        folder_path = 'pano/'

        # Luego intenta realizar la unión de imágenes

        k = 0
        while True:
            print ('pruebo con todas menos ', k)
            images = []
            for filename in glob.glob('pano/res*'):
                os.remove(filename)

            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith('.jpg'):
                    file_path = os.path.join(folder_path, file_name)
                    print ('cargo ', file_path)
                    img = cv2.imread(file_path)
                    if img is not None:
                        images.append(img)
                    else:
                        print(f"Error cargando la imagen: {file_path}")
            n = len (images)
            print ('tengo ', n)

            stitcher = cv2.Stitcher.create()
            result = stitcher.stitch(tuple(images [0:n-1]))
            if result[0] == 0:
                break
            k = k+1

        self.buildButton['text'] = 'Ready to clip'
        self.buildButton['bg'] = self.color1

        cv2.imwrite('pano/result.jpg', result[1])
        print('result')

    def markClipped (self):
        self.clipButton['text'] = 'Ready to send'
        self.clipButton['bg'] = self.color1

    def callSlider(self):
        self.clipper.Open(self.markClipped)



