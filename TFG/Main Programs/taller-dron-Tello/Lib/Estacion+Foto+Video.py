from tkinter import *
from djitellopy import Tello
import cv2 as cv
from PIL import Image, ImageTk
import threading

tello = Tello()
mover = None
takingVideo = False

# Funciones generales
def EntrarClick():
    print('Has introducido la frase --- ' + fraseEntry.get() + ' --- y has pulsado el botón entrar')

def conectar_dron():
    tello.connect()
    print("Conectado. Batería:", tello.get_battery(), "%")
    batteryLabel['text'] = str(tello.get_battery()) + " %"
    tello.streamon()

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

def mover_arriba():
    detener_movimiento()
    mover_continuo(lambda: tello.move_up(20))

def mover_abajo():
    detener_movimiento()
    mover_continuo(lambda: tello.move_down(20))
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

# Funciones de video
def takeVideoStream():
    global takingVideo
    while takingVideo:
        telloFrame = tello.get_frame_read().frame
        telloFrame = cv.resize(telloFrame, (360, 240))
        frame_rgb = cv.cvtColor(telloFrame, cv.COLOR_BGR2RGB)
        cv.imshow("tello", frame_rgb)
        cv.waitKey(1)
    cv.destroyWindow('tello')

def takeVideoButtonClick():
    global takingVideo
    takingVideo = True
    x = threading.Thread(target=takeVideoStream)
    x.start()

def stopVideoButtonClick():
    global takingVideo
    takingVideo = False

def takePictureButtonClick():
    frame = tello.get_frame_read().frame
    image = Image.fromarray(frame)
    max_size = (400, 300)
    image.thumbnail(max_size)
    photo = ImageTk.PhotoImage(image)
    picturePanel.create_image(0, 0, anchor=NW, image=photo)
    picturePanel.image = photo  # Evitar garbage collection


# INTERFAZ GRÁFICA
window = Tk()
window.geometry("400x700")
window.title("Control de Dron")

# === Frame Display ===
topFrame = LabelFrame(window, text='Display')
topFrame.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
topFrame.rowconfigure([0, 1], weight=1)
topFrame.columnconfigure([0, 1, 2], weight=1)

Button(topFrame, text="A", bg='red', fg="white").grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
Button(topFrame, text="B", bg='yellow', fg="black").grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
Button(topFrame, text="C", bg='blue', fg="white").grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)

fraseEntry = Entry(topFrame)
fraseEntry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
Button(topFrame, text="Entrar", bg='red', fg="white", command=EntrarClick).grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)

# === Frame Volar ===
bottomFrame = LabelFrame(window, text='Volar')
bottomFrame.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
for i in range(4): bottomFrame.rowconfigure(i, weight=1)
for i in range(3): bottomFrame.columnconfigure(i, weight=1)

Button(bottomFrame, text="Conectar", bg='red', fg="white", command=conectar_dron).grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="Adelante", bg='yellow', fg="black", command=mover_adelante).grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="Take-off", bg='blue', fg="white", command=takeoff_dron).grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)

Button(bottomFrame, text="Izquierda", bg='orange', fg="black", command=mover_izquierda).grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="Stop", bg='red', fg="white", command=detener_movimiento).grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="Derecha", bg='yellow', fg="black", command=mover_derecha).grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)

Button(bottomFrame, text="Aterrizar", bg='blue', fg="white", command=aterrizar).grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="Atras", bg='orange', fg="black", command=mover_atras).grid(row=2, column=1, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="Arriba", bg='pink', fg="black",command=mover_arriba).grid(row=2, column=2, padx=5, pady=5, sticky=N + S + E + W)

# Nueva fila: botones 9, 10, 11
Button(bottomFrame, text="Abajo", bg='red', fg="white",command=mover_abajo).grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="10", bg='red', fg="white").grid(row=3, column=1, padx=5, pady=5, sticky=N + S + E + W)
Button(bottomFrame, text="11", bg='red', fg="white").grid(row=3, column=2, padx=5, pady=5, sticky=N + S + E + W)

# === Frame Video ===
videoFrame = LabelFrame(window, text="Video")
videoFrame.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
videoFrame.rowconfigure([0, 1, 2, 3], weight=1)
videoFrame.columnconfigure([0, 1], weight=1)

Button(videoFrame, text="Toma video con dron", bg='red', fg="white", command=takeVideoButtonClick).grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
Button(videoFrame, text="Stop video con dron", bg='red', fg="white", command=stopVideoButtonClick).grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

Button(videoFrame, text="Toma foto con dron", bg='red', fg="white", command=takePictureButtonClick).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

batteryLabel = Label(videoFrame, text="", font=("Courier", 14, "italic"))
batteryLabel.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

picturePanel = Canvas(videoFrame, bg="white")
picturePanel.grid(row=3, column=0, columnspan=2, sticky=N + S + E + W)

window.mainloop()
