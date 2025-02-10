import cv2
import numpy as np

# Global variable to store the slider value
slider_value = 1

def on_trackbar(val):
    global slider_value
    slider_value = val
    update_window()

def update_window():
    global slider_value
    # Create a blank image
    img = np.zeros((200, 400, 3), dtype=np.uint8)
    # Put the slider value as text on the image
    cv2.putText(img, f"Slider Value: {slider_value}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # Display the image in the window
    cv2.imshow('Slider Window', img)

# Create a window for the trackbar
cv2.namedWindow('Slider Window')
cv2.createTrackbar('Select Value', 'Slider Window', 40, 6451, on_trackbar)

# Initial update to display the window with the initial slider value
update_window()

# Wait until the user presses the ESC key
while True:
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

# Destroy all windows
cv2.destroyAllWindows()