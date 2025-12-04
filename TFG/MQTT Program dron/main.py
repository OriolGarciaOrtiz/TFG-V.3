from HexsoonGUI import GUI as HexsoonGUI
import time

class DroneLauncher:
    def __init__(self):
        self.drone_gui = HexsoonGUI()
    
    def main(self):
        try:

            while True: 
                self.drone_gui.update_frame()
                time.sleep(0.01)

        except Exception as e:
            raise e



if __name__ == "__main__":

    launcher = DroneLauncher()

    launcher.main()
