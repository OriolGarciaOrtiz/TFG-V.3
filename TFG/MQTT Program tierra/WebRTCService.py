import asyncio
import json
import base64
import numpy as np
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from websockets import connect



class WebVideoService:

    def __init__(self):
        self.img_original = None
        self.img_detected = None
        self.is_connected = False

    async def display_track(self, track):
        while self.is_connected:
            frame = await track.recv()
            self.img_original = frame.to_ndarray(format="bgr24")


    def decode_image(b64string):
        if not b64string:
            return None
        img_bytes = base64.b64decode(b64string)
        arr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

    async def main(self, websocket_url: str):
        pc = RTCPeerConnection()
        print("He creado la estructura de datos")

        @pc.on("track")
        def on_track(track):
            print("Track recibido:", track.kind)
            if track.kind == "video":
                asyncio.create_task(self.display_track(track))

        async with connect(websocket_url) as ws:
            print("Ya estoy conectado al emisor. Espero una oferta ...")
            self.is_connected = True

            async for raw in ws:
                data = json.loads(raw)
                msg_type = data.get("type")

                # ===========================
                # SDP
                # ===========================
                if msg_type == "sdp":
                    desc = RTCSessionDescription(
                        sdp=data["sdp"],
                        type=data["sdp_type"]
                    )
                    await pc.setRemoteDescription(desc)
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    await ws.send(json.dumps({
                        "type": "sdp",
                        "sdp": pc.localDescription.sdp,
                        "sdp_type": pc.localDescription.type
                    }))

                # ===========================
                #  RECIBIR DOS IMÁGENES
                # ===========================
                elif msg_type == "images":
                    print("Recibido mensaje con dos imágenes")

                    # Decodificar imágenes desde base64
                    self.img_original = self.decode_image(data.get("original"))
                    self.img_detected = self.decode_image(data.get("detected"))

                    print("Ambas imágenes recibidas y decodificadas")
