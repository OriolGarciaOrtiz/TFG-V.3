"""
Hay que instalar los paquetes siguientes:
opencv-contrib-python
torch
torchvision
pandas
ultralytics
requests
djitellopy
"""

import cv2
from time import time, sleep
from ultralytics import YOLO
from djitellopy import Tello


def cv2_capture(me, model, delta_min=0):
    """
    Captura el video del dron Tello y realiza inferencia con YOLOv8.
    Presiona 'q' para salir.
    """
    # Inicia el stream del dron
    me.streamon()
    frame_read = me.get_frame_read()

    previous = time()
    print("✅ Iniciando transmisión del dron...")

    while True:
        current = time()
        delta = current - previous

        if delta > delta_min:
            frame = frame_read.frame  # Captura el frame actual del dron

            if frame is None:
                print("⚠️ No se pudo leer el frame del dron.")
                continue

            # Inference con YOLOv8
            results = model.predict(frame, conf=0.5, verbose=False)

            for r in results:
                for box in r.boxes:
                    # Coordenadas bbox
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Clase y confianza
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = model.names[cls]

                    # Dibujar bounding box y etiqueta
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame,
                                f"{name}: {conf:.2f}",
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                (255, 255, 255),
                                2)

            cv2.imshow("Tello Stream", frame)
            previous = current

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    me.streamoff()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Inicializar el dron
    me = Tello()
    me.connect()
    print(f"🔋 Nivel de batería: {me.get_battery()}%")

    # Cargar el modelo YOLOv8 (ajusta la ruta a tu modelo entrenado)
    model = YOLO("RC_exterior.pt")

    # Iniciar inferencia en video del dron
    cv2_capture(me, model, delta_min=0)
