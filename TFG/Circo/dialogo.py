
import tkinter as tk
from tkinter import simpledialog, messagebox

class MyDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title):
        self.selection = None
        self.opcion = tk.StringVar()
        self.opcion.set ("laptopCamera")
        super().__init__(parent, title)



    def body(self, frame):

        tk.Radiobutton(frame, text="Laptop camera", variable=self.opcion,
                    value="laptopCamera").pack()
        tk.Radiobutton(frame, text="Mobile phone camera", variable=self.opcion,
                    value= "mobileCamera").pack()


        return frame

    def ok_pressed(self):
        self.selection = self.opcion.get()
        self.destroy()

    def cancel_pressed(self):
        self.destroy()

    def buttonbox(self):
        self.ok_button = tk.Button(self, text="OK", width=5, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = tk.Button(
            self, text="Cancel", width=5, command=self.cancel_pressed
        )
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())

ventana = tk.Tk()



dialog = MyDialog(title="Credentials", parent=ventana)

print ("opcion elegida", dialog.selection)
ventana.mainloop()