import numpy as np
import cv2

class Zone:
    def __init__(self, points, id, row, col):
        self.points = points
        self.id = id
        self.motion_detected = False
        self.motion_detection_enabled = True
        self.motion_threshold = 650000  # Adjustable threshold
    
    def get_center(self):
        center_x = sum(p[0] for p in self.points) // len(self.points)
        center_y = sum(p[1] for p in self.points) // len(self.points)
        return (center_x, center_y)
        
    def something_in_zone(self, frame):
        # Skip if motion detection is disabled
        if not self.motion_detection_enabled:
            return
            
        # current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # If this is the first call, initialize previous frame
        if not hasattr(self, 'prev_gray'):
            self.prev_gray = gray
            return
        
        # Create mask for the zone
        mask = np.zeros_like(gray)
        points_array = np.array(self.points, np.int32)
        cv2.fillPoly(mask, [points_array], 255)
        
        # Calculate absolute difference between current and previous frames
        # But only in the zone area using the mask
        frame_diff = cv2.absdiff(gray, self.prev_gray)
        frame_diff = cv2.bitwise_and(frame_diff, frame_diff, mask=mask)
        
        # Apply threshold to difference
        _, thresh = cv2.threshold(frame_diff, 20, 255, cv2.THRESH_BINARY)
        
        # Calculate motion score (sum of thresholded pixels)
        motion_score = np.sum(thresh)
        
        # Check if motion score exceeds threshold
        if motion_score > self.motion_threshold:
            self.motion_detected = True
        
        # Update previous frame for next comparison
        self.prev_gray = gray
        
    def reset_motion(self):
        self.motion_detected = False
        
    def toggle_motion_detection(self):
        self.motion_detection_enabled = not self.motion_detection_enabled
        if not self.motion_detection_enabled:
            self.motion_detected = False