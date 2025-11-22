import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import base64
import json
import cv2
import numpy as np
import threading
import time


# ===============================
# CONFIGURACIÓN MQTT
# ===============================

BROKER_IP = "192.168.1.40"
PORT = 1883

# Topics donde el DRON envía datos
TOPIC_FRAME = "drone/frame"
TOPIC_CONTOUR = "drone/contours"
TOPIC_VELOCITY = "drone/velocities"

# Topics donde la ESTACIÓN BASE envía comandos
TOPIC_CMD_VEL = "station/velocity_cmd"


# ===============================
# CLASE ESTACIÓN BASE
# ===============================

class BaseStation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Estación Base - FPV Drone")
        self.root.geometry("1200x700")
        self.root.configure(bg="black")

        self.frame_image = None
        self.contour_image = None
        self.last_velocity = "0,0,0"

        # --- MQTT ---
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_IP, PORT, 60)
        self.client.loop_start()

        # --- GUI ---
        self.build_gui()

        # --- Start UI update loop ---
        self.update_gui()

        self.root.mainloop()

    # -----------------------------
    # MQTT EVENTS
    # -----------------------------

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado al broker MQTT")

        client.subscribe(TOPIC_FRAME)
        client.subscribe(TOPIC_CONTOUR)
        client.subscribe(TOPIC_VELOCITY)

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        # --- FRAME PRINCIPAL ---
        if topic == TOPIC_FRAME:
            self.frame_image = self.base64_to_image(payload)

        # --- FRAME DE CONTORNOS ---
        elif topic == TOPIC_CONTOUR:
            self.contour_image = self.base64_to_image(payload)

        # --- VELOCIDADES ---
        elif topic == TOPIC_VELOCITY:
            self.last_velocity = payload

    # -----------------------------
    # Convertir base64 → imagen
    # -----------------------------
    def base64_to_image(self, b64_string):
        try:
            img_data = base64.b64decode(b64_string)
            np_arr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return frame
        except:
            return None

    # -----------------------------
    # GUI
    # -----------------------------

    def build_gui(self):
        # FRAME PRINCIPAL
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(side=LEFT, padx=10, pady=10)

        # FRAME CONTORNOS
        self.contours_label = tk.Label(self.root, bg="black")
        self.contours_label.pack(side=RIGHT, padx=10, pady=10)

        # PANEL DE VELOCIDAD
        self.vel_label = tk.Label(self.root, text="Velocidades: 0,0,0",
                                  fg="white", bg="black", font=("Arial", 16))
        self.vel_label.pack(side=TOP, pady=15)

        # BOTONES DE CONTROL
        control_frame = tk.Frame(self.root, bg="black")
        control_frame.pack(side=BOTTOM, pady=20)

        tk.Button(control_frame, text="↑", width=7, command=lambda: self.send_cmd(0, 0.3, 0)).grid(row=0, column=1)
        tk.Button(control_frame, text="↓", width=7, command=lambda: self.send_cmd(0, -0.3, 0)).grid(row=2, column=1)
        tk.Button(control_frame, text="←", width=7, command=lambda: self.send_cmd(-0.3, 0, 0)).grid(row=1, column=0)
        tk.Button(control_frame, text="→", width=7, command=lambda: self.send_cmd(0.3, 0, 0)).grid(row=1, column=2)
        tk.Button(control_frame, text="STOP", width=7, command=lambda: self.send_cmd(0, 0, 0)).grid(row=1, column=1)

    # -----------------------------
    # ENVIAR COMANDOS AL DRON
    # -----------------------------

    def send_cmd(self, vx, vy, vz):
        payload = json.dumps({"vx": vx, "vy": vy, "vz": vz})
        self.client.publish(TOPIC_CMD_VEL, payload)

    # -----------------------------
    # ACTUALIZACIÓN DE VIDEO
    # -----------------------------

    def update_gui(self):
        # FRAME PRINCIPAL
        if self.frame_image is not None:
            img = cv2.cvtColor(self.frame_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # FRAME CONTORNOS
        if self.contour_image is not None:
            img = cv2.cvtColor(self.contour_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((400, 300))
            imgtk = ImageTk.PhotoImage(image=img)
            self.contours_label.imgtk = imgtk
            self.contours_label.configure(image=imgtk)

        # VELOCIDADES
        self.vel_label.configure(text=f"Velocidades: {self.last_velocity}")

        self.root.after(15, self.update_gui)  # ~66 FPS refresh


# ===============================
# INICIO DEL PROGRAMA
# ===============================

if __name__ == "__main__":
    BaseStation()
