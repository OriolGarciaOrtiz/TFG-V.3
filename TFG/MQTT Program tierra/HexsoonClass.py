import time
import yaml

from dronLink.Dron import Dron
from ultralytics import YOLO
import cv2
import numpy as np
from pymavlink import mavutil
from dronLink.modules.dron_move import _prepare_command_mov
import base64
from colorama import init, Fore
import threading
import queue
from tkinter import Tk, filedialog

class HexsoonController:
    def __init__(self):
        self.is_connected = False
        self.dron = Dron()
        self.cap = None
        self.take_off_finalizado=False

        init(autoreset=True)

        self.model = None

        self.panel_width = 320
        self.panel_height = 240

        self.h_min = 0
        self.h_max = 179
        self.s_min = 0
        self.s_max = 255
        self.v_min = 0
        self.v_max = 255

        self.t1 = 0
        self.t2 = 255

        self.detection_mode = "Color Contour"   # or "Neural Network" or None

        self.Kp_x = 0
        self.Ki_x = 0
        self.Kd_x = 0
        self.Kp_y = 0
        self.Ki_y = 0
        self.Kd_y = 0

        self.PID_mode = "PID"   # or "P", "I", "D", etc.

        self.max_velocity = 50

        self.view_mode = "Front View"  # or "Down View" etc.

        self.take_off_alt = 5

        self.try_mode = "Practice"

        self.camera_option = "Default Cam"

        self.click_connect = False
        self.click_disconnect = False

        self.uncoded_original_frame = None
        self.uncoded_detected_frame = None

        self.prev_error_x = 0
        self.prev_error_y = 0

        self.integral_x = 0
        self.integral_y = 0

        self.left_right = 0
        self.for_back = 0
        self.up_down = 0
        self.yaw = 0

        self.original_frame_RTC = None
        self.detected_frame_RTC = None

        yamlname = 'calibration_data_px.yaml'
        self.data = None
        with open(yamlname) as f:
            self.data = yaml.safe_load(f)


        self.yolo_queue = queue.Queue(maxsize=1)
        self.yolo_result = (None, [])  # (object_center, boxes_info)
        self.yolo_lock = threading.Lock()
        self.yolo_running = True

        self.yolo_thread = threading.Thread(
            target=self._yolo_worker_loop,
            daemon=True
        )
        self.yolo_thread.start()

    from pymavlink import mavutil



    def connect_drone(self):

        self.click_connect = True

        if self.try_mode == "Simulation":
            self.dron.connect('tcp:127.0.0.1:5763', 115200)

            #self.stabilizeYaw()

        elif self.try_mode == "Practice":
            #self.dron.connect('tcp:127.0.0.1:5763', 115200)
            self.dron.connect('COM3', 57600)
            #self.stabilizeYaw()
            pass

        else:
            raise ValueError(Fore.RED + "Unknown connection mode selected")
        

        self.is_connected = True


    def disconnect_drone(self):
        
        if self.is_connected:
            
            self.click_disconnect = True
            self.is_connected = False  
            self.dron.disconnect()

    def take_off_drone(self):
        if not self.is_connected:
            print("No está conectado")
            return

        print(Fore.GREEN + "Taking off...")


        self.dron.arm()
        time.sleep(0.5)

        self.dron.takeOff(self.take_off_alt)

        time.sleep(10)#Esperar x segundos a terminar el take off
        print(Fore.GREEN + "Takeoff completado")

        self.take_off_finalizado = True
        self.stabilizeYaw()

    def land_drone(self):
        
        if self.is_connected:
            
            self.dron.Land()


    def Return_To_Launch_drone(self):
        
        if self.is_connected:
            
            self.dron.RTL()


    def arm_drone(self):
        
        if self.is_connected:
            
            self.dron.arm()

    def load_model(self):

        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Models Yolo", "*.pt")],
            initialdir="Yolo Models"
        )

        try: 

            self.model = YOLO(archivo)
            print(Fore.GREEN + "YOLO model correctly loaded")

        except:

            print(Fore.RED + "Error loading YOLO model")

    def set_velocity(self):


        if not self.take_off_finalizado:
            return

        vehicle: mavutil.mavfile = getattr(self.dron, 'vehicle', None)
        if vehicle is None:
            return

        step_x = self.for_back / 100.0
        step_y = self.left_right / 100.0
        step_z = -self.up_down / 100.0

        msg = _prepare_command_mov(self.dron, step_x, step_y, step_z, bodyRef=True)
        vehicle.mav.send(msg)

    def base64_to_image(self, b64_string):
        if b64_string is None:
            return None
        img_data = base64.b64decode(b64_string)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame


    def cap_frame(self, mode: str):
        """
        Returns (original, detected) depending on the input mode and try_mode.
        """

        # ------------------------- PC CAMERA MODE -------------------------
        if mode == "Default Cam":

            try: 
                if self.cap is None:
                    self.cap = cv2.VideoCapture(0)

                ret, frame = self.cap.read()
                if not ret:
                    return None, None


                return self.get_detected_frame(frame)  # No detected frame for webcam
            
            except: 
                return None, None
        
        # ------------------------- PC CAMERA MODE -------------------------
        elif mode == "Raspi Cam":
            if self.original_frame_RTC is None:
                return None, None

            return self.original_frame_RTC, self.detected_frame_RTC
        
        # ------------------------- PC CAMERA MODE -------------------------
        elif mode == "Panoramic Cam":

            try:
                if self.cap is None:
                    self.cap = cv2.VideoCapture(0)
                ret, frame = self.cap.read()
                if not ret:
                    return None, None


                cam_matrix = np.array(self.data['camera_matrix'])
                dist_coefs = np.array(self.data['distortion_coefficients'])
                h, w = 480, 640
                new_cam_mtx, roi = cv2.getOptimalNewCameraMatrix(cam_matrix, dist_coefs, (w, h), 1, (w, h))
                x, y, w, h = roi
                u_img = cv2.undistort(frame, cam_matrix, dist_coefs, None, new_cam_mtx)

                # crop and save the undistorted image
                dst = u_img[y:y + h, x:x + w]
                dst = cv2.flip(dst, 1)

                return self.get_detected_frame(dst)
            except:
                return None, None
            
        # ------------------------- UNKNOWN MODE -------------------------
        return None, None

    def _yolo_worker_loop(self):
        while self.yolo_running:
            frame = self.yolo_queue.get()
            try:
                results = self.model.predict(frame, conf=0.3, verbose=False)

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
                        label = self.model.names[cls]

                        boxes_info.append((x1, y1, x2, y2, label, conf))

                        if area > max_area:
                            max_area = area
                            object_center = (x1 + w // 2, y1 + h // 2)

                with self.yolo_lock:
                    self.yolo_result = (object_center, boxes_info)

            except Exception as e:
                print(Fore.RED + f"YOLO worker error: {e}")
                with self.yolo_lock:
                    self.yolo_result = (None, [])

    def get_object_center(self, dil_frame, img_contour):
        """
        Returns the center of the detected object.
        """

        # -------------------- COLOR CONTOUR MODE --------------------
        if self.detection_mode == "Color Contour":
            contours, _ = cv2.findContours(
                dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
            )

            if contours:
                c = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(c)

                if area > 300:
                    x, y, w, h = cv2.boundingRect(c)
                    object_center = (x + w // 2, y + h // 2)

                    cv2.rectangle(
                        img_contour, (x, y), (x + w, y + h), (0, 255, 0), 2
                    )
                    cv2.circle(
                        img_contour, object_center, 5, (255, 0, 0), cv2.FILLED
                    )

                    return object_center, img_contour

            return None, img_contour

        # -------------------- NEURAL NETWORK MODE --------------------
        elif self.detection_mode == "Neural Network" and self.model is not None:

            # Intentar mandar frame al worker (NO BLOQUEANTE)
            try:
                self.yolo_queue.put_nowait(img_contour.copy())
            except Exception:
                # YOLO sigue ocupado → seguimos usando el último resultado
                pass

            # Recuperar último resultado procesado
            with self.yolo_lock:
                object_center, boxes_info = self.yolo_result

            # Dibujar detecciones (si existen)
            if boxes_info:
                for (x1, y1, x2, y2, label, conf) in boxes_info:
                    cv2.rectangle(
                        img_contour, (x1, y1), (x2, y2), (0, 255, 0), 2
                    )
                    cv2.putText(
                        img_contour,
                        f"{label} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        2
                    )

                if object_center is not None:
                    cv2.circle(img_contour, object_center, 5, (255, 0, 0), cv2.FILLED)

            return object_center, img_contour

        # -------------------- NO MODE SELECTED --------------------
        else:
            cv2.putText(
                img_contour,
                "No detection mode selected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            return None, img_contour

    def get_velocities(self, oject_center):

        '''
            Returns the camputed velocities to be sent to the simulator.
        '''

        if oject_center is not None:

            cx, cy = oject_center
            error_x = cx - self.panel_width / 2
            error_y = self.panel_height / 2- cy #Como en este caso la camara no es un espejo así está bien
            
            derivative_x = error_x - self.prev_error_x
            derivative_y = error_y - self.prev_error_y

            if self.PID_mode == "P":
                velocity_x = self.Kp_x * error_x
                velocity_y = self.Kp_y * error_y

            elif self.PID_mode == "I":
                velocity_x = self.Ki_x * self.integral_x
                velocity_y = self.Ki_y * self.integral_y

            elif self.PID_mode == "D":
                velocity_x = self.Kd_x * derivative_x
                velocity_y = self.Kd_y * derivative_y

            elif self.PID_mode == "PI":
                velocity_x = (self.Kp_x * error_x) + (self.Ki_x * self.integral_x)
                velocity_y = (self.Kp_y * error_y) + (self.Ki_y * self.integral_y)

            elif self.PID_mode == "PD":
                velocity_x = (self.Kp_x * error_x) + (self.Kd_x * derivative_x)
                velocity_y = (self.Kp_y * error_y) + (self.Kd_y * derivative_y)

            elif self.PID_mode == "PID":
                velocity_x = (self.Kp_x * error_x) + (self.Ki_x * self.integral_x) + (self.Kd_x * derivative_x)
                velocity_y = (self.Kp_y * error_y) + (self.Ki_y * self.integral_y) + (self.Kd_y * derivative_y)

            else:
                velocity_x = error_x
                velocity_y = error_y

            velocity_x = int(np.clip(velocity_x, -self.max_velocity, self.max_velocity))
            velocity_y = int(np.clip(velocity_y, -self.max_velocity, self.max_velocity))

            if self.view_mode == "Front View":
                self.left_right = velocity_x
                self.up_down = velocity_y
                self.for_back = 0

            else:
                self.left_right = velocity_x
                self.for_back = velocity_y
                self.up_down = 0

            if self.take_off_finalizado:
                #print("Empieza a enviar velocidades")
                self.integral_x += error_x
                self.integral_y += error_y
                self.set_velocity()



        else:
            self.left_right = 0
            self.for_back = 0
            self.up_down = 0
            self.integral_x=0
            self.integral_y=0
            self.set_velocity()


    def get_detected_frame(self, frame):


        frame_display = cv2.resize(frame, (self.panel_width, self.panel_height))
        frame_hsv = cv2.cvtColor(frame_display, cv2.COLOR_BGR2HSV)

        lower = np.array([self.h_min, self.s_min, self.v_min])
        upper = np.array([self.h_max, self.s_max, self.v_max])

        mask = cv2.inRange(frame_hsv, lower, upper)
        result = cv2.bitwise_and(frame_display, frame_display, mask=mask)

        img_blur = cv2.GaussianBlur(result, (7, 7), 1)
        img_grey = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_grey, self.t1, self.t2)
        kernel = np.ones((5, 5), np.uint8)
        img_dilated = cv2.dilate(img_canny, kernel, iterations=1)

        ''''''

        img_contour = frame_display.copy()

        object_center, img_contour = self.get_object_center(img_dilated, img_contour)

        self.get_velocities(object_center)

        return img_dilated, img_contour

    def get_frame(self):

        try:

            original_frame, detected_frame = self.cap_frame(self.camera_option)

            if original_frame is None:
                return None, None

            return original_frame, detected_frame

        except:

            return None, None
    

    def set_param(self, name, value):

        # El motivo de esta función es la siguiente. El problema era que al usar _prepare_command_mov a partir de 0.4 m/s de velocidad en
        # left right el dron empezaba a girar en yaw. Intenté hacer _prepare_command_mov_changed con el objetivo de cambiar la máscara para solo velcoidades
        # y que el movimiento no fuera por posición sino por velocidad pero segía moviendose en yaw el dron. Después pen´se que podría ser
        # a causa de que estaba cogiendo la referencia del dron pero cambiadba a la NED pero tampoco era eso. Así que como ñultima opción me quedó
        # que fuera un problema del guided mode. Esto por lo que se ve sucede por un bug / comportamiento por diseño del controlador de GUIDED de ArduCopter.
        # En el firmware ArduCopter cuando se envia un mensaje SET_POSITION_TARGET_LOCAL_NED con velocidades laterales (vy) en BODY_NED,el controlador interno asume que estás pidiendo
        # “moverte lateralmente respecto al rumbo actual”.Pero si el yaw no está bloqueado o el modo GUIDED no está limitado, el autopiloto interpreta el movimiento lateral como una
        # instrucción de girar el yaw para “alinearse” con el vector de velocidad, es decir, ArduCopter intenta mirar hacia donde te mueves.
        # Por ello he hecho esta función que mantiene el headind fijo y bloquea el yaw en modo guided cambiando las opciones de modo 0 a modo 8   

        vehicle: mavutil.mavfile = getattr(self.dron, "vehicle", None)
        msg = mavutil.mavlink.MAVLink_param_set_message(
            vehicle.target_system,
            vehicle.target_component,
            name.encode("utf-8"),
            float(value),
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )
        vehicle.mav.send(msg)


    def stabilizeYaw(self):
        self.set_param("WP_YAW_BEHAVIOR", 0)  # Mantener heading fijo
        self.set_param("GUID_OPTIONS", 8)  # Bloquear yaw en GUIDED