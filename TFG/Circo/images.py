import base64
import ssl
from tkinter import *
import tkinter as tk
from tkinter import font

import numpy as np
from PIL import Image, ImageTk
from tkinter import messagebox
from djitellopy import Tello
import time
import cv2
import os
import paho.mqtt.client as mqtt
import threading
from Gallery import GalleryMedia
import pygame
import torch
class escenarioImagenes:

    def Open(self, master, selectedBroker):
        self.drone = Tello()
        #self.galleryImages = galleryImages()
        self.galleryImages = GalleryMedia()
        print ('selected broker', selectedBroker)

        myFont3 = font.Font(family='Arial', size=10, weight='bold')

        self.windowImage = Toplevel(master)

        # Variables
        self.takePictureBool = False
        self.take_off = False
        self.connected = False
        self.detectingBool = False
        self.photo = None
        self.vect_images = []
        self.count = 0
        self.selectedBroker = selectedBroker
        self.usingJoystic = False

        # MQTT conexión
        '''print("aaaa")
        self.global_broker_address = "broker.hivemq.com"
        self.global_broker_port = 8000  # 8883

        self.client = mqtt.Client("VideoService", transport="websockets")
        # self.client.username_pw_set("dronsEETAC", "mimara1456.")
        self.client.connect(self.global_broker_address, self.global_broker_port)
        self.client.loop_start()'''

        # Configuration
        self.windowImage.geometry("650x500")
        self.windowImage.rowconfigure(0, weight=1)
        self.windowImage.rowconfigure(1, weight=1)
        self.windowImage.rowconfigure(2, weight=1)
        self.windowImage.rowconfigure(3, weight=1)


        self.windowImage.columnconfigure(0, weight=1)
        self.windowImage.columnconfigure(1, weight=1)
        self.windowImage.columnconfigure(2, weight=1)


        self.windowImage.title("Foto Page")



        # Title label
        self.titlelabel = tk.Label(self.windowImage, text="TAKE YOUR PICTURE!", height=3)
        self.titlelabel.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)
        self.titlelabel['font'] = myFont3

        self.connectBrokerButton = Button(self.windowImage, text="Connect broker", bg='#FF6103',
                                 fg='#F8F8FF', command = self.connectBroker)
        self.connectBrokerButton.grid(row=1, column=0, columnspan=3,padx=5, pady=5, sticky=N + S + E + W)

        self.picturesFrame = tk.LabelFrame(self.windowImage, text='Pictures')
        self.picturesFrame.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.picturesFrame.rowconfigure(0, weight=1)
        self.picturesFrame.rowconfigure(1, weight=1)

        self.picturesFrame.columnconfigure(0, weight=1)
        self.picturesFrame.columnconfigure(1, weight=1)
        self.picturesFrame.columnconfigure(2, weight=1)

        self.canvas = Canvas(self.picturesFrame, width=320, height=240, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)

        # Take picture button
        self.takePictureButton = Button(self.picturesFrame, text="Take Picture", height=1, bg='#0000FF',
                                        fg='#F8F8FF', command=self.takePicture)
        self.takePictureButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.takePictureButton['font'] = myFont3

        # Send picture button
        self.sendButton = Button(self.picturesFrame, text="Send Picture", height=1, bg='#0000FF',
                                 fg='#F8F8FF', command=self.sendSave)
        self.sendButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.sendButton['font'] = myFont3

        # Gallery button
        self.galleryButton = Button(self.picturesFrame, text="Image gallery", height=1, bg='#458B74',
                                    fg='#F8F8FF', command=self.gallery)
        self.galleryButton.grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)
        self.galleryButton['font'] = myFont3

        # Canvas




        self.commandsFrame = tk.LabelFrame (self.windowImage, text = 'Drone commands')
        self.commandsFrame.grid(row=2, column=1, padx=5, pady=5, sticky=N + S + E + W)

        self.commandsFrame.rowconfigure(0, weight=1)
        self.commandsFrame.rowconfigure(1, weight=1)
        self.commandsFrame.rowconfigure(2, weight=1)
        self.commandsFrame.rowconfigure(3, weight=1)
        self.commandsFrame.rowconfigure(4, weight=1)
        self.commandsFrame.rowconfigure(5, weight=1)
        self.commandsFrame.rowconfigure(5, weight=1)

        self.commandsFrame.columnconfigure(0, weight=1)
        self.commandsFrame.columnconfigure(1, weight=1)







        # Connect button
        self.connectButton = Button(self.commandsFrame, text="Connect", bg='#367E18',
                            fg='#F8F8FF', command=self.connect)
        self.connectButton.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
        self.connectButton['font'] = myFont3

        # TakeOff button
        self.takeoffDButton = Button(self.commandsFrame, text="Take Off", bg='#FF6103',
                                     fg='#F8F8FF', command=self.takeoff)
        self.takeoffDButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.takeoffDButton['font'] = myFont3

        # Land button
        self.landDButton = Button(self.commandsFrame, text="Landing", bg='#FF6103',
                                     fg='#F8F8FF', command=self.land)
        self.landDButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.landDButton['font'] = myFont3

        # Up button
        self.upButton = Button(self.commandsFrame, text="  Up  ", bg='#FF6103',
                               fg='#F8F8FF', command=self.up)
        self.upButton.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.upButton['font'] = myFont3

        # Down button
        self.downButton = Button(self.commandsFrame, text="Down", bg='#FF6103',
                                 fg='#F8F8FF', command=self.down)
        self.downButton.grid(row=2, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.downButton['font'] = myFont3

        # Forward button
        self.forwardButton = Button(self.commandsFrame, text="Forward ",  bg='#FF8C00',
                                  fg='#F8F8FF', command=self.forward)
        self.forwardButton.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.forwardButton['font'] = myFont3

        # Backward button
        self.backwardButton = Button(self.commandsFrame, text="Backward", bg='#FF8C00',
                                  fg='#F8F8FF', command=self.backward)
        self.backwardButton.grid(row=3, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.backwardButton['font'] = myFont3

        # Left button
        self.leftButton = Button(self.commandsFrame, text="  Left  ", bg='#FF8C00',
                                 fg='#F8F8FF', command=self.left)
        self.leftButton.grid(row=4, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.leftButton['font'] = myFont3

        # Right button
        self.rightButton = Button(self.commandsFrame, text=" Right ", bg='#FF8C00',
                                  fg='#F8F8FF', command=self.right)
        self.rightButton.grid(row=4, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.rightButton['font'] = myFont3


        # Rolate CW
        self.rotateCWButton = Button(self.commandsFrame, text="  Rotate CW  ", bg='#FF8C00',
                                  fg='#F8F8FF', command=self.rotateCW)
        self.rotateCWButton.grid(row=5, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.rotateCWButton['font'] = myFont3

        # Rotate CCW
        self.rotateCCWButton = Button(self.commandsFrame, text=" Rotate CCW ", bg='#FF8C00',
                                  fg='#F8F8FF', command=self.rotateCCW)
        self.rotateCCWButton.grid(row=5, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.rotateCCWButton['font'] = myFont3

        self.flipButton = Button(self.commandsFrame, text=" Flip ", bg='#FF8C00',
                                      fg='#F8F8FF', command=self.flip)
        self.flipButton.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
        self.flipButton['font'] = myFont3

        self.joysticButton = Button(self.windowImage, text="Joystic", bg='#FF6103',
                                 fg='#F8F8FF', command = self.startJoystic)
        self.joysticButton.grid(row=2, column=2, padx=5, pady=5, sticky=N + S + E + W)

        self.closeButton = Button(self.windowImage, text="Close", bg='#367E18',
                                     fg='#F8F8FF', command=self.closeImg)
        self.closeButton.grid(row=3, column=0, columnspan = 3, padx=5, pady=5, sticky=N + S + E + W)
        self.closeButton['font'] = myFont3



    def connect(self):
        try:
            self.connected = True
            # muestro el nivel de bateria
            self.connectButton['text'] = str(self.drone.get_battery())
            self.connectButton['bg'] = '#8B0000'
            print("Te has conectado correctamente al dron!")

            if not self.detectingBool:
                self.detectingBool = True
                x = threading.Thread(target=self.detecting)
                x.start()
            print("Se estan transmitiendo las imágenes de la cámara del dron")

        except Exception as e:
            messagebox.showerror("Error de conexión", "No se pudo conectar al dron. Por favor, inténtalo de nuevo.\nError: " + str(e), parent=self.windowImage)

    def connectBroker(self):
        self.client = mqtt.Client("VideoService", transport="websockets")
        self.client.tls_set(
            ca_certs=None,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None,
        )

        if self.selectedBroker == 0:
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

    def takeoff(self):
        if self.connected:
            self.drone.takeoff()
            time.sleep(2)
            self.take_off = True
            self.takeoffDButton['text'] = 'flying'
            self.takeoffDButton['bg'] = '#8B0000'
            self.state = 'flying'
        else:
            messagebox.showwarning("Error", "Antes de despegar debes conectarte al dron", parent=self.windowImage)

    def land(self):
        self.drone.land()
        messagebox.showwarning("Success", "Ya estamos en casa", parent=self.windowImage)

    def forward(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(50, 0, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def backward(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(-50, 0, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def left(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 50, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def right(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, -50, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def up(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 0, 50, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def down(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 0, -50, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def rotateCW(self):
        if self.take_off and self.connected:
            self.drone.rotate_clockwise(90)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def rotateCCW(self):
        if self.take_off and self.connected:
            self.drone.rotate_counter_clockwise(90)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    def flip(self):
        if self.take_off and self.connected:
            self.drone.send_control_command("flip l")
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowImage)

    import cv2
    import numpy as np

    def resaltar_colores_principales(self, frame, umbral_porcentaje=1):
        """
        Detecta las zonas más grandes de color verde, rojo, azul y amarillo en una imagen.
        Dibuja un contorno rojo alrededor de cada una si su área supera el porcentaje especificado.

        :param frame: Imagen en formato BGR.
        :param umbral_porcentaje: Porcentaje mínimo de área del frame para mostrar el contorno.
        :return: Imagen con contornos rojos alrededor de las zonas detectadas.
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho

        # Rangos HSV para los colores
        rangos_colores = {
            "verde": ([40, 40, 40], [80, 255, 255]),
            "azul": ([100, 150, 50], [140, 255, 255]),
            "amarillo": ([20, 100, 100], [30, 255, 255]),
            "rojo": [([0, 100, 100], [10, 255, 255]), ([160, 100, 100], [180, 255, 255])]
        }

        def procesar_color_mas_grande(mascara_color):
            contornos, _ = cv2.findContours(mascara_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contornos:
                return
            mayor = max(contornos, key=cv2.contourArea)
            area = cv2.contourArea(mayor)
            if (area / area_total) * 100 >= umbral_porcentaje:
                cv2.drawContours(frame, [mayor], -1, (0, 0, 255), 2)

        # Verde, azul, amarillo: un solo rango
        for color in ["verde", "azul", "amarillo"]:
            bajo, alto = rangos_colores[color]
            mascara = cv2.inRange(hsv, np.array(bajo), np.array(alto))
            procesar_color_mas_grande(mascara)

        # Rojo: combinar las dos máscaras
        rojo_bajo1, rojo_alto1 = rangos_colores["rojo"][0]
        rojo_bajo2, rojo_alto2 = rangos_colores["rojo"][1]

        mascara1 = cv2.inRange(hsv, np.array(rojo_bajo1), np.array(rojo_alto1))
        mascara2 = cv2.inRange(hsv, np.array(rojo_bajo2), np.array(rojo_alto2))
        mascara_rojo = cv2.bitwise_or(mascara1, mascara2)

        procesar_color_mas_grande(mascara_rojo)

        return frame
    def resaltar_zonas_verdes(self, frame,  umbral_porcentaje=1):
        """
        Recibe un frame (imagen) y resalta con contornos rojos las zonas verdes.

        :param frame: Imagen en formato BGR
        :return: Imagen con contornos rojos alrededor de las zonas verdes
        """
        # Convertimos la imagen de BGR a HSV

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Rango típico de verde en HSV
        verde_bajo = np.array([40, 40, 40])
        verde_alto = np.array([80, 255, 255])

        # Máscara para detectar verde
        mascara = cv2.inRange(hsv, verde_bajo, verde_alto)

        # Contornos encontrados
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contornos:
            return frame  # No hay verde

        # Encontrar el contorno con mayor área
        mayor_contorno = max(contornos, key=cv2.contourArea)
        area_mayor = cv2.contourArea(mayor_contorno)

        # Área total del frame
        alto, ancho = frame.shape[:2]
        area_total = alto * ancho

        # Verificar si el área del mayor contorno supera el umbral
        if (area_mayor / area_total) * 100 >= umbral_porcentaje:
            cv2.drawContours(frame, [mayor_contorno], -1, (0, 0, 255), 2)

        return frame

    def takePicture(self):
        if self.connected:
            self.count = self.count + 1
            self.frame = self.drone.get_frame_read().frame

            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.imgPicture = Image.fromarray(self.frame)
            self.imgPicture = self.imgPicture.resize((320, 240))

            self.photo = ImageTk.PhotoImage(self.imgPicture)
            self.canvas.delete("all")  # Borramos cualquier contenido previo en el canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.image = self.photo
            self.takePictureBool = True
            print("Foto tomada")
        else:
            messagebox.showwarning("Error", "Primero conéctate con el dron!", parent=self.windowImage)

    def sendSave(self):
        try:
            if self.photo and self.takePictureBool:
                self.vect_images.append(self.photo)
                frame_brg = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                cv2.imwrite("assets/telloImages/foto_tello" + str(self.count) + ".jpg", frame_brg)

                self.sendmqtt()

                print("Foto enviada y guardada")
                return self.photo
            else:
                print("No hay foto para enviar")
                return None
        except Exception as e:
            messagebox.showerror("Error de conexión",
                                 "No se pudo conectar al dron. Por favor, inténtalo de nuevo.\nError: " + str(e),
                                 parent=self.windowImage)

    def sendmqtt(self):
        image_path = "assets/telloImages/foto_tello" + str(self.count) + ".jpg"
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data)
            self.client.publish("ImagenAnna", payload=image_base64, qos=2)

    def gallery(self):
        type = 'Image'
        self.galleryImages.Open(self.windowImage,type, self.client)

    def closeImg(self):
        if self.connected:
            self.drone.streamoff()
            self.detectingBool = False
            cv2.destroyAllWindows()
        self.windowImage.destroy()


        '''if len(self.vect_images) == 0:
            messagebox.showwarning("Error", "No has guardado ninguna imagen!", parent=self.windowImage)
        else:
            print("Has guardado " + str(len(self.vect_images)) + "imagenes: " + str(self.vect_images))
            self.drone.streamoff()
            self.detectingBool = False
            self.windowImage.destroy()
            cv2.destroyAllWindows()'''

    def resalar_objetos (self, frame):
        global model
        BANANA_CLASS_ID = 46
        CARROT_CLASS_ID = 51
        DONUT_CLASS_ID = 54
        FORK_CLASS_ID = 42
        CLOCK_CLASS_ID = 74
        BEAR_CLASS_ID = 21
        STOP_CLASS_ID = 11
        RAQUET_CLASS_ID = 38
        # Convertir frame a RGB para YOLO
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Inferencia con el modelo
        results = model(img_rgb)
        # Procesar resultados
        for *box, conf, cls in results.xyxy[0]:
            if int(cls.item()) == BANANA_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Banana {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("BANANA")
            elif int(cls.item()) == CLOCK_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Clock {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("RELOJ")
            elif int(cls.item()) == DONUT_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Donut {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("DONUT")
            elif int(cls.item()) == CARROT_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Carrot {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("Zanahoria")
            elif int(cls.item()) == FORK_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Fork {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("TENEDOR")
            elif int(cls.item()) == BEAR_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Bear {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("OSO")
            elif int(cls.item()) == RAQUET_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Raquet {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("REQUETA")
            elif int(cls.item()) == STOP_CLASS_ID:
                x1, y1, x2, y2 = map(int, box)
                label = f"Stop {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                print("STOP")
        return frame

    def detecting(self):
        global model

        # Cargar el modelo YOLOv5 preentrenado de Ultralytics
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        for class_id, class_name in model.names.items():
            print(f"{class_id} → {class_name}")
        model.eval()



        self.drone.streamon()
        cv2.namedWindow("Tello Camera", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Tello Camera", 640, 480)

        while self.detectingBool and self.connected:
            frame = self.drone.get_frame_read().frame  # Captura un frame desde la cámara del Tello
            #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = self.resaltar_colores_principales(frame)
            frame = self.resalar_objetos(frame)


            cv2.imshow("Tello Camera", frame)  # Muestra el frame en una ventana
            cv2.waitKey(1)

    def joysticLoop (self):

        while self.usingJoystic:
            # Procesar eventos de pygame (necesario para actualizar el estado del joystick)
            pygame.event.pump()

            if self.joystick.get_button(8) == 1:
                self.takeoff()
            elif self.joystick.get_button(9) == 1:
                self.land()
            elif self.joystick.get_button(3) == 1:
                self.takePicture()
            elif self.joystick.get_button(0) == 1:
                self.flip()
            elif self.take_off and self.connected:
                lr = self.map_axis(self.joystick.get_axis(3))  # RC1
                fb = self.map_axis(-self.joystick.get_axis(2))  # RC2
                ud = self.map_axis(-self.joystick.get_axis(1))  # RC3
                yaw = self.map_axis(self.joystick.get_axis(0))  # RC4

                self.drone.send_rc_control(lr, fb, ud, yaw)

            time.sleep(0.1)  # Pequeña pausa para no saturar la consola

    def map_axis(self,value):
        """
        Convierte valor del eje (-1 a 1) a rango RC (-100 a 100)
        """
        if value < 0:
            value = -value
            return int(-value * value * value*value * 100)
        else:
            return int(value * value * value * value* 100)

    def startJoystic (self):


        if not self.usingJoystic:
            # Inicializar pygame y el módulo de joystick
            pygame.init()
            pygame.joystick.init()

            # Verificar si hay joysticks conectados
            if pygame.joystick.get_count() == 0:
                messagebox.showerror("Error",
                                     "No hay joystic conectado",
                                     parent=self.windowImage)

                pygame.quit()
            else:
                # Obtener el primer joystick
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.usingJoystic = True
                self.connect()
                threading.Thread (target = self.joysticLoop).start()
                self.joysticButton["bg"]="green"
                self.joysticButton["fg"] = "white"

        else:
            self.usingJoystic = False
            self.joysticButton["bg"] = "dark orange"
            self.joysticButton["fg"] = "black"
            self.joystick.quit()
            pygame.quit()


