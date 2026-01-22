import paho.mqtt.client as mqtt
import json
import time
from HexsoonGUI import GUI

class MQTT:

    def __init__(self, target_gui: GUI):

        self.target_gui = target_gui

        self.BROKER = "broker.hivemq.com"
        self.PORT = 1883
        self.TOPIC_SUB = "test/chat/tierra2dron"
        self.TOPIC_PUB = "test/chat/dron2tierra"

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.BROKER, self.PORT, 60)
        self.client.loop_start()

        self.clock_start = time.monotonic()
        self.send_interval = 0.05

        self.connect_click = False 
        self.disconnect_mode = False 

        self.running: bool = False


    def on_connect(self, client, userdata, flags, rc):
        print("Connected to broker with code", rc)
        client.subscribe(self.TOPIC_SUB)


    def on_message(self, client, userdata, msg):
        text = msg.payload.decode()
        try:
            self.set_data(text)
        except Exception as e:
            print("Invalid MQTT message:", e)


    def _to_bool(self, val):
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return val != 0
        return str(val).strip().lower() in ["true", "1", "yes", "on"]


    def set_data(self, msg: str):
        data: dict = json.loads(msg)

        # HSV
        self.target_gui.controller.colors = data.get("colors", self.target_gui.controller.colors)

        self.target_gui.controller.detection_mode = data.get("detection_mode", self.target_gui.controller.detection_mode)
        self.target_gui.controller.view_mode = data.get("view_mode", self.target_gui.controller.view_mode)
        self.target_gui.controller.type_camera_option = data.get("camera_option", self.target_gui.controller.type_camera_option)

        # PID
        self.target_gui.controller.Kp_x = float(data.get("Kp_x", self.target_gui.controller.Kp_x))
        self.target_gui.controller.Ki_x = float(data.get("Ki_x", self.target_gui.controller.Ki_x))
        self.target_gui.controller.Kd_x = float(data.get("Kd_x", self.target_gui.controller.Kd_x))
        self.target_gui.controller.Kp_y = float(data.get("Kp_y", self.target_gui.controller.Kp_y))
        self.target_gui.controller.Ki_y = float(data.get("Ki_y", self.target_gui.controller.Ki_y))
        self.target_gui.controller.Kd_y = float(data.get("Kd_y", self.target_gui.controller.Kd_y))

        # Velocity
        self.target_gui.controller.max_velocity = int(data.get("max_velocity", self.target_gui.controller.max_velocity))

        self.target_gui.controller.click_connect = self._to_bool(data.get("connect_click", False))
        self.target_gui.controller.click_disconnect = self._to_bool(data.get("disconnect_click", False))

        self.target_gui.controller.zoom_factor = float(data.get("zoom_factor", self.target_gui.controller.zoom_factor))

        self.target_gui.controller.yolo_model_name = data.get("yolo_model_name", self.target_gui.controller.yolo_model_name)
        
        self.target_gui.controller.do_actions()


    def prepare_data(self):

        data = {
            "left_right": self.target_gui.controller.left_right,
            "for_back": self.target_gui.controller.for_back,
            "up_down": self.target_gui.controller.up_down,
            "yaw": self.target_gui.controller.yaw,
            "is_connected": self.target_gui.controller.is_connected,
            "detected_color": self.target_gui.controller.detected_color
        }

        self.send_data(data)


    def send_data(self, data: dict):
        self.client.publish(self.TOPIC_PUB, json.dumps(data))


    def run_loop(self):

        while self.running:
            if self.target_gui.controller.type_camera_option == "Raspi Cam":
                self.prepare_data()
            time.sleep(self.send_interval)