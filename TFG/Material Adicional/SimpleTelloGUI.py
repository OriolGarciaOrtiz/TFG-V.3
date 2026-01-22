from TelloClass import DroneController
import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk


class SimpleTelloGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.attributes('-fullscreen', True)
        root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))
        self.controller = DroneController()
        self.video_width = 960
        self.video_height = 540
        self.panel_width = 960
        self.panel_height = 540
        self.max_velocity = 60

        self.setup_gui()

    def setup_gui(self):
        self.root.title("Simple Tello Drone Controller")
        self.root.geometry("1920x1080")

        # Column 0 = controls, PID; Column 1 = video
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        # Row weights for full expansion in column 1
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        # Create a left-side frame to hold controls + PID
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(0, weight=0)
        left_frame.grid_rowconfigure(1, weight=0)
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        self.create_control_widgets(parent=left_frame)
        self.create_tle_widgets(parent=left_frame)
        self.create_PID_widgets(parent=left_frame)

        # Video frame in column 1
        self.create_video_frame()

    def create_tle_widgets(self, parent):
        button_frame = tk.LabelFrame(parent, text="Drone Controlling", padx=10, pady=10)
        button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # Connect button
        self.take_off_btn = tk.Button(button_frame, text="Take-off", width=34, command=self.controller.safe_takeoff)
        self.take_off_btn.grid(row=0, column=0, padx=10, pady=10)

        # Connection status
        self.landing_btn = tk.Button(button_frame, text="Land", width=34, command=self.controller.landing)
        self.landing_btn.grid(row=1, column=0, padx=10, pady=10)

        # Battery label
        self.emergency_btn = tk.Button(button_frame, text="Emergency", width=34, command=self.controller.emergency)
        self.emergency_btn.grid(row=2, column=0, padx=10, pady=10)

    def create_control_widgets(self, parent):
        control_frame = tk.LabelFrame(parent, text="Drone Connection", padx=10, pady=10)
        control_frame.grid(row=0, column=0, padx=20, pady=10, sticky="n")

        # Connect button
        self.connect_btn = tk.Button(control_frame, text="Connect", width=15, command=self.drone_connection)
        self.connect_btn.grid(row=0, column=0, padx=10, pady=10)

        # Connection status
        self.connection_lbl = tk.Label(control_frame, text="Not Connected", fg="red", font=("Arial", 12))
        self.connection_lbl.grid(row=0, column=1, padx=10, pady=10)

        # Battery label
        self.battery_lbl = tk.Label(control_frame, text="Battery: --%", fg="red", font=("Arial", 12))
        self.battery_lbl.grid(row=1, column=0, columnspan=2, pady=5)

    def drone_connection(self):
        try:
            self.controller.me.connect()
            self.controller.is_connected = True
            self.controller.me.streamoff()
            self.controller.me.streamon()
            battery = self.controller.me.get_battery()
            print(f"Connected! Battery: {battery}%")
            self.connection_lbl.config(text="Connected", fg="green")
            self.battery_lbl.config(text=f"Battery: {battery}%", fg="green")
        except Exception as e:
            print("Connection failed:", e)
            self.controller.is_connected = False
            self.connection_lbl.config(text="Not Connected", fg="red")
            self.battery_lbl.config(text="Battery: --%", fg="red")

    def create_PID_widgets(self, parent):
        pid_frame = tk.LabelFrame(parent, text="PID Controls", padx=10, pady=10)
        pid_frame.grid(row=2, column=0, padx=20, pady=10, sticky="n")

        self.Kp_x = tk.DoubleVar(value=0.42)
        self.Ki_x = tk.DoubleVar(value=0.0005)
        self.Kd_x = tk.DoubleVar(value=1.9)

        tk.Label(pid_frame, text="P:").grid(row=0, column=0, sticky="w")
        tk.Scale(pid_frame, from_=0, to=2, orient="horizontal", length=240,
                 variable=self.Kp_x, resolution=0.01).grid(row=0, column=1, padx=5)

        tk.Label(pid_frame, text="I:").grid(row=1, column=0, sticky="w")
        tk.Scale(pid_frame, from_=0, to=0.01, orient="horizontal", length=240,
                 variable=self.Ki_x, resolution=0.0001).grid(row=1, column=1, padx=5)

        tk.Label(pid_frame, text="D:").grid(row=2, column=0, sticky="w")
        tk.Scale(pid_frame, from_=0, to=10, orient="horizontal", length=240,
                 variable=self.Kd_x, resolution=0.1).grid(row=2, column=1, padx=5)

    def create_video_frame(self):
        video_frame = tk.LabelFrame(self.root, text="Drone Camera", padx=10, pady=10)
        video_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky="n")

        self.video_label = tk.Label(video_frame, width=self.video_width, height=self.video_height, bg="black")
        self.video_label.pack()

    def update_frame(self):
        if self.controller.is_connected:
            self.battery_lbl.config(text=f"Battery: {self.controller.me.get_battery()}%", fg="green")

            frame_read = self.controller.me.get_frame_read()
            my_frame = frame_read.frame

            img_display = cv2.resize(my_frame, (self.panel_width, self.panel_height))
            img_contour = img_display.copy()
            img_hsv = cv2.cvtColor(img_display, cv2.COLOR_BGR2HSV)

            lower = np.array([35, 55, 100])
            upper = np.array([85, 255, 255])
            mask = cv2.inRange(img_hsv, lower, upper)
            result = cv2.bitwise_and(img_display, img_display, mask=mask)

            img_blur = cv2.GaussianBlur(result, (7, 7), 1)
            img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
            img_canny = cv2.Canny(img_gray, 166, 171)
            kernel = np.ones((5, 5), np.uint8)
            img_dil = cv2.dilate(img_canny, kernel, iterations=1)

            object_center = None
            contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(img_contour, (x, y), (x + w, y + h), (0, 255, 0), 2)
                object_center = (x + w // 2, y + h // 2)
                cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)

            if object_center:
                cx, cy = object_center
                cv2.line(img_contour, (self.panel_width // 2, self.panel_height // 2), (cx, cy), (0, 0, 255), 2)

                error_x = cx - (self.panel_width / 2)
                error_y = (self.panel_height / 2) - cy

                self.controller.integral_x += error_x
                derivative_x = error_x - self.controller.prev_error_x
                self.controller.integral_y += error_y
                derivative_y = error_y - self.controller.prev_error_y

                Kpx, Kix, Kdx = self.Kp_x.get(), self.Ki_x.get(), self.Kd_x.get()
                Kpy, Kiy, Kdy = 0.42, 0.0001, 2.5

                speed_x = int(Kpx * error_x + Kix * self.controller.integral_x + Kdx * derivative_x)
                speed_y = int(Kpy * error_y + Kiy * self.controller.integral_y + Kdy * derivative_y)

                self.controller.left_right_velocity = int(np.clip(speed_x, -self.max_velocity, self.max_velocity))
                self.controller.up_down_velocity = int(np.clip(speed_y, -self.max_velocity, self.max_velocity))

                self.controller.me.send_rc_control(self.controller.left_right_velocity,
                                                   self.controller.for_back_velocity,
                                                   self.controller.up_down_velocity,
                                                   self.controller.yaw_velocity)

                self.controller.prev_error_x, self.controller.prev_error_y = error_x, error_y

            else:
                self.controller.me.send_rc_control(0, 0, 0, 0)

            imgtk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(img_contour, cv2.COLOR_BGR2RGB)))
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(30, self.update_frame)