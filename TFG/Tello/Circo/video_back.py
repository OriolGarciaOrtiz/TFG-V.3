import ssl
from tkinter import *
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
from tkinter import messagebox
from djitellopy import Tello
import time
import paho.mqtt.client as mqtt
import cv2
import threading
import os
import base64
import queue
from Gallery import GalleryMedia


class escenarioVideo:
    def Open(self, master, selectedBroker):
        self.drone = Tello()

        #self.galleryVideo = galleryVideo()

        myFont3 = font.Font(family='Arial', size=10, weight='bold')

        self.windowVideo = Toplevel(master)
        self.galleryVideo = GalleryMedia()


        # Variables
        self.detectingBool = False  # Booleano si detecta o no la cámara del dron
        self.recording = False  # Booleano si está grabando vídeo o no
        self.count = 0
        self.connected = False
        self.take_off = False
        self.sending = False
        self.frame_queue = queue.Queue()

        # Configuration
        self.windowVideo.geometry("900x600")
        self.windowVideo.rowconfigure(0, weight=1)
        self.windowVideo.rowconfigure(1, weight=1)
        self.windowVideo.rowconfigure(2, weight=1)
        self.windowVideo.rowconfigure(3, weight=1)

        self.windowVideo.columnconfigure(1, weight=1)
        self.windowVideo.columnconfigure(2, weight=1)
        self.windowVideo.columnconfigure(3, weight=1)

        self.windowVideo.title("Video Page")

        self.imageCommand = Image.open("assets/cuadrado.png")
        self.imageCommand = self.imageCommand.resize((460, 450))
        self.photo = ImageTk.PhotoImage(self.imageCommand)
        image_label = tk.Label(self.windowVideo, image=self.photo)
        image_label.place(x=460, y=85)

        # Title label
        self.titlelabel = tk.Label(self.windowVideo, text="TAKE YOUR VIDEO!", height=3)
        self.titlelabel.place(x=400, y=15, anchor="nw")
        self.titlelabel['font'] = myFont3

        # Command label
        self.commandlabel = tk.Label(self.windowVideo, text="Drone Commands", height=1)
        self.commandlabel.place(x=600, y=95, anchor="nw")
        self.commandlabel['font'] = myFont3

        # Connect button
        self.connectDButton = Button(self.windowVideo, text="Connect", height=1, bg='#367E18',
                                     fg='#F8F8FF', command=self.connect)
        self.connectDButton.place(x=633, y=155, anchor="nw")
        self.connectDButton['font'] = myFont3

        # TakeOff button
        self.takeoffDButton = Button(self.windowVideo, text="Take Off", height=1, bg='#FF6103',
                                     fg='#F8F8FF', command=self.takeoff)
        self.takeoffDButton.place(x=590, y=205, anchor="nw")
        self.takeoffDButton['font'] = myFont3

        # Land button
        self.landDButton = Button(self.windowVideo, text="Landing", height=1, bg='#FF6103',
                                  fg='#F8F8FF', command=self.land)
        self.landDButton.place(x=670, y=205, anchor="nw")
        self.landDButton['font'] = myFont3

        # Forward button
        self.forwardButton = Button(self.windowVideo, text="Forward ", height=1, bg='#FF8C00',
                                    fg='#F8F8FF', command=self.forward)
        self.forwardButton.place(x=630, y=265, anchor="nw")
        self.forwardButton['font'] = myFont3

        # Backward button
        self.backwardButton = Button(self.windowVideo, text="Backward", height=1, bg='#FF8C00',
                                     fg='#F8F8FF', command=self.backward)
        self.backwardButton.place(x=630, y=345, anchor="nw")
        self.backwardButton['font'] = myFont3

        # FLip button
        self.flipButton = Button(self.windowVideo, text="  Flip  ", height=1, bg='#FF8C00',
                                 fg='#F8F8FF', command=self.flip)
        self.flipButton.place(x=640, y=305, anchor="nw")
        self.flipButton['font'] = myFont3

        # Left button
        self.leftButton = Button(self.windowVideo, text="  Left  ", height=1, bg='#FF8C00',
                                 fg='#F8F8FF', command=self.left)
        self.leftButton.place(x=570, y=305, anchor="nw")
        self.leftButton['font'] = myFont3

        # Right button
        self.rightButton = Button(self.windowVideo, text=" Right ", height=1, bg='#FF8C00',
                                  fg='#F8F8FF', command=self.right)
        self.rightButton.place(x=710, y=305, anchor="nw")
        self.rightButton['font'] = myFont3

        # Up button
        self.upButton = Button(self.windowVideo, text="  Up  ", height=1, bg='#FF6103',
                               fg='#F8F8FF', command=self.up)
        self.upButton.place(x=610, y=415, anchor="nw")
        self.upButton['font'] = myFont3

        # Down button
        self.downButton = Button(self.windowVideo, text="Down", height=1, bg='#FF6103',
                                 fg='#F8F8FF', command=self.down)
        self.downButton.place(x=670, y=415, anchor="nw")
        self.downButton['font'] = myFont3

        # Record button
        self.recordButton = Button(self.windowVideo, text="Record", height=1, bg='#0000FF',
                               fg='#F8F8FF', command=self.recordVideo)
        self.recordButton.place(x=170, y=530, anchor="nw")
        self.recordButton['font'] = myFont3

        # Stop button
        self.stopButton = Button(self.windowVideo, text="Stop", height=1, bg='#0000FF',
                                 fg='#F8F8FF', command=self.stopVideo)
        self.stopButton.place(x=240, y=530, anchor="nw")
        self.stopButton['font'] = myFont3

        # Send picture button
        self.sendButton = Button(self.windowVideo, text="Send", height=1, bg='#0000FF',
                                    fg='#F8F8FF', command=self.sendVideo)
        self.sendButton.place(x=300, y=530, anchor="nw")
        self.sendButton['font'] = myFont3

        # Gallery button
        self.galleryButton = Button(self.windowVideo, text="Video gallery", height=1, bg='#458B74',
                                    fg='#F8F8FF', command=self.gallery)
        self.galleryButton.place(x=780, y=20, anchor="nw")
        self.galleryButton['font'] = myFont3

        # Canvas
        self.canvas1 = Canvas(self.windowVideo, width=320, height=240, bg='white')
        self.canvas1.place(x=90, y=110, anchor="nw")

        # Close window button
        self.closeDButton = Button(self.windowVideo, text="Close", height=1, bg='#8B0000',
                                 fg='#F8F8FF', command=self.closeVideo)
        self.closeDButton.place(x=840, y=560, anchor="nw")
        self.closeDButton['font'] = myFont3

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
            self.connectDButton['text'] = str(self.drone.get_battery())
            self.connectDButton.place(x=650, y=155, anchor="nw")
            self.connectDButton['bg'] = '#8B0000'
            print("Te has conectado correctamente al dron!")

            if not self.detectingBool:
                self.detectingBool = True
                x = threading.Thread(target=self.detecting)
                x.start()
            print("Se estan transmitiendo las imágenes de la cámara del dron")

        except Exception as e:
            messagebox.showerror("Error de conexión",
                                 "No se pudo conectar al dron. Por favor, inténtalo de nuevo.\nError: " + str(e),
                                 parent=self.windowVideo)

    def detecting(self):
        self.drone.streamon()
        cv2.namedWindow("Tello Camera", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Tello Camera", 640, 480)

        while self.detectingBool and self.connected:
            frame = self.drone.get_frame_read().frame  # Captura un frame desde la cámara del Tello
            #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow("Tello Camera", frame)  # Muestra el frame en una ventana
            cv2.waitKey(1)

    def takeoff(self):
        if self.connected:
            self.drone.takeoff()
            time.sleep(2)
            self.take_off = True
            self.takeoffDButton['text'] = 'flying'
            self.takeoffDButton['bg'] = '#8B0000'
            self.state = 'flying'
        else:
            messagebox.showwarning("Error", "Antes de despegar debes conectarte al dron", parent=self.windowVideo)

    def land(self):
        self.drone.land()
        messagebox.showwarning("Success", "Ya estamos en casa", parent=self.windowVideo)

    def forward(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(50, 0, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowVideo)

    def backward(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(-50, 0, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowVideo)

    def flip(self):
        if self.take_off and self.connected:
            self.drone.send_control_command("flip l")
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowVideo)

    def left(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, -50, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowVideo)

    def right(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 50, 0, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowVideo)

    def up(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 0, 50, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowVideo)

    def down(self):
        if self.take_off and self.connected:
            self.drone.go_xyz_speed(0, 0, -50, 100)
            time.sleep(1)
        else:
            messagebox.showwarning("Error", "Primero despega el dron", parent=self.windowVideo)

    def recordVideo(self):
       if not self.recording:
           self.recording = True
           self.video_frames = []
           x = threading.Thread(target=self.recordingVideo)
           x.start()
           ''' y = threading.Thread(target=self.recordMQTT)
           y.start()'''
       else:
           messagebox.showwarning("Error", "Ya estás grabando un vídeo!", parent=self.windowVideo)

    '''
    def recordMQTT(self):
        # Enviar el streaming
        print("Sending frames")
        quality = 20
        while self.sending:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            # _, buffer = cv2.imencode('.jpg', self.frame)
            buffer_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            _, frame = cv2.imencode(".jpg", buffer_rgb, encode_param)
            print('size: ', frame.shape[0])  # tamaño de la imagen
            frame_base64 = base64.b64encode(frame)
            self.client.publish("VideoAnna", payload=frame_base64, qos=2)
            time.sleep(0.10)
    '''
    def recordingVideo(self):
        print("Recording")
        self.sending = True
        quality = 20
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        while self.recording:
            self.frame = self.drone.get_frame_read().frame
            self.video_frames.append(self.frame)
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            self.imgPicture = Image.fromarray(frame_rgb)
            self.imgPicture = self.imgPicture.resize((320,240))

            self.photo = ImageTk.PhotoImage(self.imgPicture)
            self.canvas1.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas1.image = self.photo
            _, encodedframe = cv2.imencode(".jpg",self.frame, encode_param)
            frame_base64 = base64.b64encode(encodedframe)
            self.client.publish("VideoAnna", payload=frame_base64, qos=2)

            '''frames_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.video_frames.append(frames_rgb)'''

            time.sleep(0.2)


    def stopVideo(self):
        if self.recording:
            self.recording = False
            self.sending = False
            self.canvas1.delete("all")
            print("Stop Recording")
        else:
            messagebox.showwarning("Error", "No has empezado a grabar!", parent=self.windowVideo)


    def sendVideo(self):
        # print('Frames: ', self.video_frames)
        self.count += 1

        self.save_video(self.video_frames)

        self.video_path = "assets/telloVideo/output_video" + str(self.count) + ".mp4"

        with open(self.video_path, "rb") as video_file:
            video_data = video_file.read()
            video_base64 = base64.b64encode(video_data)
            self.client.publish("FileAnna", payload=video_base64, qos=2)
            print("Vídeo enviado")


    def save_video(self, frames):
        try:
            self.file_name = "output_video" + str(self.count) + ".mp4"
            video_output_path = os.path.join("assets/telloVideo", self.file_name)

            print(frames[0].shape)
            frame_height, frame_width, _ = frames[0].shape
            video_writer = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*'mp4v'), 30,
                                           (frame_width, frame_height))

            for frame in frames:
                video_writer.write(frame)

            video_writer.release()
            print("Vídeo Saved")

        except Exception as e:
            messagebox.showerror("Error de conexión",
                                 "No se pudo guardar el vídeo correctamente!\nError: " + str(e),
                                 parent=self.windowVideo)

    def gallery(self):
        type = 'Video'
        self.galleryVideo.Open(self.windowVideo, type, self.client)

    def closeVideo(self):
        self.windowVideo.destroy()
        cv2.destroyAllWindows()


'''
class galleryVideo:

    def Open(self, master):
        self.drone = Tello()

        myFont3 = font.Font(family='Arial', size=10, weight='bold')

        self.windowVideoGallery = Toplevel(master)
        self.selected_video = None
        self.v_videos = []
        self.canvas_list = []
        self.number_img = 0

        # MQTT conexión
        self.global_broker_address = "broker.hivemq.com"
        self.global_broker_port = 8000  # 8883

        self.client = mqtt.Client("VideoService", transport="websockets")
        # self.client.username_pw_set("dronsEETAC", "mimara1456.")
        self.client.connect(self.global_broker_address, self.global_broker_port)
        self.client.loop_start()

        # Title label
        self.titlelabel = tk.Label(self.windowVideoGallery, text="Video Gallery", height=2)
        self.titlelabel.place(x=500, y=15, anchor="nw")
        self.titlelabel['font'] = myFont3

        self.windowVideoGallery.geometry("1200x600")
        self.windowVideoGallery.rowconfigure(0, weight=1)
        self.windowVideoGallery.rowconfigure(1, weight=1)
        self.windowVideoGallery.rowconfigure(2, weight=1)
        self.windowVideoGallery.rowconfigure(3, weight=1)

        self.windowVideoGallery.columnconfigure(1, weight=1)
        self.windowVideoGallery.columnconfigure(2, weight=1)
        self.windowVideoGallery.columnconfigure(3, weight=1)

        # Send videos from gallery button
        self.sendGallerybtn = Button(self.windowVideoGallery, text="Send Video", height=1, bg='#0000FF',
                                     fg='#F8F8FF', command=self.sendGallery)
        self.sendGallerybtn.place(x=500, y=530, anchor="nw")
        self.sendGallerybtn['font'] = myFont3

        # Close gallery button
        self.closeGalleryButton = Button(self.windowVideoGallery, text="Close", height=1, bg='#8B0000',
                                         fg='#F8F8FF', command=self.closeGallery)
        self.closeGalleryButton.place(x=1140, y=550, anchor="nw")
        self.closeGalleryButton['font'] = myFont3

        self.url_video = "assets/telloVideo/"
        self.create_vector_video(self.url_video)

        if len(self.v_videos) < 0:
            messagebox.showerror("Error", "No hay guardado ningún vídeo")
        else:
            self.create_gallery()

    def create_vector_video(self, folder_path):

        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.mp4'):
                file_path = os.path.join(folder_path, file_name)
                self.v_videos.append(file_path)

    def create_gallery(self):
        num_video_per_row = 6  # Número deseado de imágenes por fila
        max_video_size = 300  # Tamaño máximo de las imágenes
        min_video_size = 200  # Tamaño mínimo de las imágenes
        starting_row = 0
        padding = 20

        total_videos = len(self.v_videos)

        for i, video_path in enumerate(self.v_videos):
            #img = Image.open(video_path)

            cap = cv2.VideoCapture(video_path)

            ret, frame = cap.read()

            thumbnail = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if total_videos <= num_video_per_row:
                num_video_per_row = 4
                image_size = max_video_size
            else:
                image_size = min_video_size

            thumbnail.thumbnail((image_size, image_size))
            photo = ImageTk.PhotoImage(thumbnail)

            canvas = tk.Canvas(self.windowVideoGallery, width=image_size, height=image_size)
            canvas.create_image(0, 0, anchor="nw", image=photo)

            row_position = starting_row + i // num_video_per_row
            col_position = i % num_video_per_row

            self.number_img += 1

            canvas.grid(row=row_position, column=col_position, padx=padding, pady=padding)
            canvas.bind("<Button-1>",
                        lambda event, img_path=video_path, count=self.number_img: self.select_video(img_path, count))

            self.canvas_list.append((canvas, photo))


    def select_video(self, vd_path, count):
        self.selected_video = vd_path
        print(f"Vídeo seleccionado: {count}")

    def sendGallery(self):
        try:
            if self.selected_video:

                video_path = self.selected_video
                with open(video_path, "rb") as video_file:
                    video_data = video_file.read()
                    video_base64 = base64.b64encode(video_data)
                    self.client.publish("FileAnna", payload=video_base64, qos=2)

            else:
                print("No hay vídeo para enviar")
                return None
        except Exception as e:
            messagebox.showerror("Error de conexión",
                                 "No se pudo enviar el vídeo. Por favor, inténtalo de nuevo.\nError: " + str(e),
                                 parent=self.windowVideoGallery)

    def closeGallery(self):
        self.windowVideoGallery.destroy()'''
