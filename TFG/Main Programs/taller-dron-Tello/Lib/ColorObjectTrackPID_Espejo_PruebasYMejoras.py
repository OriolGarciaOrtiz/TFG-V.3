import cv2
import numpy as np
from djitellopy import Tello

##############################################
width = 640   # WIDTH OF THE IMAGE
height = 480  # HEIGHT OF THE IMAGE
##############################################

# CONNECT TO TELLO
me = Tello()
me.connect()
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0
me.speed = 0

print(me.get_battery())

me.streamoff()
me.streamon()

frameWidth = width
frameHeight = height

global imgContour

prev_error_x = 0
prev_error_y = 0
integral_x = 0
integral_y = 0

def empty(a):
    pass

# TRACKBARS para HSV y Canny
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV", 640, 240)
cv2.createTrackbar("HUE Min", "HSV", 32, 179, empty)
cv2.createTrackbar("HUE Max", "HSV", 43, 179, empty)
cv2.createTrackbar("SAT Min", "HSV", 57, 255, empty)
cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
cv2.createTrackbar("VALUE Min", "HSV", 84, 255, empty)
cv2.createTrackbar("VALUE Max", "HSV", 255, 255, empty)

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 640, 240)
cv2.createTrackbar("Threshold1", "Parameters", 67, 255, empty)
cv2.createTrackbar("Threshold2", "Parameters", 168, 255, empty)
cv2.createTrackbar("Area", "Parameters", 1750, 30000, empty)

# TRACKBARS para PID (rango real)
cv2.namedWindow("PID")
cv2.resizeWindow("PID", 640, 240)
cv2.createTrackbar("Kp X", "PID", 0, 100, empty)   # 0.00 - 1.00 (dividiremos entre 100 al leer)
cv2.createTrackbar("Ki X", "PID", 0, 1, empty)     # 0 - 0.001 (dividiremos entre 1000 al leer)
cv2.createTrackbar("Kd X", "PID",0, 200, empty)   # 0.00 - 2.00 (dividiremos entre 100 al leer)
cv2.createTrackbar("Kp Y", "PID", 0, 100, empty)
cv2.createTrackbar("Ki Y", "PID", 0, 1, empty)
cv2.createTrackbar("Kd Y", "PID", 0, 200, empty)


def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)

        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)

        hor = np.hstack(imgArray)
        ver = hor

    return ver


simulation = False  # Cambiar a False para vuelo real
startCounter = 0   # Cambiar a 0 para que haga el takeoff

while True:
    frame_read = me.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))
    imgContour = img.copy()
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # --- máscara y procesado ---
    h_min = cv2.getTrackbarPos("HUE Min", "HSV")
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHsv, lower, upper)
    result = cv2.bitwise_and(img, img, mask=mask)
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    imgBlur = cv2.GaussianBlur(result, (7, 7), 1)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
    kernel = np.ones((5, 5))
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

    # --- detección de contorno principal ---
    object_center = None
    contours, _ = cv2.findContours(imgDil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 2)
        object_center = (x + w // 2, y + h // 2)
        cv2.circle(imgContour, object_center, 5, (0, 0, 255), cv2.FILLED)

    # --- control con PID ---
    speed_lr, speed_fb = 0, 0
    if object_center is not None:
        cx, cy = object_center
        error_x = cx - (frameWidth / 2)
        error_y = cy - (frameHeight / 2)

        # Leemos parámetros PID desde sliders
        Kp_x = cv2.getTrackbarPos("Kp X", "PID") / 100   # 0-1
        Ki_x = cv2.getTrackbarPos("Ki X", "PID") / 10000  # 0-0.001
        Kd_x = cv2.getTrackbarPos("Kd X", "PID") / 100   # 0-2

        Kp_y = cv2.getTrackbarPos("Kp Y", "PID") / 100
        Ki_y = cv2.getTrackbarPos("Ki Y", "PID") / 10000
        Kd_y = cv2.getTrackbarPos("Kd Y", "PID") / 100

        cv2.line(imgContour, (int(frameWidth / 2), int(frameHeight / 2)), (cx, cy), (0, 0, 255), 3)

        integral_x += error_x
        derivative_x = error_x - prev_error_x

        integral_y += error_y
        derivative_y = error_y - prev_error_y

        speed_lr = int(Kp_x * error_x + Ki_x * integral_x + Kd_x * derivative_x)
        speed_fb = int(Kp_y * error_y + Ki_y * integral_y + Kd_y * derivative_y)

        prev_error_x = error_x
        prev_error_y = error_y

    # --- mandar al dron (simulación o real) ---
    me.up_down_velocity = 0
    me.yaw_velocity = 0
    me.left_right_velocity = speed_lr
    me.for_back_velocity = speed_fb

    if not simulation and startCounter == 0:
        me.takeoff()
        me.move_up(120)
        me.send_rc_control(0, 0, 0, 0)
        startCounter = 1

    if not simulation:
        me.send_rc_control(me.left_right_velocity,
                           me.for_back_velocity,
                           me.up_down_velocity,
                           me.yaw_velocity)
    else:
        print(f"Simulación → left/right: {speed_lr}, forward/back: {speed_fb}")

    stack = stackImages(0.8, ([img, result, mask_bgr],
                              [imgDil, imgContour, img]))
    cv2.imshow('Seguimiento con PID', stack)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if not simulation:
            me.land()
        break

cv2.destroyAllWindows()
