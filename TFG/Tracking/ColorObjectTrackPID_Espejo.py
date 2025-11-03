import cv2
import numpy as np
from djitellopy import Tello
import time
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

# --- Variables para medir Tu ---
last_time = time.time()
last_error_sign = None
periods = []
def empty(a):
    pass

# TRACKBARS para HSV y Canny
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV", 640, 240)
cv2.createTrackbar("HUE Min", "HSV", 60, 179, empty)
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
    #Scale=factor de escala, si tenemos un imagen de 240x320 y scale=0.9 pues reduce la imagen a 216x288
    rows = len(imgArray)
    cols = len(imgArray[0])
    #Comprueba si imgArray[0] es una lista; si sí se asume que imgArray es una matriz 2D (filas de listas).
    #Si rowsAvailable == True → tratamos imgArray como 2D (apilado en filas y columnas).
    #Si False → tratamos imgArray como 1D (una sola fila de imágenes).
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    #Si imgArray es una matriz de filas y columnas las redimensionamos apilando filas y columnas
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]: #Si la imagen tiene la misma resolución pues redimensiona directamente usando el scale
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else: #Si no tiene la misma resolución, la redimensiona para que coincida con la resolución de la primera imagen y además aplica scale
                    imgArray[x][y] = cv2.resize(imgArray[x][y],(imgArray[0][0].shape[1], imgArray[0][0].shape[0]),None,scale,scale)
                #Si la imagen es grises (2 dimensiones: alto×ancho), se convierte a BGR (3 canales). Esto evita errores al apilar imágenes que mezclen grises y color.
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)

        #Creamos una imagen en negro del tamaño base sin escalar, para hacer hor (fila vacia del tamaño de imgArray)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con=[imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x]) #Apilamos filas de imagenes
        ver = np.vstack(hor) #Apilamos la columna que nos queda
    # Si imgArray es solo una  fila de imagenes hacemos lo mismo pero apilamos todas las imagenes de una misma fila
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

# Detecta contornos y devuelve el centroide del objeto
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
            object_center = (cx, cy) #En vez de calcular un direction, devolvemos el centro del objeto detectado.
            # Dibuja el rectángulo y centro
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.circle(imgContour, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
            cv2.line(imgContour, (int(frameWidth / 2), int(frameHeight / 2)), (cx, cy), (0, 0, 255), 3)
            break  # Usamos solo el contorno más grande



simulation = True  # Cambiar a False para vuelo real
startCounter = 1  # Cambiar a 0 para que haga el takeoff
last_time = None
while True:


    frame_read = me.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))
    imgContour = img.copy()
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # --- Medimos frecuencia de muestreo ---
    now = time.time()
    if last_time is not None:  # Evita la primera iteración
        dt = now - last_time
        if dt > 0:
            print(f"dt = {dt:.4f} s, frecuencia ≈ {1 / dt:.2f} Hz")
    last_time = now

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
        c = max(contours, key=cv2.contourArea)  # contorno más grande
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 2)
        object_center = (x + w // 2, y + h // 2)
        cv2.circle(imgContour, object_center, 5, (0, 0, 255), cv2.FILLED)


    # --- control con PID ---
    speed_yaw, speed_ud = 0, 0
    if object_center is not None:
        cx, cy = object_center

        cv2.line(imgContour, (int(frameWidth / 2), int(frameHeight / 2)), (cx, cy), (0, 0, 255), 3)
        #error_x = (frameWidth / 2) - cx
        error_x = cx - (frameWidth / 2)
        error_y = (frameHeight / 2) - cy

        #Kp = 0.7  # Ganancia proporcional #Kp: cuánto corrige según el error actual.
        #Ki = 0.0005  # Ganancia integral #Ki: cuánto acumula errores pasados.
        #Kd = 0.2  # Ganancia derivativa #Kd: cuánto anticipa el cambio (suaviza).
        #Ziegler Nichols Metodo con Tu=0.75 y kp=0.7
        Kp = 0.42
        Ki = 0.0005
        Kd = 0.2

        # Variables estáticas
        integral_x += error_x
        derivative_x = error_x - prev_error_x

        integral_y += error_y
        derivative_y = error_y - prev_error_y

        # --- elegir modo ---
        valor = 6  # 1=P, 2=I, 3=D, otro=PID completo

        if valor == 0:  # Modo Ziegler–Nichols (solo Kp bajo, medir Tu)
            speed_yaw = int(Kp * error_x)
            speed_ud = 0  # no tocamos altura

            # Medir periodo Tu
            current_time = time.time()
            error_sign = np.sign(error_x)

            if last_error_sign is not None and error_sign != last_error_sign and error_sign != 0:
                Tu = current_time - last_time
                periods.append(Tu)
                print(f"Oscilación detectada, periodo = {Tu:.2f} s")
                last_time = current_time

            last_error_sign = error_sign
        elif valor == 1:   # P
            speed_yaw = int(Kp * error_x)
            speed_ud  = int(Kp * error_y)
        elif valor == 2: # I
            speed_yaw = int(Ki * integral_x)
            speed_ud = int(Ki * integral_y)
        elif valor == 3: # D
            speed_yaw = int(Kd * derivative_x)
            speed_ud = int(Kd * derivative_y)
        elif valor == 4: #PI
            speed_yaw = int(Kp * error_x + Ki * integral_x)
            speed_ud = int(Kp * error_y + Ki * integral_y)
        elif valor == 5: #PD
            speed_yaw = int(Kp * error_x + Kd * derivative_x)
            speed_ud = int(Kp * error_y + Kd * derivative_y)
        else:            # PID completo
            speed_yaw = int(Kp * error_x + Ki * integral_x + Kd * derivative_x)
            speed_ud = int(Kp * error_y + Ki * integral_y + Kd * derivative_y)

        # Actualizamos errores previos
        prev_error_x = error_x
        prev_error_y = error_y

    # --- mandar al dron (simulación o real) ---
    me.left_right_velocity = 0
    me.for_back_velocity = 0
    #speed_yaw = int(np.clip(speed_yaw, -60, 60))
    #speed_ud = int(np.clip(speed_ud, -60, 60))
    me.up_down_velocity = speed_ud
    me.yaw_velocity = speed_yaw
    # --- despegue ---
    if not simulation and startCounter == 0:
        me.takeoff()
        me.send_rc_control(0, 0, 0, 0)
        startCounter = 1

    if not simulation:
        me.send_rc_control(me.left_right_velocity,
                           me.for_back_velocity,
                           me.up_down_velocity,
                           me.yaw_velocity)
    else:
        print(f"Simulación → yaw: {speed_yaw}, up/down: {speed_ud}")

    # --- mostrar todas las imágenes en una sola ventana ---
    stack = stackImages(0.9, ([img, result, mask_bgr],
                              [imgDil, imgContour, img]))
    cv2.imshow('Seguimiento con PID', stack)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if not simulation:
            me.land()
        break

cv2.destroyAllWindows()