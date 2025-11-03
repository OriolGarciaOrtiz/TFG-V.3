import cv2 as cv
import numpy as np

# Diccionario de colores con sus rangos HSV
color_ranges = {
    'amarillo': ([28, 100, 100], [32, 255, 255]),
    'naranja': ([10, 100, 100], [20, 255, 255]),
    'verde': ([50, 100, 100], [80, 255, 255]),
    'azul': ([100, 100, 100], [130, 255, 255])
}

img = cv.imread('imagenes/bolasDiferentesMedidas.png')
img = cv.resize(img, (720, 480))
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

# Variables para guardar el contorno más grande
mayor_contorno = None
mayor_area = 0

kernel = np.ones((5, 5), np.uint8)

# Procesar cada color
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

# Dibujar solo el contorno más grande (de cualquier color)
if mayor_contorno is not None:
    res = cv.drawContours(img, [mayor_contorno], -1, (0, 255, 0), 3)

cv.imshow("res", img)
cv.waitKey(0)
cv.destroyAllWindows()