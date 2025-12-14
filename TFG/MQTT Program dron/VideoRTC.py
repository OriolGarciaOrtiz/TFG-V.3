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
        self.original = np.zeros((240, 320, 3), dtype=np.uint8)
        self.detected = np.zeros((240, 320, 3), dtype=np.uint8)

        self.is_connected = False  # Controlado desde la GUI

    async def recv(self):
        # Espera hasta que se conecte un cliente
        while not self.is_connected:
            await asyncio.sleep(0.1)

        # Crea el frame combinado
        composite = np.hstack([self.original, self.detected])

        frame = VideoFrame.from_ndarray(composite, format="bgr24")
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base

        # Limitar FPS a 30
        await asyncio.sleep(1 / 30)
        return frame



class WebRTCServer:
    def __init__(self, video_track):
        self.video_track = video_track

    async def handle_client(self, websocket):
        print("🖥️ Cliente conectado")

        pc = RTCPeerConnection()
        pc.addTrack(self.video_track)

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

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
                    print("✅ WebRTC conectado")

        except ConnectionClosed:
            print("🔌 Cliente desconectado correctamente")
        except Exception as e:
            print(f"❌ Error en handler RTC: {e}")
        finally:
            print("🧹 Cerrando recursos RTC")

    async def run(self):
        async with websockets.serve(self.handle_client, "0.0.0.0", 9999):
            print("📡 WebRTC server en ws://0.0.0.0:9999")
            await asyncio.Future()
