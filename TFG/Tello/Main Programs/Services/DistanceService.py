from TelloGUI import GUI
import cv2
import cv2.aruco as aruco
import numpy as np
import math

class ServiceDistance:

    def __init__(self, target_gui: GUI):
        
        self.target_gui = target_gui

        self.running = True


    def distance_by_ratio(self, img_display, object_center, w, h):
        ratio_width = 5.2 / 5.5
        ratio_height = 1.2
        focal_length_width = img_display.shape[0] / ratio_width
        focal_length_height = img_display.shape[1] / ratio_height
        obj_height = float(self.target_gui.entry_height.get()) if self.target_gui.entry_height.get() else 27.0
        obj_width = float(self.target_gui.entry_width.get()) if self.target_gui.entry_width.get() else 20.0

        if object_center and obj_width and obj_height and w and h:
            dist_to_camera_width = float(obj_width) * focal_length_width / w * 2 - 22
            dist_to_camera_height = float(obj_height) * focal_length_height / h * 2 - 22
            distance = (dist_to_camera_width + dist_to_camera_height) / 2
            self.target_gui.dist_label.config(text="Distance to Object: " + str(distance.__round__(0)))
            return distance.__round__(0)
        else:
            self.target_gui.dist_label.config(text="[Ratio] Distance: --")
            return None


    def distance_by_aruco(self, gray_highres, img_contour, camera_matrix, dist_coeffs):
        dictionary = aruco.getPredefinedDictionary(aruco.DICT_5X5_100)
        detector = aruco.ArucoDetector(dictionary)
        corners, ids, rejected = detector.detectMarkers(gray_highres)

        if ids is not None:
            aruco.drawDetectedMarkers(img_contour, corners, ids)
            marker_length_cm = float(self.target_gui.marker_length_entry.get()) if self.target_gui.marker_length_entry.get() else 6
            marker_length = marker_length_cm / 100  # m

            for i in range(len(ids)):
                obj_points = np.array([
                    [-marker_length / 2, -marker_length / 2, 0],
                    [marker_length / 2, -marker_length / 2, 0],
                    [marker_length / 2, marker_length / 2, 0],
                    [-marker_length / 2, marker_length / 2, 0]
                ], dtype=np.float32)

                ret, rvec, tvec = cv2.solvePnP(obj_points, corners[i], camera_matrix, dist_coeffs)
                cv2.drawFrameAxes(img_contour, camera_matrix, dist_coeffs, rvec, tvec, 0.05)
                distance = float(tvec[2]) * 100  # cm
                self.target_gui.dist_label.config(text=f"[ArUco] Distance: {distance:.2f} cm")

                return distance
        else:
            self.target_gui.dist_label.config(text="[ArUco] No marker visible")
            return None

    def distance_by_pinhole(self, camera_matrix, w, h):
        W_real = float(self.target_gui.entry_width.get()) if self.target_gui.entry_width.get() else 20.5
        H_real = float(self.target_gui.entry_height.get()) if self.target_gui.entry_height.get() else 27.5
        scale_x = 640 / self.target_gui.panel_width
        scale_y = 480 / self.target_gui.panel_height
        w_scaled = w * scale_x if w else 0
        h_scaled = h * scale_y if h else 0

        if w_scaled > 0 and h_scaled > 0:
            fx = camera_matrix[0, 0]
            fy = camera_matrix[1, 1]
            dist_width = (fx * W_real) / w_scaled
            dist_height = (fy * H_real) / h_scaled
            distance = (dist_width + dist_height) / 2
            self.target_gui.dist_label.config(text=f"[Pinhole] Distance: {distance:.2f} cm")
            return distance
        else:
            self.target_gui.dist_label.config(text="[Pinhole] No object detected")
            return None


    def distance_by_hand(self, w ,h):
        if w and h and self.target_gui.w_det and self.target_gui.h_det:
            area = w * h
            area_det = self.target_gui.w_det * self.target_gui.h_det
            diff_area = area - area_det
            self.target_gui.dist_label.config(text=f"Area Error: {diff_area}")
            if diff_area < 0:
                return math.sqrt(abs(diff_area))
            else:
                return -math.sqrt(abs(diff_area))
        else:
            return None
        

    def start(self):

        while self.running:
        
            if self.target_gui.controller.is_connected:

                mode = self.target_gui.opt_dist_method.get()

                if mode == "Distance by ratio" and self.target_gui.object_center is not None:
                    
                    self.target_gui.distance = self.distance_by_ratio(self.target_gui.img_display, 
                                                self.target_gui.object_center, self.target_gui.w, self.target_gui.h)
                elif mode == "Distance by ArUco":
                    
                    self.target_gui.distance = self.distance_by_aruco(self.target_gui.gray_highres, self.target_gui.img_contour, 
                                                self.target_gui.camera_matrix, self.target_gui.dist_coeffs)
                
                elif mode == "Distance by pinhole":
                    
                    self.target_gui.distance = self.distance_by_pinhole(self.target_gui.camera_matrix, self.target_gui.w, self.target_gui.h)
               
                elif mode == "Manual distance":
                    
                    self.target_gui.distance = self.distance_by_hand(self.target_gui.w, self.target_gui.h)
                
                else:
                    
                    self.target_gui.dist_label.config(text="No calibration available")
            
            else: 

                    self.target_gui.distance = None

    def stop(self):

        self.running = False