import time
from tkinter import *
import tkinter as tk
from pygame import mixer
from tkinter import font
from PIL import Image, ImageTk

from djitellopy import Tello
from circoPoses import CircoPoses
from circoColores import CircoColores

def enterCircoPoses():
    global mixer
    mixer.music.stop()
    circoPoses = CircoPoses()
    circoPoses.Open(root)

def enterCircoColores():
    global mixer
    mixer.music.stop()
    circoColores = CircoColores()
    circoColores.Open(root)

mixer.init()
mixer.music.load('assets/circo.mp3')
mixer.music.play()


root = Tk()
root.geometry("770x525")

image = Image.open("assets/entrada.png")
image = image.resize((770, 525), Image.ANTIALIAS)

bg = ImageTk.PhotoImage(image)
canvas1 = Canvas(root, width=770, height=525)
canvas1.pack(fill="both", expand=True)
canvas1.create_image(0, 0, image=bg, anchor="nw")

myFont = font.Font(family='Arial', size=12, weight='bold')
drone = Tello()
configuracion_escenario = [0,0,0,0]

enterButton = Button(root, text="El circo de las poses", height=1, bg='#367E18', fg='#FFE9A0', width=20, command=enterCircoPoses)
enterButton['font'] = myFont
enterButton.place (x=500, y=470, anchor="nw")

enterButton = Button(root, text="El circo de los colores", height=1, bg='#367E18', fg='#FFE9A0', width=20, command=enterCircoColores)
enterButton['font'] = myFont
enterButton.place (x=50, y=470, anchor="nw")

root.mainloop()
