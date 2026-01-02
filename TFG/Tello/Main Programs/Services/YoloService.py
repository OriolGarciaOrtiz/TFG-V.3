from TelloGUI import GUI

class ServiceYOLO:

    def __init__(self, target_gui: GUI):
        
        self.target_gui = target_gui

        self.running = True


    def _process_yolo_result(self, results):
        object_center = None
        w = h = 0
        max_area = 0
        boxes_info = []  # [(x1, y1, x2, y2, label, conf)]

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w_box, h_box = x2 - x1, y2 - y1
                area = w_box * h_box
                conf = float(box.conf[0])
                label = self.target_gui.controller.model.names[int(box.cls[0])] \
                    if hasattr(self.target_gui.controller.model, "names") else str(int(box.cls[0]))

                boxes_info.append((x1, y1, x2, y2, label, conf))

                if area > max_area:
                    max_area = area
                    w, h = w_box, h_box
                    object_center = (x1 + w_box // 2, y1 + h_box // 2)

        return object_center, int(w), int(h), None, boxes_info
    

    def _process_game_result(self, results):
        max_area = 0
        best_box = None
        detected_label = None
        boxes_info = []  # [(x1, y1, x2, y2, label_name, conf)]

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w_box, h_box = x2 - x1, y2 - y1
                area = w_box * h_box
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label_map = {0: "horse", 1: "bird", 2: "dog", 3: "cat"}
                label_name = label_map.get(cls_id, "unknown")
                boxes_info.append((x1, y1, x2, y2, label_name, conf))

                if area > max_area:
                    max_area = area
                    best_box = (x1, y1, x2, y2)
                    detected_label = label_name

        if best_box is not None:
            x1, y1, x2, y2 = best_box
            w, h = x2 - x1, y2 - y1
            cx, cy = x1 + w // 2, y1 + h // 2
            object_center = (cx, cy)
            return object_center, w, h, detected_label, boxes_info

        return None, 0, 0, None, boxes_info
    

    def start(self):

        if self.target_gui.detection_var in ["Neural Network", "Game Mode"]:

            while self.running:
            
                if self.target_gui.controller.is_connected:

                    frame = self.target_gui.yolo_frame

                    if frame is not None:

                        try:

                            results = self.target_gui.controller.model.predict(frame, conf=0.5, verbose=False)

                            if self.target_gui.detection_var == "Neural Network":

                                object_center, w, h, detected_label, boxes_info = self._process_yolo_result(results)

                            elif self.target_gui.detection_var == "Game Mode":

                                object_center, w, h, detected_label, boxes_info = self._process_game_result(results)

                            else:
                                self.target_gui.yolo_result = (None, 0, 0, None, [])

                            self.target_gui.yolo_result = (object_center, w, h, detected_label, boxes_info)

                        except:
                            self.target_gui.yolo_result = (None, 0, 0, None, [])

                    else:
                        
                        self.target_gui.yolo_result = (None, 0, 0, None, [])

                else:
                        
                        self.target_gui.yolo_result = (None, 0, 0, None, [])

        else:

            print("Mode Selected not avaialble for YOLO")
            return None
        
    def stop(self):

        self.running = False