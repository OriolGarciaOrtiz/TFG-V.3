from dronLink.Dron import Dron
from ultralytics import YOLO
from pymavlink import mavutil
from dronLink.modules.dron_move import _prepare_command_mov
#from picamera2 import Picamera2
import cv2

class HexsoonController:
    def __init__(self):
        self.is_connected = False
        self.is_deteceted = False
        self.is_armed = False
        self.cap = None
        try:
            self.model = YOLO("Yolo Models/best_RC_Final.pt")
            print("YOLO model loaded successfully.")
        except Exception as e:
            print("Could not load YOLO model:", e)
            self.model = None

        self.integral_x = 0
        self.integral_y = 0

        self.prev_error_x = 0
        self.prev_error_y = 0

        self.left_right = 0
        self.for_back = 0
        self.up_down = 0
        self.yaw = 0


    def init_camera(self, resolution=(320, 240)):
        try:

            '''
            self.cap = Picamera2()
            config = self.cap.create_video_configuration(
                main={"size": resolution, "format": "RGB888"}
            )
            self.cap.configure(config)
            self.cap.start()
            '''
            self.cap = 1

            print("Picamera2 initialized.")
        except Exception as e:
            print("Failed to initialize Picamera2:", e)
            self.cap = None

    def get_frame(self):
        if self.cap is None:
            return None
        try:

            frame = cv2.imread("IMG_20251112_155906_TIMEBURST1.jpg")
            #frame = self.cap.capture_array()

            return frame
        except:
            return None


    def connect_drone(self):

        try:
            
            self.is_connected = True
            
            print("Drone succesfully connetcted")

            if self.cap is None:
                raise Exception("Camera not initialized")
                
        except:
            
            self.is_connected = False


    def disconnect_drone(self): 
        if self.is_connected: 
            self.is_connected =  False 


    def do_actions(self, connect_click: bool, disconnect_click: bool):

        if connect_click:
            
            self.connect_drone()

        if disconnect_click:
            self.disconnect_drone()
