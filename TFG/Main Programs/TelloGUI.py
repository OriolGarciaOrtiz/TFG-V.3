import cv2
import numpy as np
import tkinter as tk
from tkinter import Scale, messagebox, OptionMenu, Label, StringVar
from PIL import Image, ImageTk
import cv2.aruco as aruco
import glob
from TelloClass import *
import math
import os
import threading
from queue import Queue
import queue  # para Queue.Full
import time


class GUI:
    def __init__(self, root):
        self.root = root
        root.attributes('-fullscreen', True)
        root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

        self.controller = DroneController()

        # === YOLO worker setup ===
        self.yolo_queue = Queue(maxsize=1)
        self.yolo_result = (None, 0, 0, [])
        self.yolo_lock = threading.Lock()

        # Si ya tienes modelo cargado, lanza worker
        self._yolo_worker = threading.Thread(target=self._yolo_worker_loop, daemon=True)
        self._yolo_worker.start()

        # === GAME MODE worker setup ===
        self.game_queue = Queue(maxsize=1)
        self.game_result = (None, 0, 0, None,[])
        self.game_lock = threading.Lock()

        self._game_worker = threading.Thread(target=self._game_worker_loop, daemon=True)
        self._game_worker.start()

        # === Cargar parámetros de cámara una vez ===
        try:
            file_path = r"taller-dron-Tello\Lib\Parameters\parametros_camara_tello.npz"
            data = np.load(file_path)
            self.camera_matrix = data['camera_matrix']
            self.dist_coeffs = data['dist_coeffs']
            print("[INFO] Parámetros de cámara cargados correctamente.")
        except Exception as e:
            self.camera_matrix = None
            self.dist_coeffs = None
            print("[WARN] No se pudieron cargar los parámetros de cámara:", e)


        self.panel_width = 320
        self.panel_height = 240

        self.w_det = None
        self.h_det = None
        self.latest_w = None
        self.latest_h = None

        self.last_detected_label = None
        self.action_done_for_label = None

        self.last_yolo_output = (None, 0, 0)
        self._yolo_thread = None

        #self.flask_server = None

        self.setup_gui()

    def setup_gui(self):
        self.root.title("Tello Drone Controller")
        self.root.geometry("1920x1080")

        # Create all GUI elements
        self.create_connection_widgets()
        self.create_control_buttons()
        self.create_calibration_buttons()
        self.create_mode_selectors()
        self.create_pid_controls()
        self.create_video_panels()
        self.create_hsv_sliders()
        self.create_velocity_display()
        self.create_distance_controls()

    def create_connection_widgets(self):
        # Connection status
        self.connected_label = Label(self.root, text="Not Connected", font=("Arial", 12))
        self.connected_label.grid(row=0, column=0, padx=5, pady=10)

        self.connect_button = tk.Button(self.root, text="Connect", command=self.drone_connection)
        self.connect_button.grid(row=0, column=1, padx=5, pady=10)

        self.battery_label = Label(self.root, text="Battery: -", font=("Arial", 12))
        self.battery_label.grid(row=0, column=3, padx=5, pady=10)

    def create_control_buttons(self):
        self.take_off_button = tk.Button(self.root, text="Take Off", command=self.controller.safe_takeoff)
        self.take_off_button.grid(row=0, column=5)

        self.alt_button = tk.Button(self.root, text="Go Up", command=lambda: self.controller.go_up(70))
        self.alt_button.place(x=720, y=10)

        self.landing_button = tk.Button(self.root, text="Landing", command=self.controller.landing)
        self.landing_button.grid(row=0,column=6)

        self.emergency_button = tk.Button(self.root, text="Emergency", command=self.controller.emergency)
        self.emergency_button.grid(row=0,column=7)

    def create_calibration_buttons(self):
        self.btn_calibration_start = tk.Button(self.root, text="Start Calibration",
                                               command=lambda: threading.Thread(target=self.start_calibration,
                                                                                daemon=True).start())
        self.btn_calibration_start.grid(row=7, column=8, padx=5, pady=10)

        self.btn_get_calibration = tk.Button(self.root, text="Get Calibrated Parameters",
                                             command=lambda: threading.Thread(target=self.get_parameters,
                                                                              daemon=True).start())
        self.btn_get_calibration.grid(row=7, column=9, padx=5, pady=10)

        self.btn_maunal_distance = tk.Button(self.root, text="Take reference distance",
                                             command=lambda: threading.Thread(target=self.get_maunal_distance,
                                                                              daemon=True).start())
        self.btn_maunal_distance.grid(row=7, column=9, padx=5, pady=10)

    def create_mode_selectors(self):

        simulation_label = tk.Label(self.root, text="Simulation Mode:", font=("Arial", 12))
        simulation_label.grid(row=1, column=3, padx=(20, 5), pady=10, sticky="w")

        self.simulation_var = tk.StringVar(value="True")
        simulation_dropdown = tk.OptionMenu(self.root, self.simulation_var, "True", "False")

        simulation_dropdown.grid(row=1, column=3, padx=(175, 0), pady=10, sticky="w")

        detection_label = tk.Label(self.root, text="Detection Mode:", font=("Arial", 12))
        detection_label.grid(row=2, column=8)

        self.detection_var = tk.StringVar(value="Color Contour")
        detection_dropdown = tk.OptionMenu(self.root, self.detection_var, "Color Contour", "Neural Network","Game Mode")
        detection_dropdown.grid(row=2, column=9)

        PID_values = ["P", "I", "D", "PD", "PI", "PID", "None"]
        Label(self.root, text="Controller used =", font=("Arial", 12)).grid(row=1, column=8)
        self.opt = tk.StringVar(value="PID")
        dropdown_x = OptionMenu(self.root, self.opt, *PID_values)
        dropdown_x.grid(row=1, column=9)

        Mode_cam = ["Mirror", "Drone Camera"]
        self.opt_cam = tk.StringVar(value="Drone Camera")
        dropdown_mode = OptionMenu(self.root, self.opt_cam, *Mode_cam)
        dropdown_mode.grid(row=0, column=9)
        Label(self.root, text="Mode used =", font=("Arial", 12)).grid(row=0, column=8)

    def create_pid_controls(self):
        
        self.Kp_x = tk.DoubleVar(value=0.42)
        self.Ki_x = tk.DoubleVar(value=0.0005)
        self.Kd_x = tk.DoubleVar(value=1.9)

        self.Kp_y = tk.DoubleVar(value=0.42)
        self.Ki_y = tk.DoubleVar(value=0.0005)
        self.Kd_y = tk.DoubleVar(value=1.9)

        self.Kp_z = tk.DoubleVar(value=0.42)
        self.Ki_z = tk.DoubleVar(value=0.0005)
        self.Kd_z = tk.DoubleVar(value=1.9)

        # --- X Axis ---
        tk.Label(self.root, text="Kp-X (Proportional)").grid(row=1, column=5, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=2.0, resolution=0.01, orient="horizontal",
                 variable=self.Kp_x, length=200).grid(row=2, column=5, padx=5, pady=5)

        tk.Label(self.root, text="Ki-X (Integral)").grid(row=1, column=6, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=0.01, resolution=0.0001, orient="horizontal",
                 variable=self.Ki_x, length=200).grid(row=2, column=6, padx=5, pady=5)

        tk.Label(self.root, text="Kd-X (Derivative)").grid(row=1, column=7, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=5, resolution=0.1, orient="horizontal",
                 variable=self.Kd_x, length=200).grid(row=2, column=7, padx=5, pady=5)

        # --- Y Axis ---
        tk.Label(self.root, text="Kp-Y (Proportional)").grid(row=3, column=5, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=2.0, resolution=0.01, orient="horizontal",
                 variable=self.Kp_y, length=200).grid(row=4, column=5, padx=5, pady=5)

        tk.Label(self.root, text="Ki-Y (Integral)").grid(row=3, column=6, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=0.01, resolution=0.0001, orient="horizontal",
                 variable=self.Ki_y, length=200).grid(row=4, column=6, padx=5, pady=5)

        tk.Label(self.root, text="Kd-Y (Derivative)").grid(row=3, column=7, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=5, resolution=0.1, orient="horizontal",
                 variable=self.Kd_y, length=200).grid(row=4, column=7, padx=5, pady=5)

        # --- Z Axis ---
        tk.Label(self.root, text="Kp-Z (Proportional)").grid(row=5, column=5, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=2.0, resolution=0.01, orient="horizontal",
                 variable=self.Kp_z, length=200).grid(row=6, column=5, padx=5, pady=5)

        tk.Label(self.root, text="Ki-Z (Integral)").grid(row=5, column=6, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=0.01, resolution=0.0001, orient="horizontal",
                 variable=self.Ki_z, length=200).grid(row=6, column=6, padx=5, pady=5)

        tk.Label(self.root, text="Kd-Z (Derivative)").grid(row=5, column=7, padx=5, pady=5)
        tk.Scale(self.root, from_=0, to=5, resolution=0.1, orient="horizontal",
                 variable=self.Kd_z, length=200).grid(row=6, column=7, padx=5, pady=5)

        # --- Max Velocity ---
        tk.Label(self.root, text="Max velocity").grid(row=6, column=3, padx=5, pady=5)
        self.max_velocity = tk.DoubleVar(value=60)
        tk.Scale(self.root, from_=0, to=60, resolution=1, orient="horizontal",
                 variable=self.max_velocity, length=200).grid(row=7, column=3, columnspan=5, padx=5, pady=5)

    def create_video_panels(self):

        frame_width = self.panel_width * 2 + 50
        frame_height = self.panel_height + 60

        video_frame = tk.LabelFrame(self.root,
                                    text="Video Feed",
                                    font=("Arial", 12),
                                    relief="sunken",
                                    bd=2,
                                    width=frame_width,
                                    height=frame_height)

        video_frame.grid(row=9, column=0, columnspan=6, rowspan=2, padx=5, pady=10)
        video_frame.grid_propagate(False)

        video_frame.columnconfigure(0, weight=1)
        video_frame.columnconfigure(1, weight=1)
        video_frame.rowconfigure(1, weight=1)

        video_titles = ["Dilated", "Contour"]
        self.video_labels = []

        for i, title in enumerate(video_titles):
            title_label = Label(video_frame, text=title, font=("Arial", 11, "bold"))
            title_label.grid(row=0, column=i, padx=15, pady=(5, 2))

            lbl = Label(video_frame,
                        width=self.panel_width // 8,
                        height=self.panel_height // 16,
                        relief='sunken',
                        bd=1,
                        bg='black')
            lbl.grid(row=1, column=i, padx=15, pady=10, sticky="nsew")
            self.video_labels.append(lbl)

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
            Scale(self.root, from_=0, to=255, orient="horizontal", variable=var, length=175).grid(row=row, column=1)
            Label(self.root, text=text, font=("Arial", 12)).grid(row=row, column=0)

    def create_velocity_display(self):
        self.lr_label = Label(self.root, text="Left-Right Velocity = 0",
                              font=("Arial", 12), width=25, anchor='w')
        self.lr_label.grid(row=2, column=3, padx=10, pady=10)

        self.fb_label = Label(self.root, text="For-Back Velocity = 0",
                              font=("Arial", 12), width=25, anchor='w')
        self.fb_label.grid(row=3, column=3, padx=10, pady=10)

        self.ud_label = Label(self.root, text="Up-Down Velocity = 0",
                              font=("Arial", 12), width=25, anchor='w')
        self.ud_label.grid(row=4, column=3, padx=10, pady=10)

        self.yaw_label = Label(self.root, text="Yaw Velocity = 0",
                               font=("Arial", 12), width=25, anchor='w')
        self.yaw_label.grid(row=5, column=3, padx=10, pady=10)

    def create_distance_controls(self):
        distance_methods = ["Distance by ratio", "Distance by ArUco", "Distance by pinhole", "Manual distance"]
        self.opt_dist_method = StringVar(value="Distance by ratio")

        Label(self.root, text="Distance Method:", font=("Arial", 12)).grid(row=3, column=8)
        dropdown_dist = OptionMenu(self.root, self.opt_dist_method, *distance_methods,
                                   command=lambda _: self.update_distance_fields())
        dropdown_dist.grid(row=3, column=9)

        # Distance control fields
        self.label_h = Label(self.root, text="Object size (cm):  H =", font=("Arial", 12))
        self.label_w = Label(self.root, text="W =", font=("Arial", 12))
        self.label_dist = Label(self.root, text="Desired Distance (cm):", font=("Arial", 12))
        self.dist_label = Label(self.root, text="Distance to Object (cm):", font=("Arial", 13))
        self.entry_width = tk.Entry(self.root, width=10)
        self.entry_height = tk.Entry(self.root, width=10)
        self.entry_dist = tk.Entry(self.root, width=10)

        # ArUco fields
        self.marker_length_label = Label(self.root, text="Marker length (cm):", font=("Arial", 12))
        self.marker_length_entry = tk.Entry(self.root, width=10)

        # Default values
        self.entry_height.insert(0, "27.5")
        self.entry_width.insert(0, "20.5")
        self.entry_dist.insert(0, "70")
        self.marker_length_entry.insert(0, "6")

        self.update_distance_fields()

    def update_distance_fields(self):
        mode = self.opt_dist_method.get()

        # Hide all widgets
        for w in [
            self.label_h, self.label_w, self.label_dist, self.dist_label,
            self.entry_width, self.entry_height, self.entry_dist,
            self.marker_length_label, self.marker_length_entry,
            self.btn_get_calibration, self.btn_calibration_start,
            self.btn_maunal_distance
        ]:
            w.grid_remove()

        if mode in ("Distance by ratio", "Distance by pinhole"):
            self.label_h.grid(row=4, column=8, padx=5, pady=5)
            self.entry_height.grid(row=4, column=9, padx=5, pady=5)
            self.label_w.grid(row=4, column=10, padx=5, pady=5)
            self.entry_width.grid(row=4, column=11, padx=5, pady=5)
            self.label_dist.grid(row=5, column=8, padx=5, pady=5)
            self.entry_dist.grid(row=5, column=9, padx=5, pady=5)
            self.dist_label.grid(row=6, column=8, columnspan=2, padx=5, pady=5)

        elif mode == "Distance by ArUco":
            self.marker_length_label.grid(row=4, column=8)
            self.dist_label.grid(row=6, column=8)
            self.marker_length_entry.grid(row=4, column=9)
            self.label_dist.grid(row=5, column=8)
            self.entry_dist.grid(row=5, column=9)
            self.btn_get_calibration.grid(row=7, column=8)
            self.btn_calibration_start.grid(row=7, column=9)

        elif mode == "Manual distance":
            self.btn_maunal_distance.grid(row=4, column=8)
            self.dist_label.grid(row=5, column=8)


    def drone_connection(self):
        try:
            self.controller.me.connect()
            self.controller.is_connected = True
            self.controller.me.streamoff()
            self.controller.me.streamon()
            print(f"Connected! Battery: {self.controller.me.get_battery()}%")
            self.connected_label.config(text="Connected", fg="green")

            #if not self.flask_server:
                #print("Starting Flask server on port 5000...")
                #self.flask_server = FlaskServer(host="0.0.0.0", port=5000)
                #self.flask_server.start()

            self.update_frame()
        except Exception as e:
            self.controller.is_connected = False
            print("Connection failed:", e)
            self.connected_label.config(text="Not Connected", fg="red")

    def get_maunal_distance(self):

        if self.latest_w and self.latest_h:
            self.w_det = self.latest_w
            self.h_det = self.latest_h
            self.dist_label.config(text=f"[Manual] Reference set: w={self.w_det:.1f}, h={self.h_det:.1f}")
            print(f"[Manual] Reference distance set: w={self.w_det}, h={self.h_det}")
        else:
            self.dist_label.config(text="[Manual] No valid detection to capture")
            print("[Manual] No object detected when trying to set reference.")

    def start_calibration(self):
        if not self.controller.is_connected:
            messagebox.showwarning("Attention", "Connect the drone before starting the calibration.")
            return

        def worker():
            try:
                os.makedirs(self.controller.IMG_SAVE_PATH, exist_ok=True)

                width, height = 640, 480

                # Usamos el stream ya abierto desde drone_connection/update_frame
                frame_read = self.controller.me.get_frame_read()

                print("\nPress 'c' to capture an image, 'q' to quit.\n")
                i = 0
                while True:
                    img = frame_read.frame
                    if img is None:
                        continue

                    img = cv2.resize(img, (width, height))
                    cv2.imshow("Tello View (Calibration)", img)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('c'):
                        filename = os.path.join(self.controller.IMG_SAVE_PATH, f"image_{i:02d}.jpg")
                        cv2.imwrite(filename, img)
                        print(f"Saved Image: {filename}")
                        i += 1
                        cv2.waitKey(200)
                    elif key == ord('q'):
                        break

                cv2.destroyAllWindows()
                messagebox.showinfo("Completed", "Image capture successfully completed.")

            except Exception as e:
                messagebox.showerror("Error", f"Error during calibration:\n{e}")

        threading.Thread(target=worker, daemon=True).start()

    def get_parameters(self):
        def worker():
            try:
                os.makedirs(self.controller.PARAM_SAVE_PATH, exist_ok=True)

                images = glob.glob(os.path.join(self.controller.IMG_SAVE_PATH, "*.jpg"))
                if len(images) == 0:
                    messagebox.showwarning("No images", "No calibration images found.")
                    return

                CHESSBOARD_SIZE = (9, 6)
                SQUARE_SIZE = 0.015
                objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
                objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)
                objp *= SQUARE_SIZE

                objpoints = []
                imgpoints = []
                gray = None
                for fname in images:
                    img = cv2.imread(fname)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

                    if ret:
                        objpoints.append(objp)
                        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30,
                                                              0.001))
                        imgpoints.append(corners2)
                        cv2.drawChessboardCorners(img, CHESSBOARD_SIZE, corners2, ret)
                        cv2.imshow('Calibration', img)
                        cv2.waitKey(100)
                    else:
                        print(f"No board detected in {fname}")

                cv2.destroyAllWindows()

                ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

                print("\nCalibration completed:")
                print("Camera matrix:\n", camera_matrix)
                print("Distortion coefficients:\n", dist_coeffs.ravel())

                mean_error = 0
                for i in range(len(objpoints)):
                    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
                    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                    mean_error += error
                print(f"\nMean reprojection error: {mean_error / len(objpoints):.4f}")

                output_file = os.path.join(self.controller.PARAM_SAVE_PATH, "parametros_camara_tello.npz")
                np.savez(output_file, camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
                print(f"Parameters saved in: {output_file}")
                messagebox.showinfo("Calibration complete", "Camera parameters have been saved successfully.")

            except Exception as e:
                messagebox.showerror("Error", f"Error while obtaining parameters:\n{e}")

        threading.Thread(target=worker, daemon=True).start()

    def detect_objects_color_contour(self, img_dil, img_contour):
        contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(img_contour, (x, y), (x + w, y + h), (0, 255, 0), 2)
            object_center = (x + w // 2, y + h // 2)
            cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)
            return object_center, w, h

        else: return None, 0, 0

    #No tira, falta de CPU o no sé el que, no sale lo de INFO, osea no llega al update frame,MIRARLO
    def detect_objects_neural_network(self, img_contour):
        #results = self.controller.model.track(img_contour, persist=True, conf=0.5, verbose=False)
        results = self.controller.model.predict(img_contour, conf=0.5, verbose=False)
        max_area = 0
        best_box = None

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w_box, h_box = x2 - x1, y2 - y1
                area = w_box * h_box
                if area > max_area:
                    max_area = area
                    best_box = (x1, y1, x2, y2, box)

        if best_box is not None:
            x1, y1, x2, y2, box = best_box
            w, h = x2 - x1, y2 - y1
            cx, cy = x1 + w // 2, y1 + h // 2
            object_center = (cx, cy)

            cv2.rectangle(img_contour, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img_contour, f"{self.controller.model.names[int(box.cls[0])]} {float(box.conf[0]):.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
            cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)
            cv2.putText(img_contour, "YOLO Detection", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            return object_center, w, h

        return None, 0, 0

    def _yolo_worker_loop(self):
        """Hilo que ejecuta la inferencia del modelo YOLO en segundo plano (sin reducción de resolución)."""
        while True:
            frame = self.yolo_queue.get()  # Espera hasta tener frame
            try:
                results = self.controller.model.predict(frame, conf=0.2, verbose=False)
                #results = self.controller.model.track(frame, persist=True, conf=0.4, verbose=False)

                # Solo procesamos para obtener el objeto más grande y su info
                object_center, w, h, boxes_info = self._process_yolo_result(results)

                with self.yolo_lock:
                    # Guardamos también info de las boxes para que el hilo principal pueda dibujar
                    self.yolo_result = (object_center, w, h, boxes_info)

            except Exception as e:
                print("[ERROR] YOLO worker:", e)
                with self.yolo_lock:
                    self.yolo_result = (None, 0, 0, [])

    def _process_yolo_result(self, results):
        """Procesa las detecciones YOLO y devuelve información para dibujar."""
        object_center = None
        w = h = 0
        max_area = 0
        boxes_info = []  # [(x1, y1, x2, y2, label, conf)]

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w_box, h_box = x2 - x1, y2 - y1
                area = w_box * h_box
                conf = float(box.conf[0])
                label = self.controller.model.names[int(box.cls[0])] \
                    if hasattr(self.controller.model, "names") else str(int(box.cls[0]))

                boxes_info.append((x1, y1, x2, y2, label, conf))

                if area > max_area:
                    max_area = area
                    w, h = w_box, h_box
                    object_center = (x1 + w_box // 2, y1 + h_box // 2)

        return object_center, int(w), int(h), boxes_info

    def detect_object_neural_network_game(self, img_contour):
        results = self.controller.model2.track(img_contour, persist=True, conf=0.5, verbose=False)
        max_area = 0
        best_box = None
        detected_label = None

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w_box, h_box = x2 - x1, y2 - y1
                area = w_box * h_box
                if area > max_area:
                    max_area = area
                    best_box = (x1, y1, x2, y2, box)
                    detected_label = int(box.cls[0])

        if best_box is not None:
            x1, y1, x2, y2, box = best_box
            w, h = x2 - x1, y2 - y1
            cx, cy = x1 + w // 2, y1 + h // 2
            object_center = (cx, cy)

            label_name = "horse" if detected_label == 0 else "bird"
            cv2.rectangle(img_contour, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(img_contour, f"{label_name.upper()} {float(box.conf[0]):.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
            cv2.circle(img_contour, object_center, 5, (255, 0, 0), cv2.FILLED)
            cv2.putText(img_contour, "GAME MODE", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            return object_center, w, h, label_name

        return None, 0, 0, None

    def _game_worker_loop(self):
        """Hilo que ejecuta el modelo2.track() (modo juego) en segundo plano (sin dibujo)."""
        while True:
            frame = self.game_queue.get()
            try:
                #results = self.controller.model2.track(frame, persist=True, conf=0.5, verbose=False)
                results = self.controller.model2.predict(frame, conf=0.5, verbose=False)
                # Procesar resultados para obtener info de las detecciones
                object_center, w, h, label_name, boxes_info = self._process_game_result(results)

                with self.game_lock:
                    self.game_result = (object_center, w, h, label_name, boxes_info)
            except Exception as e:
                print("[ERROR] GAME worker:", e)
                with self.game_lock:
                    self.game_result = (None, 0, 0, None, [])

    def _process_game_result(self, results):
        """Procesa las detecciones del modo juego y devuelve datos y boxes para dibujar."""
        max_area = 0
        best_box = None
        detected_label = None
        boxes_info = []  # [(x1, y1, x2, y2, label_name, conf)]

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w_box, h_box = x2 - x1, y2 - y1
                area = w_box * h_box
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label_name = "horse" if cls_id == 0 else "bird"
                boxes_info.append((x1, y1, x2, y2, label_name, conf))

                if area > max_area:
                    max_area = area
                    best_box = (x1, y1, x2, y2)
                    detected_label = label_name

        if best_box is not None:
            x1, y1, x2, y2 = best_box
            w, h = x2 - x1, y2 - y1
            cx, cy = x1 + w // 2, y1 + h // 2
            object_center = (cx, cy)
            return object_center, w, h, detected_label, boxes_info

        return None, 0, 0, None, boxes_info

    def distance_by_ratio(self, img_display, object_center, w, h):
        ratio_width = 5.2 / 5.5
        ratio_height = 1.2
        focal_length_width = img_display.shape[0] / ratio_width
        focal_length_height = img_display.shape[1] / ratio_height
        obj_height = float(self.entry_height.get()) if self.entry_height.get() else 27.0
        obj_width = float(self.entry_width.get()) if self.entry_width.get() else 20.0

        if object_center and obj_width and obj_height and w and h:
            dist_to_camera_width = float(obj_width) * focal_length_width / w * 2 - 22
            dist_to_camera_height = float(obj_height) * focal_length_height / h * 2 - 22
            distance = (dist_to_camera_width + dist_to_camera_height) / 2
            self.dist_label.config(text="Distance to Object: " + str(distance.__round__(0)))
            return distance.__round__(0)
        else:
            self.dist_label.config(text="[Ratio] Distance: --")
            return None

    def distance_by_aruco(self, gray_highres, img_contour, camera_matrix, dist_coeffs):
        dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
        detector = aruco.ArucoDetector(dictionary)
        corners, ids, rejected = detector.detectMarkers(gray_highres)

        if ids is not None:
            aruco.drawDetectedMarkers(img_contour, corners, ids)
            marker_length_cm = float(self.marker_length_entry.get()) if self.marker_length_entry.get() else 6
            marker_length = marker_length_cm / 100  # m

            for i in range(len(ids)):
                obj_points = np.array([
                    [-marker_length / 2, -marker_length / 2, 0],
                    [marker_length / 2, -marker_length / 2, 0],
                    [marker_length / 2, marker_length / 2, 0],
                    [-marker_length / 2, marker_length / 2, 0]
                ], dtype=np.float32)

                ret, rvec, tvec = cv2.solvePnP(obj_points, corners[i], camera_matrix, dist_coeffs)
                cv2.drawFrameAxes(img_contour, camera_matrix, dist_coeffs, rvec, tvec, 0.05)
                distance = float(tvec[2]) * 100  # cm
                self.dist_label.config(text=f"[ArUco] Distance: {distance:.2f} cm")

                return distance
        else:
            self.dist_label.config(text="[ArUco] No marker visible")
            return None

    def distance_by_pinhole(self, camera_matrix, w, h):
        W_real = float(self.entry_width.get()) if self.entry_width.get() else 20.5
        H_real = float(self.entry_height.get()) if self.entry_height.get() else 27.5
        scale_x = 640 / self.panel_width
        scale_y = 480 / self.panel_height
        w_scaled = w * scale_x if w else 0
        h_scaled = h * scale_y if h else 0

        if w_scaled > 0 and h_scaled > 0:
            fx = camera_matrix[0, 0]
            fy = camera_matrix[1, 1]
            dist_width = (fx * W_real) / w_scaled
            dist_height = (fy * H_real) / h_scaled
            distance = (dist_width + dist_height) / 2
            self.dist_label.config(text=f"[Pinhole] Distance: {distance:.2f} cm")
            return distance
        else:
            self.dist_label.config(text="[Pinhole] No object detected")
            return None

    def distance_by_hand(self, w ,h):
        if w and h and self.w_det and self.h_det:
            area = w * h
            area_det = self.w_det * self.h_det
            diff_area = area - area_det
            self.dist_label.config(text=f"Area Error: {diff_area}")
            if diff_area < 0:
                return math.sqrt(abs(diff_area))
            else:
                return -math.sqrt(abs(diff_area))
        else:
            return None

    def update_frame(self):

        if self.controller.is_connected:
            self.battery_label.config(text=f"Battery: {self.controller.me.get_battery()}%", fg="blue")
            frame_read = self.controller.me.get_frame_read()
            my_frame = frame_read.frame

            img_display = cv2.resize(my_frame, (self.panel_width, self.panel_height))
            img_contour = img_display.copy()
            img_hsv = cv2.cvtColor(img_display, cv2.COLOR_BGR2HSV)

            lower = np.array([self.h_min.get(), self.s_min.get(), self.v_min.get()])
            upper = np.array([self.h_max.get(), self.s_max.get(), self.v_max.get()])
            mask = cv2.inRange(img_hsv, lower, upper)
            result = cv2.bitwise_and(img_display, img_display, mask=mask)

            img_blur = cv2.GaussianBlur(result, (7, 7), 1)
            img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
            img_canny = cv2.Canny(img_gray, self.t1.get(), self.t2.get())
            kernel = np.ones((5, 5), np.uint8)
            img_dil = cv2.dilate(img_canny, kernel, iterations=1)

            object_center = None
            distance = None
            w, h = None, None
            detection_mode = self.detection_var.get()


            if detection_mode == "Color Contour":
                object_center, w, h = self.detect_objects_color_contour(img_dil, img_contour)

            elif detection_mode == "Neural Network" and self.controller.model is not None:
                try:
                    self.yolo_queue.put_nowait(img_contour.copy())
                except queue.Full:
                    pass

                with self.yolo_lock:
                    object_center, w, h, boxes_info = self.yolo_result

                if boxes_info:
                    for (x1, y1, x2, y2, label, conf) in boxes_info:
                        cv2.rectangle(img_contour, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(img_contour, f"{label} {conf:.2f}",
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7, (255, 255, 255), 2)


            elif detection_mode == "Game Mode" and self.controller.model2 is not None:
                try:
                    self.game_queue.put_nowait(img_contour.copy())
                except queue.Full:
                    pass

                with self.game_lock:
                    object_center, w, h, detected_label, boxes_info = self.game_result


                if boxes_info:

                    largest_box = max(
                        boxes_info,
                        key=lambda b: (b[2] - b[0]) * (b[3] - b[1])
                    )
                    x1, y1, x2, y2, label_name, conf = largest_box


                    cv2.rectangle(img_contour, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(img_contour, f"{label_name.upper()} {conf:.2f}",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (255, 255, 255), 2)


                    detected_label = label_name
                else:
                    detected_label = None

                if detected_label is not None:
                    if detected_label != self.last_detected_label:
                        if detected_label == "horse":
                            print("Detected HORSE → Drone UP 20 cm")
                            if self.simulation_var.get() == "False":
                                self.controller.me.move_up(20)
                        elif detected_label == "bird":
                            print("Detected BIRD → Drone DOWN 20 cm")
                            if self.simulation_var.get() == "False":
                                self.controller.me.move_down(20)

                        self.last_detected_label = detected_label
                        self.action_done_for_label = detected_label
            else:
                cv2.putText(img_contour, "No detection mode active", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            self.latest_w = w
            self.latest_h = h


            img_highres = cv2.resize(my_frame, (640, 480))
            gray_highres = cv2.cvtColor(img_highres, cv2.COLOR_BGR2GRAY)

            mode = self.opt_dist_method.get()

            camera_matrix = self.camera_matrix
            dist_coeffs = self.dist_coeffs


            if mode == "Distance by ratio" and object_center is not None:
                distance = self.distance_by_ratio(img_display, object_center, w, h)

            elif mode == "Distance by ArUco":
                distance = self.distance_by_aruco(gray_highres, img_contour, camera_matrix, dist_coeffs)

            elif mode == "Distance by pinhole":
                distance = self.distance_by_pinhole(camera_matrix, w, h)

            elif mode == "Manual distance":
                distance = self.distance_by_hand(w, h)
            else:
                self.dist_label.config(text="No calibration available")

            if object_center and distance is not None:
                cx, cy = object_center
                cv2.line(img_contour, (int(self.panel_width / 2), int(self.panel_height / 2)), (cx, cy), (0, 0, 255), 3)
                desired_distance = float(self.entry_dist.get()) if self.entry_dist.get() else 70

                error_x = cx - (self.panel_width / 2)
                if self.opt_cam.get() == "Drone Camera":
                    error_y = (self.panel_height / 2) - cy

                else:
                    error_y = cy - (self.panel_height / 2)


                if mode == "Distance by ratio":
                    e_max = (self.panel_width / 2 + self.panel_height / 2) / 2
                    error_z = e_max / desired_distance * distance - e_max

                elif mode == "Manual distance":
                    error_z = distance if distance else 0

                else:
                    error_z = distance - desired_distance

                self.controller.integral_x += error_x
                derivative_x = error_x - self.controller.prev_error_x
                self.controller.integral_y += error_y
                derivative_y = error_y - self.controller.prev_error_y
                self.controller.integral_z += error_z
                derivative_z = error_z - self.controller.prev_error_z

                Kpx, Kix, Kdx = self.Kp_x.get(), self.Ki_x.get(), self.Kd_x.get()
                Kpy, Kiy, Kdy = self.Kp_y.get(), self.Ki_y.get(), self.Kd_y.get()
                Kpz, Kiz, Kdz = self.Kp_z.get(), self.Ki_z.get(), self.Kd_z.get()

                if self.opt.get() == "P":
                    speed_x = int(Kpx * error_x)
                    speed_y = int(Kpy * error_y)
                    speed_z = int(Kpz * error_z)
                elif self.opt.get() == "I":
                    speed_x = int(Kix * self.controller.integral_x)
                    speed_y = int(Kiy * self.controller.integral_y)
                    speed_z = int(Kiz * self.controller.integral_z)
                elif self.opt.get() == "D":
                    speed_x = int(Kdx * derivative_x)
                    speed_y = int(Kdy * derivative_y)
                    speed_z = int(Kdz * derivative_z)
                elif self.opt.get() == "PID":
                    speed_x = int(Kpx * error_x + Kix * self.controller.integral_x + Kdx * derivative_x)
                    speed_y = int(Kpy * error_y + Kiy * self.controller.integral_y + Kdy * derivative_y)
                    speed_z = int(Kpz * error_z + Kiz * self.controller.integral_z + Kdz * derivative_z)
                elif self.opt.get() == "PD":
                    speed_x = int(Kpx * error_x + Kdx * derivative_x)
                    speed_y = int(Kpy * error_y + Kdy * derivative_y)
                    speed_z = int(Kpz * error_z + Kdz * derivative_z)
                elif self.opt.get() == "PI":
                    speed_x = int(Kpx * error_x + Kix * self.controller.integral_x)
                    speed_y = int(Kpy * error_y + Kiy * self.controller.integral_y)
                    speed_z = int(Kpz * error_z + Kiz * self.controller.integral_z)
                else:
                    speed_x, speed_y, speed_z = error_x, error_y, error_z

                self.controller.me.left_right_velocity = 0
                self.controller.me.for_back_velocity = 0
                self.controller.me.up_down_velocity = 0
                self.controller.me.yaw_velocity = 0
                if self.opt_cam.get() == "Drone Camera":
                    self.controller.me.yaw_velocity = int(np.clip(speed_x, -self.max_velocity.get(), self.max_velocity.get()))
                    self.controller.me.up_down_velocity = int(np.clip(speed_y, -self.max_velocity.get(), self.max_velocity.get()))
                    self.controller.me.for_back_velocity = int(np.clip(speed_z, -self.max_velocity.get(), self.max_velocity.get()))
                else:
                    self.controller.me.left_right_velocity = int(np.clip(speed_x, -self.max_velocity.get(), self.max_velocity.get()))
                    self.controller.me.for_back_velocity = int(np.clip(speed_y, -self.max_velocity.get(), self.max_velocity.get()))
                    self.controller.me.up_down_velocity = 0


                self.controller.prev_error_x, self.controller.prev_error_y, self.controller.prev_error_z = error_x, error_y, error_z

                if self.simulation_var.get() == "True":
                    self.controller.me.send_rc_control(0, 0, 0, 0)
                else:
                    self.controller.me.send_rc_control(self.controller.me.left_right_velocity,
                                                       self.controller.me.for_back_velocity,
                                                       self.controller.me.up_down_velocity,
                                                       self.controller.me.yaw_velocity)

                if self.opt_cam.get() == "Drone Camera":
                    self.lr_label.config(text=f"Left-Right Velocity = {0}")
                    self.fb_label.config(text=f"For-Back Velocity = {speed_z}")
                    self.ud_label.config(text=f"Up-Down Velocity = {speed_y}")
                    self.yaw_label.config(text=f"Yaw Velocity = {speed_x}")
                else:
                    self.lr_label.config(text=f"Left-Right Velocity = {speed_x}")
                    self.fb_label.config(text=f"For-Back Velocity = {speed_y}")
                    self.ud_label.config(text=f"Up-Down Velocity = {0}")
                    self.yaw_label.config(text=f"Yaw Velocity = {0}")



            frames_to_show = [img_dil, img_contour]
            for labels, f in zip(self.video_labels, frames_to_show):
                if len(f.shape) == 2:
                    f = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
                else:
                    f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
                imgtk = ImageTk.PhotoImage(Image.fromarray(f))
                labels.imgtk = imgtk
                labels.config(image=imgtk)

        detection_mode = self.detection_var.get()
        if detection_mode == "Color Contour":
            self.root.after(30, self.update_frame)
        else:
            self.root.after(30, self.update_frame)


