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


class GUI:
    def __init__(self, root):
        self.root = root
        self.is_connected = False
        self.controller = HexsoonController()
        self.panel_width = 320
        self.panel_height = 240

    #Helper para ejecutar acciones en segundo plano y que el tk no se quede pillado en las funciones de MavLink
    def run_in_thread(self, target, *args, status_msg="Executing..."):

        def task():
            try:
                self.log(status_msg)
                target(*args)
                self.log("Action Complete")
            except Exception as e:
                self.log(f"Error: {e}")

        threading.Thread(target=task, daemon=True).start()

    # El motivo de esta función es la siguiente. El problema era que al usar _prepare_command_mov a partir de 0.4 m/s de velocidad en
    # left right el dron empezaba a girar en yaw. Intenté hacer _prepare_command_mov_changed con el objetivo de cambiar la máscara para solo velcoidades
    # y que el movimiento no fuera por posición sino por velocidad pero segía moviendose en yaw el dron. Después pen´se que podría ser
    # a causa de que estaba cogiendo la referencia del dron pero cambiadba a la NED pero tampoco era eso. Así que como ñultima opción me quedó
    # que fuera un problema del guided mode. Esto por lo que se ve sucede por un bug / comportamiento por diseño del controlador de GUIDED de ArduCopter.
    # En el firmware ArduCopter cuando se envia un mensaje SET_POSITION_TARGET_LOCAL_NED con velocidades laterales (vy) en BODY_NED,el controlador interno asume que estás pidiendo
    # “moverte lateralmente respecto al rumbo actual”.Pero si el yaw no está bloqueado o el modo GUIDED no está limitado, el autopiloto interpreta el movimiento lateral como una
    # instrucción de girar el yaw para “alinearse” con el vector de velocidad, es decir, ArduCopter intenta mirar hacia donde te mueves.
    # Por ello he hecho esta función que mantiene el headind fijo y bloquea el yaw en modo guided cambiando las opciones de modo 0 a modo 8   

    def stabilizeYaw(self):
        self.set_param("WP_YAW_BEHAVIOR", 0)  # Mantener heading fijo
        self.set_param("GUID_OPTIONS", 8)  # Bloquear yaw en GUIDED

    def set_param(self, name, value):
        dron = self.controller.dron  # tipo: Dron
        vehicle: mavutil.mavfile = getattr(dron, "vehicle", None)
        msg = mavutil.mavlink.MAVLink_param_set_message(
            vehicle.target_system,
            vehicle.target_component,
            name.encode("utf-8"),
            float(value),
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        vehicle.mav.send(msg)

    def connect(self):
        try:
            mode = self.simulation_var.get()

            if mode == "Simulation":
                self.log("Connecting to simulated drone (Mission Planner TCP)...")
                self.controller.dron.connect('tcp:127.0.0.1:5763', 115200)
            elif mode == "Practice":
                self.log("Connecting to real drone on COM3...")
                self.controller.dron.connect('COM3', 57600)
            else:
                raise ValueError("Unknown connection mode selected")

            self.is_connected = True
            self.connected_label.config(text="✅ Connected", fg="green")

            self.log("Configuring yaw lock (stabilizeYaw)...")
            self.stabilizeYaw()
            self.log("Yaw stabilized (no automatic rotation).")


            self.controller.cap = cv2.VideoCapture(0)
            if not self.controller.cap.isOpened():
                raise Exception("Could not access local camera")

            self.log("Connection successful")

            self.update_frame()

        except Exception as e:
            self.log(f"Connection error: {e}")
            self.is_connected = False
            self.connected_label.config(text="❌ Not Connected", fg="red")

    def disconnect(self):
        if self.is_connected:
            self.controller.dron.disconnect()
        self.log("🔌 Disconnected from drone and camera")



    def takeoff(self, alt=3):
        if not self.is_connected:
            self.log("Drone is not connected. Cannot take off.")
            tk.messagebox.showwarning("Warning", "Connect to the drone before takeoff.")
            return

        try:
            alt = int(alt)
            if alt <= 0:
                raise ValueError("Altitude must be greater than 0")

            self.controller.dron.takeOff(alt)
            self.log(f"Taking off to {alt} meters")

        except ValueError:
            self.log("Invalid altitude value")
            tk.messagebox.showerror("Error", "Please enter a valid numeric altitude (e.g., 5 or 10).")

    def land(self):
        if self.is_connected:
            self.controller.dron.Land()
            self.log("Landing...")
    def Return_To_Launch(self):
        if self.is_connected:
            self.controller.dron.RTL()

    def arm(self):
        if self.is_connected:
            self.controller.dron.arm()
            self.log("Drone armed")

    def log(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))


    @staticmethod
    def safe_print_window(hwnd, hdc, flags):
        user32 = ctypes.windll.user32
        user32.PrintWindow.restype = ctypes.c_bool
        return user32.PrintWindow(hwnd, hdc, flags)


    def set_velocity(self, left_right, for_back, up_down, yaw=0):
        try:
            dron = self.controller.dron  # tipo: Dron
            vehicle: mavutil.mavfile = getattr(dron, "vehicle", None)
            if vehicle is None:
                self.log("No active connection with the drone (vehicle = None)")
                return

            step_x = for_back / 100.0
            step_y = left_right / 100.0
            step_z = -up_down / 100.0
            #Def de dronLink. Se supone que en mavlink  stepx seria la velocidad hacia al norte
            #(for back si bodyRef = True), set_y seria hacia el este (left-right si bodyRef = True) y set_z sería la up down (bodyRef = True). ¡

            #Problema, a veces para velocidades altas hace giros de yaw
            msg = _prepare_command_mov(dron, step_x, step_y, step_z, bodyRef=True)
            self.log(str(msg))
            print(msg)
            vehicle.mav.send(msg)

            #self.log(f"Sent speeds: X={step_x:.2f}, Y={step_y:.2f}, Z={step_z:.2f}")

        except Exception as e:
            self.log(f"Error sending speeds to the drone: {e}")

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

            frame_display = cv2.resize(frame, (self.panel_width, self.panel_height))
            frame_hsv = cv2.cvtColor(frame_display, cv2.COLOR_BGR2HSV)

            lower = np.array([self.h_min.get(), self.s_min.get(), self.v_min.get()])
            upper = np.array([self.h_max.get(), self.s_max.get(), self.v_max.get()])
            mask = cv2.inRange(frame_hsv, lower, upper)
            result = cv2.bitwise_and(frame_display, frame_display, mask=mask)

            img_blur = cv2.GaussianBlur(result, (7, 7), 1)
            img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
            img_canny = cv2.Canny(img_gray, self.t1.get(), self.t2.get())
            kernel = np.ones((5, 5), np.uint8)
            img_dil = cv2.dilate(img_canny, kernel, iterations=1)
            object_center = None
            x, y, w, h = 0, 0, 0, 0
            detection_mode = self.detection_var.get()
            img_contour = frame_display.copy()

            if detection_mode == "Color Contour":
                img_blur = cv2.GaussianBlur(result, (7, 7), 1)
                img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
                img_canny = cv2.Canny(img_gray, self.t1.get(), self.t2.get())
                kernel = np.ones((5, 5), np.uint8)
                img_dil = cv2.dilate(img_canny, kernel, iterations=1)

                contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                if contours:
                    c = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(c)
                    if cv2.contourArea(c) > 300:
                        cv2.rectangle(img_contour, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        object_center = (x + w // 2, y + h // 2)
                        cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)


            elif detection_mode == "Neural Network" and self.controller.model is not None:
                #results = self.controller.model.predict(frame_display, conf=0.5, verbose=False)
                #track tiene el objetivo de mantiene los IDs de objetos entre frames. Usa menos recursos si el objeto no se mueve mucho
                #así que quizas puede mejorar la velocidad para que la camara no vaya con tanto delay
                results = self.controller.model.track(frame_display, persist=True, conf=0.5, verbose=False)
                max_area = 0

                best_box = None

                for r in results:
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        area = (x2 - x1) * (y2 - y1)
                        if area > max_area:
                            max_area = area
                            best_box = (x1, y1, x2, y2, box)

                if best_box is not None:
                    x1, y1, x2, y2, box = best_box
                    w, h = x2 - x1, y2 - y1
                    cx, cy = x1 + w // 2, y1 + h // 2
                    object_center = (cx, cy)
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = f"{self.controller.model.names[cls]} {conf:.2f}"
                    cv2.rectangle(img_contour, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(img_contour, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)
            else:
                cv2.putText(img_contour, "No detection mode active", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            if object_center is not None:
                cx, cy = object_center
                error_x = cx - (self.panel_width / 2)
                if self.opt_cam.get() == "Front View":
                    error_y = (self.panel_height / 2) - cy
                else:  # Bottom View
                    error_y = cy - (self.panel_height / 2)

                self.controller.integral_x = getattr(self.controller, "integral_x", 0) + error_x
                self.controller.integral_y = getattr(self.controller, "integral_y", 0) + error_y
                derivative_x = error_x - getattr(self.controller, "prev_error_x", 0)
                derivative_y = error_y - getattr(self.controller, "prev_error_y", 0)

                Kpx, Kix, Kdx = self.Kp_x.get(), self.Ki_x.get(), self.Kd_x.get()
                Kpy, Kiy, Kdy = self.Kp_y.get(), self.Ki_y.get(), self.Kd_y.get()

                mode_ctrl = self.opt.get()
                if mode_ctrl == "P":
                    vx = Kpx * error_x
                    vy = Kpy * error_y
                elif mode_ctrl == "I":
                    vx = Kix * self.controller.integral_x
                    vy = Kiy * self.controller.integral_y
                elif mode_ctrl == "D":
                    vx = Kdx * derivative_x
                    vy = Kdy * derivative_y
                elif mode_ctrl == "PI":
                    vx = Kpx * error_x + Kix * self.controller.integral_x
                    vy = Kpy * error_y + Kiy * self.controller.integral_y
                elif mode_ctrl == "PD":
                    vx = Kpx * error_x + Kdx * derivative_x
                    vy = Kpy * error_y + Kdy * derivative_y
                elif mode_ctrl == "PID":
                    vx = Kpx * error_x + Kix * self.controller.integral_x + Kdx * derivative_x
                    vy = Kpy * error_y + Kiy * self.controller.integral_y + Kdy * derivative_y
                else:
                    vx, vy = error_x, error_y

                vx = int(np.clip(vx, -self.max_velocity.get(), self.max_velocity.get()))
                vy = int(np.clip(vy, -self.max_velocity.get(), self.max_velocity.get()))

                self.controller.prev_error_x = error_x
                self.controller.prev_error_y = error_y

                view_mode = self.opt_cam.get()  # Front View o Bottom View
                if view_mode == "Front View":
                    left_right = vx
                    up_down = vy
                    for_back = 0
                else:  # Bottom View
                    left_right = vx
                    for_back = vy
                    up_down = 0

                # Funciona pero se le pira la cabeza con la left right cuando la velocidad es más garnde a 40
                self.set_velocity(left_right, for_back, up_down, yaw=0)

            mission_frame = self.get_mission_planner_frame()
            if mission_frame is None:
                mission_frame = np.zeros((480, 360, 3), dtype=np.uint8)
                cv2.putText(mission_frame, "Mission Planner not found",
                            (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


        except Exception as e:
            self.log(f"Error in update_frame def: {e}")
            self.root.after(1, self.update_frame)



