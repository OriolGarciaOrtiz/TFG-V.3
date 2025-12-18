from ultralytics import YOLO
from djitellopy import Tello
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox


class DroneController:
    def __init__(self):
        self.is_connected = False
        self.prev_error_x = 0
        self.prev_error_y = 0
        self.prev_error_z = 0
        self.integral_x = 0
        self.integral_y = 0
        self.integral_z = 0

        self.model = None
        self.model2 = None
        self.model3 = None

        # Llama a la función de carga de modelos
        self.load_yolo_models()

        self.IMG_SAVE_PATH = r"taller-dron-Tello\Lib\Img_Calibracion"
        self.PARAM_SAVE_PATH = r"C:\Tello\taller-dron-Tello\Lib\Parameters"
        os.makedirs(self.IMG_SAVE_PATH, exist_ok=True)
        os.makedirs(self.PARAM_SAVE_PATH, exist_ok=True)

        self.me = Tello()
        self.me.for_back_velocity = 0
        self.me.left_right_velocity = 0
        self.me.up_down_velocity = 0
        self.me.yaw_velocity = 0
        self.me.speed = 0

        # try:
        #     self.model = YOLO("Modelo1(CocheRCp).pt") #Cambiado
        #     print("YOLO model loaded successfully.")
        # except Exception as e:
        #     print("Could not load YOLO model:", e)
        #     self.model = None
        #try:
            #self.model2 = YOLO("red_Prueba.pt")
            #print("YOLO Game Mode model loaded successfully.")
        #except Exception as e:
            #print("Could not load Game Mode model:", e)
            #self.model2 = None

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
            #threading.Thread(target=lambda: self.me.move_up(distance)).start()
            self.me.move_up(distance)
        else:
            print("[DroneController] Drone not connected. Cannot go up.")

    def load_yolo_models(self):
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana principal de Tkinter

        messagebox.showinfo(
            "Instrucciones",
            "Selecciona primero el entrenamiento del coche pequeño,\n"
            "después el modelo HBDC,\n"
            "y por último el del coche grande.")

        files = filedialog.askopenfilenames(
            title="Selecciona los 3 archivos de modelos YOLO",
            filetypes=[("YOLO model files", "*.pt")],)

        if len(files) != 3:
            messagebox.showerror(
                "Error",
                "Debes seleccionar exactamente 3 archivos de modelos.")
            return

        try:
            self.model = YOLO(files[0])
            print(f"Modelo 1 cargado: {files[0]}")
        except Exception as e:
            print("No se pudo cargar el primer modelo:", e)
            self.model = None

        try:
            self.model2 = YOLO(files[1])
            print(f"Modelo 2 cargado: {files[1]}")
        except Exception as e:
            print("No se pudo cargar el segundo modelo:", e)
            self.model2 = None

        try:
            self.model3 = YOLO(files[2])
            print(f"Modelo 3 cargado: {files[2]}")
        except Exception as e:
            print("No se pudo cargar el tercer modelo:", e)
            self.model3 = None

        root.destroy()