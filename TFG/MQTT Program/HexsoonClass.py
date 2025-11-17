from dronLink.Dron import Dron
from ultralytics import YOLO


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
