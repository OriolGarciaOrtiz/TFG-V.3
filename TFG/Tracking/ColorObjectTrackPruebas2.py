import cv2
import numpy as np
from djitellopy import Tello
#import time
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
#cap = cv2.VideoCapture(1)
#cap.set(3, frameWidth)
#cap.set(4, frameHeight)

deadZone = 100
global imgContour
global direction
def empty(a):
    pass

cv2.namedWindow("HSV")#Se abre una ventana llamada HSV con los diferentes Trackbars de colores para que los puedas ir modifcando, más adelante en el codigo se usan para definir la máscara HSV del objeto que queremos detectar
cv2.resizeWindow("HSV", 640, 240)
#En OpenCV, cuando conviertes una imagen a HSV (cv2.cvtColor(img, cv2.COLOR_BGR2HSV)), cada pixel ya no se representa en RGB (rojo, verde, azul) sino con 3 componentes:
#1.HUE(tono,matiz) sería el color en sí, esto va de 0 a 179 el amarillo está entre 20-40 que sería lo que pondríamos de mínimos y de maximo
cv2.createTrackbar("HUE Min", "HSV", 60, 179, empty)
cv2.createTrackbar("HUE Max", "HSV", 82, 179, empty)
#2.SAT: es la saturación,intensidad del color , un 0 sería un color muy gris y un 255 un color muy puro, con esto filtramos colores de saturación baja
cv2.createTrackbar("SAT Min", "HSV", 100, 255, empty)
cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
#3.VALUE: esto sería básciamente el brillo, intentamos quitar zonas sin luz, se tiene que ver bien el objeto
cv2.createTrackbar("VALUE Min", "HSV", 50, 255, empty)
cv2.createTrackbar("VALUE Max", "HSV", 255, 255, empty)
#"Threshold1" y "Threshold2" → son los valores inferior y superior que se usan en el filtro Canny para detectar bordes. Con los sliders puedes ajustar qué tan sensibles son a los cambios de intensidad.
#"Area" → establece el área mínima del contorno que quieres considerar. Si un objeto detectado tiene un área menor que ese valor, se descarta (para evitar ruido).
cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 640, 240)
cv2.createTrackbar("Threshold1", "Parameters", 166, 255, empty)
cv2.createTrackbar("Threshold2", "Parameters", 171, 255, empty)
cv2.createTrackbar("Area", "Parameters", 1750, 30000, empty)

#Stack images oma una colección de imágenes (puede ser una fila de imágenes o una matriz 2×N / M×N) y devuelve una única imagen con todas ellas apiladas (horizontalmente por fila y luego verticalmente entre filas).
#Además ajusta automáticamente el tamaño de las imágenes (aplica scale o las redimensiona para que todas tengan la misma forma), y convierte imágenes en gris a BGR para evitar errores al apilarlas con imágenes color.
#Se usa para mostrar varias etapas del procesamiento (por ejemplo: imagen original, máscara, Canny, contornos) en una sola ventana de debugging.
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

#getContours(img, imgContour) es la función que toma la imagen binaria (normalmente el resultado de Canny + dilate o una máscara) y:
#busca todos los contornos (cv2.findContours),
#filtra por área mínima (evita ruido),
#calcula propiedades del contorno (perímetro, aproximación poligonal, bounding box, centro),
#dibuja información en imgContour (contorno, rectángulo, textos, línea hacia el centro),
#decide en qué “zona” de la pantalla está el objeto (izquierda/derecha/arriba/abajo) comparando el centro del objeto con el centro del frame ± deadZone, y pinta un aviso visual (“GO LEFT”, etc.).
#Esa decisión visual es la que debería asignar una variable de control (dir) para después traducirla a velocidades del dron.
def getContours(img, imgContour):
    global direction
    direction = 5  # Centro por defecto
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        if area > areaMin:  # Solo procesar contornos grandes
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            #print(len(approx))  # Número de vértices
            x, y, w, h = cv2.boundingRect(approx)

            # Dibujar rectángulo verde y textos de depuración
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(imgContour, "Points: " + str(len(approx)),
                        (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX,
                        0.7, (0, 255, 0), 2)
            cv2.putText(imgContour, "Area: " + str(int(area)),
                        (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX,
                        0.7, (0, 255, 0), 2)
            cv2.putText(imgContour, str(int(x)) + " " + str(int(y)),
                        (x - 20, y - 45), cv2.FONT_HERSHEY_COMPLEX,
                        0.7, (0, 255, 0), 2)

            # Centro del objeto
            cx = int(x + w / 2)
            cy = int(y + h / 2)
            cv2.line(imgContour, (int(frameWidth / 2), int(frameHeight / 2)), (cx, cy), (0, 0, 255), 3)

            # Determinar zona 9 cuadrantes y dibujar visual
            if cx < int(frameWidth / 2) - deadZone:  # Izquierda
                if cy < int(frameHeight / 2) - deadZone:  # Arriba-Izquierda
                    direction = 1
                    cv2.putText(imgContour, "GO UP-LEFT", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (0, 0), (int(frameWidth / 2) - deadZone, int(frameHeight / 2) - deadZone),
                                  (0, 0, 255), cv2.FILLED)
                elif cy > int(frameHeight / 2) + deadZone:  # Abajo-Izquierda
                    direction = 7
                    cv2.putText(imgContour, "GO DOWN-LEFT", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (0, int(frameHeight / 2) + deadZone),
                                  (int(frameWidth / 2) - deadZone, frameHeight), (0, 0, 255), cv2.FILLED)
                else:  # Centro-Izquierda
                    direction = 4
                    cv2.putText(imgContour, "GO LEFT", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (0, int(frameHeight / 2) - deadZone),
                                  (int(frameWidth / 2) - deadZone, int(frameHeight / 2) + deadZone), (0, 0, 255),
                                  cv2.FILLED)

            elif cx > int(frameWidth / 2) + deadZone:  # Derecha
                if cy < int(frameHeight / 2) - deadZone:  # Arriba-Derecha
                    direction = 3
                    cv2.putText(imgContour, "GO UP-RIGHT", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (int(frameWidth / 2) + deadZone, 0),
                                  (frameWidth, int(frameHeight / 2) - deadZone), (0, 0, 255), cv2.FILLED)
                elif cy > int(frameHeight / 2) + deadZone:  # Abajo-Derecha
                    direction = 9
                    cv2.putText(imgContour, "GO DOWN-RIGHT", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (int(frameWidth / 2) + deadZone, int(frameHeight / 2) + deadZone),
                                  (frameWidth, frameHeight), (0, 0, 255), cv2.FILLED)
                else:  # Centro-Derecha
                    direction = 6
                    cv2.putText(imgContour, "GO RIGHT", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (int(frameWidth / 2) + deadZone, int(frameHeight / 2) - deadZone),
                                  (frameWidth, int(frameHeight / 2) + deadZone), (0, 0, 255), cv2.FILLED)

            else:  # Centro X
                if cy < int(frameHeight / 2) - deadZone:  # Arriba
                    direction = 2
                    cv2.putText(imgContour, "GO UP", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (int(frameWidth / 2) - deadZone, 0),
                                  (int(frameWidth / 2) + deadZone, int(frameHeight / 2) - deadZone), (0, 0, 255),
                                  cv2.FILLED)
                elif cy > int(frameHeight / 2) + deadZone:  # Abajo
                    direction = 8
                    cv2.putText(imgContour, "GO DOWN", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                    cv2.rectangle(imgContour, (int(frameWidth / 2) - deadZone, int(frameHeight / 2) + deadZone),
                                  (int(frameWidth / 2) + deadZone, frameHeight), (0, 0, 255), cv2.FILLED)
                else:  # Centro
                    direction = 5
                    cv2.putText(imgContour, "CENTER", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)


#La función display(img) sirve para dibujar en la pantalla una “guía visual” que divide la imagen en zonas de control,
# de manera que sepas si el objeto está dentro o fuera de la zona central (dead zone).
def display(img):
    #Lineas verticales
    cv2.line(img, (int(frameWidth/2) - deadZone, 0),
                  (int(frameWidth/2) - deadZone, frameHeight), (255, 255, 0), 3)
    cv2.line(img, (int(frameWidth/2) + deadZone, 0),
                  (int(frameWidth/2) + deadZone, frameHeight), (255, 255, 0), 3)
    #Cirulo rojo en el centro del frame
    cv2.circle(img, (int(frameWidth/2), int(frameHeight/2)), 5, (0, 0, 255), 5)
    #Lineas horizontales (verticales+horizontales conseguimos el tablero de cuadrados)
    cv2.line(img, (0, int(frameHeight/2) - deadZone),
                  (frameWidth, int(frameHeight/2) - deadZone), (255, 255, 0), 3)
    cv2.line(img, (0, int(frameHeight/2) + deadZone),
                  (frameWidth, int(frameHeight/2) + deadZone), (255, 255, 0), 3)


simulation = True  # Cambiar a False para vuelo real
startCounter = 1  # Cambiar a 0 para que haga el takeoff
while True:
    direction = 5
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
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    imgBlur = cv2.GaussianBlur(result, (7, 7), 1)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
    kernel = np.ones((5, 5))
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

    getContours(imgDil, imgContour)
    display(imgContour)

    # --- despegue ---
    if not simulation and startCounter == 0:
        me.takeoff()
        me.send_rc_control(0, 0, 0, 0)
        startCounter = 1

    # --- asignar velocidades ---
    speed_lr = 0
    speed_fb = 0
    speed_ud = 0
    speed_yaw = 0
    velocity = 60

    if direction == 1:
        speed_lr = 0
        speed_fb = 0
        speed_yaw = -velocity
        speed_ud = velocity
    elif direction == 2:
        speed_lr = 0
        speed_fb = 0
        speed_yaw = 0
        speed_ud = velocity
    elif direction == 3:
        speed_lr = 0
        speed_fb = 0
        speed_yaw = velocity
        speed_ud = velocity
    elif direction == 4:
        speed_lr = 0
        speed_fb = 0
        speed_ud = 0
        speed_yaw = -velocity
    elif direction == 5:
        speed_lr = 0
        speed_fb = 0
        speed_ud = 0
        speed_yaw = 0
    elif direction == 6:
        speed_lr = 0
        speed_fb = 0
        speed_ud = 0
        speed_yaw = velocity
    elif direction == 7:
        speed_lr = 0
        speed_fb = 0
        speed_yaw = -velocity
        speed_ud = -velocity
    elif direction == 8:
        speed_lr = 0
        speed_fb = 0
        speed_yaw = 0
        speed_ud = -velocity
    elif direction == 9:
        speed_lr = 0
        speed_fb = 0
        speed_yaw = velocity
        speed_ud = -velocity

    me.left_right_velocity = speed_lr
    me.for_back_velocity = speed_fb
    me.up_down_velocity = speed_ud
    me.yaw_velocity = speed_yaw

    # --- enviar comandos solo en vuelo real --- #No obstante esto no es un PID, la velocidad es constante.
    # Con un PID, la velocidad ya no es fija, sino proporcional a cuánto se ha desviado el objeto de donde debería estar. Eso da un movimiento mucho más suave y ajustado.

    if not simulation:
        me.send_rc_control(me.left_right_velocity,
                           me.for_back_velocity,
                           me.up_down_velocity,
                           me.yaw_velocity)
        print("Dirección:", direction)
    else:
        print("Dirección:", direction)

    stack = stackImages(0.9, ([img, result], [imgDil, imgContour]))
    cv2.imshow('Horizontal Stacking', stack)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if not simulation:
            me.land()
        break

cv2.destroyAllWindows()



