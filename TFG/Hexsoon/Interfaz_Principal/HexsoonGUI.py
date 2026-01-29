from HexsoonClass import *
import ctypes
import numpy as np
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import threading
from colorama import init, Fore
from CreateNewColor import CreateColor
from typing import Optional


class GUI:
    def __init__(self, root: tk.Tk):
        self.root = root

        self.is_connected: bool = False
        self.original_frame, self.detected_frame, self.mission_frame = None, None, None
        self.controller = HexsoonController()

        self.misson_panel_heigth: int = self.controller.panel_height
        self.misson_panel_width: int = int(self.misson_panel_heigth * 16 / 9)

        init(autoreset=True)

        self.FPS: int = 80

        self.user32 = ctypes.windll.user32
        self.PrintWindow = self.user32.PrintWindow

        self.running: bool = True

        self.color_values: dict | None = None

        self.presets, self.color_menu = self.load_colors("colors.txt")

        self.frames_to_show: list[np.ndarray | None] | None = None

        self.setup_gui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_frame()


    def setup_gui(self):
        self.root.title("Hexsoon Drone Controller")
        self.root.geometry("1920x1080")

        self.top_container = tk.Frame(self.root)
        self.top_container.pack(fill="both", expand=True)

        self.top_container.columnconfigure(0, weight=1)
        self.top_container.columnconfigure(1, weight=4)
        self.top_container.rowconfigure(0, weight=1)


        self.video_container = tk.LabelFrame(self.root, text="Video Frames")
        self.video_container.pack(side="bottom", fill="x", padx=10, pady=10)

        self.create_sidebar()
        self.main_frame_create()
        self.create_video_panels()

        self.create_mode_selectors()
        self.create_control_buttons()
        self.create_hsv_sliders()
        self.create_pid_controls()
        self.create_velocity_display()

        self.forget_all()


    def run_in_thread(self, target_func):

        def task():
            try:
                result = target_func()
                return result
            except Exception as e:
                print(Fore.RED + f"Error: {str(e)}")

        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        return thread
    

    def create_sidebar(self):
        self.sidebar_frame = tk.Frame(self.top_container)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        self.create_connection_widgets()
        self.create_settings_frame()


    def create_connection_widgets(self):

        self.connection_frame = tk.LabelFrame(self.sidebar_frame, text="Connection")
        self.connection_frame.grid(column=0, row=0, rowspan=2, sticky="news", padx=10, pady=10)

        self.connected_label = Label(self.connection_frame, text="Not Connected", font=("Arial", 12))
        self.connected_label.grid(row=0, column=0, padx=10, pady=10)

        tk.Button(self.connection_frame, text="Connect",
                command=lambda: self.run_in_thread(self.controller.connect_drone)).grid(row=1, column=0, padx=10, pady=10)
        
    
    def main_frame_create(self):
        self.main_frame = tk.Frame(self.top_container)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)

        self.main_frame.rowconfigure(0, weight=1)

        self.left_col = tk.Frame(self.main_frame)
        self.mid_col = tk.Frame(self.main_frame)
        self.right_col = tk.Frame(self.main_frame)

        self.left_col.grid(row=0, column=0, sticky="nsew")
        self.mid_col.grid(row=0, column=1, sticky="nsew")
        self.right_col.grid(row=0, column=2, sticky="nsew")


        for col in (self.left_col, self.mid_col, self.right_col):
            col.grid_rowconfigure(0, weight=1)
            col.grid_columnconfigure(0, weight=1)


    def create_settings_frame(self):

        self.settings_frame = tk.LabelFrame(self.sidebar_frame, text="Settings")
        self.settings_frame.grid(column=0, row=2, padx=10, rowspan=6, sticky="news")
        self.settings_frame.columnconfigure(0, weight=1)

        tk.Button(self.settings_frame, text="Main settings", command=self.show_main_settings).grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(self.settings_frame, text="PID settings", command=self.show_pid_settings).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(self.settings_frame, text="Soon").grid(row=2, column=0, padx=10, pady=10, sticky="ew")    

        tk.Button(self.settings_frame, text="Soon").grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(self.settings_frame, text="Soon").grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(self.settings_frame, text="Soon").grid(row=5, column=0, padx=10, pady=10, sticky="ew")


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

        if len(presets) == 0:

            self.color_values = {
                "Color 1": {
                    "preset": "Green",
                    "h_min": 35, "h_max": 85,
                    "s_min": 55, "s_max": 255,
                    "v_min": 100, "v_max": 255
                },
                "Color 2": {
                    "preset": "Blue",
                    "h_min": 85, "h_max": 135,
                    "s_min": 100, "s_max": 255,
                    "v_min": 100, "v_max": 255
                }
            }

        elif len(presets) == 1:

            hmin, hmax, smin, smax, vmin, vmax = presets[names[0]]

            self.color_values = {
                "Color 1": {
                    "preset": "Green",
                    "h_min": 35, "h_max": 85,
                    "s_min": 55, "s_max": 255,
                    "v_min": 100, "v_max": 255
                },
                "Color 2": {
                    "preset": names[0],
                    "h_min": hmin, "h_max": hmax,
                    "s_min": smin, "s_max": smax,
                    "v_min": vmin, "v_max": vmax
                }
            }

        else:
            hmin1, hmax1, smin1, smax1, vmin1, vmax1 = presets[names[0]]
            hmin2, hmax2, smin2, smax2, vmin2, vmax2 = presets[names[1]]

            self.color_values = {
                "Color 1": {
                    "preset": names[0],
                    "h_min": hmin1, "h_max": hmax1,
                    "s_min": smin1, "s_max": smax1,
                    "v_min": vmin1, "v_max": vmax1
                },
                "Color 2": {
                    "preset": names[1],
                    "h_min": hmin2, "h_max": hmax2,
                    "s_min": smin2, "s_max": smax2,
                    "v_min": vmin2, "v_max": vmax2
                }
            }

        return presets, names

    
    def apply_color_preset(self, *args):
        preset = self.color_opt.get()

        values = self.presets.get(preset)
        if not values:
            return

        hmin, hmax, smin, smax, vmin, vmax = values


        self.h_min.set(hmin)
        self.h_max.set(hmax)
        self.s_min.set(smin)
        self.s_max.set(smax)
        self.v_min.set(vmin)
        self.v_max.set(vmax)

        current_color = self.color_sel.get()
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

        self.h_min.set(values["h_min"])
        self.h_max.set(values["h_max"])
        self.s_min.set(values["s_min"])
        self.s_max.set(values["s_max"])
        self.v_min.set(values["v_min"])
        self.v_max.set(values["v_max"])

        self.color_opt.set(values.get("preset", self.color_menu[0]))


    def create_color(self):
        dialog = CreateColor(
            root=self.root,
            presets=self.presets,
            hexsoon=self.controller,
            cam_opt=self.type_camera_option.get(),
            zoom=float(self.zoom_var.get())
        )

        dialog.create_color()

        self.root.wait_window(dialog.window)

        self.presets, self.color_menu = self.load_colors("colors.txt")
        self.refresh_color_menu()

        

    def refresh_color_menu(self):
        menu = self.color_menu_widget["menu"]
        menu.delete(0, "end")

        for color in self.color_menu:
            menu.add_command(
                label=color,
                command=lambda value=color: self.color_opt.set(value)
            )


    def create_control_buttons(self):

        self.extra_controls_frame = tk.LabelFrame(self.mid_col, text="Controls")
        self.extra_controls_frame.grid(column=0, row=0, padx=10, pady=10, columnspan=3, rowspan=4, sticky="nw")

        tk.Label(self.extra_controls_frame, text="Take-off alt:", font=("Arial", 14)).grid(column=0, row=0, padx=10, pady=10)

        self.takeoff_height = tk.Entry(self.extra_controls_frame, width=10)
        self.takeoff_height.insert(0, "2")
        self.takeoff_height.grid(column=1, row=0, padx=10, pady=10)

        tk.Button(self.extra_controls_frame, text="Arm and Take-off",
            command=lambda: self.run_in_thread(self.controller.take_off_drone)).grid(column=0, row=1, padx=10, pady=10)

        tk.Button(self.extra_controls_frame, text="Landing",
            command=lambda: self.run_in_thread(self.controller.land_drone)).grid(column=1, row=1, padx=10, pady=10)

        tk.Button(self.extra_controls_frame, text="Disconnect",
            command=lambda: self.run_in_thread(self.controller.disconnect_drone)).grid(column=0, row=2, padx=10, pady=10)

        tk.Button(self.extra_controls_frame, text="RTL",
            command=lambda: self.run_in_thread(self.controller.Return_To_Launch_drone)).grid(column=1, row=2, padx=10, pady=10)
        
        Label(self.extra_controls_frame, text="Panoramic Zoom", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
        self.zoom_var = tk.DoubleVar(value=1.5)
        tk.Scale(self.extra_controls_frame, from_=1.0, to=20, resolution=0.1, orient="horizontal",
            variable=self.zoom_var, length=180).grid(row=3, column=1, padx=10, pady=10)


    def create_mode_selectors(self):

        self.modes_frame = tk.LabelFrame(self.right_col, text="Selection Modes")
        self.modes_frame.grid(row=0, column=0, columnspan=4, rowspan=2, sticky="nw", padx=10, pady=10)

        tk.Label(self.modes_frame, text="Detection Mode:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.detection_selection = tk.StringVar(value="Color Contour")
        tk.OptionMenu(self.modes_frame, self.detection_selection, "Color Contour", "Neural Network").grid(row=0, column=1, padx=10, pady=10, sticky="w")

        Label(self.modes_frame, text="Test mode =", font=("Arial", 14)).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.test_selection = tk.StringVar(value="Simulation")
        tk.OptionMenu(self.modes_frame, self.test_selection, "Simulation", "Practice").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        Label(self.modes_frame, text="Mode used =", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.view_selection = tk.StringVar(value="Bottom View")
        tk.OptionMenu(self.modes_frame, self.view_selection, "Front View", "Bottom View").grid(row=1, column=1, padx=9, pady=10, sticky="w")

        Label(self.modes_frame, text="Camera Used =", font=("Arial", 14)).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.type_camera_option = tk.StringVar(value="Default Cam")
        tk.OptionMenu(self.modes_frame, self.type_camera_option, "Default Cam", "Raspi Cam", "Panoramic Cam").grid(row=1, column=3, padx=9, pady=10, sticky="w")


    def create_pid_controls(self):
        
        self.Kp_x = tk.DoubleVar(value=0.1)
        self.Ki_x = tk.DoubleVar(value=0)
        self.Kd_x = tk.DoubleVar(value=0)

        self.Kp_y = tk.DoubleVar(value=0.1)
        self.Ki_y = tk.DoubleVar(value=0)
        self.Kd_y = tk.DoubleVar(value=0)

        self.pid_frame = tk.LabelFrame(self.main_frame, text="PID Control")
        self.pid_frame.grid(row=0, column=0, columnspan=4, rowspan=3, padx=10, pady=10, sticky="nw")

        self.create_pid_grid(self.pid_frame)

    def show_pid_settings(self):

        self.forget_all()

        self.pid_frame.grid(row=0, column=0, columnspan=2, sticky="nw")

    def show_main_settings(self):

        self.forget_all()
        
        self.color_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.extra_controls_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.velocity_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)
        self.modes_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        tk.Frame(self.left_col).grid(row=99, column=0, sticky="nsew")
        tk.Frame(self.mid_col).grid(row=99, column=0, sticky="nsew")
        tk.Frame(self.right_col).grid(row=99, column=0, sticky="nsew")

        self.left_col.grid_rowconfigure(0, weight=1)


    def create_pid_grid(self, parent):

        tk.Label(parent, text="Kp").grid(row=0, column=1)
        tk.Label(parent, text="Ki").grid(row=0, column=2)
        tk.Label(parent, text="Kd").grid(row=0, column=3)

        tk.Label(parent, text="X").grid(row=1, column=0, sticky="w")
        tk.Label(parent, text="Y").grid(row=2, column=0, sticky="w")

        sliders = {
            "Kp": (0, 2.0, 0.01),
            "Ki": (0, 0.01, 0.0001),
            "Kd": (0, 5, 0.1),
        }

        for col, (name, (mn, mx, res)) in enumerate(sliders.items(), start=1):

            tk.Scale(
                parent, from_=mn, to=mx, resolution=res,
                orient="horizontal",
                length=200,
                variable=getattr(self, f"{name}_x")
            ).grid(row=1, column=col, sticky="ew", padx=5)

            tk.Scale(
                parent, from_=mn, to=mx, resolution=res,
                orient="horizontal",
                length=200,
                variable=getattr(self, f"{name}_y")
            ).grid(row=2, column=col, sticky="ew", padx=5)


    def create_hsv_sliders(self):

        self.h_min, self.h_max = tk.IntVar(value=35), tk.IntVar(value=85)
        self.s_min, self.s_max = tk.IntVar(value=55), tk.IntVar(value=255)
        self.v_min, self.v_max = tk.IntVar(value=100), tk.IntVar(value=255)

        self.color_frame = tk.LabelFrame(self.left_col, text="Colors")
        self.color_frame.grid(column=0, row=0, sticky="nsew", padx=10, pady=10)

        sliders_config = [
            (self.h_min, "Hue Min:"),
            (self.h_max, "Hue Max:"),
            (self.s_min, "Sat Min:"),
            (self.s_max, "Sat Max:"),
            (self.v_min, "Value Min:"),
            (self.v_max, "Value Max:"),
        ]

        for i, (var, text) in enumerate(sliders_config):
            KEY_MAP = {
                "Hue Min:": "h_min",
                "Hue Max:": "h_max",
                "Sat Min:": "s_min",
                "Sat Max:": "s_max",
                "Value Min:": "v_min",
                "Value Max:": "v_max",
            }

            def on_slide(v, text=text):
                current_color = self.color_sel.get()
                self.color_values.setdefault(current_color, {})
                self.color_values[current_color][KEY_MAP[text]] = int(float(v))

            val = 255
            if i == 0 or i == 1:
                val = 179

            slider = tk.Scale(
                self.color_frame,
                from_=0, to=val,
                orient="horizontal",
                variable=var,
                length=200,
                command=on_slide
            )
            slider.grid(row=i, column=1, padx=10)

            Label( self.color_frame, text=text, font=("Arial", 12)).grid(row=i, column=0)

        self.color_opt = tk.StringVar(value=self.color_menu[0])
        self.color_menu_widget = tk.OptionMenu(self.color_frame, self.color_opt, *self.color_menu)
        self.color_menu_widget.grid(row=6, column=1, padx=10, pady=10)

        self.color_sel = tk.StringVar(value="Color 1")
        color_selection = tk.OptionMenu(self.color_frame, self.color_sel,
                                            "Color 1", "Color 2")
        color_selection.grid(row=6, column=0, padx=10, pady=10)

        self.create_color_button = tk.Button(self.color_frame, text="Create Color",
                                         command=lambda: self.create_color())
        self.create_color_button.grid(column=0, row=7, padx=10, pady=10)

        self.color_opt.trace_add("write", self.apply_color_preset)
        self.color_sel.trace_add("write", self.switch_color)

        self.load_model_button = tk.Button(self.color_frame, text="Load Yolo model", 
                                        command=lambda: self.run_in_thread(self.controller.load_model))
        self.load_model_button.grid(column=1, row=7, padx=10, pady=10)


    def create_velocity_display(self):

        self.velocity_frame = tk.LabelFrame(self.mid_col, text="Velocities")
        self.velocity_frame.grid(column=0, row=1, padx=10, columnspan=3, rowspan=5, sticky="nsew")
        
        self.lr_label = Label(self.velocity_frame, text="Left-Right Velocity:", 
                            font=("Arial", 14))
        self.lr_label.grid(column=0, row=0, padx=10)
        
        self.fb_label = Label(self.velocity_frame, text="For-Back Velocity:", 
                            font=("Arial", 14))
        self.fb_label.grid(column=0, row=1, padx=10)
        
        self.ud_label = Label(self.velocity_frame, text="Up-Down Velocity:", 
                            font=("Arial", 14))
        self.ud_label.grid(column=0, row=2, padx=10)
        
        self.yaw_label = Label(self.velocity_frame, text="Yaw Velocity:", 
                            font=("Arial", 14))
        self.yaw_label.grid(column=0, row=3, padx=10)


        self.lr_value = Label(self.velocity_frame, text=" 000.00", 
                            font=("Arial", 12))
        self.lr_value.grid(column=1, row=0, padx=10)
        
        self.fb_value = Label(self.velocity_frame, text="000.00", 
                            font=("Arial", 12))
        self.fb_value.grid(column=1, row=1, padx=10)
        
        self.ud_value = Label(self.velocity_frame, text="000.00", 
                            font=("Arial", 12))
        self.ud_value.grid(column=1, row=2, padx=10)
        
        self.yaw_value = Label(self.velocity_frame, text="000.00", 
                            font=("Arial", 12))
        self.yaw_value.grid(column=1, row=3, padx=10)

        Label(self.velocity_frame, text="Max velocity:", font=("Arial", 12)).grid(row=4, column=0)
        self.max_velocity = tk.DoubleVar(value=100)
        tk.Scale(self.velocity_frame, from_=0, to=100, resolution=1,
                            orient="horizontal", variable=self.max_velocity,
                            length=150).grid(row=4, column=1, padx=10, sticky="we")


    def create_video_panels(self):
        container = self.video_container

        self.video_labels = []

        for col, (title, w, h) in enumerate([
            ("HSV Mask", self.controller.panel_width, self.controller.panel_height),
            ("Contour", self.controller.panel_width, self.controller.panel_height),
            ("MissionPlanner", self.misson_panel_width, self.misson_panel_heigth),
        ]):
            frame = tk.Frame(container)
            frame.grid(row=0, column=col, padx=25)

            tk.Label(frame, text=title, font=("Arial", 12)).pack(pady=(0, 5))
            lbl = tk.Label(frame, width=w, height=h, bg="black")
            lbl.pack(pady=(0, 10))
            self.video_labels.append(lbl)

    def forget_all(self):

        self.pid_frame.grid_remove()
        self.velocity_frame.grid_remove()
        self.extra_controls_frame.grid_remove()
        self.modes_frame.grid_remove()
        self.color_frame.grid_remove()

    def transfer_data(self):

        primary: dict = self.color_values.get("Color 1", {})
        secondary: dict = self.color_values.get("Color 2", {})

        self.controller.colors = {
        "primary": {
            "range": (
                (primary.get("h_min", 0), primary.get("s_min", 0), primary.get("v_min", 0)),
                (primary.get("h_max", 255), primary.get("s_max", 255), primary.get("v_max", 255))
            ),
            "name": primary.get("preset", "Unknown")
        },
        "secondary": {
            "range": (
                (secondary.get("h_min", 0), secondary.get("s_min", 0), secondary.get("v_min", 0)),
                (secondary.get("h_max", 255), secondary.get("s_max", 255), secondary.get("v_max", 255))
            ),
            "name": secondary.get("preset", "Unknown")
        }
}
        self.controller.detection_mode = self.detection_selection.get()
        self.controller.Kp_x = self.Kp_x.get()
        self.controller.Ki_x = self.Ki_x.get()
        self.controller.Kd_x = self.Kd_x.get()
        self.controller.Kp_y = self.Kp_y.get()
        self.controller.Ki_y = self.Ki_y.get()
        self.controller.Kd_y = self.Kd_y.get()
        self.controller.max_velocity = self.max_velocity.get()
        self.controller.view_mode = self.view_selection.get()
        self.controller.take_off_alt = float(self.takeoff_height.get())
        self.controller.try_mode = self.test_selection.get()
        self.controller.type_camera_option = self.type_camera_option.get()
        self.controller.zoom_factor = self.zoom_var.get()


    def update_video_frames(self, frames: list[Optional[np.ndarray]]):

        try:
            for lbl, frame in zip(self.video_labels, frames):
                if frame is not None:
                    imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
                    lbl.imgtk = imgtk
                    lbl.config(image=imgtk)
        except Exception as e:
            print(Fore.RED + f"Error updating video frames: {e}")


    def update_velocity_labels(self):

        self.lr_value.config(text=f"{self.controller.left_right:.2f}")
        self.fb_value.config(text=f"{self.controller.for_back:.2f}")
        self.ud_value.config(text=f"{self.controller.up_down:.2f}")
        self.yaw_value.config(text=f"{self.controller.yaw:.2f}")


    def update_frame(self):

        if not self.running:
            return

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

        self.root.after(int(1000 / self.FPS), self.update_frame)


    def on_close(self):

        if self.controller.is_connected and self.controller.try_mode == "Simulation":
            self.controller.Return_To_Launch_drone()

        self.is_connected = False

