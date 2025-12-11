import asyncio
import json

import cv2
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame
import fractions
from datetime import datetime

from aiortc import VideoStreamTrack
from av import VideoFrame
import fractions
import cv2

class CustomVideoStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.frame_count = 0
        self.latest_frame_display = None   # frame principal
        self.latest_img_contour = None     # frame procesado
        self.lock = asyncio.Lock()         # para evitar race conditions

    async def recv(self):
        self.frame_count += 1

        async with self.lock:
            if self.latest_frame_display is None:
                # si aún no hay frame, espera un poco
                await asyncio.sleep(0.01)
                return await self.recv()
            
            # Preparar frame para WebRTC
            frame = cv2.cvtColor(self.latest_frame_display, cv2.COLOR_BGR2RGB)
            video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
            video_frame.pts = self.frame_count
            video_frame.time_base = fractions.Fraction(1, 30)
            return video_frame

    async def update_frames(self, frame_display, img_contour):
        """Se llama desde GUI.update_frame() para actualizar los frames"""
        async with self.lock:
            self.latest_frame_display = frame_display.copy()
            self.latest_img_contour = img_contour.copy()
