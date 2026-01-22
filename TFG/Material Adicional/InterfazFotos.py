import tkinter as tk
from tkinter import messagebox
from djitellopy import Tello
import threading
import cv2
from PIL import Image, ImageTk
import os
import time

TRAIN_PATH = r"C:\Users\joela\Desktop\Datasets\FotosDron\images\train"
VAL_PATH   = r"C:\Users\joela\Desktop\Datasets\FotosDron\images\val"

os.makedirs(TRAIN_PATH, exist_ok=True)
os.makedirs(VAL_PATH, exist_ok=True)


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

        self.master = master
        self.master.title("Dron Interface")

        self.panel_width = 320
        self.panel_height = 240

        # Drone
        self.tello = Tello()
        self.is_connected = False
        self.stop_stream = False

        self.train_prefix = "train"
        self.val_prefix = "val"
        self.train_start_index = 1
        self.val_start_index = 1

        self.connect_button = tk.Button(master, text="Conectar Tello", command=self.connect_tello)
        self.connect_button.pack(pady=5)

        self.capture_button = tk.Button(master, text="Tomar 300 Fotos", command=self.start_capture_thread, state="disabled")
        self.capture_button.pack(pady=5)

        self.panel = tk.Label(master)
        self.panel.pack()


    def connect_tello(self):
        try:
            self.tello.connect()
            self.tello.streamon()
            self.is_connected = True
            self.connect_button.config(text="Conectado", state="disabled")
            self.capture_button.config(state="normal")

            threading.Thread(target=self.update_frame, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar: {e}")


    def update_frame(self):
        while not self.stop_stream and self.is_connected:
            frame_read = self.tello.get_frame_read()
            frame = frame_read.frame

            if frame is None:
                continue

            img_display = cv2.resize(frame, (self.panel_width, self.panel_height))
            img_contour = img_display.copy()   # <- requerido

            img_rgb = cv2.cvtColor(img_contour, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            imgtk = ImageTk.PhotoImage(image=img_pil)

            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)

        print("Stream stopped")


    def start_capture_thread(self):
        threading.Thread(target=self.capture_images, daemon=True).start()

    def capture_images(self):
        if not self.is_connected:
            messagebox.showerror("Error", "Dron no conectado.")
            return

        self.capture_button.config(state="disabled")

        total = 300
        train_count = 150
        val_count = 150

        print("Comenzando captura de imágenes...")

        for i in range(total):
            frame_read = self.tello.get_frame_read()
            frame = frame_read.frame

            if frame is None:
                continue

            img_display = cv2.resize(frame, (self.panel_width, self.panel_height))
            img_contour = img_display.copy()

            if i < train_count:
                path = get_unique_filename(
                    TRAIN_PATH,
                    prefix=self.train_prefix,
                    start_index=self.train_start_index + i
                )
            else:
                real_idx = i - train_count
                path = get_unique_filename(
                    VAL_PATH,
                    prefix=self.val_prefix,
                    start_index=self.val_start_index + real_idx
                )

            cv2.imwrite(path, img_contour)
            print(f"Foto guardada: {path}")

            time.sleep(1)

        print("Captura completada.")
        messagebox.showinfo("Listo", "Se han capturado 300 imágenes.")
        self.capture_button.config(state="normal")


    def on_close(self):
        self.stop_stream = True
        if self.is_connected:
            self.tello.streamoff()
            self.tello.end()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
