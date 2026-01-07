import random

from PIL import Image as Img
from PIL import ImageTk

from Detector import Detector
import cv2
import threading
import time
import tkinter as tk
from tkinter import *
from VideoStreamer import VideoStreamer



class PoseGenerarorDetector:
    def BuildFrame (self, master ,imageSource, broker, callBack):
        print ('recino :', imageSource, broker)
        self.callBack = callBack

        self.red = '#D61355'
        self.orange = '#F94A29'
        self.yellow = '#FCE22A'
        self.blue = '#30E3DF'
        self.gray = '#ECE8DD'

        self.masterFrame = tk.Frame (master)
        self.selectionFrame = tk.Frame (self.masterFrame)
        self.selectionFrame.pack(fill=BOTH)
        self.selectionFrame.columnconfigure(0, weight=1)
        self.selectionFrame.columnconfigure(1, weight=1)
        self.selectionFrame.columnconfigure(2, weight=1)
        self.selectHandsButton = tk.Button(self.selectionFrame, text="Hand poses", bg=self.red, command=self.hands)
        self.selectHandsButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.selectHalfBodyButton = tk.Button(self.selectionFrame, text="Half body poses", bg=self.blue, command=self.halfBody)
        self.selectHalfBodyButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        self.selectFullBodyButton = tk.Button(self.selectionFrame, text="Full body poses", bg=self.orange, command=self.fullBody)
        self.selectFullBodyButton.grid(row=0, column=2, padx=5, pady=5, sticky=N + S + E + W)

        self.frame = tk.Frame (self.masterFrame)
        self.frame.pack(fill = BOTH, expand = True)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=10)
        self.frame.columnconfigure(2, weight=10)

        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self.frame.rowconfigure(4, weight=1)
        self.frame.rowconfigure(5, weight=1)
        self.frame.rowconfigure(6, weight=1)

        self.startButton = tk.Button(self.frame, text="Start catching", bg=self.gray, command=self.start)
        self.startButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.catchButton = tk.Button(self.frame, text="Catch", bg=self.gray, command=self.catch)
        self.catchButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.deleteButton = tk.Button(self.frame, text="Delete", bg=self.gray, command=self.delete)
        self.deleteButton.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.saveButton = tk.Button(self.frame, text="Save models", bg=self.gray, command=self.save)
        self.saveButton.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.radioButtonFrame = tk.Frame(self.frame)
        self.radioButtonFrame.grid(row=4, column=0, padx=5, pady=0, sticky=N + S + E + W)

        self.accuracy = tk.StringVar()
        self.accuracy.set('40')
        self.r1 = tk.Radiobutton(self.radioButtonFrame, text='Difficult', value='30', variable=self.accuracy).grid(row=0, sticky="W")
        self.r2 = tk.Radiobutton(self.radioButtonFrame, text='Medium', value='40', variable=self.accuracy).grid(row=1, sticky="W")
        self.r3 = tk.Radiobutton(self.radioButtonFrame, text='Easy', value='50', variable=self.accuracy).grid(row=2, sticky="W")


        self.detectButton = tk.Button(self.frame, text="Detect", bg=self.gray, command=self.detect)
        self.detectButton.grid(row=5, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.closeButton = tk.Button(self.frame, text="Close", bg=self.gray, command=self.close)
        self.closeButton.grid(row=6, column=0, columnspan= 3, padx=5, pady=5, sticky=N + S + E + W)
        size =10
        self.canvas1 = Canvas(self.frame, width=size, height=size, bg='white')
        self.canvas1.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.canvas2 = Canvas(self.frame, width=size, height=size, bg='white')
        self.canvas2.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.canvas3 = Canvas(self.frame, width=size, height=size, bg='white')
        self.canvas3.grid(row=2, column=1, rowspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.canvas4 = Canvas(self.frame, width=size, height=size, bg='white')
        self.canvas4.grid(row=2, column=2, rowspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.canvas5 = Canvas(self.frame, width=size, height=size, bg='white')
        self.canvas5.grid(row=4, column=1, rowspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.canvas6 = Canvas(self.frame, width=size, height=size, bg='white')
        self.canvas6.grid(row=4, column=2, rowspan=2, padx=5, pady=5, sticky=N + S + E + W)

        self.canvasList = [self.canvas1, self.canvas2, self.canvas3, self.canvas4, self.canvas5, self.canvas6]
        self.photos = []
        self.photos2 = []


        self.poseList = []
        self.takeImage = False
        self.state = 'waiting selection'
        #self.videoStreamer = VideoStreamer('laptopCamera')
        self.videoStreamer = VideoStreamer(imageSource, broker)
        self.imageSource = imageSource

        return self.masterFrame

    def hands (self):
        if self.state == 'waiting selection':
            self.detector = Detector('hand')
            self.state = 'ready to catch'
            self.selectHalfBodyButton['bg'] = self.gray
            self.selectFullBodyButton['bg'] = self.gray
            self.startButton['bg'] = self.red


    def fullBody (self):
        if self.state == 'waiting selection':
            self.detector = Detector('full body')
            self.state = 'ready to catch'
            self.selectHandsButton['bg'] = self.gray
            self.selectHalfBodyButton['bg'] = self.gray
            self.startButton['bg'] = self.red

    def halfBody (self):
        if self.state == 'waiting selection':
            self.detector = Detector('half body')
            self.state = 'ready to catch'
            self.selectHandsButton['bg'] = self.gray
            self.selectFullBodyButton['bg'] = self.gray
            self.startButton['bg'] = self.red


    def start(self):
         if self.state == 'ready to catch':
            self.state = 'catching'
            self.startButton ['bg'] = self.orange
            self.startButton['text'] = 'starting ....'
            x = threading.Thread(target=self.startVideoStream)
            x.start()


    def catch(self):
        if self.state == 'catching':
            self.takeImage = True

    '''
    def load():
        detector.load()
    '''

    def detect(self):
        if self.state == 'ready to detect':
            x = threading.Thread(target=self.detecting)
            x.start()
            self.state = 'detecting'
            self.detectButton['bg'] = self.orange
            self.detectButton['text'] = 'starting ...'
        elif self.state == 'detecting':
            self.running = False
            self.state ='ready to detect'
            self.detectButton['bg'] = self.red
            self.detectButton['text'] = 'detect'
            '''
            self.selectHandsButton['bg'] = self.red
            self.selectHalfBodyButton['bg']= self.blue
            self.selectFullBodyButton['bg'] = self.orange
            self.detectButton['bg'] = self.gray
            self.pose = 0
            for i in range (0,len(self.poseList)):
                self.canvasList[i].delete('all')
            self.poseList = []
            self.photos = []
            '''

    def make_draggable(self,widget):
        widget.bind("<Button-1>", self.on_drag_start)
        widget.bind("<B1-Motion>", self.on_drag_motion)

    def on_drag_start(self,event):
        widget = event.widget
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def on_drag_motion(self,event):
        widget = event.widget
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        widget.place(x=x, y=y)

    def save(self):
        if self.state == 'catching':
            self.detector.storePoses(self.poseList)
            self.running = False
            actions = ['adelante', 'atrás', 'izquierda', 'derecha', 'arriba', 'abajo']
            '''
            for i in range(0, len(self.poseList)):
                self.label = tk.Label (self.canvasList[i], text = actions[i]).place (x=10, y=10)
                self.label.bind("<Button-1>", self.on_drag_start)
                self.label.bind("<B1-Motion>", self.on_drag_motion)

                #self.canvasList[i].create_text(150, 5, text=actions[i], fill="green", font=('Helvetica 18 bold'),
                                               #anchor=NE)
                #self.canvasList[i].create_text(150, 5, text=u'\u2713', fill="green", font=('Helvetica 18 bold'), anchor=NE)
            '''
            self.state = 'ready to detect'
            self.startButton['bg'] = self.gray
            self.startButton['text'] = 'Start catching'
            self.catchButton['bg'] = self.gray
            self.deleteButton['bg'] = self.gray
            self.saveButton['bg'] = self.gray
            self.detectButton['bg'] = self.red
            self.closeButton['bg'] = self.yellow



    def delete(self):
        if self.state == 'catching':
            self.pose = self.pose - 1
            self.canvasList[self.pose].delete('all')
            self.poseList = self.poseList[0:-1]
            self.photos = self.photos[0:-1]
            self.photos2 = self.photos2[0:-1]

    def maxmin (self,points):
        minx = 2
        miny = 2
        maxx = -1
        maxy = -1
        for point in points:
            if point[0] < minx:
                minx = point[0]
            if point[1] < miny:
                miny = point[1]
            if point[0] > maxx:
                maxx = point[0]
            if point[1] > maxy:
                maxy = point[1]

        for point in points:
            point[0] = point[0] - minx
            point[1] = point[1] - miny

        return minx, maxx, miny, maxy

    def normalize (self,points):
        size = 10
        minx, maxx, miny, maxy = self.maxmin(points)
        width = maxx - minx
        height = maxy - miny

        for point in points:
            point[0] = point[0] * size / width + 10
            point[1] = point[1] * size / height + 10

        return points


    def startVideoStream(self):
        self.running = True
        #cap = cv2.VideoCapture(0)
        self.startButton['bg'] = self.gray
        self.startButton['text'] = 'catching ...'
        self.catchButton['bg'] = self.orange
        self.deleteButton['bg'] = self.yellow
        self.saveButton['bg'] = self.blue
        self.pose = 0

        while self.running:
            '''success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue'''

            success, img = self.videoStreamer.getFrame()
            #img = cv2.flip(img, 1)
            if success:

                landmarks, img = self.detector.markImage(img)
                if self.takeImage:
                    self.takeImage = False
                    if self.pose < 6:
                        if not any (point [0] < 0 or point [1] < 0 or point [0] > 1 or point [1] > 1 for point in landmarks):
                            self.putPicture (self.pose, img)
                            self.pose = self.pose +1
                            self.poseList.append(self.detector.normalize(landmarks))
                cv2.imshow('video', img)
                cv2.waitKey(1)
        cv2.destroyWindow('video')
        cv2.waitKey(1)


    def detecting(self):
        self.running = True
        #cap = cv2.VideoCapture(0)

        self.detectButton['bg'] = self.red
        self.detectButton['text'] = 'Stop detecting'


        while self.running:
            '''  success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue'''
            success, image = self.videoStreamer.getFrame()
            if success:
                #image = cv2.flip(image, 1)
                '''    markedImage = image
                markedImage = cv2.resize(markedImage, (800, 600))
                markedImage = self.markImage (markedImage, 0, int (self.accuracy.get()))
                #markedImage = cv2.circle(markedImage, (int(self.poseList[0][0][0])*20, int(self.poseList[0][0][1])*20), int (self.accuracy.get()), (255,0,0), 2)
                #markedImage = cv2.circle(markedImage, (int(self.poseList[0][1][0])*20, int(self.poseList[0][1][1])*20), int (self.accuracy.get()), (255,0,0), 2)
                #markedImage = cv2.circle(markedImage, (int(self.poseList[0][2][0])*20, int(self.poseList[0][2][1])*20), int (self.accuracy.get()), (255,0,0), 2)
    
    
                cv2.imshow('marked', markedImage)'''
                cv2.waitKey(1)
                res, img = self.detector.detect(image, int (self.accuracy.get()))
                cv2.putText(img, "pose "+str(res), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                img = cv2.resize(img, (800, 600))

                cv2.imshow('video', img)
                cv2.waitKey(1)
        cv2.destroyWindow('video')
        cv2.waitKey(1)

    def putPicture(self, pose, img):
        canvas = self.canvasList[pose]

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.putText(img, 'pose ' + str(pose + 1), (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
        print ('image source :', self.imageSource)
        if self.imageSource == 0:
            img = cv2.resize(img, (200, 150))

        else:
            img = cv2.resize(img, (120, 150))
        self.photos.append(img.copy())
        self.photos2.append(ImageTk.PhotoImage(image=Img.fromarray(img)))
        canvas.create_image(0, 0, image=self.photos2[-1], anchor=tk.NW)
    def close (self):
        if self.state == 'ready to detect':
            self.callBack (self.poseList, self.photos)
            self.videoStreamer.disconnect()

if __name__ == '__main__':
    poseGeneratorDetector = PoseGenerarorDetector()
    window = tk.Tk()
    window.geometry('480x480')
    frame = poseGeneratorDetector.BuildFrame(window, callBack = None)
    frame.pack(fill = BOTH, expand = True)
    window.mainloop()


