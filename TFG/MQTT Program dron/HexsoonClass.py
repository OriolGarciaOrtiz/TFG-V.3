from dronLink.Dron import Dron
from ultralytics import YOLO
from pymavlink import mavutil
from dronLink.modules.dron_move import _prepare_command_mov


class HexsoonController:
    def __init__(self):
        self.is_connected = False
        self.dron = Dron()
        self.cap = None  # Local camera (PC webcam)
        try:
            self.model = YOLO("best_RC_Final.pt")
            print("YOLO model loaded successfully.")
        except Exception as e:
            print("Could not load YOLO model:", e)
            self.model = None

        self.integral_x
        self.integral_y

        self.controller.prev_error_x
        self.controller.prev_error_y


    def connect_drone(self, mode: str):

        try:

            if mode == "Simulation":
                self.dron.connect('tcp:127.0.0.1:5763', 115200)

            elif mode == "Practice": 
                self.dron.connect('COM3', 57600)

            else: 
                raise ValueError("Unknown connection mode selected")
            
            self.is_connected = True

            if not self.cap.isOpened():
                raise Exception("Could not access local camera")
            
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


    def set_velocity(self, left_right, for_back, up_down, yaw=0):

        try:

            vehicle: mavutil.mavfile = getattr(self.dron, "vehicle", None)

            if vehicle is None:
                return

            step_x = for_back / 100.0
            step_y = left_right / 100.0
            step_z = -up_down / 100.0

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