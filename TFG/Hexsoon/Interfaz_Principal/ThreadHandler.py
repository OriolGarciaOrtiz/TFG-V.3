import threading
from HexsoonGUI import GUI
from Services.WebRTCService import DroneVideoReceiver
from Services.MissionPlannerService import MissionPlanner
from Services.MQTTService import MQTT
from Services.VideoService import ServiceVideo
from Services.YoloService import ServiceYolo
from Services.CapFrameService import ServiceCapFrame
from colorama import init, Fore
import time

class HandlerThreads:

    def __init__(self, gui: GUI):
        
        self.target_gui = gui

        init(autoreset=True)

        self.receiver = DroneVideoReceiver(target_gui = self.target_gui)
        self.mission_planner = MissionPlanner(target_gui = self.target_gui)
        self.mqtt = MQTT(target_gui = self.target_gui)
        self.video = ServiceVideo(target_gui = self.target_gui)
        self.yolo = ServiceYolo(target_gui = self.target_gui)
        self.frame_cap = ServiceCapFrame(target_gui = self.target_gui)


    def handle_video_receiver_thread(self):

        if self.receiver.running: 

            if self.target_gui.controller.type_camera_option != "Raspi Cam":

                self.receiver.stop()

                print(Fore.GREEN + "Stoping Video Reciever Thread")

        else:

            if self.target_gui.controller.type_camera_option == "Raspi Cam": 

                self.receiver.running = True

                threading.Thread(target=self.receiver.start, daemon=True).start()

                print(Fore.GREEN + "Starting Video Reciever Thread")

    
    def handle_mission_planner_thread(self):

        if not self.mission_planner.running and self.target_gui.running:

            self.mission_planner.running = True

            threading.Thread(target=self.mission_planner._mission_loop, daemon=True).start()

            print(Fore.GREEN + "Starting Mission Planner Thread")

        if not self.target_gui.running:

            self.mission_planner.running = False

            print(Fore.GREEN + "Stoping Mission Planner Thread")

    
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

    
    def handle_video_service_thread(self):

        if not self.video.running and self.target_gui.running:

            self.video.running = True

            threading.Thread(target=self.video.start, daemon=True).start()

            print(Fore.GREEN + "Starting Video Service Thread")

        if not self.video.running:

            self.video.running = False

            print(Fore.GREEN + "Stoping Video Service Thread")


    def handle_yolo_service(self):

        if not self.yolo.running and self.target_gui.controller.detection_mode == "Neural Network":

            self.yolo.running = True

            threading.Thread(target=self.yolo.start, daemon=True).start()

            print(Fore.GREEN + "Starting Yolo Service Thread")


        if self.yolo.running and self.target_gui.controller.detection_mode != "Neural Network":

            self.yolo.running = False

            print(Fore.GREEN + "Stoping Yolo Service Thread")


    def handle_frame_cap_service(self):

        if not self.frame_cap.running and self.target_gui.controller.is_connected:

            self.frame_cap.running = True

            threading.Thread(target=self.frame_cap.start, daemon=True).start()

            print(Fore.GREEN + "Starting Frame Capture Service Thread")

        if not self.target_gui.running:

            self.frame_cap.running = False

            print(Fore.GREEN + "Stoping Frame Capture Service Thread")


    def start(self):

        print(Fore.GREEN + "Starting Threads")

        while self.target_gui.running: 

            self.handle_video_receiver_thread()

            self.handle_mission_planner_thread()

            self.handle_mqtt_thread()

            self.handle_video_service_thread()

            self.handle_yolo_service()

            self.handle_frame_cap_service()

            time.sleep(1/self.target_gui.FPS)

    
    def stop(self):

        self.target_gui.running = False
        self.frame_cap.running = False
        self.receiver.running = False
        self.mission_planner.running = False
        self.mqtt.running = False
        self.video.running = False

        print(Fore.GREEN + "Stoping all Threads")

