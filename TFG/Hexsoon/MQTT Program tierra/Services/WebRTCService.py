import asyncio
import json
import traceback
from aiortc import RTCPeerConnection, RTCSessionDescription
from websockets import connect
from HexsoonGUI import GUI
from colorama import init, Fore
from aiortc.mediastreams import MediaStreamError

class DroneVideoReceiver:
    """
    Estación de tierra que recibe dual-camera feed del dron
    y actualiza la GUI HexsoonGUI.
    """
    def __init__(self, target_gui: GUI):
        self.frame_count = 0
        self.start_time = None
        self.gui = target_gui
        self.connected = False
        self.pc = None

        self.connection_lock = asyncio.Lock()

        init(autoreset=True)

        self.ip_adress = "ws://127.0.0.1:9999"             # En caso que se quieran hacer pruebas en local
        #self.ip_adress = "ws://192.168.1.102:9999"       # Para cuando se quieran hacer pruebas de vuelo

        self.running: bool = False

        self.recv_running: bool = False

    async def receive_frame(self, track, track_label):
        while not self.connected:
            await asyncio.sleep(0.05)

        self.start_time = asyncio.get_event_loop().time()

        try:
            while self.recv_running and self.running:
                frame = await track.recv()

                img = frame.to_ndarray(format="bgr24")

                if "original" in track_label:
                    self.gui.controller.original_frame_RTC = img
                elif "detected" in track_label:
                    self.gui.controller.detected_frame_RTC = img

                self.frame_count += 1

        except MediaStreamError:
            # ✔ NORMAL shutdown of the video track
            print(Fore.YELLOW + f"[RTC] Track '{track_label}' closed")

        except asyncio.CancelledError:
            # ✔ Task cancelled intentionally
            print(Fore.YELLOW + f"[RTC] Track '{track_label}' task cancelled")

        except Exception as e:
            # ❌ Real errors only
            print(Fore.RED + f"[ERROR] Unexpected RTC error ({track_label}): {e}")
            traceback.print_exc()

        finally:
            print(Fore.MAGENTA + f"[RTC] Track '{track_label}' finalizado en receive_frame")

    async def connect_to_drone(self):
        """
        Conecta al dron mediante WebSocket + WebRTC, negocia el SDP 
        y gestiona la llegada de múltiples tracks de video.
        """
        async with self.connection_lock:
            if self.connected:
                print(Fore.YELLOW + "[WARNING] Ya estás conectado al dron.")
                return

            print(Fore.BLUE + f"📡 Iniciando conexión con: {self.ip_adress}")
            
            self.pc = RTCPeerConnection()

            @self.pc.on("track")
            def on_track(track):
                if track.kind != "video":
                    return

                # Buscar el transceiver asociado a este track
                transceiver = next(
                    (
                        t for t in self.pc.getTransceivers()
                        if t.receiver and t.receiver.track == track
                    ),
                    None
                )

                if not transceiver:
                    print("⚠️ [RTC] No se encontró transceiver para el track")
                    return

                mid = transceiver.mid
                print(f"🎥 [RTC] Track recibido con MID={mid}")

                if mid == "0":
                    asyncio.create_task(self.receive_frame(track, "original"))

                elif mid == "1":
                    asyncio.create_task(self.receive_frame(track, "detected"))

                else:
                    print(f"⚠️ [RTC] MID desconocido: {mid}")

            try:
                async with connect(self.ip_adress) as websocket:
                    print(Fore.GREEN + "✅ WebSocket conectado. Esperando oferta SDP...")

                    # Esperar oferta SDP del dron (el servidor es el que inicia la oferta)
                    message = await websocket.recv()
                    data = json.loads(message)

                    if data.get("type") == "sdp" and data.get("sdp_type") == "offer":
                        # Configurar la descripción remota (oferta del dron)
                        offer = RTCSessionDescription(
                            sdp=data["sdp"],
                            type=data["sdp_type"]
                        )
                        await self.pc.setRemoteDescription(offer)
                        print(Fore.GREEN + "✅ Oferta remota establecida.")

                        # Crear la respuesta (Answer)
                        answer = await self.pc.createAnswer()
                        await self.pc.setLocalDescription(answer)

                        # Enviar la respuesta al dron
                        await websocket.send(json.dumps({
                            "type": "sdp",
                            "sdp": self.pc.localDescription.sdp,
                            "sdp_type": self.pc.localDescription.type
                        }))
                        print(Fore.GREEN + "✅ Respuesta SDP enviada.")

                        self.connected = True
                        self.recv_running = True
                        print(Fore.MAGENTA + "🚀 Conexión WebRTC establecida. Recibiendo video...")

                        # Mantener la conexión viva mientras el flag connected sea True
                        while self.connected:
                            if not self.running: # Si HandlerThreads pide parar
                                break
                            await asyncio.sleep(0.1)

                    else:
                        print(Fore.RED + f"[ERROR] Mensaje inesperado del dron: {data.get('type')}")

            except ConnectionRefusedError:
                print(Fore.RED + f"[ERROR] No se pudo conectar a {self.ip_adress}. ¿Está el servidor del dron encendido?")
            except Exception as e:
                print(Fore.RED + f"[ERROR] Error crítico en la estación de tierra: {e}")
                traceback.print_exc()
            finally:
                self.connected = False
                self.recv_running = False

                if self.pc:
                    await self.pc.close()
                    self.pc = None

                print(Fore.BLUE + "🧹 Conexión con el dron cerrada")


    def should_connect_rtc(self) -> bool:
        return (
            self.gui.controller.try_mode in ("Practice", "Simulation") and
            self.gui.controller.type_camera_option in ("Raspi Cam")
        )
    
    async def disconnect_from_drone(self):
        async with self.connection_lock:
            if not self.connected:
                return

            print(Fore.BLUE + "Disconnecting from drone...")
            self.connected = False
            self.recv_running = False


    async def connection_manager(self):
        last_state = None

        while self.running:
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
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            self.running = True
            self.connection_task = self.loop.create_task(self.connection_manager())

            self.loop.run_forever()

        except Exception as e:
            print(Fore.RED + f"[ERROR] Exception in receiver start: {e}")
            traceback.print_exc()

        finally:
            self._shutdown_loop()
            print(Fore.BLUE + "[RTC] Event loop cerrado")


    def stop(self):
        self.running = False
        self.recv_running = False
        self.connected = False

        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)



    def _shutdown_loop(self):
        pending = asyncio.all_tasks(loop=self.loop)

        for task in pending:
            task.cancel()

        if pending:
            self.loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )

        self.loop.close()
        print(Fore.BLUE + "[RTC] Event loop cerrado limpiamente")



