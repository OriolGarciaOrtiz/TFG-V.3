from dronLink.Dron import Dron
from ultralytics import YOLO
from pymavlink import mavutil
from dronLink.modules.dron_move import _prepare_command_mov
from picamera2 import Picamera2
import cv2

class HexsoonController:
    def __init__(self):
        self.is_connected = False
        self.dron = Dron()
        self.cap = None
        try:
            self.model = YOLO("Yolo Models/best_RC_Final.pt")
            print("YOLO model loaded successfully.")
        except Exception as e:
            print("Could not load YOLO model:", e)
            self.model = None

        self.integral_x = 0
        self.integral_y = 0

        self.prev_error_x = 0
        self.prev_error_y = 0

        self.left_right = 0
        self.for_back = 0
        self.up_down = 0
        self.yaw = 0


    def init_camera(self, resolution=(320, 240)):
        try:
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
            frame = self.cap.capture_array()
            return frame
        except:
            return None



    def connect_drone(self, mode: str):

        try:
            
            self.is_connected = True
            
            print("Drone succesfully connetcted")

            if self.cap is None:
                raise Exception("Camera not initialized")
                
        except:
            
            self.is_connected = False


    def disconnect_drone(self): 
        if self.is_connected:
            self.dron.disconnect()   


    def take_off_drone(self, alt = 3):
        if not self.is_connected:
            return
        
        try:
            alt = int(alt)
            if alt <= 0:
                raise ValueError("Altitude must be greater than 0")
            
            self.dron.takeOff(alt)
            
        except:
            pass


    def land_drone(self):
        if self.is_connected:
            self.dron.Land()


    def Return_To_Launch_drone(self):
        if self.is_connected:
            self.dron.RTL()


    def arm(self):
        if self.is_connected:
            self.dron.arm()


    def do_actions(self, connect_click: bool, try_mode: str, disconnect_mode: bool, takeoff_click: bool, take_off_alt, land_click: bool, rtl_click: bool, arm_click: bool):

        if connect_click:
            
            self.connect_drone(try_mode)

        if disconnect_mode:
            self.disconnect_drone()

        if takeoff_click:
            
            self.take_off_drone(take_off_alt)

        if land_click:
            self.land_drone()

        if rtl_click:
            self.Return_To_Launch_drone()

        if arm_click:
            self.arm()


    def set_velocity(self):

        try:

            vehicle: mavutil.mavfile = getattr(self.dron, "vehicle", None)

            if vehicle is None:
                return

            step_x = self.for_back / 100.0
            step_y = self.left_right / 100.0
            step_z = -self.up_down / 100.0

            msg = _prepare_command_mov(self.dron, step_x, step_y, step_z, bodyRef=True)
            print(msg)
            vehicle.mav.send(msg)

        except:
            return
        

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
