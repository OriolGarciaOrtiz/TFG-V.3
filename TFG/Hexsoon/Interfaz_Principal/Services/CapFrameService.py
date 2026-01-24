from HexsoonGUI import GUI
import time
import cv2

class ServiceCapFrame:

    def __init__(self, target_gui: GUI) -> None:
        
        self.target_gui = target_gui

        self.running = False


    def start(self):
        while self.running:
            
            if self.target_gui.is_connected:
                
                self.target_gui.controller.original, self.target_gui.controller.img_contour = self.target_gui.controller.cap_frame(self.target_gui.controller.type_camera_option)
            
            time.sleep(1/self.target_gui.FPS)
