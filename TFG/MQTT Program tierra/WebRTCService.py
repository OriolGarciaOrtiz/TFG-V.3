import asyncio
import json
import traceback
from aiortc import RTCPeerConnection, RTCSessionDescription
from websockets import connect
from HexsoonGUI import GUI


class DroneVideoReceiver:
    """
    Ground station receiving dual-camera drone feed,
    sending frames directly to HexsoonGUI.
    Improved version with debug, initial delay, and FPS tracking.
    """
    def __init__(self, target_gui: GUI):
        self.frame_count = 0
        self.running = True
        self.start_time = None
        self.gui = target_gui
        self.connected = False
        self.pc = None

    async def receive_frame(self, track):
        """
        Consume frames from drone and send them to GUI.
        """
        # Espera inicial para que el dron comience a enviar frames
        await asyncio.sleep(0.5)
        self.start_time = asyncio.get_event_loop().time()

        try:
            while self.running:
                frame = await track.recv()
                self.frame_count += 1

                # Convertir a ndarray para GUI
                img = frame.to_ndarray(format="bgr24")

                # Actualizar frames en HexsoonGUI
                self.gui.controller.original_frame_RTC = img
                self.gui.controller.detected_frame_RTC = img.copy()  # Placeholder para detección

                # Debug: mostrar pts y time_base
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

    async def connect_to_drone(self, websocket_url="ws://127.0.0.1:9999"):
        """
        Connect to drone via WebSocket + WebRTC and start receiving frames.
        """
        if self.connected:
            print("[WARNING] Already connected to drone.")
            return

        print(f"Connecting to drone at {websocket_url}")
        self.pc = RTCPeerConnection()

        try:
            async with connect(websocket_url) as websocket:
                print("Connected to drone")

                @self.pc.on("track")
                def on_track(track):
                    print(f"Track received: {track.kind}")
                    if track.kind == "video":
                        asyncio.create_task(self.receive_frame(track))
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

    def start(self, websocket_url="ws://127.0.0.1:9999"):
        """
        Run the asyncio loop in a separate thread safely.
        """
        try:
            asyncio.run(self.connect_to_drone(websocket_url))
        except Exception as e:
            print(f"[ERROR] Exception in receiver start: {e}")
            traceback.print_exc()
