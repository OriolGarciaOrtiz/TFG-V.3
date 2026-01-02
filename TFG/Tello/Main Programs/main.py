from TelloGUI import *
import tkinter as tk
from tkinter import messagebox
from Services.YoloService import ServiceYOLO

def main():
    try:

        root = tk.Tk()

        root.title("Tello Drone")

        root.state('zoomed')

        #  Modos para el circo, así no hace falta separar el codigo
        #  "Color Contour", "Neural Network", "Game Mode", "Color Game Mode"

        mode = "Color Contour"

        tello_gui = GUI(root, mode)

        yolo = ServiceYOLO(tello_gui)

        threading.Thread(target=yolo.start, daemon=True).start()

        tello_gui.update_frame()

        def on_closing():
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Tello controller:\n{str(e)}")


if __name__ == "__main__":
    main()
