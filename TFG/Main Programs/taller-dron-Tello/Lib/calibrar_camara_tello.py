import cv2
import numpy as np
import glob
import os

# Para hacer la calibración, usaremos un tablero de 10x8 (10x8 porque es la imagen que recomienda OpenCV) el cual tiene 9x6 intersecciones internas
#(las externas no nos interesan porque el borde puede ser blanco o distinto además de que cv2.findChessboardCorners no usa
# las intersecciones de los bordes.
# --- Parámetros del tablero ---
CHESSBOARD_SIZE = (9, 6)  # esquinas internas del tablero
SQUARE_SIZE = 0.015  # tamaño real del cuadro en metros (ajusta según tu impresión)

# --- Preparar puntos 3D del tablero ---
objp = np.zeros((CHESSBOARD_SIZE[0]*CHESSBOARD_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

# --- Listas para almacenar puntos de objeto e imagen ---
objpoints = []
imgpoints = []

# --- Leer todas las imágenes ---
images = glob.glob(r"C:\Tello\taller-dron-Tello\Lib\Img_Calibracion\*.jpg")
print(f"Encontradas {len(images)} imágenes.")

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        imgpoints.append(corners2)
        cv2.drawChessboardCorners(img, CHESSBOARD_SIZE, corners2, ret)
        cv2.imshow('Calibración', img)
        cv2.waitKey(100)
    else:
        print(f"No se detectó tablero en {fname}")

cv2.destroyAllWindows()

# --- Calibrar cámara ---
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("\n✅ Calibración completada:")
print("Matriz de cámara:\n", camera_matrix)
print("Coeficientes de distorsión:\n", dist_coeffs.ravel())

# --- Error de reproyección ---
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    mean_error += error
print(f"\nError de reproyección medio: {mean_error / len(objpoints):.4f}")

# Ruta donde se guardarán los parámetros
SAVE_PATH = r"C:\Tello\taller-dron-Tello\Lib\Parameters"
output_file = os.path.join(SAVE_PATH, "parametros_camara_tello.npz")

# Guardar resultados
np.savez(output_file, camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
print(f" Parámetros guardados en: {output_file}")