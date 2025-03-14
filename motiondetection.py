import cv2
import numpy as np
import httpx
BASE_URL = "http://localhost:8000/camera" #server addres
# import httpx
from zone_class import Zone

import threading # to add (perhaps) will look in to it :)
def update_server(zone_data):
    response = httpx.post(f"{BASE_URL}/zoneinfo", json=zone_data)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.text)
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
    #ini
    for zone in zones:
        update_server({"id": zone.id, "status": zone.motion_detection_enabled, "detection": zone.motion_detected})
    while cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) >= 1:
        ret, frame = cap.read()
        # Handle each zone detection ==============================================
        for index,zone in enumerate(zones):
            # Check for motion detection
            mem=zone.motion_detected
            zone.something_in_zone(frame)
            # Draw the zone in red if motion detected
            if zone.motion_detected:
                draw_zone(frame,zone.points, (0, 0, 255))  # Red for motion
                if mem==False:
                    update_server({"id": zone.id, "status": True, "detection": True})
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
        if key == ord(keyPressMapping["reset"]):
            for zone in zones:
                zone.reset_motion()
                update_server({"id": zone.id, "status": zone.motion_detection_enabled, "detection": zone.motion_detected})
        # Press '5' to toggle motion detection for all zones
        elif key == ord(keyPressMapping["toggle zones"]):
            for zone in zones:
                zone.toggle_motion_detection()
                update_server({"id": zone.id, "status": zone.motion_detection_enabled, "detection": zone.motion_detected})

        elif key == ord(keyPressMapping["toggle zone 1"]):
            zones[0].toggle_motion_detection()
            update_server({"id": zones[0].id, "status": zones[0].motion_detection_enabled, "detection": zones[0].motion_detected})
        elif key == ord(keyPressMapping["toggle zone 2"]):
            zones[1].toggle_motion_detection()
            update_server({"id": zones[1].id, "status": zones[1].motion_detection_enabled, "detection": zones[1].motion_detected})
            update_server({"id": zone.id, "status": True, "detection": True})
        elif key == ord(keyPressMapping["toggle zone 3"]):
            zones[2].toggle_motion_detection()
            update_server({"id": zones[2].id, "status": zones[2].motion_detection_enabled, "detection": zones[2].motion_detected})
        # Press 'a' to let the zones reset their motion state automatically
        elif key == ord(keyPressMapping["toggle reset motion auto"]):
            automaticZoneToggle = not automaticZoneToggle
        # Handle key presses ==============================================

<<<<<<< HEAD
# if multiple camera's connected change this to the required value
# e.g.: 
# - webcam == 1
# - Xbox Kinect == 2
# - add camera == 3
# - etc...
# these values might/might not be a one-on-one copy of your devices seen in your device manager of your OS 
cap = cv2.VideoCapture(1)
=======
# next up implement mulie cam (forgot webcam on school)



cap = cv2.VideoCapture(0)
>>>>>>> b1a2112b371bd7958a2bde30d214e3dcb736337b
zones = []
windowName = "Monitor"
waitTime = 20
keyPressMapping = {
    "reset" : '0',
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