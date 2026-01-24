import tkinter as tk
from PIL import Image, ImageTk
from djitellopy import Tello

def dame_accion (x,y):
    accion = 'nada'
    if x > 300 and x < 480 and y >12 and y < 89:
        accion = 'takeoff'
    if x > 21 and x < 115 and y > 232 and y < 310:
        accion = 'left'
    if x > 300 and x < 417 and y >422 and y < 496:
        accion = 'land'
    if x > 622 and x < 747 and y > 218 and y < 289:
        accion = 'right'
    if x > 508 and x < 750 and y > 422 and y < 484:
        accion = 'a volar'
    return accion

def mostrar_posicion(event):
    global flying
    global drone
    global practicando
    x, y = event.x, event.y
    accion = dame_accion(x, y)
    etiqueta_posicion.config(text=f'Posición del mouse: X={x}, Y={y}, accion = {accion}')

    if not practicando:
        if accion == 'takeoff' and not flying:
            drone.takeoff()
            flying = True
        elif accion == 'right' and flying:
            drone.move_right(20)
        elif accion == 'left' and flying:
            drone.move_left(20)
        elif accion == 'land' and flying:
            drone.land()
            flying = False
    elif accion == 'a volar':
        drone.connect()
        practicando = False




# Crear una ventana
ventana = tk.Tk()
flying = False
practicando = True
drone = Tello ()

ventana.title("Posición del Mouse")
ventana.geometry("800x650")
etiqueta_posicion = tk.Label(ventana, text="Posición del mouse: X=0, Y=0")
etiqueta_posicion.pack(padx=10, pady=10)
image = Image.open("assets/eyetrack.png")
image = image.resize((770, 525), Image.ANTIALIAS)

bg = ImageTk.PhotoImage(image)
canvas1 = tk.Canvas(ventana, width=770, height=525)
canvas1.pack(fill="both", expand=True)
canvas1.create_image(0, 0, image=bg, anchor="nw")
# Crear una etiqueta para mostrar la posición del mouse


# Configurar el evento de movimiento del mouse
canvas1.bind("<Motion>", mostrar_posicion)

# Ejecutar el bucle principal de la aplicación
ventana.mainloop()
