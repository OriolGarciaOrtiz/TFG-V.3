from TelloGUI import *
from SimpleTelloGUI import *
from HexsoonGUI import GUI as HexsoonGUI
import tkinter as tk
from tkinter import Label, Button, Frame, messagebox
print("gay")

class DroneLauncher:
    def __init__(self, root):
        self.root = root
        self.setup_main_gui()
        self.active_windows = []

    def setup_main_gui(self):

        self.root.title("Drone Control Launcher")
        self.root.geometry("600x800")
        self.root.configure(bg='#f0f0f0')

        # Header
        header_frame = Frame(self.root, bg='#2c3e50', height=80)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        header_frame.grid_propagate(False)

        title_label = Label(header_frame, text="Drone Control System",
                            font=("Arial", 20, "bold"), fg='white', bg='#2c3e50')
        title_label.grid(row=0, column=0, sticky="nsew")
        header_frame.columnconfigure(0, weight=1)

        # Status section
        status_frame = Frame(self.root, bg='#f0f0f0')
        status_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=10)

        self.connected_label = Label(status_frame, text="Status: No Drone Selected",
                                     font=("Arial", 12), fg='red', bg='#f0f0f0')
        self.connected_label.grid(row=0, column=0)

        # Drone selection section
        selection_frame = Frame(self.root, bg='#f0f0f0')
        selection_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        select_label = Label(selection_frame, text="Select Drone Type:",
                             font=("Arial", 14, "bold"), bg='#f0f0f0')
        select_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        selection_frame.columnconfigure(0, weight=1)
        selection_frame.columnconfigure(1, weight=1)
        selection_frame.columnconfigure(2, weight=1)

        # Drone buttons
        tello_btn = Button(selection_frame, text="Tello Drone", command=self.open_tello_controller,
                           font=("Arial", 12, "bold"), bg='#3498db', fg='white',
                           width=20, height=3, relief='raised', bd=3)
        tello_btn.grid(row=1, column=1, pady=10)  # place in center column

        simple_tello_btn = Button(selection_frame, text="Simple Tello Drone", command=self.open_simple_tello_controller,
                                  font=("Arial", 12, "bold"), bg='#3498db', fg='white',
                                  width=20, height=3, relief='raised', bd=3)
        simple_tello_btn.grid(row=2, column=1, pady=10)  # center column

        hexagon_btn = Button(selection_frame, text="Hexagon Drone", command=self.open_hexsoon_controller,
                             font=("Arial", 12, "bold"), bg='#3498db', fg='white',
                             width=20, height=3, relief='raised', bd=3)
        hexagon_btn.grid(row=3, column=1, pady=10)  # center column

        # Footer
        footer_frame = Frame(self.root, bg='#34495e', height=40)
        footer_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        footer_frame.grid_propagate(False)

        self.window_count_label = Label(footer_frame, text="Active Windows: 0",
                                        font=("Arial", 10), fg='white', bg='#34495e')
        self.window_count_label.grid(row=0, column=0, sticky="w", padx=10)

        close_all_btn = Button(footer_frame, text="Close All Windows", command=self.close_all_windows,
                               font=("Arial", 8), bg='#e74c3c', fg='white')
        close_all_btn.grid(row=0, column=1, sticky="e", padx=10)

    def open_hexsoon_controller(self):
        try:
            secondary_window = tk.Toplevel(self.root)
            secondary_window.title("Tello Drone")

            secondary_window.state('zoomed')

            secondary_window.transient(self.root)
            secondary_window.grab_set()

            hexsoon_gui = HexsoonGUI(secondary_window)
            hexsoon_gui.update_frame()

            self.active_windows.append(secondary_window)
            self.update_window_count()
            self.connected_label.config(text="Status: Tello Controller Active", fg='green')

            def on_closing():
                self.active_windows.remove(secondary_window)
                self.update_window_count()
                if not self.active_windows:
                    self.connected_label.config(text="Status: No Drone Selected", fg='red')
                secondary_window.destroy()

            secondary_window.protocol("WM_DELETE_WINDOW", on_closing)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Tello controller:\n{str(e)}")

    def open_tello_controller(self):
        try:
            secondary_window = tk.Toplevel(self.root)
            secondary_window.title("Tello Drone")

            secondary_window.state('zoomed')

            secondary_window.transient(self.root)
            secondary_window.grab_set()

            tello_gui = GUI(secondary_window)
            tello_gui.update_frame()

            self.active_windows.append(secondary_window)
            self.update_window_count()
            self.connected_label.config(text="Status: Tello Controller Active", fg='green')

            def on_closing():
                self.active_windows.remove(secondary_window)
                self.update_window_count()
                if not self.active_windows:
                    self.connected_label.config(text="Status: No Drone Selected", fg='red')
                secondary_window.destroy()

            secondary_window.protocol("WM_DELETE_WINDOW", on_closing)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Tello controller:\n{str(e)}")

    def open_simple_tello_controller(self):
        try:
            secondary_window = tk.Toplevel(self.root)
            secondary_window.title("Simple Tello Drone")

            secondary_window.state('zoomed')

            secondary_window.transient(self.root)
            secondary_window.grab_set()

            simple_tello_gui = SimpleTelloGUI(secondary_window)
            simple_tello_gui.update_frame()

            self.active_windows.append(secondary_window)
            self.update_window_count()
            self.connected_label.config(text="Status: Tello Controller Active", fg='green')

            def on_closing():
                self.active_windows.remove(secondary_window)
                self.update_window_count()
                if not self.active_windows:
                    self.connected_label.config(text="Status: No Drone Selected", fg='red')
                secondary_window.destroy()

            secondary_window.protocol("WM_DELETE_WINDOW", on_closing)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Tello controller:\n{str(e)}")

    def hexagon_placeholder(self):
        messagebox.showinfo("Coming Soon",
                            "Hexagon drone controller is under development.\n"
                            "This feature will be available in a future update.")

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def update_window_count(self):
        count = len(self.active_windows)
        self.window_count_label.config(text=f"Active Windows: {count}")

    def close_all_windows(self):
        for window in self.active_windows[:]:
            try:
                window.destroy()
            except:
                pass
        self.active_windows.clear()
        self.update_window_count()
        self.connected_label.config(text="Status: No Drone Selected", fg='red')


def main():
    try:
        root = tk.Tk()
        app = DroneLauncher(root)

        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (600 // 2)
        y = (root.winfo_screenheight() // 2) - (400 // 2)
        root.geometry(f'600x600+{x}+{y}')

        def on_closing():
            if app.active_windows:
                if messagebox.askokcancel("Quit", "Close all drone controllers and quit?"):
                    app.close_all_windows()
                    root.destroy()
            else:
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application:\n{str(e)}")


if __name__ == "__main__":
    main()
