import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import cv2
from PIL import Image, ImageTk
import os
import time
import numpy as np
import yaml


def get_unique_filename(base_folder, prefix="img", start_index=1):
    index = start_index
    while True:
        filename = f"{prefix}{index:04d}.jpg"
        path = os.path.join(base_folder, filename)
        if not os.path.exists(path):
            return path
        index += 1


class App:
    def __init__(self, master):

        yamlname = 'calibration_data_px.yaml'
        self.data = None
        with open(yamlname) as f:
            self.data = yaml.safe_load(f)

        self.master = master
        self.master.title("Hexsoon Camera Interface")

        # Parámetros
        self.panel_width = 320
        self.panel_height = 240
        self.capture_interval = 1.0  # segundos entre fotos

        # Cámara
        self.cap = None
        self.is_connected = False
        self.stop_stream = False

        # Flags de captura
        self.pause_capture = False
        self.capture_running = False

        # Carpeta destino
        self.output_folder = None

        # --- UI ---
        self.connect_button = tk.Button(
            master, text="Conectar Cámara", command=self.connect_camera
        )
        self.connect_button.pack(pady=5)

        self.capture_button = tk.Button(
            master,
            text="Tomar Fotos",
            command=self.start_capture_thread,
            state="disabled",
        )
        self.capture_button.pack(pady=5)

        self.pause_button = tk.Button(
            master,
            text="Parar",
            command=self.toggle_pause,
            state="disabled"
        )
        self.pause_button.pack(pady=5)

        self.panel = tk.Label(master)
        self.panel.pack()


    def connect_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            ret, frame = self.cap.read()

            if not self.cap.isOpened():
                raise RuntimeError("No se pudo abrir la cámara")

            self.is_connected = True
            self.connect_button.config(text="Conectada", state="disabled")
            self.capture_button.config(state="normal")

            threading.Thread(target=self.update_frame, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la cámara:\n{e}")


    def undistort_frame(self, frame):
        cam_matrix = np.array(self.data['camera_matrix'])
        dist_coefs = np.array(self.data['distortion_coefficients'])

        h, w = frame.shape[:2]
        new_cam_mtx, roi = cv2.getOptimalNewCameraMatrix(cam_matrix, dist_coefs, (w, h), 1, (w, h))
        undistorted = cv2.undistort(frame, cam_matrix, dist_coefs, None, new_cam_mtx)
        x, y, w, h = roi
        undistorted = undistorted[y:y+h, x:x+w]

        return undistorted


    def update_frame(self):
        while not self.stop_stream and self.is_connected:
            ret, frame = self.cap.read()
            if not ret:
                continue

            dst = self.undistort_frame(frame)
            dst = cv2.flip(dst, 1)
            img_display = cv2.resize(dst, (self.panel_width, self.panel_height))

            img_rgb = cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)

            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

        print("Stream stopped")


    def start_capture_thread(self):
        if self.capture_running:
            return

        # Pedir carpeta de destino
        folder = filedialog.askdirectory(title="Selecciona carpeta para guardar las fotos")
        if not folder:
            return

        self.output_folder = folder
        self.capture_running = True
        self.pause_button.config(state="normal")
        threading.Thread(target=self.capture_images, daemon=True).start()

    def toggle_pause(self):
        self.pause_capture = not self.pause_capture
        if self.pause_capture:
            self.pause_button.config(text="Reanudar")
        else:
            self.pause_button.config(text="Parar")

    def capture_images(self):
        i = 1
        while i <= 300:
            if self.pause_capture:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                continue

            dst = self.undistort_frame(frame)
            img_display = cv2.resize(dst, (self.panel_width, self.panel_height))

            path = get_unique_filename(self.output_folder, prefix="img", start_index=i)
            cv2.imwrite(path, img_display)
            print(f"Foto guardada: {path}")

            i += 1
            time.sleep(self.capture_interval)

        self.capture_running = False
        self.pause_button.config(state="disabled")
        messagebox.showinfo("Listo", "Se han capturado 300 imágenes.")
        self.capture_button.config(state="normal")


    def on_close(self):
        self.stop_stream = True
        if self.cap is not None:
            self.cap.release()
        self.master.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
