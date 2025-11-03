'''
Hay que instalar los paquetes siguientes:
opencv-contrib-python
torch
torchvision
pandas
ultralytics
requests
'''

import cv2
from time import time
from ultralytics import YOLO


def cv2_capture(model, delta_min=0):
    cap = cv2.VideoCapture(0)

    previous = time()

    while cap.isOpened():
        current = time()
        delta = current - previous

        if delta > delta_min:
            status, frame = cap.read()
            if not status:
                break

            # Inference con YOLOv8
            results = model.predict(frame, conf=0.5)

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

            cv2.imshow("frame", frame)
            previous = current

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Cargar el modelo entrenado en YOLOv8
    model = YOLO("best_RC_Final.pt")  # sustituye por la ruta a tu modelo entrenado

    # Iniciar la inferencia en webcam
    cv2_capture(model, delta_min=0)
