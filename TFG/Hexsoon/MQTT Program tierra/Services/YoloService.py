from HexsoonGUI import GUI
import numpy as np
from typing import Optional, Tuple

class ServiceYolo:


    def __init__(self, target_gui: GUI):
        
        self.running: bool = False

        self.target_gui: GUI = target_gui


    def start(self):

        while self.running:
                        
            try:
                
                results = self.target_gui.controller.model.predict(self.target_gui.controller.yolo_img, conf=0.3, verbose=False)

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

            except Exception as e:
                    
                self.yolo_result = (None, [])