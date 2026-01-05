from HexsoonGUI import GUI as HexsoonGUI
import tkinter as tk
import threading
from Services.WebRTCService import DroneVideoReceiver
from Services.MissionPlannerService import MissionPlanner
from Services.MQTTService import MQTT
from Services.VideoService import ServiceVideo


def main():
    try:

        root = tk.Tk()

        root.title("Hexagon Drone")
        root.state('zoomed')

        hexsoon_gui = HexsoonGUI(root)

        receiver = DroneVideoReceiver(target_gui = hexsoon_gui)
        mission_planner = MissionPlanner(target_gui = hexsoon_gui)
        mqtt = MQTT(target_gui = hexsoon_gui)
        video = ServiceVideo(target_gui = hexsoon_gui)

        threading.Thread(target = receiver.start, daemon = True).start()
        threading.Thread(target = mission_planner._mission_loop, daemon = True).start()
        threading.Thread(target = mqtt.run_loop, daemon = True).start()
        threading.Thread(target = video.start, daemon= True).start()
        
        hexsoon_gui.update_frame()

        def on_closing():
            receiver.running = False
            mission_planner.running = False
            mission_planner.stop()
            hexsoon_gui.on_close()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", f"Fallo al abrir controlador Hexagon:\n{str(e)}")


if __name__ == "__main__":
    main()
