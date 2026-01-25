import win32gui
import win32ui
import ctypes
import numpy as np
import cv2
from dronLink.Dron import Dron
import time
import folium
import math
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from HexsoonGUI import GUI

class MissionPlanner:
    def __init__(self, target_gui: GUI):
        self.target_gui = target_gui
        self.mission_panel_height = self.target_gui.misson_panel_heigth
        self.mission_panel_width = self.target_gui.misson_panel_width

        self.dron: Dron = self.target_gui.controller.dron

        self.running: bool = False

        self.user32 = ctypes.windll.user32
        self.PrintWindow = self.user32.PrintWindow

        # Configuración de Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={self.mission_panel_width},{self.mission_panel_height}")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.tmp_html_path = os.path.join(os.getcwd(), "temp_map.html")

    # Obtener HWND de la ventana de Mission Planner
    @staticmethod
    def get_mission_planner_hwnd():
        hwnd_list = []
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Mission Planner" in title:
                    hwnd_list.append(hwnd)
        win32gui.EnumWindows(enum_handler, None)
        return hwnd_list[0] if hwnd_list else None

    # PrintWindow seguro
    @staticmethod
    def safe_print_window(hwnd, hdc, flags):
        user32 = ctypes.windll.user32
        user32.PrintWindow.restype = ctypes.c_bool
        return user32.PrintWindow(hwnd, hdc, flags)

    # Captura Mission Planner
    def capture_mission_planner(self):
        try:
            hwnd = self.get_mission_planner_hwnd()
            if not hwnd:
                return None

            left, top, right, bot = win32gui.GetClientRect(hwnd)
            width, height = right-left, bot-top
            if width <=0 or height <=0:
                return None

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = self.safe_print_window(hwnd, saveDC.GetSafeHdc(), 1)

            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((height, width, 4))[:,:,:3]

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            if result != 1:
                return None

            img = cv2.resize(img, (self.mission_panel_width, self.mission_panel_height))
            return img
        except Exception as e:
            print(f"Error capture Mission Planner: {e}")
            return None

    # Generar mapa folium (modo Practice)
    def generate_map_frame(self):
        try:
            lat, lon, yaw = self.dron.lat, self.dron.lon, self.dron.heading
            alt = getattr(self.dron, "alt", 0)

            m = folium.Map(location=[lat, lon], zoom_start=18, tiles=None)
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri", overlay=False, control=False
            ).add_to(m)

            # CSS
            m.get_root().html.add_child(folium.Element("""
            <style>
            html, body {width:100%;height:100%;margin:0;padding:0;}
            #map {position:absolute;top:0;bottom:0;width:100%;height:100%;}
            .leaflet-tile {filter:brightness(1) contrast(1) !important; opacity:1 !important;}
            .leaflet-fade-anim .leaflet-tile {transition:none !important;}
            .leaflet-container {background:black !important;}
            </style>
            """))

            # Icono del dron
            icon_size = 40
            icon_anchor = icon_size//2
            html_icon = f"""
            <div style="width:{icon_size}px;height:{icon_size}px;transform:rotate({yaw}deg);transform-origin:50% 50%;pointer-events:none;">
            <img src="DroneMarker2.png" style="width:{icon_size}px;height:{icon_size}px;"></div>
            """
            folium.Marker([lat, lon], icon=folium.DivIcon(html=html_icon, icon_size=(icon_size,icon_size), icon_anchor=(icon_anchor,icon_anchor)),
                          popup=f"ALT:{alt:.1f} m<br>YAW:{yaw:.1f}°").add_to(m)

            # Línea de orientación
            line_length = 15
            yaw_rad = math.radians(yaw)
            dlat = (line_length*math.cos(yaw_rad))/111320
            dlon = (line_length*math.sin(yaw_rad))/(111320*math.cos(math.radians(lat)))
            folium.PolyLine([[lat,lon],[lat+dlat,lon+dlon]], color="red", weight=3, opacity=1.0).add_to(m)

            # Guardar HTML
            m.save(self.tmp_html_path)

            # Renderizar con Selenium
            self.driver.get("file:///" + self.tmp_html_path.replace("\\","/"))
            time.sleep(1.0)
            map_div = WebDriverWait(self.driver,5).until(
                EC.presence_of_element_located((By.CLASS_NAME,"folium-map"))
            )
            png = map_div.screenshot_as_png
            img = Image.open(io.BytesIO(png))
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        except Exception as e:
            print(f"Error generate map: {e}")
            return None


    def _mission_loop(self):

        while self.running:

            frame = None

            try:

                mode = self.target_gui.test_selection.get()

                if mode == "Simulation":

                    frame = self.capture_mission_planner()

                elif mode == "Practice":

                    if self.dron and self.dron.lat is not None and self.dron.lon is not None:

                        frame = self.generate_map_frame()

            except Exception as e:
                print(f"Thread error: {e}")

            self.target_gui.mission_frame = frame
            time.sleep(1/self.target_gui.FPS)
