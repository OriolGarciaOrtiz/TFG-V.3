
import math
import tkinter as tk
from tkinter import Toplevel, Canvas


# Constantes geodésicas
R_EARTH = 6378137.0

def meters_to_deg_lat(m):
    return (m / R_EARTH) * (180.0 / math.pi)


def meters_to_deg_lon(m, lat_deg):
    lat_rad = math.radians(lat_deg)
    denom = R_EARTH * math.cos(lat_rad)
    if abs(denom) < 1e-6:
        denom = 1e-6
    return (m / denom) * (180.0 / math.pi)


class GeoTracker:
    def __init__(self, initial_lat, initial_lon, area_corners,
                 canvas_size=(500, 500), padding=20, map_title="Mapa Aula",
                 external_canvas=None):
        self.external_canvas = external_canvas

        assert len(area_corners) >= 4, "area_corners debe contener al menos 4 puntos (lat, lon)."

        self.lat = float(initial_lat)
        self.lon = float(initial_lon)

        self.history = [(self.lat, self.lon)]

        self.area_corners = [(float(a), float(b)) for (a, b) in area_corners[:4]]

        # ventana y canvas
        self.canvas_width, self.canvas_height = canvas_size
        self.padding = padding
        self.map_title = map_title

        self.window = None
        self.canvas = None

        self.lat_min = None
        self.lat_max = None
        self.lon_min = None
        self.lon_max = None
        self.scale_x = 1.0
        self.scale_y = 1.0

        self.prev_px = None
        self.prev_py = None

        self.area_color = "#cfe8ff"
        self.area_outline = "#0055cc"
        self.drone_color = "green"
        self.trail_color = "red"

        self._map_drawn = False

        lats = [p[0] for p in self.area_corners]
        lons = [p[1] for p in self.area_corners]
        self.lat_min = min(lats)
        self.lat_max = max(lats)
        self.lon_min = min(lons)
        self.lon_max = max(lons)

        if self.lat < self.lat_min: self.lat_min = min(self.lat_min, self.lat) - 1e-6
        if self.lat > self.lat_max: self.lat_max = max(self.lat_max, self.lat) + 1e-6
        if self.lon < self.lon_min: self.lon_min = min(self.lon_min, self.lon) - 1e-6
        if self.lon > self.lon_max: self.lon_max = max(self.lon_max, self.lon) + 1e-6

        self._compute_map_scale()

    def _compute_map_scale(self):

        lat_span_m = (self.lat_max - self.lat_min) * (math.pi / 180.0) * R_EARTH
        lat_center = (self.lat_min + self.lat_max) / 2.0
        lon_span_m = (self.lon_max - self.lon_min) * (math.pi / 180.0) * R_EARTH * math.cos(math.radians(lat_center))

        if abs(lat_span_m) < 1e-3: lat_span_m = 1.0
        if abs(lon_span_m) < 1e-3: lon_span_m = 1.0

        usable_w = max(self.canvas_width - 2 * self.padding, 10)
        usable_h = max(self.canvas_height - 2 * self.padding, 10)

        scale_x = usable_w / lon_span_m
        scale_y = usable_h / lat_span_m

        self.scale = min(scale_x, scale_y)

        self.lon_span_m = lon_span_m
        self.lat_span_m = lat_span_m

        self.origin_lat = self.lat_min
        self.origin_lon = self.lon_min

    def open_map_window(self):
        if self.external_canvas is not None:
            self.canvas = self.external_canvas
            self.canvas_width = int(self.canvas['width'])
            self.canvas_height = int(self.canvas['height'])
        else:
            self.window = Toplevel()
            self.window.title(self.map_title)
            self.canvas = Canvas(self.window, width=self.canvas_width,
                                 height=self.canvas_height, bg="white")
            self.canvas.pack()

        pts_px = [self._latlon_to_canvas_xy(lat, lon) for (lat, lon) in self.area_corners]

        xs = [p[0] for p in pts_px]
        ys = [p[1] for p in pts_px]
        left, right = min(xs), max(xs)
        top, bottom = min(ys), max(ys)

        self.canvas.create_rectangle(
            left, top, right, bottom,
            fill=self.area_color,
            outline=self.area_outline,
            width=2
        )

        for idx, ((x, y), (lat, lon)) in enumerate(zip(pts_px, self.area_corners), start=1):
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=self.area_outline)
            self.canvas.create_text(x + 8, y, anchor="w",
                                    text=f"pos{idx}", font=("Arial", 10, "bold"))

        px0, py0 = self._latlon_to_canvas_xy(self.lat, self.lon)
        self.prev_px, self.prev_py = px0, py0

        self.drone_marker = self.canvas.create_oval(
            px0 - 5, py0 - 5, px0 + 5, py0 + 5,
            fill=self.drone_color, outline="black"
        )

        self.coord_text = self.canvas.create_text(
            10, 10, anchor="nw", text=f"{self.lat:.6f}, {self.lon:.6f}"
        )

        self._map_drawn = True

    def _latlon_to_canvas_xy(self, lat, lon):

        north_m = (lat - self.origin_lat) * (math.pi / 180.0) * R_EARTH
        lat_center = (self.lat_min + self.lat_max) / 2.0
        east_m = (lon - self.origin_lon) * (math.pi / 180.0) * R_EARTH * math.cos(math.radians(lat_center))

        x_px = self.padding + east_m * self.scale
        y_px = self.padding + ( (self.lat_span_m - north_m) * self.scale )
        if abs(self.lat_span_m) < 1e-6:
            y_px = self.padding + (self.canvas_height - 2*self.padding)/2

        return x_px, y_px

    def _canvas_xy_to_latlon(self, x_px, y_px):
        east_m = (x_px - self.padding) / self.scale
        north_m = self.lat_span_m - ( (y_px - self.padding) / self.scale )
        lat = self.origin_lat + (north_m / R_EARTH) * (180.0 / math.pi)
        lat_center = (self.lat_min + self.lat_max) / 2.0
        lon = self.origin_lon + (east_m / (R_EARTH * math.cos(math.radians(lat_center)))) * (180.0 / math.pi)
        return lat, lon

    def update_with_velocities(self, vx_cm_s, vy_cm_s, yaw_deg, dt, plot=True):

        vx = float(vx_cm_s) / 100.0
        vy = float(vy_cm_s) / 100.0

        dx_body = vx * dt
        dy_body = vy * dt

        yaw_rad = math.radians(float(yaw_deg))
        dx_world = dx_body * math.cos(yaw_rad) - dy_body * math.sin(yaw_rad)
        dy_world = dx_body * math.sin(yaw_rad) + dy_body * math.cos(yaw_rad)

        north_m = dx_world
        east_m = dy_world

        dlat = meters_to_deg_lat(north_m)
        dlon = meters_to_deg_lon(east_m, self.lat)

        self.lat += dlat
        self.lon += dlon

        self.history.append((self.lat, self.lon))

        if plot and self._map_drawn:
            self.plot_current_position()

        return self.lat, self.lon

    def plot_current_position(self):
        if not self._map_drawn:
            return

        px, py = self._latlon_to_canvas_xy(self.lat, self.lon)

        if self.prev_px is not None and self.prev_py is not None:
            self.canvas.create_line(self.prev_px, self.prev_py, px, py, fill=self.trail_color, width=2)

        try:
            self.canvas.coords(self.drone_marker, px-5, py-5, px+5, py+5)
        except Exception:
            self.drone_marker = self.canvas.create_oval(px-5, py-5, px+5, py+5, fill=self.drone_color, outline="black")

        self.canvas.itemconfigure(self.coord_text, text=f"{self.lat:.6f}, {self.lon:.6f}")

        self.prev_px, self.prev_py = px, py