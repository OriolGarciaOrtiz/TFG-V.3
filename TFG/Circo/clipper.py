
import time
from datetime import datetime
import cv2
import numpy as np


from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import Scale, Button

import glob
import os
class clipper:
    def agregar_marco_rojo(self):
        alto, ancho = self.img.shape[:2]

        # Define el color rojo en formato BGR (azul, verde, rojo)
        color_rojo = (0, 0, 255)
        top= self.grosor_borde_superior
        botton= self.grosor_borde_inferior
        left = self.grosor_borde_izquierdo
        right = self.grosor_borde_derecho

        for j in range(top):
            for i in range(ancho):
                self.img[j, i] = color_rojo
        for j in range(alto - botton, alto):
            for i in range(ancho):
                self.img[j, i] = color_rojo
        for j in range(alto):
            for i in range(left):
                self.img[j, i] = color_rojo
        for j in range(alto):
            for i in range(ancho - right, ancho):
                self.img[j, i] = color_rojo
            # Naming a window


    def actualizar_borde_superior(self,valor):

        self.grosor_borde_superior = int (valor)
        self.agregar_marco_rojo()
        cv2.imshow("Resized_Window", self.img)

    def actualizar_borde_inferior(self,valor):
        self.grosor_borde_inferior = int(valor)
        self.agregar_marco_rojo()
        cv2.imshow("Resized_Window", self.img)

    def actualizar_borde_izquierdo(self,valor):
        self.grosor_borde_izquierdo= int(valor)
        self.agregar_marco_rojo()
        cv2.imshow("Resized_Window", self.img)

    def actualizar_borde_derecho(self,valor):
        self.grosor_borde_derecho= int(valor)
        self.agregar_marco_rojo()
        cv2.imshow("Resized_Window", self.img)


    def cortar (self):

        marco = 50
        alto, ancho = self.img.shape[:2]
        print ('alto, ancho ', alto,ancho)

        a = self.grosor_borde_superior - marco
        b = alto - self.grosor_borde_inferior + marco
        c = self.grosor_borde_izquierdo -marco
        d = ancho - self.grosor_borde_derecho + marco
        print ('a,b,c,d ', a,b,c,d)


        self.crop_img = self.img[a:b, c:d]
        font = cv2.FONT_HERSHEY_SIMPLEX

        fecha_actual = datetime.now()
        formato_espanol = "%d/%m/%Y"
        fecha_formateada = fecha_actual.strftime(formato_espanol)
        frase = 'Gracias por su visita al campus de la UPC en Castelldefels ('+ fecha_formateada+')'
        frase = self.textoRecordatorio.get() + ' ('+ fecha_formateada+')'
        #frase = 'Gracias por su visita ('+ fecha_formateada+')'
        textSize = cv2.getTextSize( frase, fontFace=font, fontScale=1, thickness=2)
        print ('text size ', textSize)
        pos = (d - c - textSize [0][0])//2
        print ('pos ', pos)
        cv2.putText(self.crop_img, frase, (pos, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


        cv2.namedWindow("cropped", cv2.WINDOW_NORMAL)

        # Using resizeWindow()
        cv2.resizeWindow("cropped", d // 4, b// 4)
        cv2.imshow("cropped", self.crop_img)
        self.cortarButton['bg'] = 'green'

    def descargar (self):
        cv2.imwrite('pano/res.jpg',  self.crop_img)
        cv2.destroyAllWindows()
        self.descargarButton['bg'] = 'green'

    def reiniciar (self):
        cv2.destroyAllWindows()
        self.descargarButton['bg'] = 'red'
        self.cortarButton['bg'] = 'red'

        self.img = cv2.imread('pano/result.jpg')

        self.grosor_borde_superior = 50
        self.grosor_borde_inferior = 50
        self.grosor_borde_izquierdo = 50
        self.grosor_borde_derecho = 50
        self.grosor_top_slider.set(50)
        self.grosor_bottom_slider.set(50)
        self.grosor_left_slider.set(50)
        self.grosor_right_slider.set(50)


        alto, ancho = self.img.shape[:2]
        cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)
        self.agregar_marco_rojo()

        # Using resizeWindow()
        cv2.resizeWindow("Resized_Window", ancho // 4, alto // 4)

        # Displaying the image
        cv2.imshow("Resized_Window", self.img)
        cv2.imshow("Resized_Window", self.img)

    def cerrar (self):
        cv2.destroyAllWindows()
        self.ventana.destroy()
        self.callback ()

    def Open (self, callback):
        self.callback = callback
        self.ventana = tk.Tk()
        self.ventana.title("Agregar Borde Rojo")
        self.ventana.rowconfigure(0, weight=1)
        self.ventana.rowconfigure(1, weight=1)
        self.ventana.rowconfigure(2, weight=1)
        self.ventana.rowconfigure(3, weight=1)
        self.ventana.rowconfigure(4, weight=1)
        self.ventana.rowconfigure(5, weight=1)
        self.ventana.rowconfigure(6, weight=1)



        self.ventana.columnconfigure(0, weight=1)
        self.ventana.columnconfigure(1, weight=1)
        self.ventana.columnconfigure(2, weight=1)
        self.ventana.columnconfigure(3, weight=1)



        self.grosor_top_slider = Scale(self.ventana, from_=50, to=500, orient=tk.HORIZONTAL, label="Borde superior", length=300,
                              command=self.actualizar_borde_superior)
        self.grosor_top_slider.set(50)
        self.grosor_top_slider.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)

        self.grosor_bottom_slider = Scale(self.ventana, from_=50, to=500, orient=tk.HORIZONTAL, label="Borde inferior", length=300,
                              command=self.actualizar_borde_inferior)
        self.grosor_bottom_slider.set(50)
        self.grosor_bottom_slider.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)

        self.grosor_left_slider = Scale(self.ventana, from_=50, to=500, orient=tk.HORIZONTAL, label="Borde izquierdo", length=300,
                              command=self.actualizar_borde_izquierdo)
        self.grosor_left_slider.set(50)
        self.grosor_left_slider.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)

        self.grosor_right_slider = Scale(self.ventana, from_=50, to=500, orient=tk.HORIZONTAL, label="Borde derecho", length=300,
                              command=self.actualizar_borde_derecho)
        self.grosor_right_slider.set(50)
        self.grosor_right_slider.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)

        self.textoRecordatorioLbl = Label (self.ventana, text= 'Texto para la frase de recuerdo')
        self.textoRecordatorioLbl.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + W)

        self.textoRecordatorio = Entry (self.ventana)

        self.textoRecordatorio.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
        self.textoRecordatorio.insert (0, "Gracies per la vostra visita a la Fira del Coneixement")

        self.cortarButton = Button(self.ventana, text="Cortar", bg= 'red', fg = 'white', command=self.cortar)
        self.cortarButton.grid(row=6, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.descargarButton = Button(self.ventana, text="Descargar", bg= 'red', fg = 'white',command=self.descargar)
        self.descargarButton.grid(row=6, column=1, padx=5, pady=5, sticky=N + S + E + W)

        self.reiniciarButton = Button(self.ventana, text="Reiniciar", bg= 'red', fg = 'white',command=self.reiniciar)
        self.reiniciarButton.grid(row=6, column=2, padx=5, pady=5, sticky=N + S + E + W)

        self.cerrarButton = Button(self.ventana, text="Cerrar",bg= 'red', fg = 'white', command=self.cerrar)
        self.cerrarButton.grid(row=6, column=3, padx=5, pady=5, sticky=N + S + E + W)

        self.img = cv2.imread('pano/result.jpg')

        self.grosor_borde_superior = 50
        self.grosor_borde_inferior = 50
        self.grosor_borde_izquierdo = 50
        self.grosor_borde_derecho = 50

        self.agregar_marco_rojo()
        alto, ancho = self.img.shape[:2]
        cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)

        # Using resizeWindow()
        cv2.resizeWindow("Resized_Window", ancho//4, alto//4)

        # Displaying the image
        cv2.imshow("Resized_Window", self.img)
        self.ventana.mainloop()

