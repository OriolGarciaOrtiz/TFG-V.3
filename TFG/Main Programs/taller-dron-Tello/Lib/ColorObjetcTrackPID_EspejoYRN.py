import cv2
import numpy as np
from djitellopy import Tello
from ultralytics import YOLO

##############################################
width = 640   # WIDTH OF THE IMAGE
height = 480  # HEIGHT OF THE IMAGE
##############################################

# --- conexión con el dron ---
me = Tello()
me.connect()
print(me.get_battery())
me.streamoff()
me.streamon()

# --- carga del modelo YOLO entrenado ---
model = YOLO("best_RC_Final.pt")  # tu modelo entrenado

frameWidth = width
frameHeight = height

# Variables PID
prev_error_x, prev_error_y = 0, 0
integral_x, integral_y = 0, 0

# --- sliders para PID ---
def empty(a): pass

cv2.namedWindow("PID")
cv2.resizeWindow("PID", 640, 240)
cv2.createTrackbar("Kp X", "PID", 10, 100, empty)   # ejemplo: 0.3
cv2.createTrackbar("Ki X", "PID", 0, 10, empty)     # ejemplo: 0.0
cv2.createTrackbar("Kd X", "PID", 10, 200, empty)   # ejemplo: 0.1
cv2.createTrackbar("Kp Y", "PID", 10, 100, empty)
cv2.createTrackbar("Ki Y", "PID", 0, 10, empty)
cv2.createTrackbar("Kd Y", "PID", 10, 200, empty)

simulation = True  # Cambiar a False para vuelo real
startCounter = 1   # Cambiar a 0 para que haga el takeoff

while True:
    frame_read = me.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))
    imgContour = img.copy()

    # --- inferencia con YOLO ---
    results = model.predict(img, conf=0.5, verbose=False)#conf=Confianza con la que quieres que empiece a detectar el objeto

    object_center = None
    max_area = 0

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            w, h = x2 - x1, y2 - y1
            area = w * h

            if area > max_area:  # quedarnos con el objeto más grande
                max_area = area
                object_center = (x1 + w // 2, y1 + h // 2)

            # Dibujar bbox
            cv2.rectangle(imgContour, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(imgContour, f"{model.names[int(box.cls[0])]} {float(box.conf[0]):.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)

    # --- control con PID ---
    speed_lr, speed_fb = 0, 0
    if object_center is not None:
        cx, cy = object_center
        error_x = cx - (frameWidth / 2)
        error_y = cy - (frameHeight / 2)

        # Leemos parámetros PID desde sliders
        Kp_x = cv2.getTrackbarPos("Kp X", "PID") / 100   # 0-1
        Ki_x = cv2.getTrackbarPos("Ki X", "PID") / 1000  # 0-0.01
        Kd_x = cv2.getTrackbarPos("Kd X", "PID") / 100   # 0-2

        Kp_y = cv2.getTrackbarPos("Kp Y", "PID") / 100
        Ki_y = cv2.getTrackbarPos("Ki Y", "PID") / 1000
        Kd_y = cv2.getTrackbarPos("Kd Y", "PID") / 100

        integral_x += error_x
        derivative_x = error_x - prev_error_x

        integral_y += error_y
        derivative_y = error_y - prev_error_y

        speed_lr = int(Kp_x * error_x + Ki_x * integral_x + Kd_x * derivative_x)
        speed_fb = int(Kp_y * error_y + Ki_y * integral_y + Kd_y * derivative_y)

        prev_error_x = error_x
        prev_error_y = error_y

        # Dibujar línea de error
        cv2.line(imgContour, (int(frameWidth / 2), int(frameHeight / 2)), (cx, cy), (0, 0, 255), 3)
        cv2.circle(imgContour, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

    # --- mandar al dron ---
    me.up_down_velocity = 0
    me.yaw_velocity = 0
    me.left_right_velocity = speed_lr
    me.for_back_velocity = speed_fb

    if not simulation and startCounter == 0:
        me.takeoff()
        me.move_up(100)
        me.send_rc_control(0, 0, 0, 0)
        startCounter = 1

    if not simulation:
        me.send_rc_control(me.left_right_velocity,
                           me.for_back_velocity,
                           me.up_down_velocity,
                           me.yaw_velocity)
    else:
        print(f"Simulación → left/right: {speed_lr}, forward/back: {speed_fb}")

    # Mostrar cámara con bbox + centro
    cv2.imshow('Seguimiento YOLO + PID', imgContour)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if not simulation:
            me.land()
        break

cv2.destroyAllWindows()
