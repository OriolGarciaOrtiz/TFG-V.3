from HexsoonGUI import GUI as HexsoonGUI
import time
import asyncio
import threading 

class DroneLauncher:
    def __init__(self):    
                    
        # Thread para WebRTC
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        self.drone_gui = HexsoonGUI(self.loop)
        
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def main(self):
        try:
            while True:
                
                self.drone_gui.update_frame()

                time.sleep(0.01)

        except Exception as e:
            raise e
          
          
if __name__ == "__main__":

    dron = DroneLauncher()
    dron.main()

