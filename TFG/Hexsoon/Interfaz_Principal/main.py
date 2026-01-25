from HexsoonGUI import GUI as HexsoonGUI
import tkinter as tk
import threading
from ThreadHandler import HandlerThreads

def main():
    try:

        root = tk.Tk()

        root.title("Hexagon Drone")
        root.attributes('-fullscreen', True)

        hexsoon_gui = HexsoonGUI(root)

        thread_handler = HandlerThreads(hexsoon_gui)

        threading.Thread(target=thread_handler.start, daemon=True).start()

        def on_closing():
            root.after(0, cleanup_and_exit)
            root.withdraw()


        def cleanup_and_exit():

            thread_handler.stop()
            hexsoon_gui.on_close()
            hexsoon_gui.controller.disconnect_drone()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", f"Fallo al abrir controlador Hexagon:\n{str(e)}")


if __name__ == "__main__":
    main()
