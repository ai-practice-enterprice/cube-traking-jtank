import cv2
import numpy as np
import os
import shutil
from zone_class import Zone

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#Main window 
cv2.namedWindow("scherm", cv2.WINDOW_NORMAL)
cv2.resizeWindow("scherm", 1600, 1200)
cv2.moveWindow("scherm", 870, 100)
zones=[]


    
def get_zones():
    global zones
    start=(0,477)
    area=(160,240)#X,Y
    between=240
    aantal=3
    row=2
    colom=3
    number=1
    zones_points=[]
    for i in range(aantal):
        zone_point=[(start[0],start[1]-area[1]),(start[0]+area[0],start[1]-area[1]),(start[0]+area[0],start[1]),(start[0],start[1])]
        zones_points.append(zone_point)
        start= (start[0]+between,start[1])
    for points in zones_points:
     zones.append(Zone(points,number,row,colom))
     number+=1
    print(zones)
    ret, frame = cap.read()
    set_zone_color(frame,zones)
def set_zone_color(frame,zones):
    for zone  in zones:
        zone.calculate_subzone_colors(frame,True)
        print(zone.subzone_colors_cal)


def draw_zone(zone,color):
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
            draw_zone(zone.points,(0, 165, 255))
            zone.somting_in_zone(frame)
            for x in zone.active_subzones:
               print(zone.active_subzones)
            #    draw_zone(zone.active_subzones[x[0]],(0,255,0))
    cv2.imshow("scherm",frame)
    cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()