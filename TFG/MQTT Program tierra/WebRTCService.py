import asyncio
import json
import traceback
from aiortc import RTCPeerConnection, RTCSessionDescription
from websockets import connect
from HexsoonGUI import GUI


class DroneVideoReceiver:
    """
    Estación de tierra que recibe dual-camera feed del dron
    y actualiza la GUI HexsoonGUI.
    """
    def __init__(self, target_gui: GUI):
        self.frame_count = 0
        self.running = True
        self.start_time = None
        self.gui = target_gui
        self.connected = False
        self.pc = None

    async def receive_frame(self, track, track_id):
        """
        Recibir frames de un track específico y actualizar la GUI.
        """
        await asyncio.sleep(0.5)
        self.start_time = asyncio.get_event_loop().time()

        try:
            while self.running:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")

                # Actualizar GUI según track
                if "original" in track_id:
                    self.gui.controller.original_frame_RTC = img
                elif "detected" in track_id:
                    self.gui.controller.detected_frame_RTC = img
                else:
                    print(f"[WARNING] Track unknown: {track_id}")

                self.frame_count += 1

                # Debug cada 10 frames
                if self.frame_count % 10 == 0:
                    print(f"[DEBUG] Frame #{self.frame_count} | pts={frame.pts}, time_base={frame.time_base}")

                # FPS cada 60 frames
                if self.frame_count % 60 == 0:
                    elapsed = asyncio.get_event_loop().time() - self.start_time
                    fps = self.frame_count / elapsed if elapsed > 0 else 0
                    print(f"Frames received: {self.frame_count}, FPS: {fps:.1f}")

        except Exception as e:
            print(f"[ERROR] Error receiving frames: {e}")
            traceback.print_exc()

    async def connect_to_drone(self, websocket_url="ws://192.168.1.102:9999"):
        """
        Conectar al dron mediante WebSocket + WebRTC y recibir ambos tracks.
        """
        if self.connected:
            print("[WARNING] Already connected to drone.")
            return

        print(f"Connecting to drone at {websocket_url}")
        self.pc = RTCPeerConnection()

        try:
            async with connect(websocket_url) as websocket:
                print("Connected to drone")

                # Registrar callback para recibir tracks
                @self.pc.on("track")
                def on_track(track):
                    print(f"Track received: {track.kind}, id={track.id}")
                    if track.kind == "video":
                        asyncio.create_task(self.receive_frame(track, track.id))
                    else:
                        print(f"Ignoring non-video track: {track.kind}")

                # Esperar oferta SDP del dron
                message = await websocket.recv()
                data = json.loads(message)

                if data.get("type") == "sdp" and data.get("sdp_type") == "offer":
                    offer = RTCSessionDescription(
                        sdp=data["sdp"],
                        type=data["sdp_type"]
                    )
                    await self.pc.setRemoteDescription(offer)

                    # Crear y enviar answer
                    answer = await self.pc.createAnswer()
                    await self.pc.setLocalDescription(answer)
                    await websocket.send(json.dumps({
                        "type": "sdp",
                        "sdp": self.pc.localDescription.sdp,
                        "sdp_type": self.pc.localDescription.type
                    }))

                    self.connected = True
                    print("✅ WebRTC connection established. Receiving frames...")

                    # Mantener conexión viva mientras self.running
                    while self.running:
                        await asyncio.sleep(0.1)

                else:
                    print(f"[WARNING] Unexpected message from drone: {data.get('type')}")

        except ConnectionRefusedError:
            print(f"[ERROR] Cannot connect to {websocket_url}. Ensure drone server is running.")
        except Exception as e:
            print(f"[ERROR] Ground station error: {e}")
            traceback.print_exc()
        finally:
            if self.pc:
                await self.pc.close()
            self.connected = False
            print(f"Total frames received: {self.frame_count}")
            print("Drone connection closed.")

    def start(self, websocket_url="ws://192.168.1.102:9999"):
        """
        Ejecutar la conexión al dron en un loop asyncio.
        """
        try:
            asyncio.run(self.connect_to_drone(websocket_url))
        except Exception as e:
            print(f"[ERROR] Exception in receiver start: {e}")
            traceback.print_exc()
