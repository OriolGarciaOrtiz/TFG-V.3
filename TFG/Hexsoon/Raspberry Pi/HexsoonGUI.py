from HexsoonClass import *


class GUI:
    def __init__(self):
        self.controller = HexsoonController()
        self.controller.init_camera()
        self.panel_width = self.controller.panel_width
        self.panel_height = self.controller.panel_height

        self.frame_display = None
        self.img_contour = None

        self.running = True

        self.FPS = 30


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

            self.frame_display = img_dilated
            self.img_contour = img_contour

        except Exception as e:
            print(f"Error in update_frame: {e}")
