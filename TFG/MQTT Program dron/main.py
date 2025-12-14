import threading
import asyncio
import time

from HexsoonGUI import GUI
from VideoRTC import DroneVideoTrack, WebRTCServer

class DroneLauncher:
    def __init__(self):
        self.video_track_original = DroneVideoTrack()
        self.video_track_detected = DroneVideoTrack()
        self.gui = GUI()

        self.webrtc = WebRTCServer(self.video_track_original, self.video_track_detected)

        threading.Thread(
            target=lambda: asyncio.run(self.webrtc.run()),
            daemon=True
        ).start()

    def main(self):
        while True:
            self.gui.update_frame()

            if self.gui.frame_display is not None:
                self.video_track_original.frame = self.gui.frame_display
                self.video_track_detected.frame = self.gui.img_contour

                self.video_track_original.is_connected = self.gui.controller.is_connected
                self.video_track_detected.is_connected = self.gui.controller.is_connected

            time.sleep(0.01)


if __name__ == "__main__":
    DroneLauncher().main()
