from ultralytics import YOLO
from djitellopy import Tello
import os
import threading


class DroneController:
    def __init__(self):
        self.is_connected = False
        self.prev_error_x = 0
        self.prev_error_y = 0
        self.prev_error_z = 0
        self.integral_x = 0
        self.integral_y = 0
        self.integral_z = 0

        base_dir = os.path.dirname(__file__)

        self.IMG_SAVE_PATH = os.path.join(base_dir, "taller-dron-Tello", "Lib", "Img_Calibracion")
        self.PARAM_SAVE_PATH = os.path.join(base_dir, "taller-dron-Tello", "Lib", "Parameters")

        os.makedirs(self.IMG_SAVE_PATH, exist_ok=True)
        os.makedirs(self.PARAM_SAVE_PATH, exist_ok=True)

        self.me = Tello()
        self.me.for_back_velocity = 0
        self.me.left_right_velocity = 0
        self.me.up_down_velocity = 0
        self.me.yaw_velocity = 0
        self.me.speed = 0

        model_path = os.path.join(base_dir, "taller-dron-Tello", "Lib", "best_RC_Final.pt")
        try:
            self.model = YOLO(model_path)
            print("YOLO model loaded successfully.")
        except Exception as e:
            print("Could not load YOLO model:", e)
            self.model = None

    def safe_takeoff(self):
        if self.is_connected:
            threading.Thread(target=self.me.takeoff).start()

    def landing(self):
        if self.is_connected:
            threading.Thread(target=self.me.land).start()

    def emergency(self):
        if self.is_connected:
            threading.Thread(target=self.me.emergency).start()