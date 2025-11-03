from tkinter import *
from djitellopy import Tello

tello = Tello()
mover = None  # Variable global para almacenar el job after()
def EntrarClick ():
    print ('Has introducido la frase --- ' + fraseEntry.get() + ' --- y has pulsado el botón entrar')

def conectar_dron():
    tello.connect()
    print("Conectado. Batería:", tello.get_battery(), "%")
def takeoff_dron():
    tello.takeoff()

def mover_adelante():
    detener_movimiento()
    mover_continuo(lambda: tello.move_forward(20))

def mover_izquierda():
    detener_movimiento()
    mover_continuo(lambda: tello.move_left(20))

def mover_atras():
    detener_movimiento()
    mover_continuo(lambda: tello.move_back(20))

def mover_derecha():
    detener_movimiento()
    mover_continuo(lambda: tello.move_right(20))

def mover_continuo(accion):
    global mover
    accion()
    mover = window.after(1000, lambda: mover_continuo(accion))

def detener_movimiento():
    global mover
    if mover is not None:
        window.after_cancel(mover)
        mover = None
        print("Movimiento detenido")

def aterrizar():
    detener_movimiento()
    tello.land()
    print("Aterrizando...")

window = Tk()
window.geometry("400x400")
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.columnconfigure(0, weight=1)

topFrame = LabelFrame (window, text ='Display')
topFrame.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
topFrame.rowconfigure(0, weight=1)
topFrame.rowconfigure(1, weight=1)
topFrame.columnconfigure(0, weight=1)
topFrame.columnconfigure(1, weight=1)
topFrame.columnconfigure(2, weight=1)

AButton = Button(topFrame, text="A", bg='red', fg="white")
AButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
BButton = Button(topFrame, text="B", bg='yellow', fg="black")
BButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
CButton = Button(topFrame, text="C", bg='blue', fg="white")
CButton.grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)

fraseEntry = Entry(topFrame)
fraseEntry.grid(row=1, column=0, columnspan = 2, padx=5, pady=5, sticky=N + S + E + W)

EntrarButton = Button(topFrame, text="Entrar", bg='red', fg="white",command=EntrarClick)
EntrarButton.grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)


bottomFrame = LabelFrame (window, text ='Volar')
bottomFrame.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

bottomFrame.rowconfigure(0, weight=1)
bottomFrame.rowconfigure(1, weight=1)
bottomFrame.rowconfigure(2, weight=1)
bottomFrame.columnconfigure(0, weight=1)
bottomFrame.columnconfigure(1, weight=1)
bottomFrame.columnconfigure(2, weight=1)

Button1 = Button(bottomFrame, text="Conectar", bg='red', fg="white", command=conectar_dron)
Button1.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

Button2 = Button(bottomFrame, text="Adelante", bg='yellow', fg="black", command=mover_adelante)
Button2.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

Button3 = Button(bottomFrame, text="Take-off", bg='blue', fg="white", command=takeoff_dron)
Button3.grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)

Button4 = Button(bottomFrame, text="Izquierda", bg='orange', fg="black", command=mover_izquierda)
Button4.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

Button5 = Button(bottomFrame, text="Stop", bg='red', fg="white", command=detener_movimiento)
Button5.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)

Button6 = Button(bottomFrame, text="Derecha", bg='yellow', fg="black", command=mover_derecha)
Button6.grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)

Button7 = Button(bottomFrame, text="Aterrizar", bg='blue', fg="white", command=aterrizar)
Button7.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)

Button8 = Button(bottomFrame, text="Atras", bg='orange', fg="black", command=mover_atras)
Button8.grid(row=2, column=1, padx=5, pady=5, sticky=N + S + E + W)

Button9 = Button(bottomFrame, text="9", bg='pink', fg="black")  # Sin uso
Button9.grid(row=2, column=2, padx=5, pady=5, sticky=N + S + E + W)


window.mainloop()