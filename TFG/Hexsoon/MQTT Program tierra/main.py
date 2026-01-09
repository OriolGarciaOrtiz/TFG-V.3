from HexsoonGUI import GUI as HexsoonGUI
import tkinter as tk
import threading
from ThreadHandler import HandlerThreads


def main():
    try:

        root = tk.Tk()

        root.title("Hexagon Drone")
        root.state('zoomed')

        hexsoon_gui = HexsoonGUI(root)

        thread_handler = HandlerThreads(hexsoon_gui)

        threading.Thread(target=thread_handler.start, daemon=True).start()
        
        hexsoon_gui.update_frame()

        def on_closing():
            hexsoon_gui.on_close()
            thread_handler.stop()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", f"Fallo al abrir controlador Hexagon:\n{str(e)}")


if __name__ == "__main__":
    main()
