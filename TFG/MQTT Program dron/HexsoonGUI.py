from HexsoonClass import *
import numpy as np
import paho.mqtt.client as mqtt
import json
import base64


class GUI:
    def __init__(self):
        self.is_connected = False
        self.controller = HexsoonController()
        self.controller.init_camera()
        self.panel_width = 320
        self.panel_height = 240

        self.BROKER = "broker.hivemq.com"
        self.PORT = 1883
        self.TOPIC_SUB = "test/chat/tierra2dron"  # Escucha al publicador
        self.TOPIC_PUB = "test/chat/dron2tierra"  # Envía respuesta
        
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(self.BROKER, self.PORT, 60)
        self.client.subscribe(self.TOPIC_SUB)
        self.client.loop_start()

        '''  All the params that have to be sent with MQTT to the drone fromm the GUI  '''

        # --- HSV thresholds ---
        self.h_min = 0
        self.h_max = 179
        self.s_min = 0
        self.s_max = 255
        self.v_min = 0
        self.v_max = 255

        self.t1 = 0
        self.t2 = 255

        # --- Detection mode ---
        self.detection_mode = "Color Contour"   # or "Neural Network" or None

        # --- PID ---
        self.Kp_x = 0
        self.Ki_x = 0
        self.Kd_x = 0
        self.Kp_y = 0
        self.Ki_y = 0
        self.Kd_y = 0

        self.PID_mode = "PID"   # or "P", "I", "D", etc.

        # --- Drone velocity limits ---
        self.max_velocity = 50

        # --- View mode ---
        self.view_mode = "Front View"  # or "Down View" etc.

        # --- Takeoff altitude ---
        self.take_off_alt = 3

        self.try_mode = "Practice"

        self.connect_click = False
        self.disconnect_mode = False
        self.takeoff_click = False
        self.land_click = False
        self.rtl_click = False
        self.arm_click = False

        # També s'ha d'enviar el model de Yolo que es vol fer servir


    def on_message(self, client, userdata, msg): 
        
        text: str = msg.payload.decode()

        self.set_data(text)     


    def set_data(self, msg):
        
        data: dict = json.loads(msg)

        self.h_min = int(data.get("h_min", self.h_min))
        self.h_max = int(data.get("h_max", self.h_max))
        self.s_min = int(data.get("s_min", self.s_min))
        self.s_max = int(data.get("s_max", self.s_max))
        self.v_min = int(data.get("v_min", self.v_min))
        self.v_max = int(data.get("v_max", self.v_max))

        self.t1 = int(data.get("t1", self.t1))
        self.t2 = int(data.get("t2", self.t2))

        self.detection_mode = data.get("detection_mode", self.detection_mode)

        self.Kp_x = float(data.get("Kp_x", self.Kp_x))
        self.Ki_x = float(data.get("Ki_x", self.Ki_x))
        self.Kd_x = float(data.get("Kd_x", self.Kd_x))
        self.Kp_y = float(data.get("Kp_y", self.Kp_y))
        self.Ki_y = float(data.get("Ki_y", self.Ki_y))
        self.Kd_y = float(data.get("Kd_y", self.Kd_y))

        self.PID_mode = data.get("PID_mode", self.PID_mode)

        self.max_velocity = int(data.get("max_velocity", self.max_velocity))

        # FIXED: view_mode should come from data["view_mode"]
        self.view_mode = data.get("view_mode", self.view_mode)

        self.take_off_alt = int(data.get("take_off_alt", self.take_off_alt))

        self.try_mode = data.get("try_mode", self.try_mode)

        self.connect_click = bool(data.get("connect_click", self.connect_click))
        self.disconnect_mode = bool(data.get("disconnect_mode", self.disconnect_mode))
        self.takeoff_click = bool(data.get("takeoff_click", self.takeoff_click))
        self.land_click = bool(data.get("land_click", self.land_click))
        self.rtl_click = bool(data.get("rtl_click", self.rtl_click))
        self.arm_click = bool(data.get("arm_click", self.arm_click))
         

    def prepare_data(self, original_frame, detection_frame) -> dict:
        # Encode original frame
        _, buffer_original = cv2.imencode(".jpg", original_frame)
        img_b64_original = base64.b64encode(buffer_original).decode()

        # Encode detected/contour frame
        _, buffer_detected = cv2.imencode(".jpg", detection_frame)
        img_b64_detected = base64.b64encode(buffer_detected).decode()
    
        # Prepare dictionary
        data: dict = {
            'left_right': self.controller.left_right,
            'for_back': self.controller.for_back,
            'up_down': self.controller.up_down,
            'yaw': self.controller.yaw,
            'frame_display': img_b64_original,
            'img_contour': img_b64_detected,
            'is_connected' : self.is_connected
        }

        self.send_data(data)


    def send_data(self, data: dict):
        
        message: str = json.dumps(data)

        self.client.publish(self.TOPIC_PUB, message)

    def log(self, message):
        #print(message)
        pass

    
    def update_frame(self):
            
        try:

            self.controller.do_actions(self.connect_click, self.try_mode, self.disconnect_mode,
                                       self.takeoff_click, self.take_off_alt, self.land_click,
                                       self.rtl_click, self.arm_click)
                                       
            
            if not self.controller.is_connected:
                self.log("Drone not connected.")
                return
            
            else:

                if self.controller.cap is None:
                    self.log("Camera not initialized")
                    return

                frame = self.controller.get_frame()
                if frame is None:
                    print("Could not read frame from the PiCamera.")
                    return


                frame_display = cv2.resize(frame, (self.panel_width, self.panel_height))
                frame_hsv = cv2.cvtColor(frame_display, cv2.COLOR_BGR2HSV)

                lower = np.array([self.h_min, self.s_min, self.v_min])
                upper = np.array([self.h_max, self.s_max, self.v_max])
                mask = cv2.inRange(frame_hsv, lower, upper)
                result = cv2.bitwise_and(frame_display, frame_display, mask=mask)

                img_blur = cv2.GaussianBlur(result, (7, 7), 1)
                img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
                img_canny = cv2.Canny(img_gray, self.t1, self.t2)
                kernel = np.ones((5, 5), np.uint8)
                img_dil = cv2.dilate(img_canny, kernel, iterations=1)

                object_center = None
                x, y, w, h = 0, 0, 0, 0
                img_contour = frame_display.copy()

                if self.detection_mode == "Color Contour":

                    contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    if contours:
                        c = max(contours, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(c)
                        if cv2.contourArea(c) > 300:
                            cv2.rectangle(img_contour, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            object_center = (x + w // 2, y + h // 2)
                            cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)


                elif self.detection_mode == "Neural Network" and self.controller.model is not None:

                    # Track tiene el objetivo de mantiene los IDs de objetos entre frames. Usa menos recursos si el objeto no se mueve mucho
                    # así que quizas puede mejorar la velocidad para que la camara no vaya con tanto delay
                    results = self.controller.model.track(frame_display, persist=True, conf=0.5, verbose=False)
                    max_area = 0

                    best_box = None

                    for r in results:
                        for box in r.boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            area = (x2 - x1) * (y2 - y1)
                            if area > max_area:
                                max_area = area
                                best_box = (x1, y1, x2, y2, box)

                    if best_box is not None:
                        x1, y1, x2, y2, box = best_box
                        w, h = x2 - x1, y2 - y1
                        cx, cy = x1 + w // 2, y1 + h // 2
                        object_center = (cx, cy)
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = f"{self.controller.model.names[cls]} {conf:.2f}"
                        cv2.rectangle(img_contour, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(img_contour, label, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                        cv2.circle(img_contour, object_center, 5, (0, 0, 255), cv2.FILLED)
                else:
                    cv2.putText(img_contour, "No detection mode active", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                if object_center is not None:
                    cx, cy = object_center
                    error_x = cx - (self.panel_width / 2)

                    if self.view_mode == "Front View":
                        error_y = (self.panel_height / 2) - cy
                    else:  
                        error_y = cy - (self.panel_height / 2)

                    self.controller.integral_x = getattr(self.controller, "integral_x", 0) + error_x
                    self.controller.integral_y = getattr(self.controller, "integral_y", 0) + error_y
                    derivative_x = error_x - getattr(self.controller, "prev_error_x", 0)
                    derivative_y = error_y - getattr(self.controller, "prev_error_y", 0)

                    Kpx, Kix, Kdx = self.Kp_x, self.Ki_x, self.Kd_x
                    Kpy, Kiy, Kdy = self.Kp_y, self.Ki_y, self.Kd_y

                    if self.PID_mode == "P":
                        vx = Kpx * error_x
                        vy = Kpy * error_y
                    elif self.PID_mode == "I":
                        vx = Kix * self.controller.integral_x
                        vy = Kiy * self.controller.integral_y
                    elif self.PID_mode == "D":
                        vx = Kdx * derivative_x
                        vy = Kdy * derivative_y
                    elif self.PID_mode == "PI":
                        vx = Kpx * error_x + Kix * self.controller.integral_x
                        vy = Kpy * error_y + Kiy * self.controller.integral_y
                    elif self.PID_mode == "PD":
                        vx = Kpx * error_x + Kdx * derivative_x
                        vy = Kpy * error_y + Kdy * derivative_y
                    elif self.PID_mode == "PID":
                        vx = Kpx * error_x + Kix * self.controller.integral_x + Kdx * derivative_x
                        vy = Kpy * error_y + Kiy * self.controller.integral_y + Kdy * derivative_y
                    else:
                        vx, vy = error_x, error_y

                    vx = int(np.clip(vx, -self.max_velocity, self.max_velocity))
                    vy = int(np.clip(vy, -self.max_velocity, self.max_velocity))

                    self.controller.prev_error_x = error_x
                    self.controller.prev_error_y = error_y

                    if self.view_mode == "Front View":
                        self.controller.left_right = vx
                        self.controller.up_down = vy
                        self.controller.for_back = 0
                    else:
                        self.controller.left_right = vx
                        self.controller.for_back = vy
                        self.controller.up_down = 0

                    self.controller.set_velocity()

                self.prepare_data(frame_display, img_contour)

                return


        except Exception as e:
            self.log(f"Error in update_frame def: {e}")
            return

