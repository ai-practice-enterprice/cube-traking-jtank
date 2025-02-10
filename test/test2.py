
# filepath: /d:/school/openCVmagazijn/test2.py
import cv2
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create a window for trackbars
cv2.namedWindow('Red Mask Adjustments')

# Initialize trackbars for lower_red1
cv2.createTrackbar('Lower H1', 'Red Mask Adjustments', 0, 180, lambda x: None)
cv2.createTrackbar('Lower S1', 'Red Mask Adjustments', 100, 255, lambda x: None)
cv2.createTrackbar('Lower V1', 'Red Mask Adjustments', 50, 255, lambda x: None)

# Initialize trackbars for upper_red1
cv2.createTrackbar('Upper H1', 'Red Mask Adjustments', 10, 180, lambda x: None)
cv2.createTrackbar('Upper S1', 'Red Mask Adjustments', 255, 255, lambda x: None)
cv2.createTrackbar('Upper V1', 'Red Mask Adjustments', 255, 255, lambda x: None)

# Initialize trackbars for lower_red2
cv2.createTrackbar('Lower H2', 'Red Mask Adjustments', 170, 180, lambda x: None)
cv2.createTrackbar('Lower S2', 'Red Mask Adjustments', 100, 255, lambda x: None)
cv2.createTrackbar('Lower V2', 'Red Mask Adjustments', 50, 255, lambda x: None)

# Initialize trackbars for upper_red2
cv2.createTrackbar('Upper H2', 'Red Mask Adjustments', 180, 180, lambda x: None)
cv2.createTrackbar('Upper S2', 'Red Mask Adjustments', 255, 255, lambda x: None)
cv2.createTrackbar('Upper V2', 'Red Mask Adjustments', 255, 255, lambda x: None)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get trackbar positions
    lh1 = cv2.getTrackbarPos('Lower H1', 'Red Mask Adjustments')
    ls1 = cv2.getTrackbarPos('Lower S1', 'Red Mask Adjustments')
    lv1 = cv2.getTrackbarPos('Lower V1', 'Red Mask Adjustments')
    uh1 = cv2.getTrackbarPos('Upper H1', 'Red Mask Adjustments')
    us1 = cv2.getTrackbarPos('Upper S1', 'Red Mask Adjustments')
    uv1 = cv2.getTrackbarPos('Upper V1', 'Red Mask Adjustments')
    lh2 = cv2.getTrackbarPos('Lower H2', 'Red Mask Adjustments')
    ls2 = cv2.getTrackbarPos('Lower S2', 'Red Mask Adjustments')
    lv2 = cv2.getTrackbarPos('Lower V2', 'Red Mask Adjustments')
    uh2 = cv2.getTrackbarPos('Upper H2', 'Red Mask Adjustments')
    us2 = cv2.getTrackbarPos('Upper S2', 'Red Mask Adjustments')
    uv2 = cv2.getTrackbarPos('Upper V2', 'Red Mask Adjustments')

    lower_red1 = np.array([lh1, ls1, lv1])
    upper_red1 = np.array([uh1, us1, uv1])
    lower_red2 = np.array([lh2, ls2, lv2])
    upper_red2 = np.array([uh2, us2, uv2])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    cv2.imshow('Original', frame)
    cv2.imshow('Red Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()