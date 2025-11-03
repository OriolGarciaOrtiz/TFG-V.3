import cv2
import numpy as np
from djitellopy import Tello
import tkinter as tk
from tkinter import Label, Scale, OptionMenu
from PIL import Image, ImageTk
import threading

# ---------------- Globals ----------------
is_connected = False
prev_error_x = 0
prev_error_y = 0
prev_error_z = 0
integral_x = 0
integral_y = 0
integral_z = 0


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
Label(root, text="Max velocity:", font=("Arial", 12)).place(x=400, y=300)
max_velocity = tk.DoubleVar(value=60)
velocity_slider = tk.Scale(root, from_=0, to=60, resolution=1, orient="horizontal", variable=max_velocity, length=300)
velocity_slider.place(x=400, y=325)

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
lr_label.place(x=400, y=100)
fb_label = Label(root, text="For-Back Velocity = 0", font=("Arial", 14))
fb_label.place(x=400, y=150)
ud_label = Label(root, text="Up-Down Velocity = 0", font=("Arial", 14))
ud_label.place(x=400, y=200)
yaw_label = Label(root, text="Yaw Velocity = 0", font=("Arial", 14))
yaw_label.place(x=400, y=250)

# ---------------- Distance computation ----------------
Label(root, text="Object size (cm):  H =", font=("Arial", 14)).place(x=400, y=15)
Label(root, text="W =", font=("Arial", 14)).place(x=675, y=15)
Label(root, text="Object distance (cm):", font=("Arial", 14)).place(x=400, y=55)
dist_label = tk.Label(root, text="Distance to Object:", font=("Arial", 14))
dist_label.place(x=800, y=20)
entry_width = tk.Entry(root, width=10)
entry_width.place(x=600, y=20)
entry_height = tk.Entry(root, width=10)
entry_height.place(x=720, y=20)
entry_dist = tk.Entry(root, width=10)
entry_dist.place(x=600, y=60)


# ---------------- Frame updating ----------------
def update_frame():
    global prev_error_x, prev_error_y, prev_error_z, integral_x, integral_y, integral_z

    if is_connected:
        battery_label.config(text=f"Battery: {me.get_battery()}%", fg="blue")
        frame_read = me.get_frame_read()
        my_frame = frame_read.frame
        img = cv2.resize(my_frame, (panel_width, panel_height))
        img_contour = img.copy()
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # HSV Mask
        lower = np.array([h_min.get(), s_min.get(), v_min.get()])
        upper = np.array([h_max.get(), s_max.get(), v_max.get()])
        mask = cv2.inRange(img_hsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)

        # Canny process
        img_blur = cv2.GaussianBlur(result, (7, 7), 1)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_gray, t1.get(), t2.get())
        kernel = np.ones((5, 5), np.uint8)
        img_dil = cv2.dilate(img_canny, kernel, iterations=1)

        # Main contour
        object_center = None
        dist_to_camera_width = None
        dist_to_camera_height = None
        obj_height = entry_height.get()
        obj_width = entry_width.get()
        contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(img_contour, (x, y), (x+w, y+h), (0, 255, 0), 2)
            object_center = (x + w//2, y + h//2)
            ratio_width = 5.2/5.5
            ratio_height = 1.2
            focal_length_width = img.shape[0]/ratio_width
            focal_length_height = img.shape[1] / ratio_height
            if obj_height is not None and obj_width is not None:
                try:
                    dist_to_camera_width = float(obj_width) * focal_length_width / w * 2 - 22
                    dist_to_camera_height = float(obj_height) * focal_length_height / h * 2 - 22
                except ValueError:
                    print(f"Invalid object height or width value: {obj_height}")
                    dist_to_camera_width = 0
                    dist_to_camera_height = 0
            else:
                dist_to_camera_width = 0
                dist_to_camera_height = 0

            cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)

        # PID
        if object_center:
            cx, cy = object_center
            error_x = 0
            error_y = 0
            error_z = 0

            mean_dist_camera = (dist_to_camera_width + dist_to_camera_height) / 2

            dist_label.config(text="Distance to Object: " + str(mean_dist_camera.__round__(0)))

            if obj_height is not None:
                try:
                    e_max = (panel_width / 2 + panel_height / 2) / 2
                    error_z = e_max/int(entry_dist.get())*mean_dist_camera - e_max
                except ValueError:
                    print(f"Invalid object distance value: {obj_height}")

            if opt_cam.get() == "Mirror":
                error_x = cx - (panel_width / 2)
                error_y = cy - (panel_height / 2)

            elif opt_cam.get() == "Drone Camera":
                error_x = cx - (panel_width / 2)
                error_y = (panel_height / 2) - cy

            integral_x += error_x
            derivative_x = error_x - prev_error_x

            integral_y += error_y
            derivative_y = error_y - prev_error_y

            integral_z += error_z
            derivative_z = error_z - prev_error_z

            if opt.get() == "P":
                speed_x = int(Kp_x.get()*error_x)
                speed_y = int(Kp_y.get()*error_y)
                speed_z = int(Kp_z.get() * error_z)
            elif opt.get() == "I":
                speed_x = int(Ki_x.get()*integral_x)
                speed_y = int(Ki_y.get()*integral_y)
                speed_z = int(Ki_z.get() * integral_z)
            elif opt.get() == "D":
                speed_x = int(Kd_x.get()*derivative_x)
                speed_y = int(Kd_y.get()*derivative_y)
                speed_z = int(Ki_z.get() * integral_z)
            elif opt.get() == "PID":
                speed_x = int(Kp_x.get()*error_x + Ki_x.get()*integral_x + Kd_x.get()*derivative_x)
                speed_y = int(Kp_y.get()*error_z + Ki_y.get()*integral_y + Kd_y.get()*derivative_y)
                speed_z = int(Kp_z.get()*error_z + Ki_z.get()*integral_z + Kd_z.get()*derivative_z)
            elif opt.get() == "PD":
                speed_x = int(Kp_x.get() * error_x + Kd_x.get() * derivative_x)
                speed_y = int(Kp_y.get() * error_y + Kd_y.get() * derivative_y)
                speed_z = int(Kp_z.get() * error_z + Kd_z.get() * derivative_z)
            elif opt.get() == "PI":
                speed_x = int(Kp_x.get() * error_x + Ki_x.get() * integral_x)
                speed_y = int(Kp_y.get() * error_y + Ki_y.get() * integral_y)
                speed_z = int(Kp_z.get() * error_z + Ki_z.get() * integral_z)
            else:
                speed_x = error_x
                speed_y = error_y
                speed_z = error_z

            me.left_right_velocity = 0
            me.for_back_velocity = 0
            me.up_down_velocity = 0
            me.yaw_velocity = 0

            if opt_cam.get() == "Mirror":
                me.left_right_velocity = int(np.clip(speed_x, -max_velocity.get(), max_velocity.get()))
                me.for_back_velocity = int(np.clip(speed_y, -max_velocity.get(), max_velocity.get()))
                me.up_down_velocity = int(np.clip(speed_z, -max_velocity.get(), max_velocity.get()))

            if opt_cam.get() == "Drone Camera":
                me.yaw_velocity = int(np.clip(speed_x, -max_velocity.get(), max_velocity.get()))
                me.up_down_velocity = int(np.clip(speed_y, -max_velocity.get(), max_velocity.get()))
                me.for_back_velocity = int(np.clip(speed_z, -max_velocity.get(), max_velocity.get()))

            prev_error_x, prev_error_y, prev_error_z = error_x, error_y, error_z

            me.send_rc_control(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)

        else:
            me.left_right_velocity = 0
            me.for_back_velocity = 0
            me.up_down_velocity = 0
            me.yaw_velocity = 0
            me.send_rc_control(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)
            dist_label.config(text="Distance to Object: ")

        # Update Labels
        lr_label.config(text=f"Left-Right Velocity = {me.left_right_velocity}")
        fb_label.config(text=f"For-Back Velocity = {me.for_back_velocity}")
        ud_label.config(text=f"Up-Down Velocity = {me.up_down_velocity}")
        yaw_label.config(text=f"Yaw Velocity = {me.yaw_velocity}")

        # Video actualization
        frames_to_show = [img, result, img_canny, img_dil, img_contour]
        for labels, f in zip(video_labels, frames_to_show):
            if len(f.shape) == 2:
                f = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)
            else:
                f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(Image.fromarray(f))
            labels.imgtk = imgtk
            labels.config(image=imgtk)

    # Execute every 30 ms
    root.after(30, update_frame)


# ---------------- Start Loop ----------------
update_frame()
root.mainloop()
