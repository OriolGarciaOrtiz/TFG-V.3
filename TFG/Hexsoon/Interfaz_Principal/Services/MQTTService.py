import paho.mqtt.client as mqtt
import json
import time
from HexsoonGUI import GUI

class MQTT:

    def __init__(self, target_gui: GUI):

        self.target_gui = target_gui

        self.BROKER = "broker.hivemq.com"
        self.PORT = 1883
        self.TOPIC_SUB = "test/chat/dron2tierra"
        self.TOPIC_PUB = "test/chat/tierra2dron"

        self.client = mqtt.Client()
        self.client.on_message = self.on_message

        self.client.connect(self.BROKER, self.PORT, 60)
        self.client.subscribe(self.TOPIC_SUB)
        self.client.loop_start()

        self.clock_start = time.monotonic()
        self.send_interval = 0.5

        self.running: bool = False


    def on_message(self, client, userdata, msg):
        if self.target_gui.controller.type_camera_option == "Raspi Cam":
            text = msg.payload.decode('utf-8')
            self.set_data(text)
            pass

    def set_data(self, msg: str):
        try:
            data: dict = json.loads(msg)

            self.target_gui.controller.left_right = float(data.get("left_right", self.target_gui.controller.left_right))
            self.target_gui.controller.for_back = float(data.get("for_back", self.target_gui.controller.for_back))
            self.target_gui.controller.up_down = float(data.get("up_down", self.target_gui.controller.up_down))
            self.target_gui.controller.yaw = float(data.get("yaw", self.target_gui.controller.yaw))
            self.target_gui.controller.is_connected = data.get("is_connected", self.target_gui.controller.is_connected)
            self.target_gui.controller.detected_color = data.get("detected_color", self.target_gui.controller.detected_color)

            self.target_gui.controller.set_velocity()
        except:
            pass

    def prepare_all_data(self) -> str:
        """Prepare COMPLETE data package with ALL parameters"""
        msg_dict = {

            # HSV values
            'colors': self.target_gui.controller.colors,

            # Detection and modes
            'detection_mode': self.target_gui.detection_selection.get(),
            'view_mode': self.target_gui.view_selection.get(),
            'camera_option': self.target_gui.type_camera_option.get(),

            # PID values
            'Kp_x': self.target_gui.Kp_x.get(),
            'Ki_x': self.target_gui.Ki_x.get(),
            'Kd_x': self.target_gui.Kd_x.get(),
            'Kp_y': self.target_gui.Kp_y.get(),
            'Ki_y': self.target_gui.Ki_y.get(),
            'Kd_y': self.target_gui.Kd_y.get(),

            # Other settings
            'max_velocity': self.target_gui.max_velocity.get(),

            # Click states 
            'connect_click': self.target_gui.controller.click_connect,
            'disconnect_click': self.target_gui.controller.click_disconnect,

            'zoom_factor' : self.target_gui.controller.zoom_factor,

            'yolo_model_name' : self.target_gui.controller.yolo_model_name
        }

        return json.dumps(msg_dict)

    def send_data(self):

        now = time.monotonic()

        if now - self.clock_start >= self.send_interval:
            try:
                msg = self.prepare_all_data()

                self.client.publish(self.TOPIC_PUB, msg)

                self.target_gui.controller.click_connect = False
                self.target_gui.controller.click_disconnect = False

                self.clock_start = now
            except:
                pass

    def run_loop(self):

        while self.running:
            if self.target_gui.type_camera_option.get() == "Raspi Cam":
                self.send_data()
            time.sleep(0.5)