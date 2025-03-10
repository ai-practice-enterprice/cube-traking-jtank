import cv2
import numpy as np
import os
import shutil
import httpx
from zone_class import Zone

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
    keyPressMapping: dict[str,str]
):
    while cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) >= 1:
        ret, frame = cap.read()
        for zone in zones:
            # Check for motion detection
            zone.something_in_zone(frame)
            # Draw the zone in red if motion detected
            if zone.motion_detected:
                draw_zone(frame,zone.points, (0, 0, 255))  # Red for motion
            else:
                draw_zone(frame,zone.points, (0, 165, 255))  # Orange for no motion

            # Add text to zones
            center = zone.get_center()
            status_text = "Active" if zone.motion_detection_enabled else "Inactive"
            cv2.putText(frame, f"Zone {zone.number}: {status_text}", 
                    (center[0] - 50, center[1]), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow(windowName, frame)
        
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
        # Handle key presses ==============================================


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
}

cv2.namedWindow(windowName, cv2.WINDOW_KEEPRATIO)
get_zones(zones)

if __name__ == '__main__':
    main(zones,cap,waitTime,windowName,keyPressMapping)

cv2.destroyAllWindows()
cv2.waitKey(1)