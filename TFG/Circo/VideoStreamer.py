import ssl

import cv2

import paho.mqtt.client as mqtt

import cv2 as cv2
import numpy as np
import base64

class VideoStreamer:
    def on_connect(self,client, userdata, flags, rc):
        if rc == 0:
            print("Connection OK")
        else:
            print("Bad connection")

    def on_disconnect(self, client, userdata, rc):
        print("disconnected OK")
        self.client.loop_stop()

    def on_message(self, cli, userdata, message):
        command = message.topic
        print ('recibo ', command)
        if command == 'videoFrameAnna':
            image = base64.b64decode(bytes(message.payload.decode("utf-8"), "utf-8"))
            npimg = np.frombuffer(image, dtype=np.uint8)
            image = cv2.imdecode(npimg, 1)
            img = cv2.resize(image, (300, 400))
            self.img = cv2.flip(img, 1)
            self.imageReady = True


    ''' def __init__(self, source, broker):
        self.img = None
        self.imageReady = False
        self.source = source
        if source == 'laptopCamera':
            print ('vamos con la camara')
            self.cap = cv2.VideoCapture(0)
        else:
            print ('vamos con el broker')
            self.client = mqtt.Client("VideoService", transport="websockets")


            self.client.username_pw_set(
                "dronsEETAC", "mimara1456."
            )

            self.client.tls_set(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None,
            )
            print('voy a conectarme')
            self.client.connect("dronseetac.upc.edu", 8883)

            self.client.on_message = self.on_message  # Callback function executed when a message is received
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.max_queued_messages_set(1)
            self.client.max_inflight_messages_set(1)

            self.client.subscribe('videoFrameAnna')
            print('Waiting connection')

            self.client.loop_start()
    '''



    def __init__(self, source, broker):
        self.img = None
        self.imageReady = False
        self.source = source
        print ('recibo', source, broker)

        if source == 0:
            self.cap = cv2.VideoCapture(0)
        else:
            print ('vamos con el broker')
            self.client = mqtt.Client("VideoService", transport="websockets")
            self.client.tls_set(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None,
            )
            if broker == 0:
                self.client.username_pw_set(
                    "dronsEETAC", "mimara1456."
                )
                print ('dronseetac')
                self.client.connect("dronseetac.upc.edu", 8883)
            else:
                print ('hivemq')
                self.client.connect("broker.hivemq.com", 8884)

            self.client.on_message = self.on_message  # Callback function executed when a message is received
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.max_queued_messages_set(1)
            self.client.max_inflight_messages_set(1)
            self.client.subscribe('videoFrameAnna')
            print('Waiting connection')
            self.client.loop_start()


    def getFrame (self):
        if self.source == 0:
            success, image = self.cap.read()
            img = cv2.resize(image, (400, 300))
            img = cv2.flip(img, 1)
            return success,img
        else:
            return self.imageReady, self.img

    def disconnect (self):
        if self.source == 1:
            self.client.disconnect()
        else:
            self.cap.release()


