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

        self.IMG_SAVE_PATH = r"taller-dron-Tello\Lib\Img_Calibracion"
        self.PARAM_SAVE_PATH = r"taller-dron-Tello\Lib\Parameters"
        os.makedirs(self.IMG_SAVE_PATH, exist_ok=True)
        os.makedirs(self.PARAM_SAVE_PATH, exist_ok=True)

        self.me = Tello()
        self.me.for_back_velocity = 0
        self.me.left_right_velocity = 0
        self.me.up_down_velocity = 0
        self.me.yaw_velocity = 0
        self.me.speed = 0

        try:
            self.model = YOLO(r"Yolo Models\RC_exterior.pt")
            print("YOLO model loaded successfully.")
        except Exception as e:
            print("Could not load YOLO model:", e)
            self.model = None
        try:
            self.model2 = YOLO(r"Yolo Models\red_Prueba.pt")
            print("YOLO Game Mode model loaded successfully.")
        except Exception as e:
            print("Could not load Game Mode model:", e)
            self.model2 = None

    def safe_takeoff(self):
        if self.is_connected:
            threading.Thread(target=self.me.takeoff).start()

    def landing(self):
        if self.is_connected:
            threading.Thread(target=self.me.land).start()

    def emergency(self):
        if self.is_connected:
            threading.Thread(target=self.me.emergency).start()

    def go_up(self, distance=70):
        if self.is_connected:
            threading.Thread(target=lambda: self.me.move_up(distance)).start()
        else:
            print("[DroneController] Drone not connected. Cannot go up.")