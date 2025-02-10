import cv2
import numpy as np
import copy

cap = cv2.VideoCapture(0)
filternum = 0

#window 
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
Threshold = 50
blur = 5
# Initialisatie variabelen
old_frame = []
points = []
sqares = []
count_point=0
camera_dictance=120
def filter(frame, hsv, mask):
    global filternum
    key = cv2.waitKey(1) & 0xFF
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
        raise ValueError("The number of points must be divisible by 4.")
    
    def is_square(points, tolerance=2500):
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
    result_2d_array.extend(ordered_squares)
    return result_2d_array

def draw_square(frame, square, corner=(0, 255, 0), center=(255, 0, 0), dia=2):
    mx, my = 0, 0
    for point in square:
        cv2.circle(frame, point, dia, corner, -1)
        mx += point[0]
        my += point[1]
    if len(square) == 4:
        mx //= 4
        my //= 4
        cv2.circle(frame, (mx, my), dia+1, center, -1)
        cv2.putText(frame, f"X:{mx},Y:{my}", (mx-45, my+45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

def draw_ui(frame,sqares):
    cv2.putText(frame, f"cubes:{sqares}", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, f"camera distance ", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    frame = cv2.GaussianBlur(frame, (blur, blur), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    
    # Bewegingsdetectie
    if len(old_frame) == 0:
        old_frame = frame.copy()
        for _ in range(gem): #hier neem ik een gemidelde van (gem)aantal frames om ruis weg te werken 
            ret, frame = cap.read()
            if not ret:
                break
            frames=[]
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            frame = cv2.GaussianBlur(frame, (blur, blur), 0)
            frames.append(frame)
        frame=np.average(frames, axis=0).astype(np.uint8)
        backup_sqare=copy.deepcopy(sqares)
        points = get_points(frame, mask_red)
        try:
            sqares=[]
            arrange_squares(sqares,points)
            count_point=len(points)
        except Exception as e:
            sqares=copy.deepcopy(backup_sqare)
            print(f"Error: {e}")
    diff = cv2.absdiff(frame, old_frame)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh_diff = cv2.threshold(gray_diff, Threshold, 255, cv2.THRESH_BINARY)
    
    if np.sum(thresh_diff) > 0:
        old_frame = frame.copy()
        backup_sqare=copy.deepcopy(sqares)
        points = get_points(frame, mask_red)
        if len(points) <= (count_point + 8):
            try:
                sqares=[]
                arrange_squares(sqares,points)
            except Exception as e:
                sqares=copy.deepcopy(backup_sqare)
                old_frame=[]
                print(f"Error: {e}")
    for square in sqares:
        if len(square) == 4:
            draw_square(frame, square)
    # draw_ui(frame,len(sqares))
    filter(frame, hsv, mask_red)
cap.release()
cv2.destroyAllWindows()