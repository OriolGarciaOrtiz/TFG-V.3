import time
import yaml
from tkinter import filedialog
from dronLink.Dron import Dron
from ultralytics import YOLO
import cv2
import numpy as np
from pymavlink import mavutil
from dronLink.modules.dron_move import _prepare_command_mov
from dronLink.modules.dron_RC_override import send_rc
from colorama import init, Fore
import threading
import queue
from typing import Optional, Tuple


class HexsoonController:
    def __init__(self):
        self.is_connected: bool = False
        self.dron: Dron = Dron()
        self.cap = None
        self.take_off_finalizado: bool = False

        init(autoreset=True)

        self.color_opt: str | None = None

        self.detected_color: str | None = None
        self.model: YOLO | None = None

        self.panel_width: int = 320
        self.panel_height: int = 240

        self.colors: dict | None = None

        self.zoom_factor: float = 1.5

        self.t1: int = 166
        self.t2: int = 171

        self.detection_mode: str | None = None

        self.Kp_x: float = 0
        self.Ki_x: float = 0
        self.Kd_x: float = 0
        self.Kp_y: float = 0
        self.Ki_y: float = 0
        self.Kd_y: float = 0

        self.max_velocity: int = 50

        self.view_mode: str | None = None

        self.take_off_alt: int = 2

        self.try_mode: str | None = None

        self.type_camera_option: str | None = None

        self.click_connect: bool = False
        self.click_disconnect: bool = False

        self.uncoded_original_frame: np.ndarray | None = None
        self.uncoded_detected_frame: np.ndarray | None = None

        self.prev_error_x: float = 0
        self.prev_error_y: float = 0

        self.integral_x: float = 0
        self.integral_y: float = 0

        self.left_right: float = 0
        self.for_back: float = 0
        self.up_down: float = 0
        self.yaw: float = 0

        self.original_frame_RTC: np.ndarray | None = None
        self.detected_frame_RTC: np.ndarray | None = None

        yamlname: str = 'calibration_data_px.yaml'
        self.data: dict | None = None
        with open(yamlname) as f:
            self.data = yaml.safe_load(f)

        self.yolo_queue: queue = queue.Queue(maxsize=1)
        self.yolo_result: tuple[tuple[int, int] | None, list] = (None, [])
        self.yolo_lock: threading.Lock = threading.Lock()
        self.yolo_running: bool = True

        self.yolo_thread = threading.Thread(
            target=self._yolo_worker_loop,
            daemon=True
        )
        self.yolo_thread.start()

    def load_model(self):

        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            initialdir="Yolo Models",
            filetypes=[("PyTorch model (*.pt)", "*.pt")]
        )

        try: 

            self.model = YOLO(archivo)
            print(Fore.GREEN + "YOLO model correctly loaded")

        except:

            print(Fore.RED + "Error loading YOLO model")


    def connect_drone(self):

        self.click_connect = True

        if self.try_mode == "Simulation":
            
            self.dron.connect('tcp:127.0.0.1:5763', 115200)

            print(Fore.GREEN + "Drone connected...")

        elif self.try_mode == "Practice":

            self.dron.connect('COM4', 57600)

            print(Fore.GREEN + "Drone connected...")

        else:
            raise ValueError(Fore.RED + "Unknown connection mode selected")

        self.is_connected = True


    def disconnect_drone(self):

        if self.is_connected:
            self.click_disconnect = True
            self.dron.disconnect()

            print(Fore.GREEN + "Drone disconnected...")


    def take_off_drone(self):
        
        if not self.is_connected:
            
            return

        print(Fore.GREEN + "Taking off...")

        self.dron.arm()
        time.sleep(0.5)

        self.dron.takeOff(self.take_off_alt)

        time.sleep(10)
        print(Fore.GREEN + "Takeoff complete")

        self.take_off_finalizado = True
        self.stabilizeYaw()


    def land_drone(self):

        if self.is_connected:
            self.dron.Land()


    def Return_To_Launch_drone(self):

        if self.is_connected:

            print(Fore.GREEN + "Returning to Launch...")

            self.dron.RTL()
        

    def arm_drone(self):

        if self.is_connected:
            self.dron.arm()


    def set_velocity(self): #OJO, cambios
        if not self.take_off_finalizado:
            return
        
        vehicle: mavutil.mavfile = getattr(self.dron, 'vehicle', None)

        if vehicle is None:
            return
        
        if self.detection_mode == "Color Contour":

            if self.view_mode == "Front View":

                if self.detected_color == "color1":

                    step_x = self.for_back / 100.0
                    step_y = self.left_right / 100.0
                    step_z = 0  # OJO, lo pongo todo a cero por si acaso que a veces se movia el dron
                    msg = _prepare_command_mov(self.dron, step_x, step_y, step_z, bodyRef=True)
                    vehicle.mav.send(msg)

                elif self.detected_color == "color2":

                    yaw_input = self.yaw / 300.0  # Valores entre -1 y 1 porque velocityx solo puede ir entre -100 a 100
                    yaw_pwm = 1500 + int(
                        yaw_input * 150)  # Para que la velocidad no sea super alta le ponemos un límite de +-150 porque si queremos usar los mismos Kp,Ki,Kd que los de left right el yaw se mueve demasiado según las pruebas que he hecho en simulación
                    yaw_pwm = max(1100, min(1900,
                                            yaw_pwm))  # Para tenerlo aún más seguro hay que poner esto ya que el rango válido de RC en Arducopter es 1100-1900. Si le das más o menos puede ser peligroso pra el equilibrio
                    send_rc(self.dron, 1500, 1500, 1500,
                            yaw_pwm)  # Ponemos todo a 1500 que es para que se mentanega a la misma altura
                    # Para poner bien las labels:

            else:
                step_x = self.for_back / 100.0
                step_y = self.left_right / 100.0
                step_z = 0  # OJO, lo pongo todo a cero por si acaso que a veces se movia el dron
                msg = _prepare_command_mov(self.dron, step_x, step_y, step_z, bodyRef=True)
                vehicle.mav.send(msg)

        elif self.detection_mode == "Neural Network" and self.view_mode == "Bottom View":
            step_x = self.for_back / 100.0
            step_y = self.left_right / 100.0
            step_z = 0  # OJO, lo pongo todo a cero por si acaso que a veces se movia el dron
            msg = _prepare_command_mov(self.dron, step_x, step_y, step_z, bodyRef=True)
            vehicle.mav.send(msg)
        else:
            msg = _prepare_command_mov(self.dron, 0, 0, 0, bodyRef=True)
            vehicle.mav.send(msg)


    def zoom_frame(self, frame: np.ndarray, zoom_factor: float=1.5) -> np.ndarray:

        if zoom_factor <= 1.0:
            return frame

        h, w = frame.shape[:2]

        new_w = int(w / zoom_factor)
        new_h = int(h / zoom_factor)

        cx, cy = w // 2, h // 2

        x1 = max(cx - new_w // 2, 0)
        y1 = max(cy - new_h // 2, 0)
        x2 = min(cx + new_w // 2, w)
        y2 = min(cy + new_h // 2, h)

        cropped = frame[y1:y2, x1:x2]

        zoomed = cv2.resize(
            cropped,
            (w, h),
            interpolation=cv2.INTER_LINEAR
        )

        return zoomed
    

    def cap_frame(self, mode: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:

        # ------------------------- PC CAMERA MODE -------------------------
        if mode == "Default Cam":

            try:
                if self.cap is None:
                    self.cap = cv2.VideoCapture(0)

                ret, frame = self.cap.read()
                if not ret:
                    return None, None

                return self.get_detected_frame(frame)

            except:
                return None, None

        # ------------------------- PC CAMERA MODE -------------------------
        elif mode == "Raspi Cam":
            if self.original_frame_RTC is None:
                return None, None

            return self.original_frame_RTC, self.detected_frame_RTC

        # ------------------------- Panoramic CAMERA MODE -------------------------
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

                dst = self.zoom_frame(dst, zoom_factor=self.zoom_factor)

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


    def get_object_center(self, dil_frame: Optional[np.ndarray], img_contour: Optional[np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:

        if self.detection_mode == "Color Contour":
            contours, _ = cv2.findContours(
                dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
            )

            if contours:
                c = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(c)

                if area > 100:
                    x, y, w, h = cv2.boundingRect(c)
                    object_center = (x + w // 2, y + h // 2)

                    # Dibujar rectángulo y círculo
                    cv2.rectangle(img_contour, (x, y), (x + w, y + h), (0, 0, 0), 2)
                    cv2.circle(img_contour, object_center, 5, (0, 0, 0), cv2.FILLED)

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

    def get_velocities(self, oject_center: Optional[tuple[int, int]]):

        if oject_center is not None:

            cx, cy = oject_center
            error_x = self.panel_width / 2 -cx
            error_y = self.panel_height / 2 - cy

            derivative_x = error_x - self.prev_error_x
            derivative_y = error_y - self.prev_error_y
            self.prev_error_x = error_x
            self.prev_error_y = error_y

            velocity_x = (self.Kp_x * error_x) + (self.Ki_x * self.integral_x) + (self.Kd_x * derivative_x)
            velocity_y = (self.Kp_y * error_y) + (self.Ki_y * self.integral_y) + (self.Kd_y * derivative_y)

            velocity_x = int(np.clip(velocity_x, -self.max_velocity, self.max_velocity))
            velocity_y = int(np.clip(velocity_y, -self.max_velocity, self.max_velocity))

            if self.view_mode == "Front View" and self.detection_mode == "Color Contour":
                
                if self.detected_color == "color1":
                    self.left_right = velocity_x
                    self.yaw = 0

                elif self.detected_color == "color2":
                    self.left_right = 0
                    self.yaw = velocity_x

                else:
                    self.left_right = 0
                    self.yaw = 0

                self.for_back = 0
                self.up_down = 0

            else:
                self.left_right = velocity_x
                self.for_back = velocity_y
                self.up_down = 0
                self.yaw = 0

            if self.take_off_finalizado:
                self.integral_x += error_x
                self.integral_y += error_y
                self.set_velocity()

        else:
            self.left_right = 0
            self.for_back = 0
            self.up_down = 0
            self.integral_x = 0
            self.integral_y = 0
            self.set_velocity()


    def get_detected_frame(self, frame: Optional[np.ndarray]) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:

        frame_display: np.ndarray | None = cv2.resize(frame, (self.panel_width, self.panel_height))
        frame_hsv: np.ndarray | None = cv2.cvtColor(frame_display, cv2.COLOR_BGR2HSV)

        c1, c2 = self.colors["primary"]["range"], self.colors["secondary"]["range"]

        # -------- COLOR 1 --------
        lower1 = np.array(c1[0])
        upper1 = np.array(c1[1])
        mask1 = cv2.inRange(frame_hsv, lower1, upper1)

        # -------- COLOR 2 --------
        lower2 = np.array(c2[0])
        upper2 = np.array(c2[1])
        mask2 = cv2.inRange(frame_hsv, lower2, upper2)

        kernel = np.ones((5, 5), np.uint8)
        mask1 = cv2.dilate(mask1, kernel, iterations=1)
        mask2 = cv2.dilate(mask2, kernel, iterations=1)

        # -------- SELECCIÓN DEL COLOR DOMINANTE --------
        def max_area(mask):
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return 0
            return max(cv2.contourArea(c) for c in contours)

        area1 = max_area(mask1)
        area2 = max_area(mask2)

        name: str = "None"

        if area1 > 100 and area1 >= area2:
            mask = mask1
            self.detected_color = "color1"
            name = self.colors["primary"]["name"]
        elif area2 > 100:
            mask = mask2
            self.detected_color = "color2"
            name = self.colors["secondary"]["name"]
        else:
            mask = np.zeros_like(mask1)
            self.detected_color = None

        # -------- PIPELINE ORIGINAL --------
        result = cv2.bitwise_and(frame_display, frame_display, mask=mask)

        img_blur = cv2.GaussianBlur(result, (7, 7), 1)
        img_grey = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_grey, self.t1, self.t2)
        img_dilated = cv2.dilate(img_canny, kernel, iterations=1)

        img_contour: np.ndarray | None = frame_display.copy()

        object_center, img_contour = self.get_object_center(img_dilated, img_contour)

        # DEBUG VISUAL (opcional pero útil)
        cv2.putText(img_contour,f"COLOR: {name}",(10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0) if self.detected_color == "color1" else (0, 0, 0), 2)

        self.get_velocities(object_center)

        return img_dilated, img_contour

    def get_frame(self) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:

        try:

            original_frame, detected_frame = self.cap_frame(self.type_camera_option)

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