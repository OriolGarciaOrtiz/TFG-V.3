import asyncio
import json
import traceback
from aiortc import RTCPeerConnection, RTCSessionDescription
from websockets import connect
from HexsoonGUI import GUI
from colorama import init, Fore

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

        self.connection_lock = asyncio.Lock()

        init(autoreset=True)

        self.ip_adress = "ws://127.0.0.1:9999"             # En caso que se quieran hacer pruebas en local
        #self.ip_adress = "ws://192.168.1.102:9999"       # Para cuando se quieran hacer pruebas de vuelo

    async def receive_frame(self, track, track_label):
        """
        Recibir frames de un track específico y actualizar la GUI.
        """
        await asyncio.sleep(0.5)
        self.start_time = asyncio.get_event_loop().time()

        try:
            while self.connected:

                frame = await track.recv()

                if frame is None: 
                    return

                img = frame.to_ndarray(format="bgr24")

                # Actualizar GUI según track
                if "original" in track_label:
                    self.gui.controller.original_frame_RTC = img
                elif "detected" in track_label:
                    self.gui.controller.detected_frame_RTC = img
                else:
                    print(Fore.YELLOW + f"[WARNING] Track unknown: {track_label}")

                self.frame_count += 1

        except Exception as e:
            print(Fore.RED + f"[ERROR] Error receiving frames: {e}")
            traceback.print_exc()

    async def connect_to_drone(self):
        """
        Conectar al dron mediante WebSocket + WebRTC solo si el modo es 'Practice'.
        """
        
        async with self.connection_lock:

            if self.connected:
                print(Fore.YELLOW + "[WARNING] Already connected to drone.")
                return

            print(Fore.BLUE + f"Connecting to drone at {self.ip_adress}")
            self.pc = RTCPeerConnection()

        try:
            async with connect(self.ip_adress) as websocket:
                print(Fore.GREEN + "Connected to WebRTC")

                # Registrar callback para recibir tracks
                @self.pc.on("track")
                def on_track(track):
                    if track.kind != "video":
                        return

                    # Asignar por orden
                    if not hasattr(self, "_video_track_1"):
                        self._video_track_1 = track
                        asyncio.create_task(self.receive_frame(track, "original"))
                    else:
                        self._video_track_2 = track
                        asyncio.create_task(self.receive_frame(track, "detected"))

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
                    print(Fore.GREEN + "WebRTC connection established. Receiving frames...")

                    while self.connected:
                        await asyncio.sleep(0.1)

                else:
                    print(Fore.YELLOW + f"[WARNING] Unexpected message from drone: {data.get('type')}")

        except ConnectionRefusedError:
            print(Fore.RED + f"[ERROR] Cannot connect to {self.ip_adress}. Ensure drone server is running.")
        except Exception as e:
            print(Fore.RED + f"[ERROR] Ground station error: {e}")
            traceback.print_exc()
        finally:
            if self.pc:
                await self.pc.close()
            self.connected = False
            print(Fore.BLUE + "Drone connection closed.")


    def should_connect_rtc(self) -> bool:
        return (
            self.gui.controller.try_mode in ("Practice", "Simulation") and
            self.gui.controller.camera_option in ("Raspi Cam", "Panoramic Cam")
        )
    
    async def disconnect_from_drone(self):
        async with self.connection_lock:
            if not self.connected:
                return

            print(Fore.BLUE + "Disconnecting from drone...")
            self.connected = False

    async def connection_manager(self):
        last_state = None

        while True:
            current_state = self.should_connect_rtc()

            if current_state != last_state:
                if current_state and not self.connected:
                    print(Fore.GREEN + "[RTC] Conditions met → connecting")
                    asyncio.create_task(self.connect_to_drone())

                elif not current_state and self.connected:
                    print(Fore.YELLOW + "[RTC] Conditions not met → disconnecting")
                    await self.disconnect_from_drone()

                last_state = current_state

            await asyncio.sleep(0.2)


    def start(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.create_task(self.connection_manager())
            loop.run_forever()

        except Exception as e:
            print(Fore.RED + f"[ERROR] Exception in receiver start: {e}")
            traceback.print_exc()
