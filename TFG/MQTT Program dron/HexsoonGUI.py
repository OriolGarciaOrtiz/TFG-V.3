from HexsoonClass import *
import cv2
import numpy as np
import paho.mqtt.client as mqtt
from picamera import PiCamera


class GUI:
    def __init__(self, root):
        self.root = root
        self.is_connected = False
        self.controller = HexsoonController()
        self.panel_width = 320
        self.panel_height = 240

        self.BROKER = "broker.hivemq.com"
        self.PORT = 1883
        self.TOPIC_SUB = "test/chat/pub"  # Escucha al publicador
        self.TOPIC_PUB = "test/chat/sub"  # Envía respuesta

        self.client = mqtt.Client()
        self.client.on_message = self.recieve_data

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

        # Hace falta usar todos los comandos que tiene el dron (connect, disconnect...)


    def recieve_data(self, client, userdata, msg): 
        text = msg.payload.decode()
        print("📥 MQTT recibido:", text)


    def set_data(self):
        pass


    def prepare_data(self):
        pass


    def send_data(self):
        pass

    
    def update_frame(self):
        try:
            if not self.controller.is_connected or not self.controller.cap or not self.controller.cap.isOpened():
                self.log("Camera not initialized or drone not connected.")
                return

            ret, frame = self.controller.cap.read()
            if not ret or frame is None:
                self.log("Could not read frame from the camera.")
                self.root.after(100, self.update_frame)
                return

            frame_display = cv2.resize(frame, (self.panel_width, self.panel_height))
            frame_hsv = cv2.cvtColor(frame_display, cv2.COLOR_BGR2HSV)

            lower = np.array([self.h_min, self.s_min, self.v_min])
            upper = np.array([self.h_max, self.s_max, self.v_max])
            mask = cv2.inRange(frame_hsv, lower, upper)
            result = cv2.bitwise_and(frame_display, frame_display, mask=mask)

            img_blur = cv2.GaussianBlur(result, (7, 7), 1)
            img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
            img_canny = cv2.Canny(img_gray, self.t1.get(), self.t2.get())
            kernel = np.ones((5, 5), np.uint8)
            img_dil = cv2.dilate(img_canny, kernel, iterations=1)

            object_center = None
            x, y, w, h = 0, 0, 0, 0
            img_contour = frame_display.copy()

            if self.detection_mode == "Color Contour":
                img_blur = cv2.GaussianBlur(result, (7, 7), 1)
                img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
                img_canny = cv2.Canny(img_gray, self.t1.get(), self.t2.get())
                kernel = np.ones((5, 5), np.uint8)
                img_dil = cv2.dilate(img_canny, kernel, iterations=1)

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
                    left_right = vx
                    up_down = vy
                    for_back = 0
                else:
                    left_right = vx
                    for_back = vy
                    up_down = 0

                self.controller.set_velocity(left_right, for_back, up_down, yaw=0)


        except Exception as e:
            self.log(f"Error in update_frame def: {e}")
            self.root.after(1, self.update_frame)



