from HexsoonClass import *
import win32gui
import win32ui
import ctypes
import cv2
import numpy as np
import tkinter as tk
from tkinter import Scale, Label
from PIL import Image, ImageTk
import threading
import queue
import paho.mqtt.client as mqtt
import json
import time
from colorama import init, Fore


class GUI:
    def __init__(self, root):
        self.root = root
        self.is_connected = False
        self.original_frame, self.detected_frame, self.mission_frame = None, None, None
        self.controller = HexsoonController()

        self.misson_panel_heigth = 400
        self.misson_panel_width = int(self.misson_panel_heigth * 16/9)

        init(autoreset=True)
        
        # Thread-safe queues
        self.video_queue = queue.Queue(maxsize=2)
        self.velocity_queue = queue.Queue(maxsize=10)
        self.mission_queue = queue.Queue(maxsize=2)

        self.user32 = ctypes.windll.user32
        self.PrintWindow = self.user32.PrintWindow
        
        # Thread control
        self.running = True
        
        self.setup_gui()

        '''  Data that has to be sent from the drone to the GUI  '''
        self.BROKER = "broker.hivemq.com" 
        self.PORT = 1883
        self.TOPIC_SUB = "test/chat/dron2tierra"  # Escucha al publicador
        self.TOPIC_PUB = "test/chat/tierra2dron"  # Envía respuesta

        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        
        self.client.connect(self.BROKER, self.PORT, 60)
        self.client.subscribe(self.TOPIC_SUB)
        self.client.loop_start()

        # Timer for sending ALL data every 0.5 seconds
        self.clock_start = time.monotonic()  # Initialize timer
        self.send_interval = 0.5  # Send every 0.5 seconds

        # Start threads
        self.thread_video = threading.Thread(target=self.thread_video_func, daemon=True)
        self.thread_velocities = threading.Thread(target=self.thread_velocities_func, daemon=True)
        self.thread_get_frame = threading.Thread(target=self.thread_get_frame_func, daemon=True)
        self.thread_get_mission_planner = threading.Thread(target=self.thread_mission_planner_func, daemon=True)

        self.thread_video.start()
        self.thread_velocities.start()  
        self.thread_get_frame.start()
        self.thread_get_mission_planner.start()
        
        # Start main update loop
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

    def on_message(self, client, userdata, msg): 
        if self.controller.try_mode == "Practice":
            text = msg.payload.decode('utf-8')
            self.set_data(text)

    def set_data(self, msg: str):
        try:
            data = json.loads(msg)
            
            self.controller.left_right = float(data.get("left_right", self.controller.left_right))
            self.controller.for_back = float(data.get("for_back", self.controller.for_back))
            self.controller.up_down = float(data.get("up_down", self.controller.up_down))
            self.controller.yaw = float(data.get("yaw", self.controller.yaw))
            self.controller.is_connected = data.get("is_connected", self.controller.is_connected)
        except Exception as e:
            print(Fore.RED + f"Error setting data: {e}")

    def prepare_all_data(self) -> str:
        """Prepare COMPLETE data package with ALL parameters"""
        msg_dict = {
            # HSV values
            'h_min': self.h_min.get(),
            'h_max': self.h_max.get(),
            's_min': self.s_min.get(),
            's_max': self.s_max.get(),
            'v_min': self.v_min.get(),
            'v_max': self.v_max.get(),
            't1': self.t1.get(),
            't2': self.t2.get(),
            
            # Detection and modes
            'detection_mode': self.detection_var.get(),
            'view_mode': self.opt_cam.get(),
            'try_mode': self.simulation_var.get(),
            'PID_mode': self.opt.get(),
            'camera_option': self.camera_option.get(),
            
            # PID values
            'Kp_x': self.Kp_x.get(),
            'Ki_x': self.Ki_x.get(),
            'Kd_x': self.Kd_x.get(),
            'Kp_y': self.Kp_y.get(),
            'Ki_y': self.Ki_y.get(),
            'Kd_y': self.Kd_y.get(),
            
            # Other settings
            'max_velocity': self.max_velocity.get(),
            
            # Click states from CONTROLLER (not pending_clicks)
            'connect_click': self.controller.click_connect,
            'disconnect_click': self.controller.click_disconnect,
        }
            
        return json.dumps(msg_dict)

    def send_data(self):
        '''
        Send ALL parameters every 0.5 seconds
        '''
        now = time.monotonic()

        if now - self.clock_start >= self.send_interval:
            try:
                msg = self.prepare_all_data()
                self.client.publish(self.TOPIC_PUB, msg)
                
                self.controller.click_connect = False
                self.controller.click_disconnect = False
                
                self.clock_start = now
            except Exception as e:
                print(Fore.RED + f"Error sending data: {e}")

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
        
        # Start the thread
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        return thread

    def create_connection_widgets(self):
        self.connected_label = Label(self.root, text="Not Connected", font=("Arial", 14))
        self.connected_label.grid(row=0, column=0, padx=10, pady=10)

        # Use original command that sets controller.click_connect
        self.connect_button = tk.Button(self.root, text="Connect", 
                                       command=lambda: self.run_in_thread(self.controller.connect_drone))
        self.connect_button.grid(row=0, column=1, padx=10, pady=10)

        self.battery_label = Label(self.root, text="Battery: -", font=("Arial", 14))
        self.battery_label.grid(row=0, column=2, padx=10, pady=10)


    def create_control_buttons(self):
        # Arm Button - use controller.arm directly
        self.arm_button = tk.Button(self.root, text="Arm", command=lambda: self.run_in_thread(self.controller.arm_drone))
        self.arm_button.grid(column=4, row=1, padx=10, pady=10)

        self.takeoff_height = tk.Entry(self.root, width=10)
        self.takeoff_height.insert(0, "8")
        self.takeoff_height.grid(column=2, row=1, padx=10, pady=10)

        # Take off button - use controller.take_off_drone directly
        self.take_off_button = tk.Button(self.root, text="Take Off",
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
        dropdown_mode.grid(row=0, column=9, padx=9, pady=10)
        Label(self.root, text="Mode used =", font=("Arial", 14)).grid(row=0, column=8, padx=10, pady=10)

        Label(self.root, text="Camera Used =", font=("Arial", 14)).grid(row=1, column=6, padx=10, pady=10)
        Opt_cam = ["Default Cam", "Raspi Cam", "Panormaic Cam"]
        self.camera_option = tk.StringVar(value="Default Camera")
        dropdown_cam_opt = tk.OptionMenu(self.root, self.camera_option, *Opt_cam)
        dropdown_cam_opt.grid(row=1, column=7, padx=9, pady=10)

    def create_pid_controls(self):
        self.Kp_x = tk.DoubleVar(value=0.42)
        self.Ki_x = tk.DoubleVar(value=0.0005)
        self.Kd_x = tk.DoubleVar(value=1.9)

        self.Kp_y = tk.DoubleVar(value=0.42)
        self.Ki_y = tk.DoubleVar(value=0.0005)
        self.Kd_y = tk.DoubleVar(value=1.9)

        self.create_pid_slider_set("X", 150)
        self.create_pid_slider_set("Y", 250)

        Label(self.root, text="Max velocity:", font=("Arial", 12)).grid(row=7, column=3)
        self.max_velocity = tk.DoubleVar(value=60)
        velocity_slider = tk.Scale(self.root, from_=0, to=60, resolution=1, 
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
        self.t1, self.t2 = tk.IntVar(value=166), tk.IntVar(value=171)

        sliders_config = [
            (self.h_min, "Hue Min:", 1),
            (self.h_max, "Hue Max:", 2),
            (self.s_min, "Sat Min:", 3),
            (self.s_max, "Sat Max:", 4),
            (self.v_min, "Value Min:", 5),
            (self.v_max, "Value Max:", 6),
            (self.t1, "Threshold1", 7),
            (self.t2, "Threshold2", 8)
        ]

        for var, text, row in sliders_config:
            Scale(self.root, from_=0, to=255, orient="horizontal", 
                  variable=var, length=200).grid(row=row, column=1)
            Label(self.root, text=text, font=("Arial", 12)).grid(row=row, column=0)

    def create_velocity_display(self):
        self.lr_label = Label(self.root, text="Left-Right Velocity = 0", font=("Arial", 14))
        self.lr_label.grid(column=3, row=3)
        self.fb_label = Label(self.root, text="For-Back Velocity = 0", font=("Arial", 14))
        self.fb_label.grid(column=3, row=4)
        self.ud_label = Label(self.root, text="Up-Down Velocity = 0", font=("Arial", 14))
        self.ud_label.grid(column=3, row=5)
        self.yaw_label = Label(self.root, text="Yaw Velocity = 0", font=("Arial", 14))
        self.yaw_label.grid(column=3, row=6)

    def create_video_panels(self):
        container = tk.Frame(self.root)
        container.place(relx=0.5, rely=0.9, anchor="s", relwidth=1.0, height=400)
        self.video_labels = []

        # Subframe HSV Mask
        hsv_frame = tk.Frame(container)
        hsv_frame.grid(row=0, column=0, padx=25)
        tk.Label(hsv_frame, text="HSV Mask", font=("Arial", 12)).pack(pady=(0, 2))
        hsv_lbl = tk.Label(hsv_frame, width=self.controller.panel_width, height=self.controller.panel_height, bg="black")
        hsv_lbl.pack()
        self.video_labels.append(hsv_lbl)

        # Subframe Contour
        contour_frame = tk.Frame(container)
        contour_frame.grid(row=0, column=1, padx=25)
        tk.Label(contour_frame, text="Contour", font=("Arial", 12)).pack(pady=(0, 2))
        contour_lbl = tk.Label(contour_frame, width=self.controller.panel_width, height=self.controller.panel_height, bg="black")
        contour_lbl.pack()
        self.video_labels.append(contour_lbl)

        # Subframe MissionPlanner
        mission_frame = tk.Frame(container)
        mission_frame.grid(row=0, column=2, padx=25)
        tk.Label(mission_frame, text="MissionPlanner", font=("Arial", 12)).pack(pady=(0, 5))
        mission_lbl = tk.Label(mission_frame, width=self.misson_panel_width, height=self.misson_panel_heigth, bg="black")
        mission_lbl.pack(pady=(0, 30))
        self.video_labels.append(mission_lbl)

    @staticmethod
    def get_mission_planner_hwnd():
        result = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Mission Planner" in title:
                    result.append(hwnd)

        win32gui.EnumWindows(enum_handler, None)
        return result[0] if result else None

    @staticmethod
    def safe_print_window(hwnd, hdc, flags):
        user32 = ctypes.windll.user32
        user32.PrintWindow.restype = ctypes.c_bool
        return user32.PrintWindow(hwnd, hdc, flags)

    def get_mission_planner_frame(self):
        try:
            hwnd = self.get_mission_planner_hwnd()
            if not hwnd:
                return None

            left, top, right, bot = win32gui.GetClientRect(hwnd)
            width = right - left
            height = bot - top
            if width <= 0 or height <= 0:
                return None

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = self.safe_print_window(hwnd, saveDC.GetSafeHdc(), 1)

            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img.shape = (height, width, 4)
            img = img[:, :, :3]

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            if result != 1:
                return None

            img = cv2.resize(img, (self.misson_panel_width, self.misson_panel_heigth))
            
            return img

        except Exception as e:
            print(Fore.RED + f"Error capturing Mission Planner: {e}")
            return None

    def transfer_data(self):
        """Transfer GUI settings to controller"""
        self.controller.h_min = self.h_min.get()
        self.controller.h_max = self.h_max.get()
        self.controller.t1 = self.t1.get()
        self.controller.t2 = self.t2.get()
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

    def thread_video_func(self):
        """Thread for processing and displaying video frames"""
        
        while self.running:
            try:
                # Check if GUI is still alive
                if not hasattr(self, 'root') or not self.root.winfo_exists():
                    break
                    
                # Get frames from queue
                if not self.video_queue.empty():
                    original_frame, detected_frame = self.video_queue.get(timeout=0.1)
                    
                    # Convert frames for display
                    frames_to_show = []
                    for frame in [original_frame, detected_frame]:
                        if frame is not None:
                            # Convert BGR to RGB for PIL if needed
                            if len(frame.shape) == 3 and frame.shape[2] == 3:
                                try:
                                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                except:
                                    pass
                            frames_to_show.append(frame)
                        else:
                            # Create black frame as placeholder
                            black_frame = np.zeros((self.controller.panel_height, self.controller.panel_width, 3), dtype=np.uint8)
                            frames_to_show.append(black_frame)
                    
                    # Get mission planner frame from stored attribute
                    mission_frame = getattr(self, 'mission_frame', None)
                    
                    if mission_frame is None:
                        # Show placeholder if no mission frame available
                        mission_frame = np.zeros((self.misson_panel_width, self.misson_panel_heigth, 3), dtype=np.uint8)
                        cv2.putText(mission_frame, "Mission Planner not found",
                                (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        
                    else:
                        mission_frame = cv2.cvtColor(mission_frame, cv2.COLOR_BGR2RGB)
                    
                    frames_to_show.append(mission_frame)
                    
                    # Update GUI in main thread
                    self.root.after(0, self.update_video_frames, frames_to_show)
                    
                time.sleep(0.033)  # ~30 FPS
                
            except tk.TclError:
                break
            except queue.Empty:
                time.sleep(0.01)
            except Exception as e:
                print(Fore.RED + f"Video thread error: {e}")
                time.sleep(0.1)

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

    def thread_velocities_func(self):
        """Thread for updating velocity displays"""
        while self.running:
            try:
                # Get velocity data from queue
                if not self.velocity_queue.empty():
                    lr, fb, ud, yaw = self.velocity_queue.get(timeout=0.1)
                    self.controller.left_right = lr
                    self.controller.for_back = fb
                    self.controller.up_down = ud
                    self.controller.yaw = yaw
                    
                    # Update GUI in main thread
                    self.controller.set_velocity()
                    self.root.after(0, self.update_velocity_labels)
                
                time.sleep(0.05)  # 20 Hz update rate
                
            except queue.Empty:
                time.sleep(0.01)
            except Exception as e:
                print(Fore.RED + f"Velocity thread error: {e}")
                time.sleep(0.1)

    def update_velocity_labels(self):
        """Update velocity labels in main thread"""
        self.lr_label.config(text=f"Left-Right Velocity = {self.controller.left_right:.2f}")
        self.fb_label.config(text=f"For-Back Velocity = {self.controller.for_back:.2f}")
        self.ud_label.config(text=f"Up-Down Velocity = {self.controller.up_down:.2f}")
        self.yaw_label.config(text=f"Yaw Velocity = {self.controller.yaw:.2f}")

    def thread_get_frame_func(self):
        """Thread for getting camera frames"""
        while self.running:
            try:
                
                # Get frames based on mode
                if self.controller.try_mode == "Practice":
                    original_frame, detected_frame = self.controller.get_frame("Practice")
                elif self.controller.try_mode == "Simulation":
                    original_frame, detected_frame = self.controller.get_frame("Simulation")
                else:
                    original_frame, detected_frame = None, None
                
                #if original_frame is not None and detected_frame is not None:
                # Put frames in queue for video thread
                if not self.video_queue.full():
                    self.video_queue.put((original_frame, detected_frame), timeout=0.1)
                
                # Put velocity data in queue
                if not self.velocity_queue.full():
                    self.velocity_queue.put((
                        self.controller.left_right,
                        self.controller.for_back,
                        self.controller.up_down,
                        self.controller.yaw
                    ), timeout=0.1)
                
                time.sleep(0.033)  # ~30 FPS
                
            except queue.Full:
                time.sleep(0.01)
            except Exception as e:
                print(Fore.RED + f"Frame thread error: {e}")
                time.sleep(0.1)

    def thread_mission_planner_func(self):
        """Thread for getting Mission Planner frames"""
        
        while self.running:
            try:
                mission_frame = self.get_mission_planner_frame()
                
                if mission_frame is not None:
                    self.mission_frame = mission_frame
               
                time.sleep(0.1)  # 10 FPS for mission planner
                
            except queue.Full:
                time.sleep(0.01)
            except Exception as e:
                print(Fore.RED + f"Mission planner thread error: {e}")
                time.sleep(0.5)

    def update_frame(self):
        try:

            self.transfer_data()

            # Update connection status
            if self.controller.is_connected:
                status_text = "Connected"
                color = "green"
                self.is_connected = True
            else:
                status_text = "Not Connected"
                color = "red"
                self.is_connected = False
                
            self.connected_label.config(text=status_text, fg=color)
            
            # Send ALL data every 0.5 seconds in Practice mode
            if self.controller.try_mode == "Practice":
                self.send_data()
            
        except Exception as e:
            print(Fore.RED + f"Error in update_frame: {e}")
        
        # Schedule next update
        self.root.after(30, self.update_frame)

    def cleanup(self):
            self.running = False