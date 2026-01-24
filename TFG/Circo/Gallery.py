import base64
from tkinter import *
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
from tkinter import messagebox
from djitellopy import Tello
import time
import cv2
import os
import paho.mqtt.client as mqtt
import threading


class GalleryMedia():

    def Open(self, master, typeImage, client):
        self.drone = Tello()
        self.client = client

        myFont3 = font.Font(family='Arial', size=10, weight='bold')

        self.windowGallery = Toplevel(master)
        self.selected_image = None
        self.v_media = []
        self.canvas_list = []
        self.number_img = 0
        self.typeImage = typeImage

        self.windowGallery.geometry("1200x400")
        self.windowGallery.rowconfigure(0, weight=1)
        self.windowGallery.rowconfigure(1, weight=1)
        self.windowGallery.rowconfigure(2, weight=1)
        self.windowGallery.columnconfigure(0, weight=1)
        self.windowGallery.columnconfigure(1, weight=1)

        self.titlelabel = tk.Label(self.windowGallery, text=self.typeImage + " Gallery", height=2)
        self.titlelabel.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)
        self.titlelabel['font'] = myFont3

        self.galleryFrame =tk.LabelFrame (self.windowGallery, text = self.typeImage+'s')
        self.galleryFrame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.galleryFrame.rowconfigure(0, weight=1)
        self.galleryFrame.rowconfigure(1, weight=1)
        self.galleryFrame.columnconfigure(0, weight=1)
        self.galleryFrame.columnconfigure(1, weight=1)
        self.galleryFrame.columnconfigure(2, weight=1)
        self.galleryFrame.columnconfigure(3, weight=1)
        self.galleryFrame.columnconfigure(4, weight=1)
        self.galleryFrame.columnconfigure(5, weight=1)

        # Send pictures from gallery button
        self.sendGallerybtn = Button(self.windowGallery, text="Send", height=1, bg='#0000FF',
                                     fg='#F8F8FF', command=self.sendGallery)
        self.sendGallerybtn.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.sendGallerybtn['font'] = myFont3

        # Close gallery button
        self.closeGalleryButton = Button(self.windowGallery, text="Close", height=1, bg='#8B0000',
                                     fg='#F8F8FF', command=self.closeGallery)
        self.closeGalleryButton.grid(row=2, column=1, padx=5, pady=5, sticky=N + S + E + W)
        self.closeGalleryButton['font'] = myFont3

        if self.typeImage == 'Image':
            self.url_images = "assets/telloImages/"
            self.create_vector(self.url_images)

            if len(self.v_media) < 0:
                messagebox.showerror("Error", "No has guardado ninguna foto")
            else:
                self.create_gallery()

        if self.typeImage == 'Video':
            self.url_video = "assets/telloVideo/"
            self.create_vector(self.url_video)

            if len(self.v_media) < 0:
                messagebox.showerror("Error", "No hay guardado ningún vídeo")
            else:
                self.create_gallery()

    def create_vector(self, folder_path):

        for file_name in os.listdir(folder_path):
            if self.typeImage == 'Image':
                if file_name.lower().endswith('.jpg'):
                    file_path = os.path.join(folder_path, file_name)
                    self.v_media.append(file_path)
            if self.typeImage == 'Video':
                if file_name.lower().endswith('.mp4'):
                    file_path = os.path.join(folder_path, file_name)
                    self.v_media.append(file_path)

    def create_gallery_back(self):
        num_images_per_row = 6  # Número deseado de imágenes por fila
        max_image_size = 300  # Tamaño máximo de las imágenes
        min_image_size = 200  # Tamaño mínimo de las imágenes
        starting_row = 0
        padding = 20

        total_media = len(self.v_media)

        for i, media_path in enumerate(self.v_media):

            if total_media <= num_images_per_row:
                num_images_per_row = 4
                image_size = max_image_size
            else:
                image_size = min_image_size


            if self.typeImage == 'Image':
                img = Image.open(media_path)
                img.thumbnail((image_size, image_size))
                photo = ImageTk.PhotoImage(img)
            if self.typeImage == 'Video':
                cap = cv2.VideoCapture(media_path)
                ret, frame = cap.read()
                thumbnail = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                thumbnail.thumbnail((image_size, image_size))
                photo = ImageTk.PhotoImage(thumbnail)


            canvas = tk.Canvas(self.windowGallery, width=image_size, height=image_size)
            canvas.create_image(0, 0, anchor="nw", image=photo)

            row_position = starting_row + i // num_images_per_row
            col_position = i % num_images_per_row

            self.number_img += 1

            canvas.grid(row=row_position, column=col_position, padx=padding, pady=padding)
            canvas.bind("<Button-1>",
                        lambda event, img_path=media_path, count=self.number_img, can = canvas: self.select_image(img_path,
                                                                                                        count, can))

            self.canvas_list.append((canvas, photo))

    def create_gallery(self):
        num_images_per_row = 6  # Número deseado de imágenes por fila
        max_image_size = 300  # Tamaño máximo de las imágenes
        min_image_size = 200  # Tamaño mínimo de las imágenes
        starting_row = 0
        padding = 20

        total_media = len(self.v_media)

        for i, media_path in enumerate(self.v_media):

            if total_media <= num_images_per_row:
                num_images_per_row = 4
                image_size = max_image_size
            else:
                image_size = min_image_size

            if self.typeImage == 'Image':
                img = Image.open(media_path)
                img.thumbnail((160, 120))
                photo = ImageTk.PhotoImage(img)
            if self.typeImage == 'Video':
                cap = cv2.VideoCapture(media_path)
                ret, frame = cap.read()
                thumbnail = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                thumbnail.thumbnail((image_size, image_size))
                photo = ImageTk.PhotoImage(thumbnail)

            canvas = tk.Canvas(self.galleryFrame, width=160, height=120)
            canvas.create_image(0, 0, anchor="nw", image=photo)


            row_position = i//6
            col_position = i % 6

            self.number_img += 1

            canvas.grid(row=row_position, column=col_position, padx=5, pady=5)
            canvas.bind("<Button-1>",
                        lambda event, img_path=media_path, can=canvas: self.select_image(img_path, can))

            self.canvas_list.append((canvas, photo))

    def select_image(self, img_path, selectedCanvas):
        self.selected_image = img_path
        for canvas in self.canvas_list:
            canvas[0].config(highlightthickness =0)

        selectedCanvas.config(highlightthickness =2)
        selectedCanvas.config(highlightbackground='red')

    def sendGallery(self):
        try:
            if self.selected_image:

                image_path = self.selected_image
                with open(image_path, "rb") as image_file:
                    image_data = image_file.read()
                    image_base64 = base64.b64encode(image_data)

                    if self.typeImage == 'Image':
                        self.client.publish("ImagenAnna", payload=image_base64, qos=2)
                    if self.typeImage == 'Video':
                        self.client.publish("FileAnna", payload=image_base64, qos=2)
            else:
                print("No hay foto para enviar")
                return None
        except Exception as e:
            messagebox.showerror("Error de conexión",
                                 "No se pudo enviar la imagen. Por favor, inténtalo de nuevo.\nError: " + str(e),
                                 parent=self.windowGallery)

    def closeGallery(self):
        self.windowGallery.destroy()