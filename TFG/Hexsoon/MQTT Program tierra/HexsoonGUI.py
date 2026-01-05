from HexsoonClass import *
import ctypes
import cv2
import numpy as np
import tkinter as tk
from tkinter import Label, messagebox
from PIL import Image, ImageTk
import threading
import queue
import time
from colorama import init, Fore


class GUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.is_connected = False
        self.original_frame, self.detected_frame, self.mission_frame = None, None, None
        self.controller = HexsoonController()

        self.misson_panel_heigth = 400
        self.misson_panel_width = int(self.misson_panel_heigth * 16 / 9)

        init(autoreset=True)

        self.FPS = 45

        self.video_queue = queue.Queue(maxsize=2)

        self.user32 = ctypes.windll.user32
        self.PrintWindow = self.user32.PrintWindow

        self.running = True

        self.presets, self.color_menu = self.load_colors("colors.txt")

        self.frames_to_show = None

        self.setup_gui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.color_values = {
            "Color 1": {"preset": "Green", "h_min": 35, "h_max": 85, "s_min": 55, "s_max": 255, "v_min": 100, "v_max": 255},
            "Color 2": {"preset": "Blue",  "h_min": 85, "h_max": 135, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 255},
        }

        self.thread_get_frame = threading.Thread(target=self.thread_get_frame_func, daemon=True)

        self.thread_get_frame.start()

        self.update_frame()


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
        self.create_zoom_slider()


    def run_in_thread(self, target_func, status_msg="Executing..."):
        """Helper to run actions in background threads"""

        def task():
            try:
                print(Fore.BLUE + status_msg)
                result = target_func()
                print(Fore.GREEN + "Action complete")
                return result
            except Exception as e:
                print(Fore.RED + f"Error: {str(e)}")

        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        return thread


    def create_connection_widgets(self):
        self.connected_label = Label(self.root, text="Not Connected", font=("Arial", 14))
        self.connected_label.grid(row=0, column=0, padx=10, pady=10)

        self.connect_button = tk.Button(self.root, text="Connect",
                                        command=lambda: self.run_in_thread(self.controller.connect_drone))
        self.connect_button.grid(row=0, column=1, padx=10, pady=10)

        self.battery_label = Label(self.root, text="Battery: -", font=("Arial", 14))
        self.battery_label.grid(row=0, column=2, padx=10, pady=10)


    def load_colors(self, path: str):
        presets = {}
        names = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                name = line.split("'", 2)[1]
                values = tuple(map(int, line.split("'", 2)[2].split()))

                presets[name] = values
                names.append(name)

        return presets, names

    
    def apply_color_preset(self, *args):
        preset = self.color_opt.get()

        values = self.presets.get(preset)
        if not values:
            return

        hmin, hmax, smin, smax, vmin, vmax = values

        # Update sliders directly
        self.h_min.set(hmin)
        self.h_max.set(hmax)
        self.s_min.set(smin)
        self.s_max.set(smax)
        self.v_min.set(vmin)
        self.v_max.set(vmax)

        # Update the currently selected color values
        current_color = self.color_sel.get()  # "Color 1" or "Color 2"
        self.color_values[current_color] = {
            "preset": preset,
            "h_min": hmin, "h_max": hmax,
            "s_min": smin, "s_max": smax,
            "v_min": vmin, "v_max": vmax
        }


    def switch_color(self, *_):
        selected = self.color_sel.get()
        values = self.color_values.get(selected)
        
        if not values:
            return

        # Restore last slider values for this color
        self.h_min.set(values["h_min"])
        self.h_max.set(values["h_max"])
        self.s_min.set(values["s_min"])
        self.s_max.set(values["s_max"])
        self.v_min.set(values["v_min"])
        self.v_max.set(values["v_max"])

        # Restore preset dropdown
        self.color_opt.set(values.get("preset", "Green"))


    def create_color(self):
        window = tk.Toplevel(self.root)
        window.title("Create Color")
        window.resizable(False, False)

        # -------------------------
        # Color name
        # -------------------------
        tk.Label(window, text="Color name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = tk.Entry(window, width=22)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        # -------------------------
        # HSV variables
        # -------------------------
        h_min = tk.IntVar(value=0)
        h_max = tk.IntVar(value=255)
        s_min = tk.IntVar(value=0)
        s_max = tk.IntVar(value=255)
        v_min = tk.IntVar(value=0)
        v_max = tk.IntVar(value=255)

        sliders = [
            (h_min, "Hue Min:", 0, 179),
            (h_max, "Hue Max:", 0, 179),
            (s_min, "Sat Min:", 0, 255),
            (s_max, "Sat Max:", 0, 255),
            (v_min, "Value Min:", 0, 255),
            (v_max, "Value Max:", 0, 255),
        ]

        for i, (var, text, frm, to) in enumerate(sliders, start=1):
            tk.Label(window, text=text).grid(row=i, column=0, padx=10, pady=4, sticky="w")
            tk.Scale(
                window,
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
                h_min.get(), h_max.get(),
                s_min.get(), s_max.get(),
                v_min.get(), v_max.get(),
            )

            # Append to file
            with open("colors.txt", "a", encoding="utf-8") as f:
                f.write(f"\n'{name}' " + " ".join(map(str, values)))

            self.presets, self.color_menu = self.load_colors("colors.txt")

            self.root.after(0, self.refresh_color_menu)

            window.destroy()

        tk.Button(window, text="Create", command=create).grid(
            row=len(sliders) + 1,
            column=0,
            columnspan=2,
            pady=12
        )


    def refresh_color_menu(self):
        menu = self.color_menu_widget["menu"]
        menu.delete(0, "end")

        for color in self.color_menu:
            menu.add_command(
                label=color,
                command=lambda value=color: self.color_opt.set(value)
            )


    def create_control_buttons(self):
        self.color_opt = tk.StringVar(value="Green")
        self.color_menu_widget = tk.OptionMenu(self.root, self.color_opt, *self.color_menu)
        self.color_menu_widget.grid(row=7, column=1, padx=10, pady=10)

        self.color_sel = tk.StringVar(value="Color 1")
        color_selection = tk.OptionMenu(self.root, self.color_sel,
                                            "Color 1", "Color 2")
        color_selection.grid(row=7, column=0, padx=10, pady=10)

        self.create_color_button = tk.Button(self.root, text="Create Color",
                                         command=lambda: self.create_color())
        self.create_color_button.grid(column=0, row=8, padx=10, pady=10)

        self.color_opt.trace_add("write", self.apply_color_preset)
        self.color_sel.trace_add("write", self.switch_color)

        self.takeoff_height = tk.Entry(self.root, width=10)
        self.takeoff_height.insert(0, "2")
        self.takeoff_height.grid(column=2, row=1, padx=10, pady=10)

        # Take off button - use controller.take_off_drone directly
        self.take_off_button = tk.Button(self.root, text="Arm and Take-off",
                                         command=lambda: self.run_in_thread(self.controller.take_off_drone))
        self.take_off_button.grid(column=3, row=1, padx=10, pady=10)

        # Landing Button - use controller.land_drone directly
        self.landing_button = tk.Button(self.root, text="Landing",
                                        command=lambda: self.run_in_thread(self.controller.land_drone))
        self.landing_button.grid(column=2, row=2, padx=10, pady=10)

        # Disconnect button - use controller.disconnect_drone directly
        self.disconnect_button = tk.Button(self.root, text="Disconnect",
                                           command=lambda: self.run_in_thread(self.controller.disconnect_drone))
        self.disconnect_button.grid(column=3, row=2, padx=10, pady=10)

        # RTL button - use controller.Return_To_Launch_drone directly
        self.RTL_button = tk.Button(self.root, text="RTL",
                                    command=lambda: self.run_in_thread(self.controller.Return_To_Launch_drone))
        self.RTL_button.grid(column=4, row=2, padx=10, pady=10)
        
        self.load_model_button = tk.Button(self.root, text="Load Yolo model", 
                                        command=lambda: self.run_in_thread(self.controller.load_model))
        self.load_model_button.grid(column=1, row=8, padx=10, pady=10)


    def create_mode_selectors(self):
        self.simulation_var = tk.StringVar(value="Simulation")
        simulation_dropdown = tk.OptionMenu(self.root, self.simulation_var,
                                            "Simulation", "Practice")
        simulation_dropdown.grid(row=0, column=3, padx=10, pady=10)

        detection_label = tk.Label(self.root, text="Detection Mode:", font=("Arial", 14))
        detection_label.grid(row=0, column=4, padx=(20, 5), pady=10)

        self.detection_var = tk.StringVar(value="Color Contour")
        detection_dropdown = tk.OptionMenu(self.root, self.detection_var,
                                           "Color Contour", "Neural Network")
        detection_dropdown.grid(row=0, column=5, padx=10, pady=10)

        PID_values = ["P", "I", "D", "PD", "PI", "PID", "None"]
        Label(self.root, text="Controller used =", font=("Arial", 14)).grid(row=0, column=6, padx=10, pady=10)
        self.opt = tk.StringVar(value="PID")
        dropdown_x = tk.OptionMenu(self.root, self.opt, *PID_values)
        dropdown_x.grid(row=0, column=7, padx=10, pady=10)

        Mode_cam = ["Front View", "Bottom View"]
        self.opt_cam = tk.StringVar(value="Bottom View")
        dropdown_mode = tk.OptionMenu(self.root, self.opt_cam, *Mode_cam)
        dropdown_mode.grid(row=1, column=5, padx=9, pady=10)
        Label(self.root, text="Mode used =", font=("Arial", 14)).grid(row=1, column=4, padx=10, pady=10)

        Label(self.root, text="Camera Used =", font=("Arial", 14)).grid(row=1, column=6, padx=10, pady=10)
        Opt_cam = ["Default Cam", "Raspi Cam", "Panoramic Cam"]
        self.camera_option = tk.StringVar(value="Default Cam")
        dropdown_cam_opt = tk.OptionMenu(self.root, self.camera_option, *Opt_cam)
        dropdown_cam_opt.grid(row=1, column=7, padx=9, pady=10)


    def create_pid_controls(self):
        self.Kp_x = tk.DoubleVar(value=0.1)
        self.Ki_x = tk.DoubleVar(value=0)
        self.Kd_x = tk.DoubleVar(value=0)

        self.Kp_y = tk.DoubleVar(value=0.1)
        self.Ki_y = tk.DoubleVar(value=0)
        self.Kd_y = tk.DoubleVar(value=0)

        self.create_pid_slider_set("X", 150)
        self.create_pid_slider_set("Y", 250)

        Label(self.root, text="Max velocity:", font=("Arial", 12)).grid(row=7, column=3)
        self.max_velocity = tk.DoubleVar(value=100)
        velocity_slider = tk.Scale(self.root, from_=0, to=100, resolution=1,
                                   orient="horizontal", variable=self.max_velocity,
                                   length=200)
        velocity_slider.grid(row=8, column=3)


    def create_pid_slider_set(self, axis, y_pos):
        kp_label = tk.Label(self.root, text=f"Kp-{axis} (Proportional)")
        kp_label.place(x=800, y=y_pos)

        kp_var = getattr(self, f"Kp_{axis.lower()}")
        kp_slider = tk.Scale(self.root, from_=0, to=2.0, resolution=0.01,
                             orient="horizontal", variable=kp_var, length=200)
        kp_slider.place(x=800, y=y_pos + 25)

        ki_label = tk.Label(self.root, text=f"Ki-{axis} (Integral)")
        ki_label.place(x=1000, y=y_pos)

        ki_var = getattr(self, f"Ki_{axis.lower()}")
        ki_slider = tk.Scale(self.root, from_=0, to=0.01, resolution=0.0001,
                             orient="horizontal", variable=ki_var, length=200)
        ki_slider.place(x=1000, y=y_pos + 25)

        kd_label = tk.Label(self.root, text=f"Kd-{axis} (Derivative)")
        kd_label.place(x=1200, y=y_pos)

        kd_var = getattr(self, f"Kd_{axis.lower()}")
        kd_slider = tk.Scale(self.root, from_=0, to=5, resolution=0.1,
                             orient="horizontal", variable=kd_var, length=200)
        kd_slider.place(x=1200, y=y_pos + 25)


    def create_hsv_sliders(self):
        self.h_min, self.h_max = tk.IntVar(value=35), tk.IntVar(value=85)
        self.s_min, self.s_max = tk.IntVar(value=55), tk.IntVar(value=255)
        self.v_min, self.v_max = tk.IntVar(value=100), tk.IntVar(value=255)

        sliders_config = [
            (self.h_min, "Hue Min:"),
            (self.h_max, "Hue Max:"),
            (self.s_min, "Sat Min:"),
            (self.s_max, "Sat Max:"),
            (self.v_min, "Value Min:"),
            (self.v_max, "Value Max:"),
        ]

        for i, (var, text) in enumerate(sliders_config):
            def on_slide(v, var=var, text=text):
                current_color = self.color_sel.get()
                key_base = text.split()[0].lower()  # 'hue', 'sat', 'value'
                key_suffix = "_min" if "Min" in text else "_max"
                key = key_base[0] + key_suffix  # e.g., 'h_min'
                self.color_values[current_color][key] = int(float(v))

            slider = tk.Scale(
                self.root,
                from_=0, to=255,
                orient="horizontal",
                variable=var,
                length=200,
                command=on_slide
            )
            slider.grid(row=i + 1, column=1)

            Label(self.root, text=text, font=("Arial", 12)).grid(row=i + 1, column=0)


    def create_zoom_slider(self): #OJO, nueva función para poder hacer zoom en tiempo real
        Label(self.root, text="Panoramic Zoom", font=("Arial", 12)).grid(row=9, column=0, padx=10, pady=5)

        self.zoom_var = tk.DoubleVar(value=1.5)

        zoom_slider = tk.Scale(
            self.root,
            from_=1.0,
            to=20,
            resolution=0.1,
            orient="horizontal",
            variable=self.zoom_var,
            length=200
        )
        zoom_slider.grid(row=9, column=1, padx=10, pady=5)


    def create_velocity_display(self):
        label_width = 28
        
        self.lr_label = Label(self.root, text="Left-Right Velocity = 0.00", 
                            font=("Arial", 14), width=label_width, anchor="w")
        self.lr_label.grid(column=3, row=3, sticky="w")
        
        self.fb_label = Label(self.root, text="For-Back Velocity = 0.00", 
                            font=("Arial", 14), width=label_width, anchor="w")
        self.fb_label.grid(column=3, row=4, sticky="w")
        
        self.ud_label = Label(self.root, text="Up-Down Velocity = 0.00", 
                            font=("Arial", 14), width=label_width, anchor="w")
        self.ud_label.grid(column=3, row=5, sticky="w")
        
        self.yaw_label = Label(self.root, text="Yaw Velocity = 0.00", 
                            font=("Arial", 14), width=label_width, anchor="w")
        self.yaw_label.grid(column=3, row=6, sticky="w")



    def create_video_panels(self):
        container = tk.Frame(self.root)
        container.place(relx=0.5, rely=0.9, anchor="s", relwidth=1.0, height=400)
        self.video_labels = []

        # Subframe HSV Mask
        hsv_frame = tk.Frame(container)
        hsv_frame.grid(row=0, column=0, padx=25)
        tk.Label(hsv_frame, text="HSV Mask", font=("Arial", 12)).pack(pady=(0, 2))
        hsv_lbl = tk.Label(hsv_frame, width=self.controller.panel_width, height=self.controller.panel_height,
                           bg="black")
        hsv_lbl.pack()
        self.video_labels.append(hsv_lbl)

        # Subframe Contour
        contour_frame = tk.Frame(container)
        contour_frame.grid(row=0, column=1, padx=25)
        tk.Label(contour_frame, text="Contour", font=("Arial", 12)).pack(pady=(0, 2))
        contour_lbl = tk.Label(contour_frame, width=self.controller.panel_width, height=self.controller.panel_height,
                               bg="black")
        contour_lbl.pack()
        self.video_labels.append(contour_lbl)

        # Subframe MissionPlanner
        mission_frame = tk.Frame(container)
        mission_frame.grid(row=0, column=2, padx=25)
        tk.Label(mission_frame, text="MissionPlanner", font=("Arial", 12)).pack(pady=(0, 5))
        mission_lbl = tk.Label(mission_frame, width=self.misson_panel_width, height=self.misson_panel_heigth,
                               bg="black")
        mission_lbl.pack(pady=(0, 30))
        self.video_labels.append(mission_lbl)


    def transfer_data(self):
        """Transfer GUI settings to controller"""
        primary = self.color_values.get("Color 1", {})
        secondary = self.color_values.get("Color 2", {})

        self.controller.colors = {
            "primary": (
                (primary.get("h_min", 0), primary.get("s_min", 0), primary.get("v_min", 0)),
                (primary.get("h_max", 255), primary.get("s_max", 255), primary.get("v_max", 255))
            ),
            "secondary": (
                (secondary.get("h_min", 0), secondary.get("s_min", 0), secondary.get("v_min", 0)),
                (secondary.get("h_max", 255), secondary.get("s_max", 255), secondary.get("v_max", 255))
            )
        }
        self.controller.detection_mode = self.detection_var.get()
        self.controller.Kp_x = self.Kp_x.get()
        self.controller.Ki_x = self.Ki_x.get()
        self.controller.Kd_x = self.Kd_x.get()
        self.controller.Kp_y = self.Kp_y.get()
        self.controller.Ki_y = self.Ki_y.get()
        self.controller.Kd_y = self.Kd_y.get()
        self.controller.PID_mode = self.opt.get()
        self.controller.max_velocity = self.max_velocity.get()
        self.controller.view_mode = self.opt_cam.get()
        self.controller.take_off_alt = float(self.takeoff_height.get())
        self.controller.try_mode = self.simulation_var.get()
        self.controller.camera_option = self.camera_option.get()
        self.controller.zoom_factor = self.zoom_var.get()


    def update_video_frames(self, frames):
        """Update video frames in main thread (Tkinter safe)"""
        try:
            for lbl, frame in zip(self.video_labels, frames):
                if frame is not None:
                    imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
                    lbl.imgtk = imgtk
                    lbl.config(image=imgtk)
        except Exception as e:
            print(Fore.RED + f"Error updating video frames: {e}")


    def update_velocity_labels(self):
        """Update velocity labels in main thread"""

        self.lr_label.config(text=f"Left-Right Velocity = {self.controller.left_right:.2f}")
        self.fb_label.config(text=f"For-Back Velocity = {self.controller.for_back:.2f}")
        self.ud_label.config(text=f"Up-Down Velocity = {self.controller.up_down:.2f}")
        self.yaw_label.config(text=f"Yaw Velocity = {self.controller.yaw:.2f}")


    def thread_get_frame_func(self):

        while self.running:
            try:
                original_frame, detected_frame = None, None
                if self.controller.is_connected:
                    original_frame, detected_frame = self.controller.get_frame()

                while not self.video_queue.empty():
                    self.video_queue.get_nowait()

                self.video_queue.put((original_frame, detected_frame))

                time.sleep(1/self.FPS)

            except queue.Full:
                time.sleep(1/self.FPS)
            except Exception as e:
                print(Fore.RED + f"Frame thread error: {e}")
                time.sleep(1/self.FPS)


    def update_frame(self):
        try:

            self.transfer_data()

            if self.controller.is_connected:
                status_text = "Connected"
                color = "green"
                self.is_connected = True
            else:
                status_text = "Not Connected"
                color = "red"
                self.is_connected = False

            self.connected_label.config(text=status_text, fg=color)

            if self.frames_to_show:
            
                self.update_video_frames(self.frames_to_show)

            self.update_velocity_labels()

        except Exception as e:
            print(Fore.RED + f"Error in update_frame: {e}")

        self.root.after(30, self.update_frame)


    def on_close(self):
        self.running = False
        self.root.after(100, self.root.destroy)
