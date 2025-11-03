'''
Hay que instalar los paquetes siguioentee:
opencv-contrib-python
torch
torchvision
pandas
ultralytics
requests
'''


import cv2
from time import time

import torch
import pathlib


def cv2_capture(model, delta_min):
    cap = cv2.VideoCapture(0)

    previous = time()
    delta = 0

    while cap.isOpened():
        current = time()
        delta = current - previous

        if delta > delta_min:
            status, frame = cap.read()

            if not status:
                break

            # Inference
            pred = model(frame)
            # xmin,ymin,xmax,ymax
            df = pred.pandas().xyxy[0]
            # Filter by confidence
            df = df[df["confidence"] > 0.5]

            for i in range(df.shape[0]):
                bbox = df.iloc[i][["xmin", "ymin", "xmax", "ymax"]].values.astype(int)

                # print bboxes: frame -> (xmin, ymin), (xmax, ymax)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 0, 0), 2)
                # print text
                cv2.putText(frame,
                            f"{df.iloc[i]['name']}: {round(df.iloc[i]['confidence'], 4)}",
                            (bbox[0], bbox[1] - 15),
                            cv2.FONT_HERSHEY_PLAIN,
                            1,
                            (255, 255, 255),
                            2)

            cv2.imshow("frame", frame)

            previous = current

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()


if __name__ == '__main__':
    # Needed to solve "Error: cannot instantiate 'PosixPath' on your system" in Windows
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    # Loading the model (pytorch-hub is not needed if yolov5 is cloned and with requirements.txt intalled)
    myModel = torch.hub.load ('ultralytics/yolov5', 'custom', path='best_straw.pt')  # custom
    #myModel = hubconf.custom(path='best.pt')  # custom

    # Initiate the inference
    cv2_capture(model=myModel, delta_min=0)
