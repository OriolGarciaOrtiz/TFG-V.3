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


        self.click_connect = False
        self.click_disconnect = False
        self.click_take_off = False
        self.click_land = False
        self.click_RTL = False
        self.click_arm = False

    # Hace falta volver a colocar todos los bottones a false después de cada iteración

    def connect_drone(self):

        self.click_connect = True


    def disconnect_drone(self): 
        
        if self.is_connected:
            
            self.click_disconnect = True   


    def take_off_drone(self):
        
        if self.is_connected:
            
            self.click_take_off = True


    def land_drone(self):
        
        if self.is_connected:
            
            self.click_land = True


    def Return_To_Launch_drone(self):
        
        if self.is_connected:
            
            self.click_RTL = False


    def arm(self):
        
        if self.is_connected:
            
            self.click_arm = True
