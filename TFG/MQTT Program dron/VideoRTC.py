from av import VideoFrame
import asyncio
import numpy as np
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from websockets.exceptions import ConnectionClosed

class DroneVideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.frame = np.zeros((240, 320, 3), dtype=np.uint8)

        self.is_connected = False

    async def recv(self):
        while not self.is_connected:
            await asyncio.sleep(0.1)

        frame = VideoFrame.from_ndarray(self.frame, format="bgr24")
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base

        await asyncio.sleep(1 / 30)
        return frame



class WebRTCServer:
    def __init__(self, video_track_original: DroneVideoTrack, video_track_detected: DroneVideoTrack):
        self.video_track_original = video_track_original
        self.video_track_detected = video_track_detected

        self.camera_option = "Default Cam"

    async def handle_client(self, websocket):
        print("🖥️ Cliente conectado")

        pc = RTCPeerConnection()
        sender_original = pc.addTrack(self.video_track_original)
        sender_original._track_label = "original"
        
        sender_detected = pc.addTrack(self.video_track_detected)
        sender_detected._track_label = "detected"

        # Crear oferta SDP
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Enviar oferta al cliente
        await websocket.send(json.dumps({
            "type": "sdp",
            "sdp": pc.localDescription.sdp,
            "sdp_type": pc.localDescription.type
        }))

        try:
            async for msg in websocket:
                data = json.loads(msg)
                if data["type"] == "sdp":
                    answer = RTCSessionDescription(
                        sdp=data["sdp"],
                        type=data["sdp_type"]
                    )
                    await pc.setRemoteDescription(answer)

                    enabled = (self.camera_option == "Raspi Cam")

                    self.video_track_detected.is_connected = enabled
                    self.video_track_detected.is_connected = enabled
                    print("✅ WebRTC conectado")

        except ConnectionClosed:
            print("🔌 Cliente desconectado correctamente")
        except Exception as e:
            print(f"❌ Error en handler RTC: {e}")
        finally:
            self.video_track_original.is_connected = False
            self.video_track_detected.is_connected = False
            await pc.close()
            print("🧹 Cerrando recursos RTC")

    async def run(self):
        async with websockets.serve(self.handle_client, "0.0.0.0", 9999):
            print("📡 WebRTC server en ws://0.0.0.0:9999")
            await asyncio.Future()
