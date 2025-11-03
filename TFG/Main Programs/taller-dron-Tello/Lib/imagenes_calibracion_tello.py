import cv2
import numpy as np
from djitellopy import Tello
import time
import os
#Esto servirá para hacer fotos a un tablero de ajedrez para sacar los parámetros de la cámara
# Configuración de cámara
width, height = 640, 480
SAVE_PATH = r"C:\Tello\taller-dron-Tello\Lib\Img_Calibracion"
os.makedirs(SAVE_PATH, exist_ok=True)

# Conexión con el dron
tello = Tello()
tello.connect()
print(f"Batería: {tello.get_battery()}%")

tello.streamoff()
tello.streamon()
frame_read = tello.get_frame_read()

print("\nPresiona 'c' para capturar una imagen, 'q' para salir.\n")

i = 0
while True:
    img = frame_read.frame
    img = cv2.resize(img, (width, height))
    cv2.imshow("Vista Tello", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        filename = os.path.join(SAVE_PATH, f"imagen_{i:02d}.jpg")
        cv2.imwrite(filename, img)
        print(f" Imagen guardada: {filename}")
        i += 1
        time.sleep(0.5)
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
tello.streamoff()
