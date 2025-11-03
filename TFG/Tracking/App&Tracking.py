import cv2
import numpy as np
from djitellopy import Tello
import tkinter as tk
from tkinter import Label, Scale, OptionMenu
from PIL import Image, ImageTk
import threading
# ---------------- Globales ----------------
is_connected = False
prev_error_x = 0
prev_error_y = 0
integral_x = 0
integral_y = 0
errorXlist = list()
errorYlist = list()
start_error = False

# ---------------- Conexión con el dron ----------------
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
    global start_error
    if is_connected:
        threading.Thread(target=me.takeoff).start()
        start_error = True


def landing():
    if is_connected:
        threading.Thread(target=me.land).start()

def emergency():
    if is_connected:
        threading.Thread(target=me.emergency).start()

# ---------------- Inicialización dron ----------------
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

# Labels y botones
connected_label = Label(root, text="Not Connected", font=("Arial", 14))
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

PID_values = ["P", "I", "D", "PD", "PI", "PID", "None"]
Label(root, text="Controller used =", font=("Arial", 14)).place(x=1200, y=100)

# PID dropdown
opt = tk.StringVar(value="None")
dropdown_x = OptionMenu(root, opt, *PID_values)
dropdown_x.place(x=1350, y=100)


Mode_cam = ["Espejo", "Camara Dron"]
opt_cam = tk.StringVar(value="Camara Dron")
dropdown_mode = OptionMenu(root, opt_cam, *Mode_cam)
dropdown_mode.place(x=1675, y=100)
Label(root, text="Mode used =", font=("Arial", 14)).place(x=1550, y=100)

# Sliders PID-X
Kp_x = tk.DoubleVar(value=0.42)
Ki_x = tk.DoubleVar(value=0.0005)
Kd_x = tk.DoubleVar(value=2.5)

Kp_y = tk.DoubleVar(value=0.42)
Ki_y = tk.DoubleVar(value=0.0005)
Kd_y = tk.DoubleVar(value=2.5)

kp_label_x = tk.Label(root, text="Kp-X (Proportional)")
kp_label_x.place(x=800, y=200)
kp_slider_x = tk.Scale(root, from_=0, to=2.0, resolution=0.01, orient="horizontal", variable=Kp_x, length=300)
kp_slider_x.place(x=800, y=225)

ki_label_x = tk.Label(root, text="Ki-X (Integral)")
ki_label_x.place(x=1100, y=200)
ki_slider_x = tk.Scale(root, from_=0, to=0.01, resolution=0.0001, orient="horizontal", variable=Ki_x, length=300)
ki_slider_x.place(x=1100, y=225)

kd_label_x = tk.Label(root, text="Kd-X (Derivative)")
kd_label_x.place(x=1400, y=200)
kd_slider_x = tk.Scale(root, from_=0, to=5, resolution=0.1, orient="horizontal", variable=Kd_x, length=300)
kd_slider_x.place(x=1400, y=225)

# Sliders PID-Y
kp_label_y = tk.Label(root, text="Kp-Y (Proportional)")
kp_label_y.place(x=800, y=300)
kp_slider_y = tk.Scale(root, from_=0, to=2.0, resolution=0.01, orient="horizontal", variable=Kp_y, length=300)
kp_slider_y.place(x=800, y=325)

ki_label_y = tk.Label(root, text="Ki-Y (Integral)")
ki_label_y.place(x=1100, y=300)
ki_slider_y = tk.Scale(root, from_=0, to=0.01, resolution=0.0001, orient="horizontal", variable=Ki_y, length=300)
ki_slider_y.place(x=1100, y=325)

kd_label_y = tk.Label(root, text="Kd-Y (Derivative)")
kd_label_y.place(x=1400, y=300)
kd_slider_y = tk.Scale(root, from_=0, to=5, resolution=0.1, orient="horizontal", variable=Kd_y, length=300)
kd_slider_y.place(x=1400, y=325)

# Velocidad máxima
Label(root, text="Max velocity:", font=("Arial", 12)).place(x=400, y=300)
max_velocity = tk.DoubleVar(value=60)
velocity_slider = tk.Scale(root, from_=0, to=60, resolution=1, orient="horizontal", variable=max_velocity, length=300)
velocity_slider.place(x=400, y=325)

# Panel de video
video_frame = tk.Frame(root)
video_frame.place(relx=0.5, rely=1.0, anchor="s", relwidth=1.0, height=400)

video_titles = ["Original", "HSV Mask", "Edges", "Dilated", "Contour"]
video_labels = []

panel_width, panel_height = 320, 240
for i, title in enumerate(video_titles):
    Label(video_frame, text=title, font=("Arial", 12)).grid(row=0, column=i, padx=15, pady=(5,2))
    lbl = Label(video_frame, width=panel_width, height=panel_height)
    lbl.grid(row=1, column=i, padx=15, pady=10)
    video_labels.append(lbl)
    video_frame.columnconfigure(i, weight=1, uniform="cols")

# Sliders HSV y Canny
h_min, h_max = tk.IntVar(value=60), tk.IntVar(value=82)
s_min, s_max = tk.IntVar(value=100), tk.IntVar(value=255)
v_min, v_max = tk.IntVar(value=50), tk.IntVar(value=255)

slider_defs = [
    ("Hue Min", h_min, 0, 179, 70),
    ("Hue Max", h_max, 0, 179, 100),
    ("Sat Min", s_min, 0, 255, 130),
    ("Sat Max", s_max, 0, 255, 160),
    ("Value Min", v_min, 0, 255, 190),
    ("Value Max", v_max, 0, 255, 220),
]

for text, var, mn, mx, y in slider_defs:
    Scale(root, from_=mn, to=mx, orient="horizontal", variable=var, length=200).place(x=100, y=y)
    Label(root, text=text+":", font=("Arial", 12)).place(x=10, y=y)

t1, t2 = tk.IntVar(value=166), tk.IntVar(value=171)
Scale(root, from_=0, to=255, orient="horizontal", variable=t1, length=200).place(x=100, y=370)
Scale(root, from_=0, to=255, orient="horizontal", variable=t2, length=200).place(x=100, y=420)
Label(root, text="Threshold1", font=("Arial", 12)).place(x=10, y=370)
Label(root, text="Threshold2", font=("Arial", 12)).place(x=10, y=420)

# ---------------- Labels de velocidad ----------------
lr_label = Label(root, text="Left-Right Velocity = 0", font=("Arial", 14))
lr_label.place(x=400, y=100)
fb_label = Label(root, text="For-Back Velocity = 0", font=("Arial", 14))
fb_label.place(x=400, y=150)
ud_label = Label(root, text="Up-Down Velocity = 0", font=("Arial", 14))
ud_label.place(x=400, y=200)
yaw_label = Label(root, text="Yaw Velocity = 0", font=("Arial", 14))
yaw_label.place(x=400, y=250)

# ---------------- Función de actualización ----------------
def update_frame():
    global prev_error_x, prev_error_y, integral_x, integral_y

    if is_connected:
        battery_label.config(text=f"Battery: {me.get_battery()}%", fg="blue")
        frame_read = me.get_frame_read()
        myFrame = frame_read.frame
        img = cv2.resize(myFrame, (panel_width, panel_height))
        imgContour = img.copy()
        imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Máscara HSV
        lower = np.array([h_min.get(), s_min.get(), v_min.get()])
        upper = np.array([h_max.get(), s_max.get(), v_max.get()])
        mask = cv2.inRange(imgHsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)

        # Procesado Canny
        imgBlur = cv2.GaussianBlur(result, (7, 7), 1)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
        imgCanny = cv2.Canny(imgGray, t1.get(), t2.get())
        kernel = np.ones((5,5), np.uint8)
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

        # Contorno principal
        object_center = None
        area_rectangle = 0
        contours, _ = cv2.findContours(imgDil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(imgContour, (x, y), (x+w, y+h), (0,255,0), 2)
            object_center = (x + w//2, y + h//2)
            area_rectangle = w*h
            cv2.circle(imgContour, object_center, 5, (0,0,255), cv2.FILLED)

        # PID
        if object_center:
            cx, cy = object_center
            error_x = 0
            error_y = 0
            frame_area = img.shape[0] * img.shape[1]
            AR = area_rectangle / frame_area
            #print(AR)
            if opt_cam.get() == "Espejo":
                error_x = cx - (panel_width / 2)
                error_y = cy - (panel_height / 2)

            elif opt_cam.get() == "Camara Dron":
                error_x = cx - (panel_width / 2)
                error_y = (panel_height / 2) - cy

            if start_error:
                errorXlist.append(error_x)
                errorYlist.append(error_y)

            integral_x += error_x
            derivative_x = error_x - prev_error_x

            integral_y += error_y
            derivative_y = error_y - prev_error_y

            if opt.get() == "P":
                speed_x = int(Kp_x.get()*error_x)
                speed_y = int(Kp_y.get()*error_y)
            elif opt.get() == "I":
                speed_x = int(Ki_x.get()*integral_x)
                speed_y = int(Ki_y.get()*integral_y)
            elif opt.get() == "D":
                speed_x = int(Kd_x.get()*derivative_x)
                speed_y = int(Kd_y.get()*derivative_y)
            elif opt.get() == "PID":
                speed_x = int(Kp_x.get()*error_x + Ki_x.get()*integral_x + Kd_x.get()*derivative_x)
                speed_y = int(Kp_y.get()*error_y + Ki_y.get()*integral_y + Kd_y.get()*derivative_y)
            elif opt.get() == "PD":
                speed_x = int(Kp_x.get() * error_x + Kd_x.get() * derivative_x)
                speed_y = int(Kp_y.get() * error_y + Kd_y.get() * derivative_y)
            elif opt.get() == "PI":
                speed_x = int(Kp_x.get() * error_x + Ki_x.get() * integral_x)
                speed_y = int(Kp_y.get() * error_y + Ki_y.get() * integral_y)
            else:
                speed_x = error_x
                speed_y = error_y

            if opt_cam.get() == "Espejo":
                me.left_right_velocity = int(np.clip(speed_x, -max_velocity.get(), max_velocity.get()))
                me.for_back_velocity = int(np.clip(speed_y, -max_velocity.get(), max_velocity.get()))

            if opt_cam.get() == "Camara Dron":
                me.yaw_velocity = int(np.clip(speed_x, -max_velocity.get(), max_velocity.get()))
                me.up_down_velocity = int(np.clip(speed_y, -max_velocity.get(), max_velocity.get()))

            prev_error_x, prev_error_y = error_x, error_y

            me.send_rc_control(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)

        else:
            me.left_right_velocity = 0
            me.for_back_velocity = 0
            me.up_down_velocity = 0
            me.yaw_velocity = 0
            me.send_rc_control(0, 0, 0, 0)


        # Actualizar labels
        lr_label.config(text=f"Left-Right Velocity = {me.left_right_velocity}")
        fb_label.config(text=f"For-Back Velocity = {me.for_back_velocity}")
        ud_label.config(text=f"Up-Down Velocity = {me.up_down_velocity}")
        yaw_label.config(text=f"Yaw Velocity = {me.yaw_velocity}")

        # Actualizar video
        frames_to_show = [img, result, imgCanny, imgDil, imgContour]
        for lbl, f in zip(video_labels, frames_to_show):
            if len(f.shape) == 2:
                f = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
            else:
                f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(Image.fromarray(f))
            lbl.imgtk = imgtk
            lbl.config(image=imgtk)

    # Ejecutar cada 30ms
    root.after(30, update_frame)

# ---------------- Iniciar loop ----------------
update_frame()
root.mainloop()
