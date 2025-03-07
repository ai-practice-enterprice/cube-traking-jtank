import cv2
import numpy as np
import os
import shutil
from zone_class import Zone

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Main window 
cv2.namedWindow("scherm", cv2.WINDOW_NORMAL)
cv2.resizeWindow("scherm", 1600, 1200)
cv2.moveWindow("scherm", 870, 100)
zones = []

def get_zones():
    global zones
    start = (0, 477)
    area = (160, 240)  # X,Y
    between = 240
    aantal = 3
    row = 2
    colom = 3
    number = 1
    zones_points = []
    for i in range(aantal):
        zone_point = [(start[0], start[1] - area[1]), 
                      (start[0] + area[0], start[1] - area[1]), 
                      (start[0] + area[0], start[1]), 
                      (start[0], start[1])]
        zones_points.append(zone_point)
        start = (start[0] + between, start[1])
    
    for points in zones_points:
        zones.append(Zone(points, number, row, colom))
        number += 1
    
    print(zones)
    ret, frame = cap.read()

def draw_zone(zone, color):
    pts = np.array(zone, np.int32)
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
    overlay = frame.copy()
    cv2.fillPoly(overlay, [pts], color=color)
    alpha = 0.3  # Transparency factor
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

get_zones()

while True:
    ret, frame = cap.read()
    
    for zone in zones:
        # Check for motion detection
        zone.somting_in_zone(frame)
        
        # Draw the zone in red if motion detected
        if zone.motion_detected:
            draw_zone(zone.points, (0, 0, 255))  # Red for motion
        else:
            draw_zone(zone.points, (0, 165, 255))  # Orange for no motion
            
        # Add text to
        center = zone.get_center()
        status_text = "Active" if zone.motion_detection_enabled else "Inactive"
        cv2.putText(frame, f"Zone {zone.number}: {status_text}", 
                   (center[0] - 50, center[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Display frame
    cv2.imshow("scherm", frame)
    
    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    
    # 'q' to quit
    if key == ord('q'):
        break
    
    # '0' to reset all motion detection
    elif key == ord('0'):
        for zone in zones:
            zone.reset_motion()
            
    # Press '5' to toggle motion detection for all zones
    elif key == ord('5'):
        for zone in zones:
            zone.toggle_motion_detection()
    elif key == ord('1'):
            zones[0].toggle_motion_detection()
    elif key == ord('2'):
         zones[0].toggle_motion_detection()
    elif key == ord('3'):
         zones[0].toggle_motion_detection()


cap.release()
cv2.destroyAllWindows()