from HexsoonClass import *
import pygetwindow as gw
import mss
from pymavlink import mavutil
from dronLink.modules.dron_move import _prepare_command_mov
import win32gui
import win32ui
import win32con
import win32api
import ctypes
import cv2
import numpy as np
import tkinter as tk
from tkinter import Scale, messagebox, OptionMenu, Label, StringVar
from PIL import Image, ImageTk
import threading
import paho.mqtt.client as mqtt
import json
import time


class GUI:
    def __init__(self, root):
        self.root = root
        self.is_connected = False
        self.controller = HexsoonController()
        self.panel_width = 320
        self.panel_height = 240
        self.setup_gui()

        '''  Data that has to be sent from the drone to the GUI  '''

        self.cap_normal = None
        self.cap_detected = None

        self.left_right = 0
        self.for_back = 0
        self.up_down = 0


        self.BROKER = "broker.hivemq.com" 
        self.PORT = 1883
        self.TOPIC_SUB = "test/chat/pub"  # Escucha al publicador
        self.TOPIC_PUB = "test/chat/sub"  # Envía respuesta

        self.client = mqtt.Client()
        self.client.on_message = self.receive_data
        self.client.connect(self.BROKER, self.PORT, 60)
        self.client.subscribe(self.TOPIC_SUB)
        self.client.loop_start()

        self.clock_start = time.monotonic()

    def setup_gui(self):
        self.root.title("Hexsoon Drone Controller")
        self.root.geometry("1920x1080")
        self.create_connection_widgets()
        self.create_video_panels()
        self.create_mode_selectors()
        self.create_control_buttons()
        self.create_hsv_sliders()
        self.create_pid_controls()
        self.create_velocity_display()
        self.create_status_label()

    def receive_data(self): 
        pass

    def set_data(self):
        pass

    def prepare_data(self) -> str:
        msg_dict: dict = {'left_right': self.left_right,
                        'for_back': self.for_back,
                        'up_down': self.up_down}

        msg: str = json.dumps(msg_dict)
        return msg

    def send_data(self):
        
        '''
         Se enviaran los mensages cada 3 segundos del de la GUI para no tener que saturar 
         las comunicaciones
        '''

        msg = self.prepare_data()

        now = time.monotonic()

        if now - self.clock_start >= 3:
            self.client.publish(msg)

            self.clock_start = now


    def run_in_thread(self, target, *args, status_msg="Executing..."):

        #Helper para ejecutar acciones en segundo plano y que el tk no se quede pillado en las funciones de MavLink

        def task():
            try:
                self.log(status_msg)
                target(*args)
                self.log("Action Complete")
            except Exception as e:
                self.log(f"Error: {e}")

        threading.Thread(target=task, daemon=True).start()


    def create_connection_widgets(self):
        self.connected_label = Label(self.root, text="Not Connected", font=("Arial", 14))
        self.connected_label.grid(row=0, column=0, padx=10, pady=10)

        self.connect_button = tk.Button(self.root, text="Connect", command=self.controller.connect_drone)
        self.connect_button.grid(row=0, column=1, padx=10, pady=10)

        self.battery_label = Label(self.root, text="Battery: -", font=("Arial", 14))
        self.battery_label.grid(row=0, column=2, padx=10, pady=10)

    def create_status_label(self):
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(self.root, textvariable=self.status_var, font=("Consolas", 12), fg="white", bg="black")
        status_label.place(x=10, y=735, width=1000, height=20)

    def log(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))

    def create_control_buttons(self):
        # Arm Button
        self.arm_button = tk.Button(self.root,text="Arm",command=lambda: self.run_in_thread(self.arm, status_msg="Arming..."))
        self.arm_button.place(x=560, y=70)


        self.takeoff_height = tk.Entry(self.root, width=10)
        self.takeoff_height.insert(0, "8")
        self.takeoff_height.place(x=480, y=75)

        # Take off button
        self.take_off_button = tk.Button(self.root,text="Take Off",command=lambda: self.run_in_thread(lambda: self.controller.take_off_drone(int(self.takeoff_height.get())),status_msg="Taking off..."))
        self.take_off_button.place(x=400, y=70)

        # Landing Button
        self.landing_button = tk.Button(self.root,text="Landing",command=lambda: self.run_in_thread(self.land, status_msg="Landing..."))
        self.landing_button.place(x=400, y=120)

        # Disconnect button
        self.disconnect_button = tk.Button(self.root,text="Disconnect",command=lambda: self.run_in_thread(self.controller.disconnect_drone, status_msg="Disconnecting..."))
        self.disconnect_button.place(x=640, y=70)

        # RTL button
        self.RTL_button = tk.Button(self.root,text="RTL",command=lambda: self.run_in_thread(self.controller.Return_To_Launch,status_msg="Returning to launch point..."))
        self.RTL_button.place(x=480, y=120)



    def create_mode_selectors(self):
        self.simulation_var = tk.StringVar(value="Simulation")
        simulation_dropdown = tk.OptionMenu(self.root, self.simulation_var, "Simulation", "Practice")
        simulation_dropdown.grid(row=0, column=6, padx=10, pady=10)

        detection_label = tk.Label(self.root, text="Detection Mode:", font=("Arial", 14))
        detection_label.grid(row=0, column=7, padx=(20, 5), pady=10)

        self.detection_var = tk.StringVar(value="Color Contour")
        detection_dropdown = tk.OptionMenu(self.root, self.detection_var, "Color Contour", "Neural Network")
        detection_dropdown.grid(row=0, column=8, padx=10, pady=10)

        PID_values = ["P", "I", "D", "PD", "PI", "PID", "None"]
        Label(self.root, text="Controller used =", font=("Arial", 14)).place(x=1200, y=100)
        self.opt = tk.StringVar(value="PID")
        dropdown_x = tk.OptionMenu(self.root, self.opt, *PID_values)
        dropdown_x.place(x=1350, y=95)

        Mode_cam = ["Front View", "Bottom View"]
        self.opt_cam = tk.StringVar(value="Front View")
        dropdown_mode = tk.OptionMenu(self.root, self.opt_cam, *Mode_cam)
        dropdown_mode.place(x=1325, y=20)
        Label(self.root, text="Mode used =", font=("Arial", 14)).place(x=1200, y=25)

    def create_pid_controls(self):
        self.Kp_x = tk.DoubleVar(value=0.42)
        self.Ki_x = tk.DoubleVar(value=0.0005)
        self.Kd_x = tk.DoubleVar(value=1.9)

        self.Kp_y = tk.DoubleVar(value=0.42)
        self.Ki_y = tk.DoubleVar(value=0.0005)
        self.Kd_y = tk.DoubleVar(value=1.9)

        self.create_pid_slider_set("X", 150)
        self.create_pid_slider_set("Y", 250)

        Label(self.root, text="Max velocity:", font=("Arial", 12)).place(x=400, y=370)
        self.max_velocity = tk.DoubleVar(value=60)
        velocity_slider = tk.Scale(self.root, from_=0, to=60, resolution=1, orient="horizontal",
                                   variable=self.max_velocity, length=300)
        velocity_slider.place(x=400, y=400)

    def create_pid_slider_set(self, axis, y_pos):
        kp_label = tk.Label(self.root, text=f"Kp-{axis} (Proportional)")
        kp_label.place(x=800, y=y_pos)
        kp_slider = tk.Scale(self.root, from_=0, to=2.0, resolution=0.01, orient="horizontal",
                             variable=getattr(self, f"Kp_{axis.lower()}"), length=200)
        kp_slider.place(x=800, y=y_pos + 25)

        ki_label = tk.Label(self.root, text=f"Ki-{axis} (Integral)")
        ki_label.place(x=1000, y=y_pos)
        ki_slider = tk.Scale(self.root, from_=0, to=0.01, resolution=0.0001, orient="horizontal",
                             variable=getattr(self, f"Ki_{axis.lower()}"), length=200)
        ki_slider.place(x=1000, y=y_pos + 25)

        kd_label = tk.Label(self.root, text=f"Kd-{axis} (Derivative)")
        kd_label.place(x=1200, y=y_pos)
        kd_slider = tk.Scale(self.root, from_=0, to=5, resolution=0.1, orient="horizontal",
                             variable=getattr(self, f"Kd_{axis.lower()}"), length=200)
        kd_slider.place(x=1200, y=y_pos + 25)

    def create_hsv_sliders(self):
        self.h_min, self.h_max = tk.IntVar(value=35), tk.IntVar(value=85)
        self.s_min, self.s_max = tk.IntVar(value=55), tk.IntVar(value=255)
        self.v_min, self.v_max = tk.IntVar(value=100), tk.IntVar(value=255)
        self.t1, self.t2 = tk.IntVar(value=166), tk.IntVar(value=171)

        sliders_config = [
            (self.h_min, "Hue Min:", 50, 60),
            (self.h_max, "Hue Max:", 100, 110),
            (self.s_min, "Sat Min:", 150, 160),
            (self.s_max, "Sat Max:", 200, 210),
            (self.v_min, "Value Min:", 250, 260),
            (self.v_max, "Value Max:", 300, 310),
            (self.t1, "Threshold1", 350, 370),
            (self.t2, "Threshold2", 400, 420)
        ]

        for var, text, y_pos, label_y in sliders_config:
            Scale(self.root, from_=0, to=255, orient="horizontal", variable=var, length=200).place(x=100, y=y_pos)
            Label(self.root, text=text, font=("Arial", 12)).place(x=10, y=label_y)

    def create_velocity_display(self):
        self.lr_label = Label(self.root, text="Left-Right Velocity = 0", font=("Arial", 14))
        self.lr_label.place(x=400, y=170)
        self.fb_label = Label(self.root, text="For-Back Velocity = 0", font=("Arial", 14))
        self.fb_label.place(x=400, y=220)
        self.ud_label = Label(self.root, text="Up-Down Velocity = 0", font=("Arial", 14))
        self.ud_label.place(x=400, y=270)
        self.yaw_label = Label(self.root, text="Yaw Velocity = 0", font=("Arial", 14))
        self.yaw_label.place(x=400, y=320)

    def create_video_panels(self):
        container = tk.Frame(self.root)
        container.place(relx=0.5, rely=0.9, anchor="s", relwidth=1.0, height=400)
        self.video_labels = []

        #Subrame HSV Mask
        hsv_frame = tk.Frame(container)
        hsv_frame.grid(row=0, column=0, padx=50)
        tk.Label(hsv_frame, text="HSV Mask", font=("Arial", 12)).pack(pady=(0, 2))
        hsv_lbl = tk.Label(hsv_frame, width=320, height=240, bg="black")
        hsv_lbl.pack()
        self.video_labels.append(hsv_lbl)

        #Subframe Contour
        contour_frame = tk.Frame(container)
        contour_frame.grid(row=0, column=1, padx=50)
        tk.Label(contour_frame, text="Contour", font=("Arial", 12)).pack(pady=(0, 2))
        contour_lbl = tk.Label(contour_frame, width=320, height=240, bg="black")
        contour_lbl.pack()
        self.video_labels.append(contour_lbl)

        #Subframe MissionPlanner
        mission_frame = tk.Frame(container)
        mission_frame.grid(row=0, column=2, padx=50)
        tk.Label(mission_frame, text="MissionPlanner", font=("Arial", 12)).pack(pady=(0, 5))
        mission_lbl = tk.Label(mission_frame, width=600, height=400, bg="black")
        mission_lbl.pack(pady=(0, 30))
        self.video_labels.append(mission_lbl)

    @staticmethod
    def safe_print_window(hwnd, hdc, flags):
        user32 = ctypes.windll.user32
        user32.PrintWindow.restype = ctypes.c_bool
        return user32.PrintWindow(hwnd, hdc, flags)

    def get_mission_planner_frame(self):
        try:
            hwnd = win32gui.FindWindow(None, "Mission Planner 1.3.83 build 1.3.9384.38258 ArduCopter V4.7.0-dev (661d2eab) on")
            if hwnd == 0:
                def enumHandler(h, result):
                    title = win32gui.GetWindowText(h)
                    if "Mission Planner 1.3.83 build 1.3.9384.38258 ArduCopter V4.7.0-dev" in title:
                        result.append(h)

                result = []
                win32gui.EnumWindows(enumHandler, result)
                if not result:
                    return None
                hwnd = result[0]

            left, top, right, bot = win32gui.GetClientRect(hwnd)
            width = right - left
            height = bot - top
            if width <= 0 or height <= 0:
                return None

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = self.safe_print_window(hwnd, saveDC.GetSafeHdc(), 1)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img.shape = (height, width, 4)
            img = img[:, :, :3]

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            if result != 1:
                return None

            img = cv2.resize(img, (600, 400))
            return img

        except Exception as e:
            self.log(f"Error capturing Mission Planner: {e}")
            return None


    def update_frame(self):
        try:
            if not self.is_connected or not self.controller.cap or not self.controller.cap.isOpened():
                self.log("Camera not initialized or drone not connected.")
                return

            ret, frame = self.controller.cap.read()
            if not ret or frame is None:
                self.log("Could not read frame from the camera.")
                self.root.after(100, self.update_frame)
                return
                        

            # Mostrar en GUI
            self.lr_label.config(text=f"Left-Right Velocity = {self.left_right}")
            self.fb_label.config(text=f"For-Back Velocity = {self.for_back}")
            self.ud_label.config(text=f"Up-Down Velocity = {self.up_down}")
            self.yaw_label.config(text="Yaw Velocity = 0")

            mission_frame = self.get_mission_planner_frame()
            if mission_frame is None:
                mission_frame = np.zeros((480, 360, 3), dtype=np.uint8)
                cv2.putText(mission_frame, "Mission Planner not found",
                            (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


            frames_to_show = [self.cap_normal, self.cap_detected, mission_frame]
            for lbl, frame in zip(self.video_labels, frames_to_show):
                if len(frame.shape) == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
                lbl.imgtk = imgtk
                lbl.config(image=imgtk)


            self.root.after(1, self.update_frame) #Probar a cambiar el valor

        except Exception as e:
            self.log(f"Error in update_frame def: {e}")
            self.root.after(1, self.update_frame)



