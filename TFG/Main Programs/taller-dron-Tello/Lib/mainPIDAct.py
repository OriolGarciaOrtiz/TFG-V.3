import cv2
import numpy as np
from djitellopy import Tello
import tkinter as tk
from tkinter import  Scale, messagebox, OptionMenu, Label, StringVar
from PIL import Image, ImageTk
import threading
import cv2.aruco as aruco
import os
import glob
from ultralytics import YOLO

# ---------------- Globals ----------------
is_connected = False
prev_error_x = 0
prev_error_y = 0
prev_error_z = 0
integral_x = 0
integral_y = 0
integral_z = 0

# Paths
IMG_SAVE_PATH = r"C:\Tello\taller-dron-Tello\Lib\Img_Calibracion"
PARAM_SAVE_PATH = r"C:\Tello\taller-dron-Tello\Lib\Parameters"
os.makedirs(IMG_SAVE_PATH, exist_ok=True)
os.makedirs(PARAM_SAVE_PATH, exist_ok=True)
def start_calibration():
    if not is_connected:
        messagebox.showwarning("Attention", "Connect the drone before starting the calibration.")
        return

    def worker():
        try:
            SAVE_PATH = r"C:\Tello\taller-dron-Tello\Lib\Img_Calibracion"
            os.makedirs(SAVE_PATH, exist_ok=True)

            width, height = 640, 480

            # Usamos el stream ya abierto desde drone_connection/update_frame
            frame_read = me.get_frame_read()

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
                    filename = os.path.join(SAVE_PATH, f"image_{i:02d}.jpg")
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



def get_parameters():
    def worker():
        try:
            IMG_PATH = r"C:\Tello\taller-dron-Tello\Lib\Img_Calibracion"
            SAVE_PATH = r"C:\Tello\taller-dron-Tello\Lib\Parameters"
            os.makedirs(SAVE_PATH, exist_ok=True)

            images = glob.glob(os.path.join(IMG_PATH, "*.jpg"))
            if len(images) == 0:
                messagebox.showwarning("No images", "No calibration images found.")
                return

            CHESSBOARD_SIZE = (9, 6)
            SQUARE_SIZE = 0.015
            objp = np.zeros((CHESSBOARD_SIZE[0]*CHESSBOARD_SIZE[1], 3), np.float32)
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
                                                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
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

            output_file = os.path.join(SAVE_PATH, "parametros_camara_tello.npz")
            np.savez(output_file, camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
            print(f"Parameters saved in: {output_file}")
            messagebox.showinfo("Calibration complete", "Camera parameters have been saved successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Error while obtaining parameters:\n{e}")

    threading.Thread(target=worker, daemon=True).start()


# ---------------- Drone connection ----------------
def drone_connection():
    global is_connected, me
    try:
        me.connect()
        is_connected = True
        me.streamoff()
        me.streamon()
        print(f"Connected! Battery: {me.get_battery()}%")
        connected_label.config(text="Connected", fg="green")
    except Exception as e:
        is_connected = False
        print("Connection failed:", e)
        connected_label.config(text="Not Connected", fg="red")


def safe_takeoff():
    if is_connected:
        threading.Thread(target=me.takeoff).start()


def landing():
    if is_connected:
        threading.Thread(target=me.land).start()


def emergency():
    if is_connected:
        threading.Thread(target=me.emergency).start()



# ---------------- Drone initialization ----------------
me = Tello()
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0
me.speed = 0

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Drone Controller PID")
root.geometry("1920x1080")

# # ---------------- Basic Labels and buttons ----------------
connected_label = Label(root, text="Not Connected", font=("Arial", 14))
connected_label.grid(row=0, column=0, padx=10, pady=10)

connect_button = tk.Button(root, text="Connect", command=drone_connection)
connect_button.grid(row=0, column=1, padx=10, pady=10)

battery_label = Label(root, text="Battery: -", font=("Arial", 14))
battery_label.grid(row=0, column=2, padx=10, pady=10)

take_off_button = tk.Button(root, text="Take Off", command=safe_takeoff)
take_off_button.place(x=800, y=100)

landing_button = tk.Button(root, text="Landing", command=landing)
landing_button.place(x=900, y=100)

emergency_button = tk.Button(root, text="Emergency", command=emergency)
emergency_button.place(x=1000, y=100)

btn_calibration_start = tk.Button(root, text="Start Calibration", command=lambda: threading.Thread(target=start_calibration, daemon=True).start())
btn_calibration_start.grid(row=0, column=3, padx=10, pady=10)

btn_get_calibration = tk.Button(root, text="Get Calibrated Parameters", command=lambda: threading.Thread(target=get_parameters, daemon=True).start())
btn_get_calibration.grid(row=0, column=4, padx=10, pady=10)

# ---------------- Simulation Mode ----------------
simulation_label = tk.Label(root, text="Simulation Mode:", font=("Arial", 14))
simulation_label.grid(row=0, column=5, padx=(20, 5), pady=10)

simulation_var = tk.StringVar(value="True")
simulation_dropdown = tk.OptionMenu(root, simulation_var, "True", "False")
simulation_dropdown.grid(row=0, column=6, padx=10, pady=10)

#Object detection mode

detection_label = tk.Label(root, text="Detection Mode:", font=("Arial", 14))
detection_label.grid(row=0, column=7, padx=(20, 5), pady=10)

detection_var = tk.StringVar(value="Color Contour")
detection_dropdown = tk.OptionMenu(root, detection_var, "Color Contour", "Neural Network")
detection_dropdown.grid(row=0, column=8, padx=10, pady=10)


# ---------------- PID dropdown ----------------
PID_values = ["P", "I", "D", "PD", "PI", "PID", "None"]
Label(root, text="Controller used =", font=("Arial", 14)).place(x=1200, y=100)
opt = tk.StringVar(value="PID")
dropdown_x = OptionMenu(root, opt, *PID_values)
dropdown_x.place(x=1350, y=95)


# ---------------- Camera modes ----------------
Mode_cam = ["Mirror", "Drone Camera"]
opt_cam = tk.StringVar(value="Drone Camera")
dropdown_mode = OptionMenu(root, opt_cam, *Mode_cam)
dropdown_mode.place(x=1325, y=20)
Label(root, text="Mode used =", font=("Arial", 14)).place(x=1200, y=25)

# ---------------- K values ----------------
Kp_x = tk.DoubleVar(value=0.42)
Ki_x = tk.DoubleVar(value=0.0005)
Kd_x = tk.DoubleVar(value=1.9)

Kp_y = tk.DoubleVar(value=0.42)
Ki_y = tk.DoubleVar(value=0.0005)
Kd_y = tk.DoubleVar(value=1.9)

Kp_z = tk.DoubleVar(value=0.42)
Ki_z = tk.DoubleVar(value=0.0005)
Kd_z = tk.DoubleVar(value=1.9)


# ---------------- Sliders PID-X ----------------
kp_label_x = tk.Label(root, text="Kp-X (Proportional)")
kp_label_x.place(x=800, y=150)
kp_slider_x = tk.Scale(root, from_=0, to=2.0, resolution=0.01, orient="horizontal", variable=Kp_x, length=200)
kp_slider_x.place(x=800, y=175)

ki_label_x = tk.Label(root, text="Ki-X (Integral)")
ki_label_x.place(x=1000, y=150)
ki_slider_x = tk.Scale(root, from_=0, to=0.01, resolution=0.0001, orient="horizontal", variable=Ki_x, length=200)
ki_slider_x.place(x=1000, y=175)

kd_label_x = tk.Label(root, text="Kd-X (Derivative)")
kd_label_x.place(x=1200, y=150)
kd_slider_x = tk.Scale(root, from_=0, to=5, resolution=0.1, orient="horizontal", variable=Kd_x, length=200)
kd_slider_x.place(x=1200, y=175)

# ---------------- Sliders PID-Y ----------------
kp_label_y = tk.Label(root, text="Kp-Y (Proportional)")
kp_label_y.place(x=800, y=250)
kp_slider_y = tk.Scale(root, from_=0, to=2.0, resolution=0.01, orient="horizontal", variable=Kp_y, length=200)
kp_slider_y.place(x=800, y=275)

ki_label_y = tk.Label(root, text="Ki-Y (Integral)")
ki_label_y.place(x=1000, y=250)
ki_slider_y = tk.Scale(root, from_=0, to=0.01, resolution=0.0001, orient="horizontal", variable=Ki_y, length=200)
ki_slider_y.place(x=1000, y=275)

kd_label_y = tk.Label(root, text="Kd-Y (Derivative)")
kd_label_y.place(x=1200, y=250)
kd_slider_y = tk.Scale(root, from_=0, to=5, resolution=0.1, orient="horizontal", variable=Kd_y, length=200)
kd_slider_y.place(x=1200, y=275)

# ---------------- Sliders PID-Z ----------------
kp_label_z = tk.Label(root, text="Kp-Z (Proportional)")
kp_label_z.place(x=800, y=350)
kp_slider_z = tk.Scale(root, from_=0, to=2.0, resolution=0.01, orient="horizontal", variable=Kp_z, length=200)
kp_slider_z.place(x=800, y=375)

ki_label_z = tk.Label(root, text="Ki-Z (Integral)")
ki_label_z.place(x=1000, y=400)
ki_slider_z = tk.Scale(root, from_=0, to=0.01, resolution=0.0001, orient="horizontal", variable=Ki_z, length=200)
ki_slider_z.place(x=1000, y=375)

kd_label_z = tk.Label(root, text="Kd-Z (Derivative)")
kd_label_z.place(x=1200, y=350)
kd_slider_z = tk.Scale(root, from_=0, to=5, resolution=0.1, orient="horizontal", variable=Kd_z, length=200)
kd_slider_z.place(x=1200, y=375)

# ---------------- Maximum velocity ----------------
Label(root, text="Max velocity:", font=("Arial", 12)).place(x=400, y=370)
max_velocity = tk.DoubleVar(value=60)
velocity_slider = tk.Scale(root, from_=0, to=60, resolution=1, orient="horizontal", variable=max_velocity, length=300)
velocity_slider.place(x=400, y=400)

# ---------------- Video Panels ----------------
video_frame = tk.Frame(root)
video_frame.place(relx=0.5, rely=1.0, anchor="s", relwidth=1.0, height=400)
video_titles = ["Original", "HSV Mask", "Edges", "Dilated", "Contour"]
video_labels = []

panel_width, panel_height = 320, 240
for i, title in enumerate(video_titles):
    Label(video_frame, text=title, font=("Arial", 12)).grid(row=0, column=i, padx=15, pady=(5, 2))
    lbl = Label(video_frame, width=panel_width, height=panel_height)
    lbl.grid(row=1, column=i, padx=15, pady=10)
    video_labels.append(lbl)
    video_frame.columnconfigure(i, weight=1, uniform="cols")

# ---------------- Sliders HSV y Canny ----------------
h_min, h_max = tk.IntVar(value=35), tk.IntVar(value=85)
s_min, s_max = tk.IntVar(value=55), tk.IntVar(value=255)
v_min, v_max = tk.IntVar(value=100), tk.IntVar(value=255)

# ---------------- Color sliders ----------------
Scale(root, from_=0, to=255, orient="horizontal", variable=h_min, length=200).place(x=100, y=50)
Label(root, text="Hue Min:", font=("Arial", 12)).place(x=10, y=60)

Scale(root, from_=0, to=255, orient="horizontal", variable=h_max, length=200).place(x=100, y=100)
Label(root, text="Hue Max:", font=("Arial", 12)).place(x=10, y=110)

Scale(root, from_=0, to=255, orient="horizontal", variable=s_min, length=200).place(x=100, y=150)
Label(root, text="Sat Min:", font=("Arial", 12)).place(x=10, y=160)

Scale(root, from_=0, to=255, orient="horizontal", variable=s_max, length=200).place(x=100, y=200)
Label(root, text="Sat Max:", font=("Arial", 12)).place(x=10, y=210)

Scale(root, from_=0, to=255, orient="horizontal", variable=v_min, length=200).place(x=100, y=250)
Label(root, text="Value Min:", font=("Arial", 12)).place(x=10, y=260)

Scale(root, from_=0, to=255, orient="horizontal", variable=v_max, length=200).place(x=100, y=300)
Label(root, text="Value Max:", font=("Arial", 12)).place(x=10, y=310)

# ---------------- Threshold sliders ----------------
t1, t2 = tk.IntVar(value=166), tk.IntVar(value=171)
Scale(root, from_=0, to=255, orient="horizontal", variable=t1, length=200).place(x=100, y=350)
Scale(root, from_=0, to=255, orient="horizontal", variable=t2, length=200).place(x=100, y=400)
Label(root, text="Threshold1", font=("Arial", 12)).place(x=10, y=370)
Label(root, text="Threshold2", font=("Arial", 12)).place(x=10, y=420)

# ---------------- Velocity labels ----------------
lr_label = Label(root, text="Left-Right Velocity = 0", font=("Arial", 14))
lr_label.place(x=400, y=170)
fb_label = Label(root, text="For-Back Velocity = 0", font=("Arial", 14))
fb_label.place(x=400, y=220)
ud_label = Label(root, text="Up-Down Velocity = 0", font=("Arial", 14))
ud_label.place(x=400, y=270)
yaw_label = Label(root, text="Yaw Velocity = 0", font=("Arial", 14))
yaw_label.place(x=400, y=320)


distance_methods = ["Distance by ratio", "Distance by ArUco", "Distance by pinhole"]
opt_dist_method = StringVar(value="Distance by ratio")

Label(root, text="Distance Method:", font=("Arial", 14)).place(x=1200, y=150)
dropdown_dist = OptionMenu(root, opt_dist_method, *distance_methods, command=lambda _: update_distance_fields())
dropdown_dist.place(x=1400, y=145)


# Ratio
label_h = Label(root, text="Object size (cm):  H =", font=("Arial", 14))
label_w = Label(root, text="W =", font=("Arial", 14))
label_dist = Label(root, text="Desired Distance (cm):", font=("Arial", 14))
dist_label = Label(root, text="Distance to Object (cm):", font=("Arial", 14))
entry_width = tk.Entry(root, width=10)
entry_height = tk.Entry(root, width=10)
entry_dist = tk.Entry(root, width=10)

#Aruco
marker_length_label = Label(root, text="Marker length (cm):", font=("Arial", 14))
marker_length_entry = tk.Entry(root, width=10)



# --- Default values ---
entry_height.insert(0, "27.5")
entry_width.insert(0, "20.5")
entry_dist.insert(0, "70")
marker_length_entry.insert(0, "6")

def update_distance_fields():
    mode = opt_dist_method.get()

    for w in [label_h, label_w, label_dist, dist_label,
              entry_width, entry_height, entry_dist,
              marker_length_label, marker_length_entry]:
        w.place_forget()

    if mode == "Distance by ratio" or mode == "Distance by pinhole":
        label_h.place(x=400, y=60)
        label_w.place(x=675, y=60)
        label_dist.place(x=400, y=110)
        dist_label.place(x=800, y=60)
        entry_width.place(x=720, y=65)
        entry_height.place(x=595, y=65)
        entry_dist.place(x=600, y=115)
    elif mode == "Distance by ArUco":
        marker_length_label.place(x=400, y=60)
        dist_label.place(x=800, y=60)
        marker_length_entry.place(x=570, y=65)
        label_dist.place(x=400, y=110)
        entry_dist.place(x=600, y=115)



# Initialize default view
update_distance_fields()


#Load NN
try:
    model = YOLO("best_RC_Final.pt")
    print("YOLO model loaded successfully.")
except Exception as e:
    print("Could not load YOLO model:", e)
    model = None

# ---------------- Frame updating ----------------

def update_frame():
    global prev_error_x, prev_error_y, prev_error_z, integral_x, integral_y, integral_z

    if is_connected:
        battery_label.config(text=f"Battery: {me.get_battery()}%", fg="blue")
        frame_read = me.get_frame_read()
        my_frame = frame_read.frame

        img_display = cv2.resize(my_frame, (panel_width, panel_height))
        img_contour = img_display.copy()
        img_hsv = cv2.cvtColor(img_display, cv2.COLOR_BGR2HSV)

        lower = np.array([h_min.get(), s_min.get(), v_min.get()])
        upper = np.array([h_max.get(), s_max.get(), v_max.get()])
        mask = cv2.inRange(img_hsv, lower, upper)
        result = cv2.bitwise_and(img_display, img_display, mask=mask)

        img_blur = cv2.GaussianBlur(result, (7, 7), 1)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_gray, t1.get(), t2.get())
        kernel = np.ones((5, 5), np.uint8)
        img_dil = cv2.dilate(img_canny, kernel, iterations=1)

        object_center = None
        distance = None
        x, y, w, h = 0, 0, 0, 0
        detection_mode = detection_var.get()

        if detection_mode == "Color Contour":
            contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(img_contour, (x, y), (x + w, y + h), (0, 255, 0), 2)
                object_center = (x + w // 2, y + h // 2)
                cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)

        elif detection_mode == "Neural Network" and model is not None:
            results = model.predict(img_contour, conf=0.5, verbose=False)
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
                cv2.putText(img_contour, f"{model.names[int(box.cls[0])]} {float(box.conf[0]):.2f}",
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)
                cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)

                cv2.putText(img_contour, "YOLO Detection", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            cv2.putText(img_contour, "No detection mode active", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        img_highres = cv2.resize(my_frame, (640, 480))
        gray_highres = cv2.cvtColor(img_highres, cv2.COLOR_BGR2GRAY)

        mode = opt_dist_method.get()
        PARAM_PATH = r"C:\Tello\taller-dron-Tello\Lib\Parameters"
        file_path = os.path.join(PARAM_PATH, "parametros_camara_tello.npz")
        #PROBLEMA: Las imagenes están en 320x240 pero yo la calibración la hago para 640x480 así que he tenido que reescalar
        #para el pinhole y usar 640x480 en aruco. Lo suyo sería cambiar la calibración a 320x240 pero la calidad va a bajar bastante
        # y no va a sacar distancias focales tan precisas
        if mode == "Distance by ratio" and object_center is not None:
            ratio_width = 5.2 / 5.5
            ratio_height = 1.2
            focal_length_width = img_display.shape[0] / ratio_width
            focal_length_height = img_display.shape[1] / ratio_height
            obj_height = float(entry_height.get()) if entry_height.get() else 27.0
            obj_width = float(entry_width.get()) if entry_width.get() else 20.0

            if object_center and obj_width and w > 0:
                dist_to_camera_width = float(obj_width) * focal_length_width / w * 2 - 22
                dist_to_camera_height = float(obj_height) * focal_length_height / h * 2 - 22
                distance = (dist_to_camera_width + dist_to_camera_height) / 2
                dist_label.config(text="Distance to Object: " + str(distance.__round__(0)))
            else:
                dist_label.config(text="[Ratio] Distance: --")

        elif mode in ["Distance by ArUco", "Distance by pinhole"] and os.path.exists(file_path):
            data = np.load(file_path)
            camera_matrix = data['camera_matrix']
            dist_coeffs = data['dist_coeffs']

            if mode == "Distance by ArUco":
                dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
                detector = aruco.ArucoDetector(dictionary)
                corners, ids, rejected = detector.detectMarkers(gray_highres)

                if ids is not None:
                    aruco.drawDetectedMarkers(img_contour, corners, ids)
                    marker_length_cm = float(marker_length_entry.get()) if marker_length_entry.get() else 6
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
                        dist_label.config(text=f"[ArUco] Distance: {distance:.2f} cm")
                else:
                    dist_label.config(text="[ArUco] No marker visible")

            elif mode == "Distance by pinhole" and object_center is not None:
                W_real = float(entry_width.get()) if entry_width.get() else 20.5
                H_real = float(entry_height.get()) if entry_height.get() else 27.5
                scale_x = 640 / panel_width
                scale_y = 480 / panel_height
                w_scaled = w * scale_x
                h_scaled = h * scale_y

                if w_scaled > 0 and h_scaled > 0:
                    fx = camera_matrix[0, 0]
                    fy = camera_matrix[1, 1]
                    dist_width = (fx * W_real) / w_scaled
                    dist_height = (fy * H_real) / h_scaled
                    distance = (dist_width + dist_height) / 2
                    dist_label.config(text=f"[Pinhole] Distance: {distance:.2f} cm")
                else:
                    dist_label.config(text="[Pinhole] No object detected")

        else:
            dist_label.config(text="No calibration available")

        if object_center and distance is not None:
            cx, cy = object_center
            cv2.line(img_contour, (int(panel_width / 2), int(panel_height / 2)), (cx, cy), (0, 0, 255), 3)
            desired_distance = float(entry_dist.get()) if entry_dist.get() else 70

            error_x = cx - (panel_width / 2)
            error_y = (panel_height / 2) - cy

            if mode == "Distance by ratio":
                e_max = (panel_width / 2 + panel_height / 2) / 2
                error_z = e_max / desired_distance * distance - e_max
            else:  # ArUco o Pinhole
                error_z = distance - desired_distance

            integral_x += error_x
            derivative_x = error_x - prev_error_x
            integral_y += error_y
            derivative_y = error_y - prev_error_y
            integral_z += error_z
            derivative_z = error_z - prev_error_z

            Kpx, Kix, Kdx = Kp_x.get(), Ki_x.get(), Kd_x.get()
            Kpy, Kiy, Kdy = Kp_y.get(), Ki_y.get(), Kd_y.get()
            Kpz, Kiz, Kdz = Kp_z.get(), Ki_z.get(), Kd_z.get()

            if opt.get() == "P":
                speed_x = int(Kpx * error_x)
                speed_y = int(Kpy * error_y)
                speed_z = int(Kpz * error_z)
            elif opt.get() == "I":
                speed_x = int(Kix * integral_x)
                speed_y = int(Kiy * integral_y)
                speed_z = int(Kiz * integral_z)
            elif opt.get() == "D":
                speed_x = int(Kdx * derivative_x)
                speed_y = int(Kdy * derivative_y)
                speed_z = int(Kdz * derivative_z)
            elif opt.get() == "PID":
                speed_x = int(Kpx*error_x + Kix*integral_x + Kdx*derivative_x)
                speed_y = int(Kpy*error_y + Kiy*integral_y + Kdy*derivative_y)
                speed_z = int(Kpz*error_z + Kiz*integral_z + Kdz*derivative_z)
            elif opt.get() == "PD":
                speed_x = int(Kpx*error_x + Kdx*derivative_x)
                speed_y = int(Kpy*error_y + Kdy*derivative_y)
                speed_z = int(Kpz*error_z + Kdz*derivative_z)
            elif opt.get() == "PI":
                speed_x = int(Kpx*error_x + Kix*integral_x)
                speed_y = int(Kpy*error_y + Kiy*integral_y)
                speed_z = int(Kpz*error_z + Kiz*integral_z)
            else:
                speed_x, speed_y, speed_z = error_x, error_y, error_z

            me.left_right_velocity = 0
            me.for_back_velocity = 0
            me.up_down_velocity = 0
            me.yaw_velocity = 0

            me.yaw_velocity = int(np.clip(speed_x, -max_velocity.get(), max_velocity.get()))
            me.up_down_velocity = int(np.clip(speed_y, -max_velocity.get(), max_velocity.get()))
            me.for_back_velocity = int(np.clip(speed_z, -max_velocity.get(), max_velocity.get()))

            prev_error_x, prev_error_y, prev_error_z = error_x, error_y, error_z

            if simulation_var.get() == "True":
                me.send_rc_control(0, 0, 0, 0)
            else:
                me.send_rc_control(me.left_right_velocity,
                                   me.for_back_velocity,
                                   me.up_down_velocity,
                                   me.yaw_velocity)

        frames_to_show = [img_display, result, img_canny, img_dil, img_contour]
        for labels, f in zip(video_labels, frames_to_show):
            if len(f.shape) == 2:
                f = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
            else:
                f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(Image.fromarray(f))
            labels.imgtk = imgtk
            labels.config(image=imgtk)

    root.after(1, update_frame)
    #root.after(30, update_frame)



# ---------------- Start Loop ----------------
update_frame()
root.mainloop()
