import cv2
import numpy as np
import os
import shutil
import httpx
from zone_class import Zone

import threading # to add (perhaps)
# IMPROVEMENTS =======================================
# consider using the standard python module "threading"
# while Python doesn't use multiple threads under the hood (due to the GIL)
# threading will allow you to improve the usage of 1 single thread
# by keeping every part of the thread busy
# https://realpython.com/intro-to-python-threading/
# IMPROVEMENTS =======================================

def get_zones(
    zones: list,
    start: tuple[int,int] = (0, 477),
    area: tuple[int,int] = (160, 240),  # X,Y
    between: int = 240,
    number_of_zones: int = 3,
    row: int = 2,
    colom: int = 3,
    number: int = 1,
    zones_points: list = []
):
    for i in range(number_of_zones):
        zone_point = [
            (start[0], start[1] - area[1]), 
            (start[0] + area[0], start[1] - area[1]), 
            (start[0] + area[0], start[1]), 
            (start[0], start[1])
        ]
        zones_points.append(zone_point)
        start = (start[0] + between, start[1])
    
    for points in zones_points:
        zones.append(Zone(points, number, row, colom))
        number += 1
    
    print(zones)

def draw_zone(frame, zone, color):
    pts = np.array(zone, np.int32)
    overlay = frame.copy()
    alpha = 0.3  # Transparency factor

    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
    cv2.fillPoly(overlay, [pts], color=color)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def main(
    zones: list[Zone], 
    cap: cv2.VideoCapture,
    waitTime: 500,
    windowName: str,
    keyPressMapping: dict[str,str],
    automaticZoneToggle: bool = False,
):
    while cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) >= 1:
        ret, frame = cap.read()
        # Handle each zone detection ==============================================
        for zone in zones:
            # Check for motion detection
            zone.something_in_zone(frame)
            # Draw the zone in red if motion detected
            if zone.motion_detected:
                draw_zone(frame,zone.points, (0, 0, 255))  # Red for motion
            else:
                draw_zone(frame,zone.points, (0, 165, 255))  # Orange for no motion
        # Handle each zone detection ==============================================

        # draw the image to the main window        
        cv2.imshow(windowName, frame)

        # if enabled will handle the ressetting of all zones automatically
        if automaticZoneToggle:
            for zone in zones:
                zone.reset_motion()
        
        # Handle key presses ==============================================
        key = cv2.waitKey(waitTime) & 0xFF
        # '0' to reset all motion detection
        if key == ord(keyPressMapping["quit"]):
            for zone in zones:
                zone.reset_motion()
        # Press '5' to toggle motion detection for all zones
        elif key == ord(keyPressMapping["toggle zones"]):
            for zone in zones:
                zone.toggle_motion_detection()
        elif key == ord(keyPressMapping["toggle zone 1"]):
            zones[0].toggle_motion_detection()
        elif key == ord(keyPressMapping["toggle zone 2"]):
            zones[1].toggle_motion_detection()
        elif key == ord(keyPressMapping["toggle zone 3"]):
            zones[2].toggle_motion_detection()
        # Press 'a' to let the zones reset their motion state automatically
        elif key == ord(keyPressMapping["toggle reset motion auto"]):
            automaticZoneToggle = not automaticZoneToggle
        # Handle key presses ==============================================

# if multiple camera's connected change this to the required value
# e.g.: 
# - webcam == 1
# - Xbox Kinect == 2
# - add camera == 3
# - etc...
# these values might/might not be a one-on-one copy of your devices seen in your device manager of your OS 
cap = cv2.VideoCapture(0)
zones = []
windowName = "Monitor"
waitTime = 20
keyPressMapping = {
    "quit" : '0',
    "toggle zones" : '5',
    "toggle zone 1" : '1',
    "toggle zone 2" : '2',
    "toggle zone 3" : '3',
    "toggle reset motion auto" : 'a',
}

cv2.namedWindow(windowName, cv2.WINDOW_KEEPRATIO)
get_zones(zones)

if __name__ == '__main__':
    main(zones,cap,waitTime,windowName,keyPressMapping)

cv2.destroyAllWindows()
cv2.waitKey(1)