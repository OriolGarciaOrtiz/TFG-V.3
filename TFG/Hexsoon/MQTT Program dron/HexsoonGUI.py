from HexsoonClass import *

import numpy as np
import paho.mqtt.client as mqtt
import json
import json

class GUI:
    def __init__(self):
        self.controller = HexsoonController()
        self.controller.init_camera()
        self.panel_width = 320
        self.panel_height = 240

        # MQTT config
        self.BROKER = "broker.hivemq.com"
        self.PORT = 1883
        self.TOPIC_SUB = "test/chat/tierra2dron"
        self.TOPIC_PUB = "test/chat/dron2tierra"
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.BROKER, self.PORT, 60)
        self.client.loop_start()
        
        # Button states
        self.connect_click = False 
        self.disconnect_mode = False 

        self.frame_display = None
        self.img_contour = None

        self.running = True

    # MQTT -----------------------

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to broker with code", rc)
        client.subscribe(self.TOPIC_SUB)

    def on_message(self, client, userdata, msg):
        text = msg.payload.decode()
        try:
            self.set_data(text)
        except Exception as e:
            print("Invalid MQTT message:", e)


    # Convert values safely to bool
    def _to_bool(self, val):
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return val != 0
        return str(val).strip().lower() in ["true", "1", "yes", "on"]


    def set_data(self, msg: str):
        data: dict = json.loads(msg)

        # HSV
        self.controller.colors = data.get("colors", self.controller.colors)

        self.controller.detection_mode = data.get("detection_mode", self.controller.detection_mode)
        self.controller.view_mode = data.get("view_mode", self.controller.view_mode)
        self.controller.type_camera_option = data.get("camera_option", self.controller.type_camera_option)

        # PID
        self.controller.Kp_x = float(data.get("Kp_x", self.controller.Kp_x))
        self.controller.Ki_x = float(data.get("Ki_x", self.controller.Ki_x))
        self.controller.Kd_x = float(data.get("Kd_x", self.controller.Kd_x))
        self.controller.Kp_y = float(data.get("Kp_y", self.controller.Kp_y))
        self.controller.Ki_y = float(data.get("Ki_y", self.controller.Ki_y))
        self.controller.Kd_y = float(data.get("Kd_y", self.controller.Kd_y))

        # Velocity
        self.controller.max_velocity = int(data.get("max_velocity", self.controller.max_velocity))

        self.connect_click = self._to_bool(data.get("connect_click", False))
        self.disconnect_click = self._to_bool(data.get("disconnect_click", False))

        self.controller.zoom_factor = float(data.get("zoom_factor", self.controller.zoom_factor))
        
        self.controller.do_actions(
                self.connect_click, self.disconnect_click
            )


    def prepare_data(self):

        data = {
            "left_right": self.controller.left_right,
            "for_back": self.controller.for_back,
            "up_down": self.controller.up_down,
            "yaw": self.controller.yaw,
            "is_connected": self.controller.is_connected,
        }

        #print(data)

        self.send_data(data)

    def send_data(self, data: dict):
        self.client.publish(self.TOPIC_PUB, json.dumps(data))


    def update_frame(self):
        
        try:
                
            if not self.controller.is_connected:
                return

            if self.controller.cap is None:
                return

            frame = self.controller.get_frame()

            if frame is None:

                print("Could not read frame from PiCamera.")
                return
            
            frame = self.controller.zoom_frame(frame, self.controller.zoom_factor)

            img_dilated, img_contour = self.controller.get_detected_frame(frame)

            self.prepare_data()

            self.frame_display = img_dilated
            self.img_contour = img_contour

        except Exception as e:
            print(f"Error in update_frame: {e}")
