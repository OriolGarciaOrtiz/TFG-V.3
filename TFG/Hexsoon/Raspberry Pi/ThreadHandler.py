import threading
from HexsoonGUI import GUI
import asyncio
from Services.VideoRTC import DroneVideoTrack, WebRTCServer
from Services.YoloService import ServiceYolo
from Services.MQTTService import MQTT
from colorama import init, Fore
import time

class HandlerThreads:

    def __init__(self, gui: GUI):
        
        self.target_gui = gui

        init(autoreset=True)

        self.video_track_original = DroneVideoTrack("original")
        self.video_track_detected = DroneVideoTrack("detected")

        self.RTC = WebRTCServer(self.video_track_original, self.video_track_detected)
        self.yolo = ServiceYolo(target_gui = self.target_gui)
        self.mqtt = MQTT(target_gui=self.target_gui)

        self.RTC_thread = threading.Thread(target=lambda: asyncio.run(self.RTC.run()), daemon=True)
        self.RTC_thread.start()
        self.RTC.running = True



    def handle_video_receiver_thread(self):
        # Actualiza frames siempre
        if self.target_gui.frame_display is not None:
            self.video_track_original.frame = self.target_gui.frame_display.copy()
        if self.target_gui.img_contour is not None:
            self.video_track_detected.frame = self.target_gui.img_contour.copy()

        self.RTC.camera_option = self.target_gui.controller.type_camera_option

        # Solo activar/desactivar la transmisión de frames según la cámara
        if self.target_gui.controller.type_camera_option == "Raspi Cam":
            self.video_track_original.is_connected = True
            self.video_track_detected.is_connected = True
        else:
            self.video_track_original.is_connected = False
            self.video_track_detected.is_connected = False


    
    def handle_mqtt_thread(self):

        if self.mqtt.running: 

            if self.target_gui.controller.type_camera_option != "Raspi Cam":

                self.mqtt.running = False

                print(Fore.GREEN + "Stoping MQTT Thread")

        else:

            if self.target_gui.controller.type_camera_option == "Raspi Cam": 

                self.mqtt.running = True

                threading.Thread(target=self.mqtt.run_loop, daemon=True).start()

                print(Fore.GREEN + "Starting MQTT Thread")


    def handle_yolo_service(self):

        if not self.yolo.running and self.target_gui.controller.detection_mode == "Neural Network":

            self.yolo.running = True

            threading.Thread(target=self.yolo.start, daemon=True).start()

            print(Fore.GREEN + "Starting Yolo Service Thread")


        if self.yolo.running and self.target_gui.controller.detection_mode != "Neural Network":

            self.yolo.running = False

            print(Fore.GREEN + "Stoping Yolo Service Thread")


    def start(self):

        print(Fore.GREEN + "Starting Threads")

        while self.target_gui.running: 

            self.handle_video_receiver_thread()

            self.handle_mqtt_thread()

            self.handle_yolo_service()

            time.sleep(1/self.target_gui.FPS)

    
    def stop(self):

        self.target_gui.running = False
        self.RTC.running = False
        self.yolo.running = False
        self.mqtt.running = False

        print(Fore.GREEN + "Stoping all Threads")

