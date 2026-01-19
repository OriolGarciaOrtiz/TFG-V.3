from av import VideoFrame
import asyncio
import numpy as np
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from websockets.exceptions import ConnectionClosed
import cv2

class DroneVideoTrack(VideoStreamTrack):
    def __init__(self, window_name):
        super().__init__()
        self.frame = np.zeros((240, 320, 3), dtype=np.uint8)
        self.is_connected = False
        self.window_name = window_name

    async def recv(self):
        try:
            # Decide qué frame enviar
            if not self.is_connected or self.frame is None:
                frame_to_send = np.zeros((240, 320, 3), dtype=np.uint8)
            else:
                frame_to_send = self.frame

            # 🔹 Asegurar que el frame sea 3D
            if frame_to_send.ndim == 2:  # si es H×W, convertir a H×W×3
                frame_to_send = cv2.cvtColor(frame_to_send, cv2.COLOR_GRAY2BGR)

            video_frame = VideoFrame.from_ndarray(frame_to_send, format="bgr24")
            pts, time_base = await self.next_timestamp()
            video_frame.pts = pts
            video_frame.time_base = time_base

            await asyncio.sleep(1/30)

        except Exception as e:
            print(f"[recv ERROR] {e}")
            # Si falla, enviar frame negro seguro
            video_frame = VideoFrame.from_ndarray(np.zeros((240, 320, 3), dtype=np.uint8), format="bgr24")

        return video_frame


class WebRTCServer:
    def __init__(self, video_track_original: DroneVideoTrack, video_track_detected: DroneVideoTrack):
        self.video_track_original = video_track_original
        self.video_track_detected = video_track_detected
        self.camera_option = "Raspi Cam"

        self.running = False

    async def handle_client(self, websocket):
        print("🖥️ Cliente conectado")

        pc = RTCPeerConnection()

        pc.addTransceiver(self.video_track_original, direction="sendonly")
        pc.addTransceiver(self.video_track_detected,direction="sendonly")

        print("🎥 Tracks enviados: original, detected")

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Send offer to client
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

                    # Enable video frames if using Raspi Cam
                    self.video_track_original.is_connected = True
                    self.video_track_detected.is_connected = True
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
