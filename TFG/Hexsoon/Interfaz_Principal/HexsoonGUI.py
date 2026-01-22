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

        self.misson_panel_heigth: int = 400
        self.misson_panel_width: int = int(self.misson_panel_heigth * 16 / 9)

        init(autoreset=True)

        self.FPS: int = 45

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
        self.create_connection_widgets()
        self.create_video_panels()
        self.create_mode_selectors()
        self.create_control_buttons()
        self.create_hsv_sliders()
        self.create_pid_controls()
        self.create_velocity_display()
        self.create_zoom_slider()


    def run_in_thread(self, target_func):
        """Helper to run actions in background threads"""

        def task():
            try:
                result = target_func()
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
        self.color_opt = tk.StringVar(value=self.color_menu[0])
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

        tk.Label(self.root, text="Take-off alt:", font=("Arial", 14)).grid(column=2, row=0)

        self.takeoff_height = tk.Entry(self.root, width=10)
        self.takeoff_height.insert(0, "2")
        self.takeoff_height.grid(column=3, row=0, padx=10, pady=10)

        self.take_off_button = tk.Button(self.root, text="Arm and Take-off",
                                         command=lambda: self.run_in_thread(self.controller.take_off_drone))
        self.take_off_button.grid(column=2, row=1, padx=10, pady=10)

        self.landing_button = tk.Button(self.root, text="Landing",
                                        command=lambda: self.run_in_thread(self.controller.land_drone))
        self.landing_button.grid(column=2, row=2, padx=10, pady=10)

        self.disconnect_button = tk.Button(self.root, text="Disconnect",
                                           command=lambda: self.run_in_thread(self.controller.disconnect_drone))
        self.disconnect_button.grid(column=3, row=2, padx=10, pady=10)

        self.RTL_button = tk.Button(self.root, text="RTL",
                                    command=lambda: self.run_in_thread(self.controller.Return_To_Launch_drone))
        self.RTL_button.grid(column=3, row=1, padx=10, pady=10)
        
        self.load_model_button = tk.Button(self.root, text="Load Yolo model", 
                                        command=lambda: self.run_in_thread(self.controller.load_model))
        self.load_model_button.grid(column=1, row=8, padx=10, pady=10)


    def create_mode_selectors(self):

        tk.Label(self.root, text="Detection Mode:", font=("Arial", 14)).grid(row=0, column=4, padx=(20, 5), pady=10)
        self.detection_selection = tk.StringVar(value="Color Contour")
        detection_menu = tk.OptionMenu(self.root, self.detection_selection, "Color Contour", "Neural Network")
        detection_menu.grid(row=0, column=5, padx=10, pady=10)

        Label(self.root, text="Test mode =", font=("Arial", 14)).grid(row=0, column=6, padx=10, pady=10)
        self.test_selection = tk.StringVar(value="Simulation")
        test_menu = tk.OptionMenu(self.root, self.test_selection, "Simulation", "Practice")
        test_menu.grid(row=0, column=7, padx=10, pady=10)

        Label(self.root, text="Mode used =", font=("Arial", 14)).grid(row=1, column=4, padx=10, pady=10)
        self.view_selection = tk.StringVar(value="Bottom View")
        view_menu = tk.OptionMenu(self.root, self.view_selection, "Front View", "Bottom View")
        view_menu.grid(row=1, column=5, padx=9, pady=10)


        Label(self.root, text="Camera Used =", font=("Arial", 14)).grid(row=1, column=6, padx=10, pady=10)
        self.type_camera_option = tk.StringVar(value="Default Cam")
        type_camera_menu = tk.OptionMenu(self.root, self.type_camera_option, "Default Cam", "Raspi Cam", "Panoramic Cam")
        type_camera_menu.grid(row=1, column=7, padx=9, pady=10)


    def create_pid_controls(self):
        self.Kp_x = tk.DoubleVar(value=0.1)
        self.Ki_x = tk.DoubleVar(value=0)
        self.Kd_x = tk.DoubleVar(value=0)

        self.Kp_y = tk.DoubleVar(value=0.1)
        self.Ki_y = tk.DoubleVar(value=0)
        self.Kd_y = tk.DoubleVar(value=0)

        self.create_pid_slider_set("X", 150)
        self.create_pid_slider_set("Y", 250)

        Label(self.root, text="Max velocity:", font=("Arial", 12)).grid(row=7, column=2)
        self.max_velocity = tk.DoubleVar(value=100)
        velocity_slider = tk.Scale(self.root, from_=0, to=100, resolution=1,
                                   orient="horizontal", variable=self.max_velocity,
                                   length=200)
        velocity_slider.grid(row=7, column=3)


    def create_pid_slider_set(self, axis: str, y_pos: int):
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
                self.root,
                from_=0, to=val,
                orient="horizontal",
                variable=var,
                length=200,
                command=on_slide
            )
            slider.grid(row=i + 1, column=1)

            Label(self.root, text=text, font=("Arial", 12)).grid(row=i + 1, column=0)


    def create_zoom_slider(self):
        Label(self.root, text="Panoramic Zoom", font=("Arial", 12)).grid(row=8, column=2, padx=10, pady=5)

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
        zoom_slider.grid(row=8, column=3, padx=10, pady=5)


    def create_velocity_display(self):
        
        self.lr_label = Label(self.root, text="Left-Right Velocity:", 
                            font=("Arial", 14))
        self.lr_label.grid(column=2, row=3, padx=(20, 0))
        
        self.fb_label = Label(self.root, text="For-Back Velocity:", 
                            font=("Arial", 14))
        self.fb_label.grid(column=2, row=4, padx=(20, 0))
        
        self.ud_label = Label(self.root, text="Up-Down Velocity:", 
                            font=("Arial", 14))
        self.ud_label.grid(column=2, row=5, padx=(20, 0))
        
        self.yaw_label = Label(self.root, text="Yaw Velocity:", 
                            font=("Arial", 14))
        self.yaw_label.grid(column=2, row=6, padx=(20, 0))


        self.lr_value = Label(self.root, text=" 000.00", 
                            font=("Arial", 12))
        self.lr_value.grid(column=3, row=3)
        
        self.fb_value = Label(self.root, text="000.00", 
                            font=("Arial", 12))
        self.fb_value.grid(column=3, row=4)
        
        self.ud_value = Label(self.root, text="000.00", 
                            font=("Arial", 12))
        self.ud_value.grid(column=3, row=5)
        
        self.yaw_value = Label(self.root, text="000.00", 
                            font=("Arial", 12))
        self.yaw_value.grid(column=3, row=6)


    def create_video_panels(self):
        container = tk.Frame(self.root)
        container.place(relx=0.5, rely=0.9, anchor="s", relwidth=1.0, height=400)
        self.video_labels = []

        hsv_frame = tk.Frame(container)
        hsv_frame.grid(row=0, column=0, padx=25)
        tk.Label(hsv_frame, text="HSV Mask", font=("Arial", 12)).pack(pady=(0, 2))
        hsv_lbl = tk.Label(hsv_frame, width=self.controller.panel_width, height=self.controller.panel_height,
                           bg="black")
        hsv_lbl.pack()
        self.video_labels.append(hsv_lbl)

        contour_frame = tk.Frame(container)
        contour_frame.grid(row=0, column=1, padx=25)
        tk.Label(contour_frame, text="Contour", font=("Arial", 12)).pack(pady=(0, 2))
        contour_lbl = tk.Label(contour_frame, width=self.controller.panel_width, height=self.controller.panel_height,
                               bg="black")
        contour_lbl.pack()
        self.video_labels.append(contour_lbl)

        mission_frame = tk.Frame(container)
        mission_frame.grid(row=0, column=2, padx=25)
        tk.Label(mission_frame, text="MissionPlanner", font=("Arial", 12)).pack(pady=(0, 5))
        mission_lbl = tk.Label(mission_frame, width=self.misson_panel_width, height=self.misson_panel_heigth,
                               bg="black")
        mission_lbl.pack(pady=(0, 30))
        self.video_labels.append(mission_lbl)


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

                self.controller.original, self.controller.img_contour = self.controller.cap_frame(self.controller.type_camera_option)

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

        self.controller.yolo_running = False

        if self.controller.is_connected:
            self.controller.Return_To_Launch_drone()

        self.is_connected = False

