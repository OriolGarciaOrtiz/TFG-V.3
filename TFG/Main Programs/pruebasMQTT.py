import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import base64
import json
import cv2
import numpy as np
import time

# ===============================
# CONFIGURACIÓN MQTT
# ===============================
BROKER_IP = "broker.hivemq.com"
PORT = 1883

TOPIC_SUB = "test/chat/pub"  # la estación escucha aquí
TOPIC_PUB = "test/chat/sub"  # la estación envía comandos aquí

# ===============================
# CLASE ESTACIÓN BASE
# ===============================
class BaseStation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Estación Base - FPV Drone")
        self.root.geometry("1100x600")
        self.root.configure(bg="black")

        self.frame_image = None
        self.contour_image = None
        self.left_right = 0
        self.for_back = 0
        self.up_down = 0
        self.yaw = 0

        self.start_time = time.monotonic()
        self.connect_sent = False  # para enviar connect_click solo una vez

        # --- MQTT ---
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_IP, PORT, 60)
        self.client.loop_start()

        # --- GUI ---
        self.build_gui()
        self.update_gui()
        self.root.mainloop()

    # -----------------------------
    # MQTT EVENTS
    # -----------------------------
    def on_connect(self, client, userdata, flags, rc):
        print("Conectado al broker MQTT")
        client.subscribe(TOPIC_SUB)

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.frame_image = self.base64_to_image(data.get("frame_display"))
            self.contour_image = self.base64_to_image(data.get("img_contour"))

            self.left_right = data.get("left_right", 0)
            self.for_back = data.get("for_back", 0)
            self.up_down = data.get("up_down", 0)
            self.yaw = data.get("yaw", 0)
        except Exception as e:
            print("Error procesando mensaje:", e)

    # -----------------------------
    # Convertir base64 → imagen
    # -----------------------------
    def base64_to_image(self, b64_string):
        if b64_string is None:
            return None
        img_data = base64.b64decode(b64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame

    # -----------------------------
    # GUI
    # -----------------------------
    def build_gui(self):
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(side=LEFT, padx=10, pady=10)

        self.contours_label = tk.Label(self.root, bg="black")
        self.contours_label.pack(side=RIGHT, padx=10, pady=10)

        self.vel_label = tk.Label(self.root, text="Velocidades: 0,0,0,0", fg="white", bg="black", font=("Arial", 16))
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
        payload = json.dumps({'vx': vx, 'vy': vy, 'vz': vz})
        self.client.publish(TOPIC_PUB, payload)
        print(f"Enviado comando: {vx}, {vy}, {vz}")

    # -----------------------------
    # ENVIAR CONNECT_CLICK UNA VEZ DESPUÉS DE 10 SEGUNDOS
    # -----------------------------
    def check_connect_click(self):
        now = time.monotonic()
        if not self.connect_sent and now - self.start_time >= 10:
            payload = json.dumps({'connect_click': True})
            self.client.publish(TOPIC_PUB, payload)
            self.connect_sent = True
            print("Enviado connect_click = True")

    # -----------------------------
    # ACTUALIZACIÓN DE VIDEO
    # -----------------------------
    def update_gui(self):
        # Verificar si enviar connect_click
        self.check_connect_click()

        # FRAME PRINCIPAL
        if self.frame_image is not None:
            img = cv2.cvtColor(self.frame_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((640,480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # FRAME CONTORNOS
        if self.contour_image is not None:
            img = cv2.cvtColor(self.contour_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((400,300))
            imgtk = ImageTk.PhotoImage(image=img)
            self.contours_label.imgtk = imgtk
            self.contours_label.configure(image=imgtk)

        # VELOCIDADES
        self.vel_label.configure(text=f"Velocidades: {self.left_right}, {self.for_back}, {self.up_down}, {self.yaw}")

        self.root.after(15, self.update_gui)

# ===============================
# INICIO DEL PROGRAMA
# ===============================
if __name__ == "__main__":
    BaseStation()
