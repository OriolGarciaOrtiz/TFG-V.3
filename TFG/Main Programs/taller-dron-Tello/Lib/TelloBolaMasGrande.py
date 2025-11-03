from djitellopy import Tello
import cv2 as cv
import numpy as np
import time  # Para temporizar movimientos si es necesario

# Inicialización del dron
tello = Tello()
tello.connect()
print(f"Batería: {tello.get_battery()}%")
tello.streamon()
tello.takeoff()  # Se puede comentar para pruebas sin vuelo

# (Opcional: mostrar una imagen de ejemplo)
img = cv.imread('imagenes/bolasDiferentesMedidas.png')
img = cv.resize(img, (720, 480))
cv.imshow("img", img)

# Rango de colores en HSV
color_ranges = {
    'amarillo': ([28, 100, 100], [32, 255, 255]),
    'naranja': ([10, 100, 100], [20, 255, 255]),
    'verde': ([50, 100, 100], [80, 255, 255]),
    'azul': ([100, 100, 100], [130, 255, 255])
}

kernel = np.ones((5, 5), np.uint8)

# Control de detección para evitar repeticiones
ultimo_color_detectado = None
tiempo_ultimo_comando = time.time()

while True:
    frame = tello.get_frame_read().frame
    frame = cv.resize(frame, (640, 480))
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    mayor_contorno = None
    mayor_area = 0
    color_detectado = None

    for color, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)

        mask = cv.inRange(hsv, lower_np, upper_np)
        erosion = cv.erode(mask, kernel, iterations=2)
        erosion_dilate = cv.dilate(erosion, kernel, iterations=3)

        contours, _ = cv.findContours(erosion_dilate, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv.contourArea(cnt)
            if area > mayor_area:
                mayor_area = area
                mayor_contorno = cnt
                color_detectado = color  # Guardamos el color del mayor contorno,osea solo tendrá en cuenta el objeto más grande

    # Dibuja el contorno
    if mayor_contorno is not None:
        cv.drawContours(frame, [mayor_contorno], -1, (0, 255, 0), 3)

        # Controlar la frecuencia con la que se envían comandos
        if color_detectado != ultimo_color_detectado or (time.time() - tiempo_ultimo_comando) > 5:
            if color_detectado == 'amarillo':
                print("Color amarillo detectado: avanzando")
                tello.send_rc_control(0, 50, 0, 0)
            elif color_detectado == 'verde':
                print("Color verde detectado: aterrizando")
                tello.land()
                break  # Salimos del bucle después de aterrizar

            ultimo_color_detectado = color_detectado
            tiempo_ultimo_comando = time.time()

    cv.imshow("Detección Bola Más Grande", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break
#Se sale del bucle si se presiona la tecla q y cierra todo
cv.destroyAllWindows()
tello.streamoff()
