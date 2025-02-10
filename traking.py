import cv2
import numpy as np
import os
import shutil
from box_class import Box
from zone_class import Zone

cap = cv2.VideoCapture(0)

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
point_tolerance = 42 # als de punten binnen een tolerantie van de oude punten vallen worden ze genegeert (om flikeren en onnodige berekekningen te voor kommen)
blur = 5 #moet onneven getal zijn voor de fucie GaussianBlur (aders geeft die een error)
old_gem_points=[]
list_points=[]
points = []
gem=4
error_rate_mem=8
error_rate=0
#imgage folder
folder='extracted_boxes'
# Initialisatie variabelen
sqares = []
boxes=[]
zones=[]
#globale debug vaiable
sucess=1
fail=1
max_slider=0
slider_box=0
slider_filter=0
slider_zone=0

def display_images_in_grid(folder, grid_size=(3, 3), window_name="Image Grid"):
    # Get list of all PNG files in the folder
    image_files = [f for f in os.listdir(folder) if f.endswith('.png')]
    
    # Calculate the number of rows and columns for the grid
    rows, cols = grid_size
    num_images = len(image_files)
    size=150
    # Read images and resize them to fit in the grid
    images = []
    for image_file in image_files:
        img = cv2.imread(os.path.join(folder, image_file))
        if img is not None:
            img = cv2.resize(img, (size,size))
            images.append(img)
    # Create a blank canvas for the grid
    grid_height = rows * size
    grid_width = cols * size
    grid_image = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)
    
    # Place images in the grid
    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        y_offset = row * size
        x_offset = col * size
        grid_image[y_offset:y_offset+img.shape[0], x_offset:x_offset+img.shape[1]] = img
        
    # Display the grid
    cv2.imshow(window_name, grid_image)
    cv2.moveWindow(window_name, 50, 730)
def update_boxes(sqares):
    global boxes
    boxes=[]
    rat,frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    for index, sqare in enumerate(sqares, start=1):
        box_mask(frame, sqare, index)
        if cv2.getWindowProperty("Image Grid", cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow("Image Grid")
        display_images_in_grid(folder)
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
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        cap.release()
        cv2.destroyAllWindows()
        exit()
    if slider_filter == 0:
        display_frame = frame.copy()
    elif slider_filter == 1:
        if mask is not None:
            display_frame = cv2.bitwise_and(frame, frame, mask=mask)
        else:
            display_frame = frame.copy()
    elif slider_filter == 2:
        if mask is not None:
            display_frame = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        else:
            display_frame = frame.copy()
    elif slider_filter == 3:
        display_frame = hsv.copy()
    cv2.imshow("scherm", display_frame)
def box_mask(frame, points,number):
    # Check if the folder exists
    if os.path.exists(folder):
        if number==1:
            # clear the folder
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        # If it does not exist, create the folder
        os.makedirs(folder)
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(points, dtype=np.int32)], 255)
    roi = cv2.bitwise_and(frame, frame, mask=mask)
    x, y, w, h = cv2.boundingRect(np.array(points, dtype=np.int32))
    cropped_box = roi[y:y+h, x:x+w]
    output_path=f"{folder}/extracted_box{number}.png"
    cv2.imwrite(output_path, cropped_box)
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
def are_points_within_tolerance(list1, list2, tolerance):
    if len(list1) != len(list2):
        return False
    tolerance_sq = tolerance ** 2
    for (x1, y1), (x2, y2) in zip(list1, list2):
        dx = x1 - x2
        dy = y1 - y2
        distance_sq = dx ** 2 + dy ** 2
        if distance_sq > tolerance_sq:
            return False
    return True
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
        raise ValueError(f"No valid squares arrangement found. number of points got {len(points)}")
    
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
    cv2.putText(frame, f"X:{box.center[0]},Y:{box.center[1]},N:{box.number}", (box.center[0]-45, box.center[1]+45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

def draw_debug(sqares):
    global sucess, fail,max_slider,slider_box
    text_size=0.6
    debug_frame = cv2.imread('debug.png')# :) fun
    cv2.putText(debug_frame, f"points: {len(points)}", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    cv2.putText(debug_frame, f"cubes: {len(sqares)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX,text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    cv2.putText(debug_frame, f"error rate points: {error_rate}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    totaal=sucess+fail
    key = cv2.waitKey(120) & 0xFF
    if key == ord('e'):
        sucess = 1
        fail = 1
    cv2.putText(debug_frame, f"sucess: {sucess-1} {round((sucess/totaal)*100)}%  fail: {fail-1} {round((fail/totaal)*100)}% totaal:{totaal} ", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    if slider_box == len(sqares)+1:
        cv2.putText(debug_frame, f"selected: all", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    elif slider_box !=0 and len(boxes)>=slider_box:
        cv2.putText(debug_frame, f"Box:{slider_box} UL{sqares[slider_box-1][0]},UR{sqares[slider_box-1][1]},DL{sqares[slider_box-1][2]},DR{sqares[slider_box-1][0]}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)
    else:
        cv2.putText(debug_frame, f"selected: none", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 0, 0), round(text_size), cv2.LINE_AA)

    if max_slider != len(sqares):
        max_slider=len(sqares)
        debug_window(max_slider+1)

    cv2.imshow("debug", debug_frame)
def debug_window(max):
    global slider_box
    if cv2.getWindowProperty("debug", cv2.WND_PROP_VISIBLE) >= 1:
        cv2.destroyWindow("debug")
    cv2.namedWindow("debug", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("debug", 800, 600)
    cv2.moveWindow("debug", 50, 100)
    cv2.createTrackbar('box', 'debug', max, max, lambda x: update_slider(x,1))
    cv2.createTrackbar('filter', 'debug', 0, 3, lambda x: update_slider(x,2))
    cv2.createTrackbar('zone', 'debug', 3, 3, lambda x: update_slider(x,3))

def update_slider(val, select):
    global slider_box, slider_filter, slider_zone
    if select == 1:
        slider_box = val
    elif select == 2:
        slider_filter = val
    elif select == 3:
        slider_zone = val

def get_solution():
    for zone in sub
get_zones()
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frame = cv2.GaussianBlur(frame, (blur, blur), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    points = get_points(frame, mask_red)
    if len(list_points)<gem:
        if len(points) % 4 == 0 :
            if len(list_points)==0 or (len(points) == len(list_points[-1]) and are_points_within_tolerance(points, list_points[-1],point_tolerance)) :
                list_points.append(points)
                error_rate=error_rate_mem
            else:
                error_rate-=1
                if error_rate==0:
                    list_points=[]
                    error_rate=error_rate_mem
    else  :
        transposed = list(zip(*list_points))
        gem_points = []
        for groep in transposed: # het gemidelde uitreken van de gem points
            # Verzamel alle x- en y-punten voor de huidige groep
            x_points = [t[0] for t in groep]
            y_points = [t[1] for t in groep]

            # Bereken het gemiddelde voor x en y
            gem_x = sum(x_points) / len(x_points)
            gem_y = sum(y_points) / len(y_points)

            # Voeg het gemiddelde toe als tuple (gecast naar integers)
            gem_points.append((int(gem_x), int(gem_y)))
        list_points=[]
        error_rate=error_rate_mem
        if len(old_gem_points) == 0 or not are_points_within_tolerance(old_gem_points,gem_points,point_tolerance):
            try:
                sqares=[]
                arrange_squares(sqares,gem_points)
                update_boxes(sqares)
                old_gem_points=gem_points
                # print(boxes)
                sucess+=1
            except Exception as e:
                print(f"Error: {e}")
                fail+=1

    for zone in zones:
        if slider_zone ==1 or slider_zone==3:
            draw_zone(zone.points,(0, 165, 255))
        if slider_zone ==2 or slider_zone==3:
            for x in zone.corect_boxes:
               draw_zone(zone.subzones[x[1]],(0,255,0))
            for x in zone.incorect_boxes:
               draw_zone(zone.subzones[x[1]],(0,0,255))
    if slider_box == len(boxes)+1:
        for box in boxes:
                draw_box(frame, box)
    elif slider_box !=0 and len(boxes)>=slider_box:
         draw_box(frame, boxes[slider_box-1])
    draw_debug(sqares)
    filter(frame, hsv, mask_red)
cap.release()
cv2.destroyAllWindows()