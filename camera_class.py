import cv2
import time
from threading import Thread
# IMPROVEMENTS =======================================
# consider using the standard python module "threading"
# while Python doesn't use multiple threads under the hood (due to the GIL)
# threading will allow you to improve the usage of 1 single thread
# by keeping every part of the thread busy
# https://realpython.com/intro-to-python-threading/
# https://stackoverflow.com/questions/58293187/opencv-real-time-streaming-video-capture-is-slow-how-to-drop-frames-or-get-sync
# NOTE: it might be that the read part of cv2 is already in it's own thread
# IMPROVEMENTS =======================================


class CameraThreaded():
    def __init__(
        self,
        videoCapture: cv2.VideoCapture,
        fps=30,
        windowName="monitor"
    ):
        self.cameraCapture = videoCapture
        self.cameraCapture.set(cv2.CAP_PROP_BUFFERSIZE,2)
        
        self.FPS = 1/fps
        self.FPS_MS = int(1000*(self.FPS))

        self.windowName = windowName

        # Start frame retrieval thread
        self.thread = Thread(target=self.read_frame, args=())
        self.thread.daemon = True
        self.thread.start()

    def read_frame(self):
        while True:
            if self.cameraCapture.isOpened():
                (self.status, self.frame) = self.cameraCapture.read()
            time.sleep(self.FPS)

    def show_frame(self):
        # draw the image to the main window    
        cv2.imshow(self.windowName, self.frame)
        print("showed frame")
        