import time
from HexsoonGUI import GUI
from ThreadHandler import HandlerThreads
import threading

class DroneLauncher:
    def __init__(self):

        self.gui = GUI()
        self.thread_handler = HandlerThreads(self.gui)

        threading.Thread(target=self.thread_handler.start, daemon=True).start()


    def main(self):

        while True:
            
            self.gui.update_frame()

            time.sleep(0.1/self.gui.FPS)


if __name__ == "__main__":
    DroneLauncher().main()
