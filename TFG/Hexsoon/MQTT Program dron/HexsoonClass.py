from ultralytics import YOLO
import cv2
import numpy as np
import yaml

class HexsoonController:
    def __init__(self):
        
        self.is_connected = False
        self.is_deteceted = False
        self.is_armed = False
        self.cap = None

        self.color_opt: str | None = None
        
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

        self.integral_x = 0
        self.integral_y = 0

        self.prev_error_x = 0
        self.prev_error_y = 0

        self.left_right = 0
        self.for_back = 0
        self.up_down = 0
        self.yaw = 0


        try:
            self.model = YOLO("Yolo Models/best_RC_Final.pt")
            print("YOLO model loaded successfully.")
        except Exception as e:
            print("Could not load YOLO model:", e)
            self.model = None

        yamlname: str = 'calibration_data_px.yaml'
        self.data: dict | None = None
        with open(yamlname) as f:
            self.data = yaml.safe_load(f)

        self.yolo_result: tuple[tuple[int, int] | None, list] = (None, [])

        self.cam = 0


    def init_camera(self, resolution=(320, 240)):
        try:

            if self.cap is None:

                if self.cam == 0:

                    self.cap = cv2.VideoCapture(0)

                if self.cam == 1:

                    from picamera2 import Picamera2

                    self.cap = Picamera2()
                    config = self.cap.create_video_configuration(
                        main={"size": resolution, "format": "RGB888"}
                    )
                    self.cap.configure(config)
                    self.cap.start()
                
            print("Picamera2 initialized.")

        except Exception as e:
            print("Failed to initialize Picamera2:", e)
            self.cap = None

    def get_frame(self):

        if self.cap is None:

            return None
        
        try:

            if self.cam == 0:

                ret, frame = self.cap.read()

                if not ret and not self.cap.isOpened():
                    return None
                
                frame = cv2.resize(frame, (320, 240))

            if self.cam == 1:
                
                frame = self.cap.capture_array()
            
            return frame
        
        except:

            return None


    def connect_drone(self):

        try:
            
            self.is_connected = True
            
            print("Drone succesfully connetcted")

            if self.cap is None:
                raise Exception("Camera not initialized")
                
        except:
            
            self.is_connected = False


    def disconnect_drone(self): 
        if self.is_connected: 
            self.is_connected =  False 


    def do_actions(self, connect_click: bool, disconnect_click: bool):

        if connect_click:
            
            self.connect_drone()

        if disconnect_click:
            self.disconnect_drone()


    def get_contour(self, frame):

        frame_display = cv2.resize(frame, (self.panel_width, self.panel_height))
        frame_hsv = cv2.cvtColor(frame_display, cv2.COLOR_BGR2HSV)

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

        original_frame: np.ndarray | None = frame_display.copy()

        object_center, img_contour = self.get_object_center(img_dilated, original_frame)

        # DEBUG VISUAL (opcional pero útil)
        cv2.putText(img_contour,f"COLOR: {name}",(10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0) if self.detected_color == "color1" else (0, 0, 0), 2)

        self.get_velocities(object_center)

        return img_dilated, img_contour
    
    def get_velocities(self, oject_center):

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

            if self.view_mode == "Front View":
                
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

            self.integral_x += error_x
            self.integral_y += error_y

        else:

            self.left_right = 0
            self.for_back = 0
            self.up_down = 0
            self.integral_x = 0
            self.integral_y = 0


    def get_object_center(self, dil_frame, original_frame):

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

                    cv2.rectangle(original_frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
                    cv2.circle(original_frame, object_center, 5, (0, 0, 0), cv2.FILLED)

                    return object_center, original_frame

            return None, original_frame

        # -------------------- NEURAL NETWORK MODE --------------------
        elif self.detection_mode == "Neural Network" and self.model is not None:

            object_center, boxes_info = self.yolo_result

            if boxes_info:
                for (x1, y1, x2, y2, label, conf) in boxes_info:
                    cv2.rectangle(
                        original_frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                    )
                    cv2.putText(
                        original_frame,
                        f"{label} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        2
                    )

                if object_center is not None:
                    cv2.circle(original_frame, object_center, 5, (255, 0, 0), cv2.FILLED)

            return object_center, original_frame

        # -------------------- NO MODE SELECTED --------------------
        else:
            cv2.putText(
                original_frame,
                "No detection mode/model selected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )
            return None, original_frame


    def get_detected_frame(self, frame):

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

        original_frame: np.ndarray | None = frame_display.copy()

        object_center, img_contour = self.get_object_center(img_dilated, original_frame)

        # DEBUG VISUAL (opcional pero útil)
        cv2.putText(img_contour,f"COLOR: {name}",(10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0) if self.detected_color == "color1" else (0, 0, 0), 2)

        self.get_velocities(object_center)

        return img_dilated, img_contour
    

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
