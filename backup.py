import cv2
import numpy as np
import copy
from box_class import Box
from zone_class import Zone

cap = cv2.VideoCapture(0)
filternum = 0

#Main window 
cv2.namedWindow("scherm", cv2.WINDOW_NORMAL)
cv2.resizeWindow("scherm", 1600, 1200)
cv2.moveWindow("scherm", 870, 100)

# Rode kleurbereiken
lower_red1 = np.array([0, 95, 40])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 95, 40])
upper_red2 = np.array([180, 255, 255])


# deze variable dienen om ruis weg te krijgen en stabiel te kunen tracken
gem = 6
Threshold = 50# voor motion dedection
point_tolerance = 10 # als de punten binnen een tolerantie van de oude punten vallen worden ze genegeert (om flikeren en onnodige berekekningen te voor kommen)
blur = 5 #moet onneven getal zijn voor de fucie GaussianBlur (aders geeft die een error)
Can_tringer=True
tringer=20
count_tinger=tringer
# Initialisatie variabelen
old_points=[]
points = []
sqares = []
boxes=[]
zones=[]
camera_dictance=120 #nog niet in gebruik is voor later om irl maten om te zetten naar digitale maten
#globale debug vaiable
sucess=1
fail=1
max_slider=0
slider_val=0

def update_boxes(sqares):
    global boxes
    boxes=[]
    ret, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    for sqare in sqares:
        box = Box(sqare, 1)  # dit numer later nog veranderen naar het nummer van de box
        # box = Box(sqare, get_box_digit(box_mask(frame, sqare)))
        boxes.append(box)
    for zone in zones:
        zone.boxes_in_zone(boxes)

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
def filter(frame, hsv, mask):
    global filternum
    key = cv2.waitKey(3) & 0xFF
    if key == ord('w'):
        filternum = (filternum + 1) % 4
    elif key == ord('s'):
        filternum = (filternum - 1) % 4
    elif key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()
        
    if filternum == 0:
        display_frame = frame.copy()
    elif filternum == 1:
        if mask is not None:
            display_frame = cv2.bitwise_and(frame, frame, mask=mask)
        else:
            display_frame = frame.copy()
    elif filternum == 2:
        if mask is not None:
            display_frame = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        else:
            display_frame = frame.copy()
    elif filternum == 3:
        display_frame = hsv.copy()
    
    cv2.imshow("scherm", display_frame)
def box_mask(frame, points, output_path='extracted_roi.png'):
    # Create a mask for the ROI
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], 255)

    # Apply the mask to the frame
    roi = cv2.bitwise_and(frame, frame, mask=mask)

    # Find the bounding box of the ROI
    x, y, w, h = cv2.boundingRect(np.array(points, dtype=np.int32))

    # Crop the ROI from the frame
    cropped_roi = roi[y:y+h, x:x+w]

    # Save the extracted ROI
    cv2.imwrite(output_path, cropped_roi)
def motion_detection():
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    if not ret:
        print("Failed to read frames")
        cap.release()
        return 0

    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, Threshold, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # print(1)
        return True
    else:
        # print(0)
        return False
def get_points(frame, mask):
    points = []
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 15:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                points.append((cX, cY))
                # cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
    return points

def arrange_squares(result_2d_array, points):
    if len(points) % 4 != 0:
        raise ValueError(f"The number of points must be divisible by 4. number of points got {len(points)}")
    
    def is_square(points, tolerance=1800):
        if len(points) != 4:
            return False
        dists = []
        for i in range(4):
            for j in range(i+1, 4):
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist_sq = dx*dx + dy*dy
                dists.append(dist_sq)
        dists.sort()
        if len(dists) < 6:
            return False
        if not all(abs(d - dists[0]) < tolerance for d in dists[:4]):
            return False
        if not (abs(dists[4] - dists[5]) < tolerance and abs(dists[4] - 2*dists[0]) < tolerance):
            return False
        return True
    
    from itertools import combinations
    possible_squares = []
    for quad in combinations(points, 4):
        if is_square(quad):
            possible_squares.append(quad)
    
    used = set()
    solution = []
    all_points_set = set(points)
    
    def backtrack():
        nonlocal used, solution
        if len(used) == len(all_points_set):
            return True
        for square in possible_squares:
            square_set = set(square)
            if square_set.isdisjoint(used):
                used.update(square_set)
                solution.append(square)
                if backtrack():
                    return True
                used.difference_update(square_set)
                solution.pop()
        return False
    
    if not backtrack():
        raise ValueError("No valid squares arrangement found.")
    
    ordered_squares = []
    for sq in solution:
        sorted_sq = sorted(sq, key=lambda p: (p[1], p[0]))  # Sort by y then x
        ordered_squares.append(sorted_sq)
    ordered_squares.sort(key=lambda x: (x[0][1], x[0][0]))  # Sort squares by upper-left (y, x)
    # Verander de volgorde van de hoeken naar UL, UR, DL, DR
    for square in ordered_squares:
        ul = square[0]
        ur = square[1]
        dl = square[3]
        dr = square[2]
        square[0], square[1], square[2], square[3] = ul, ur, dl, dr
    result_2d_array.extend(ordered_squares)
    return result_2d_array
def draw_zone(zone,color):
    pts = np.array(zone, np.int32)
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
    overlay = frame.copy()
    cv2.fillPoly(overlay, [pts], color=color)
    alpha = 0.3  # Transparency factor
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
def draw_box(frame, box, corner=(0, 255, 0), center=(255, 0, 0), dia=2):
    for point in box.points:
        cv2.circle(frame, point, dia, corner, -1)
    cv2.circle(frame,box.center, dia+1, center, -1)
    cv2.putText(frame, f"X:{box.center[0]},Y:{box.center[1]}", (box.center[0]-45, box.center[1]+45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

def draw_debug(sqares):
    global sucess, fail,max_slider,slider_val
    text_size=0.6
    debug_frame = cv2.imread('debug.png')# :) fun
    cv2.putText(debug_frame, f"points: {len(points)}", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    cv2.putText(debug_frame, f"cubes: {len(sqares)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX,text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    cv2.putText(debug_frame, f"camera distance: {camera_dictance}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    totaal=sucess+fail
    key = cv2.waitKey(1) & 0xFF
    if key == ord('e'):
        sucess = 1
        fail = 1
    cv2.putText(debug_frame, f"sucess: {sucess-1} {round((sucess/totaal)*100)}%  fail: {fail-1} {round((fail/totaal)*100)}% totaal:{totaal} ", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    if slider_val == len(sqares)+1:
        cv2.putText(debug_frame, f"selected: all", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    elif slider_val !=0:
        cv2.putText(debug_frame, f"Box:{slider_val} UL{sqares[slider_val-1][0]},UR{sqares[slider_val-1][1]},DL{sqares[slider_val-1][2]},DR{sqares[slider_val-1][0]}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    else:
        cv2.putText(debug_frame, f"selected: none", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)

    if max_slider != len(sqares):
        max_slider=len(sqares)
        debug_window(max_slider+1)

    cv2.imshow("debug", debug_frame)
def debug_window(max):
    global slider_val
    if cv2.getWindowProperty("debug", cv2.WND_PROP_VISIBLE) >= 1:
        cv2.destroyWindow("debug")
    cv2.namedWindow("debug", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("debug", 800, 600)
    cv2.moveWindow("debug", 50, 100)
    cv2.createTrackbar('Select Square', 'debug', 0, max, lambda x: update_slider(x))
def update_slider(val):
    global slider_val
    slider_val = val
get_zones()
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frame = cv2.GaussianBlur(frame, (blur, blur), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)

    if motion_detection():
        Can_tringer=True
        count_tinger=tringer
    else:
        if count_tinger!=0:
            count_tinger-=1
        if Can_tringer and count_tinger==0:
            Can_tringer=False
            backup_sqare=copy.deepcopy(sqares)
            points = get_points(frame, mask_red)
            use_points = True
            if len(old_points) == len(points):
                for p1, p2 in zip(points, old_points):
                    if abs(p1[0] - p2[0]) > point_tolerance or abs(p1[1] - p2[1]) > point_tolerance:
                        use_points = False
                        break
            if use_points==True and (len(points)%4)==0:
                try:
                    sqares=[]
                    arrange_squares(sqares,points)
                    update_boxes(sqares)
                    print(boxes)
                    sucess+=1
                except Exception as e:
                    sqares=copy.deepcopy(backup_sqare)
                    Can_tringer=True
                    count_tinger=tringer
                    print(f"Error: {e}")
                    fail+=1
            else:
                 Can_tringer=True
                 count_tinger=tringer
    for zone in zones:
        draw_zone(zone.points,(0, 165, 255))
        for x in zone.corect_boxes:
           draw_zone(zone.subzones[x[1]],(0,255,0))
        for x in zone.incorect_boxes:
           draw_zone(zone.subzones[x[1]],(0,0,255))
    if slider_val == len(boxes)+1:
        for box in boxes:
                draw_box(frame, box)
    elif slider_val !=0:
         draw_box(frame, boxes[slider_val-1])
    draw_debug(sqares)
    filter(frame, hsv, mask_red)
cap.release()
cv2.destroyAllWindows()