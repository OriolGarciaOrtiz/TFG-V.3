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

deadZone = 100
global imgContour
global object_center

def empty(a):
    pass

# TRACKBARS para HSV y Canny
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV", 640, 240)
cv2.createTrackbar("HUE Min", "HSV", 46, 179, empty)
cv2.createTrackbar("HUE Max", "HSV", 82, 179, empty)
cv2.createTrackbar("SAT Min", "HSV", 100, 255, empty)
cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
cv2.createTrackbar("VALUE Min", "HSV", 50, 255, empty)
cv2.createTrackbar("VALUE Max", "HSV", 255, 255, empty)

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 640, 240)
cv2.createTrackbar("Threshold1", "Parameters", 166, 255, empty)
cv2.createTrackbar("Threshold2", "Parameters", 171, 255, empty)
cv2.createTrackbar("Area", "Parameters", 1750, 30000, empty)


#Guardan memoria del error previo e integran errores acumulados.
prev_error_x = 0
prev_error_y = 0
integral_x = 0
integral_y = 0


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
                    imgArray[x][y] = cv2.resize(imgArray[x][y],(imgArray[0][0].shape[1], imgArray[0][0].shape[0]),None,scale,scale)
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
                imgArray[x] = cv2.resize(imgArray[x],(imgArray[0].shape[1], imgArray[0].shape[0]),None,scale,scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)

        hor = np.hstack(imgArray)
        ver = hor

    return ver


def getContours(img, imgContour):
    global object_center
    object_center = None
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        if area > areaMin:
            x, y, w, h = cv2.boundingRect(cnt)
            cx = int(x + w / 2)
            cy = int(y + h / 2)
            object_center = (cx, cy)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.circle(imgContour, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
            break


def display(img):
    cv2.line(img, (int(frameWidth/2) - deadZone, 0),
                  (int(frameWidth/2) - deadZone, frameHeight), (255, 255, 0), 3)
    cv2.line(img, (int(frameWidth/2) + deadZone, 0),
                  (int(frameWidth/2) + deadZone, frameHeight), (255, 255, 0), 3)
    cv2.circle(img, (int(frameWidth/2), int(frameHeight/2)), 5, (0, 0, 255), 5)
    cv2.line(img, (0, int(frameHeight/2) - deadZone),
                  (frameWidth, int(frameHeight/2) - deadZone), (255, 255, 0), 3)
    cv2.line(img, (0, int(frameHeight/2) + deadZone),
                  (frameWidth, int(frameHeight/2) + deadZone), (255, 255, 0), 3)


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
        Kp, Ki, Kd = 0.2, 0, 0.2
        cv2.line(imgContour, (int(frameWidth / 2), int(frameHeight / 2)), (cx, cy), (0, 0, 255), 3)
        integral_x += error_x
        derivative_x = error_x - prev_error_x

        integral_y += error_y
        derivative_y = error_y - prev_error_y

        valor = 6  # 1=P, 2=I, 3=D, otro=PID completo

        if valor == 1:
            speed_lr = int(Kp * error_x)
            speed_fb = int(Kp * error_y)
        elif valor == 2:
            speed_lr = int(Ki * integral_x)
            speed_fb = int(Ki * integral_y)
        elif valor == 3:
            speed_lr = int(Kd * derivative_x)
            speed_fb = int(Kd * derivative_y)
        elif valor == 4: #PI
            speed_lr = int(Kp * error_x + Ki * integral_x)
            speed_fb = int(Kp * error_y + Ki * integral_y)
        elif valor == 5: #PD
            speed_lr = int(Kp * error_x + Kd * derivative_x)
            speed_fb = int(Kp * error_y + Kd * derivative_y)
        else:
            speed_lr = int(Kp * error_x + Ki * integral_x + Kd * derivative_x)
            speed_fb = int(Kp * error_y + Ki * integral_y + Kd * derivative_y)

        prev_error_x = error_x
        prev_error_y = error_y

    # --- mandar al dron (simulación o real) ---
    me.up_down_velocity = 0
    me.yaw_velocity = 0
    #speed_lr = int(np.clip(speed_lr, -60, 60))
    #speed_fb = int(np.clip(speed_fb, -60, 60))
    me.left_right_velocity = speed_lr
    me.for_back_velocity  = speed_fb

    if not simulation and startCounter == 0:
        me.takeoff()
        me.move_up(140)
        me.send_rc_control(0, 0, 0, 0)
        startCounter = 1

    if not simulation:
        me.send_rc_control(me.left_right_velocity,
                           me.for_back_velocity,
                           me.up_down_velocity,
                           me.yaw_velocity)
    else:
        print(f"Simulación → left/right: {speed_lr}, forward/back: {speed_fb}")

    stack = stackImages(0.9, ([img, result, mask_bgr],
                              [imgDil, imgContour, img]))
    cv2.imshow('Seguimiento con PID', stack)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if not simulation:
            me.land()
        break

cv2.destroyAllWindows()
