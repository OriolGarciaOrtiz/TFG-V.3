from HexsoonGUI import GUI
import cv2
import numpy as np
import time
import tkinter as tk
import queue

class ServiceVideo:

    def __init__(self, target_gui: GUI):
        
        self.target_gui = target_gui

        self.running: bool = False


    def start(self):

        while self.running:
            
            try:

                # Get frames from queue
                if not self.target_gui.video_queue.empty():
                    original_frame, detected_frame = self.target_gui.video_queue.get(timeout=0.1)

                    # Convert frames for display
                    frames_to_show = []
                    for frame in [original_frame, detected_frame]:
                        if frame is not None:
                            # Convert BGR to RGB for PIL if needed
                            if len(frame.shape) == 3 and frame.shape[2] == 3:
                                try:
                                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                except:
                                    pass
                            frames_to_show.append(frame)
                        else:
                            # Create black frame as placeholder
                            black_frame = np.zeros((self.target_gui.controller.panel_height, self.target_gui.controller.panel_width, 3),
                                                   dtype=np.uint8)
                            frames_to_show.append(black_frame)

                    # Get mission planner frame from stored attribute
                    mission_frame = getattr(self.target_gui, 'mission_frame', None)

                    if mission_frame is None:
                        # Show placeholder if no mission frame available
                        mission_frame = np.zeros((self.target_gui.misson_panel_width, self.target_gui.misson_panel_heigth, 3), dtype=np.uint8)
                        cv2.putText(mission_frame, "Mission Planner not found",
                                    (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                    else:
                        mission_frame = cv2.cvtColor(mission_frame, cv2.COLOR_BGR2RGB)

                    frames_to_show.append(mission_frame)

                    self.target_gui.frames_to_show = frames_to_show

                time.sleep(1/self.target_gui.FPS)

            except tk.TclError:
                break
            except queue.Empty:
                time.sleep(1/self.target_gui.FPS)
            except Exception as e:
                print("Video thread error: {e}")
                time.sleep(1/self.target_gui.FPS)
