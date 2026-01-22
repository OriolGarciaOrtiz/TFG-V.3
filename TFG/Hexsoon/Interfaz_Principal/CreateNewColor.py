import tkinter as tk
from tkinter import messagebox
from HexsoonClass import HexsoonController
from PIL import Image, ImageTk
import cv2


class CreateColor:

    def __init__(self, root: tk.Tk, presets, hexsoon: HexsoonController, cam_opt: str, zoom: float):
        
        self.root = root

        self.presets = presets

        self.window: tk.Toplevel | None

        self.cam = hexsoon

        self.cam_opt = cam_opt

        self.zoom = zoom

        self.mean_h = 0
        self.mean_s = 0
        self.mean_v = 0

    
    def create_color(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Create Color")
        self.window.resizable(False, False)

        tk.Label(self.window, text="Color name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = tk.Entry(self.window, width=22)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.h_min = tk.IntVar(value=0)
        self.h_max = tk.IntVar(value=179)
        self.s_min = tk.IntVar(value=0)
        self.s_max = tk.IntVar(value=255)
        self.v_min = tk.IntVar(value=0)
        self.v_max = tk.IntVar(value=255)


        sliders = [
            (self.h_min, "Hue Min:", 0, 179),
            (self.h_max, "Hue Max:", 0, 179),
            (self.s_min, "Sat Min:", 0, 255),
            (self.s_max, "Sat Max:", 0, 255),
            (self.v_min, "Value Min:", 0, 255),
            (self.v_max, "Value Max:", 0, 255),
        ]


        for i, (var, text, frm, to) in enumerate(sliders, start=1):
            tk.Label(self.window, text=text).grid(row=i, column=0, padx=10, pady=4, sticky="w")
            tk.Scale(
                self.window,
                from_=frm,
                to=to,
                orient="horizontal",
                variable=var,
                length=220
            ).grid(row=i, column=1, padx=10)

        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Missing name", "Please enter a color name.")
                return

            if name in self.presets:
                messagebox.showwarning("Duplicate", "Color already exists.")
                return

            values = (
                self.h_min.get(), self.h_max.get(),
                self.s_min.get(), self.s_max.get(),
                self.v_min.get(), self.v_max.get(),
            )

            # Append to file
            with open("colors.txt", "a", encoding="utf-8") as f:
                f.write(f"\n'{name}' " + " ".join(map(str, values)))

            self.window_destroy()

        tk.Button(self.window, text="Create", command=create).grid(
            row=len(sliders) + 1,
            column=0,
            columnspan=2,
            pady=12,
            padx=50
        )

        tk.Button(self.window, text="Extract", command=self.extract_color).grid(
            row=len(sliders) + 1,
            column=1,
            columnspan=2,
            pady=12,
            padx=50
        )

    def window_destroy(self):

        self.window.destroy()


    def extract_color(self):
        extr_window = tk.Toplevel(self.window)
        extr_window.title("Extract Color")
        extr_window.resizable(False, False)

        # Label to display video
        video_label = tk.Label(extr_window, text="Initializing camera...", font=("Arial", 12))
        video_label.pack(padx=10, pady=10)

        hsv_frame = tk.Frame(extr_window)
        hsv_frame.pack(pady=5)

        hue_label = tk.Label(hsv_frame, text="Hue: --", width=15)
        hue_label.grid(row=0, column=0, padx=5)

        sat_label = tk.Label(hsv_frame, text="Saturation: --", width=15)
        sat_label.grid(row=0, column=1, padx=5)

        val_label = tk.Label(hsv_frame, text="Value: --", width=15)
        val_label.grid(row=0, column=2, padx=5)

        tk.Button(hsv_frame, text="Extract", command=self.extract).grid(row=1, column=1)


        def update_frame():

            if self.cam.cap is None:

                self.cam.cap = cv2.VideoCapture(0)

                extr_window.after(30, update_frame)

            _, frame = self.cam.cap_frame(self.cam_opt)

            if frame is not None:

                h, w, _ = frame.shape
                square_size = 10

                cx, cy = w // 2, h // 2
                half = square_size // 2

                # Safe ROI
                y1 = max(cy - half, 0)
                y2 = min(cy + half, h)
                x1 = max(cx - half, 0)
                x2 = min(cx + half, w)

                roi = frame[y1:y2, x1:x2]

                # Convert ROI to HSV (BGR → HSV)
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                self.mean_h = int(hsv_roi[:, :, 0].mean())
                self.mean_s = int(hsv_roi[:, :, 1].mean())
                self.mean_v = int(hsv_roi[:, :, 2].mean())

                hue_label.config(text=f"Hue: {self.mean_h}")
                sat_label.config(text=f"Saturation: {self.mean_s}")
                val_label.config(text=f"Value: {self.mean_v}")

                # Convert BGR to RGB if needed
                if frame.shape[-1] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Draw center dot
                cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)

                image = Image.fromarray(frame)
                image = image.resize((640, 360))
                imgtk = ImageTk.PhotoImage(image=image)

                video_label.config(image=imgtk, text="")
                video_label.image = imgtk

            extr_window.after(30, update_frame)

        update_frame()

    def extract(self):

        h_margin = 5
        sv_margin = 5

        self.h_min.set(max(self.mean_h - h_margin, 0))
        self.h_max.set(min(self.mean_h + h_margin, 179))

        self.s_min.set(max(self.mean_s - sv_margin, 0))
        self.s_max.set(min(self.mean_s + sv_margin, 255))

        self.v_min.set(max(self.mean_v - sv_margin, 0))
        self.v_max.set(min(self.mean_v + sv_margin, 255))

