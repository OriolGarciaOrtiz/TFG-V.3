from ultralytics import YOLO
from djitellopy import Tello
import os
import threading
from tkinter import filedialog


class DroneController:
    def __init__(self):
        self.is_connected = False
        self.prev_error_x = 0
        self.prev_error_y = 0
        self.prev_error_z = 0
        self.integral_x = 0
        self.integral_y = 0
        self.integral_z = 0

        self.model: YOLO | None = None

        self.IMG_SAVE_PATH = r"taller-dron-Tello\Lib\Img_Calibracion"
        self.PARAM_SAVE_PATH = r"taller-dron-Tello\Lib\Parameters"
        os.makedirs(self.IMG_SAVE_PATH, exist_ok=True)
        os.makedirs(self.PARAM_SAVE_PATH, exist_ok=True)

        self.me = Tello()
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 0

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
            self.me.move_up(distance)
        else:
            print("[DroneController] Drone not connected. Cannot go up.")

    def load_yolo_model(self):

        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            initialdir="Yolo Models",
            filetypes=[("PyTorch model (*.pt)", "*.pt")]
        )

        try: 

            self.model = YOLO(archivo)
            print("YOLO model correctly loaded")

        except:

            print("Error loading YOLO model")