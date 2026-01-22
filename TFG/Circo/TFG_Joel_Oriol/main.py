from .TelloGUI import GUI
import tkinter as tk
from typing import Optional

def main_code(mode: str, main_root: Optional[tk.Tk] = None):

    try:

        if main_root is not None: 

            root = tk.Toplevel(main_root)

        else:

            root = tk.Tk()

        root.title("Tello Drone")

        root.state('zoomed')

        tello_gui = GUI(root, mode)

        tello_gui.update_frame()

        def on_closing():
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        if main_root is None:
            root.mainloop()

    except Exception as e:
        print("Error", f"Failed to open Tello controller:\n{str(e)}")


if __name__ == "__main__":

    #  Modos para el circo, así no hace falta separar el codigo
    #  "Color Contour", "Neural Network", "Game Mode", "Color Game Mode"

    mode = "Color Game Mode"

    main_code(mode)




