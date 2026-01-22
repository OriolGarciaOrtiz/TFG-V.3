from TelloGUI import *
import tkinter as tk
from tkinter import messagebox

def main(mode: str):
    try:

        root = tk.Tk()

        root.title("Tello Drone")

        root.state('zoomed')

        tello_gui = GUI(root, mode)

        tello_gui.update_frame()

        def on_closing():
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Tello controller:\n{str(e)}")


if __name__ == "__main__":

    #  Modos para el circo, así no hace falta separar el codigo
    #  "Color Contour", "Neural Network", "Game Mode", "Color Game Mode"

    mode = "Color Game Mode"

    main(mode)
