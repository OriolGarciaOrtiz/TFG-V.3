import threading
import asyncio
import time
import cv2
from HexsoonGUI import GUI
from VideoRTC import DroneVideoTrack, WebRTCServer

class DroneLauncher:
    def __init__(self):
        self.video_track_original = DroneVideoTrack("original")
        self.video_track_detected = DroneVideoTrack("detected")
        self.gui = GUI()

        self.webrtc = WebRTCServer(self.video_track_original, self.video_track_detected)

        threading.Thread(
            target=lambda: asyncio.run(self.webrtc.run()),
            daemon=True
        ).start()

    def main(self):
        while True:
            self.gui.update_frame()

            # Actualiza los frames aunque no estés conectado aún
            if self.gui.frame_display is not None:
                self.video_track_original.frame = self.gui.frame_display.copy()
            if self.gui.img_contour is not None:
                self.video_track_detected.frame = self.gui.img_contour.copy()

            # Mantener la cámara seleccionada en el WebRTC
            self.webrtc.camera_option = self.gui.controller.type_camera_option

            time.sleep(0.03)



if __name__ == "__main__":
    DroneLauncher().main()
