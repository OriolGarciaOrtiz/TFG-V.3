import cv2 as cv
import numpy as np

img = cv.imread('imagenes/muchasPelotas.jpg')
img = cv.resize(img, (720, 480))
cv.imshow("img", img)

hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

# Rango de colores en HSV
color_ranges = {
    'amarillo': ([28, 100, 100], [32, 255, 255]), #Upper y lower values de diferentes colores para que pueda dibujar el contorno
    'naranja': ([10, 100, 100], [20, 255, 255]),
    'verde': ([50, 100, 100], [80, 255, 255]),
    'azul': ([100, 100, 100], [130, 255, 255])
}

kernel = np.ones((5, 5), np.uint8)

for color, (lower, upper) in color_ranges.items():
    lower_np = np.array(lower)
    upper_np = np.array(upper)

    mask = cv.inRange(hsv, lower_np, upper_np)
    erosion = cv.erode(mask, kernel, iterations=2)
    erosion_dilate = cv.dilate(erosion, kernel, iterations=3)

    contours, _ = cv.findContours(erosion_dilate, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) #Detecta todos los contornos según los rangos de colores que hayamos puesto


    for cnt in contours:
        cv.drawContours(img, [cnt], -1, (0, 255, 0), 3) #Dibuja los contornos de un color verdoso

cv.imshow("res", img)
cv.waitKey(0)