import time
from tkinter import *
import tkinter as tk
from pygame import mixer
from tkinter import font
from PIL import Image, ImageTk

from djitellopy import Tello
from circoPoses import CircoPoses
from circoColores import CircoColores
from circoImagenes import CircoImagenes
import paho.mqtt.client as mqtt
import ssl

def enterCircoPoses():
    global mixer
    mixer.music.stop()
    circoPoses = CircoPoses()
    circoPoses.Open(root)

def enterCircoImagenes():
    global mixer, client
    mixer.music.stop()
    circoImagenes = CircoImagenes()
    circoImagenes.Open(root)

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
image = image.resize((770, 525))

bg = ImageTk.PhotoImage(image)
canvas1 = Canvas(root, width=770, height=525)
canvas1.pack(fill="both", expand=True)
canvas1.create_image(0, 0, image=bg, anchor="nw")

myFont = font.Font(family='Arial', size=12, weight='bold')
drone = Tello()
configuracion_escenario = [0,0,0,0]

enterButton = Button(root, text="El circo de las poses", height=1, bg='#367E18', fg='#FFE9A0', width=20, command=enterCircoPoses)




enterButton['font'] = myFont
enterButton.place(x=500, y=470, anchor="nw")

enterButton = Button(root, text="El circo de las imágenes", height=1, bg='#367E18', fg='#FFE9A0', width=20, command=enterCircoImagenes)
enterButton['font'] = myFont
enterButton.place(x=275, y=470, anchor="nw")

enterButton = Button(root, text="El circo de los colores", height=1, bg='#367E18', fg='#FFE9A0', width=20, command=enterCircoColores)
enterButton['font'] = myFont
enterButton.place(x=50, y=470, anchor="nw")

# MQTT conexión
'''print("aaaa")
global_broker_address = "broker.hivemq.com"
global_broker_port = 8000  # 8883

client = mqtt.Client("VideoService", transport="websockets")
client.username_pw_set("dronsEETAC", "mimara1456.")
client.tls_set(
    ca_certs=None,
    certfile=None,
    keyfile=None,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS,
    ciphers=None,
)
# client.connect("classpip.upc.edu", 8883)
client.connect("dronseetac.upc.edu", 8883)
#client.connect(global_broker_address, global_broker_port)
client.loop_start()'''


root.mainloop()
