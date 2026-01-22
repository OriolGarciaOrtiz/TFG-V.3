import numpy as np
from HexsoonGUI import GUI
import time


class ServiceYolo:

    def __init__(self, target_gui: GUI):
        
        self.running: bool = False

        self.target_gui: GUI = target_gui


    def start(self):

        while self.running:

            yolo_img = self.target_gui.controller.get_frame()
                        
            try:

                if yolo_img is not None and self.target_gui.controller.model is not None:

                    if yolo_img.dtype != np.uint8:
                        yolo_img = yolo_img.astype(np.uint8)

                    if yolo_img.ndim == 2:
                        yolo_img = np.stack([yolo_img] * 3, axis=-1)
                    elif yolo_img.ndim == 3 and yolo_img.shape[2] == 1:
                        yolo_img = np.concatenate([yolo_img] * 3, axis=2)

                    results = self.target_gui.controller.model.predict(
                        yolo_img, conf=0.3, verbose=False
                    )

                    object_center = None
                    boxes_info = []
                    max_area = 0

                    for r in results:
                        
                        for box in r.boxes:
                            
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            w, h = x2 - x1, y2 - y1
                            area = w * h
                            conf = float(box.conf[0])
                            cls = int(box.cls[0])
                            label = self.target_gui.controller.model.names[cls]

                            boxes_info.append((x1, y1, x2, y2, label, conf))

                            if area > max_area:
                                max_area = area
                                object_center = (x1 + w // 2, y1 + h // 2)
                        
                    self.target_gui.controller.yolo_result = (object_center, boxes_info)

                else:

                    self.target_gui.controller.yolo_result = (None, [])

            except Exception as e:

                print(e)
                    
                self.target_gui.controller.yolo_result = (None, [])

            time.sleep(1/self.target_gui.FPS)