import cv2

import cv2
import numpy as np

# Initialize QR code detector
qr_detector = cv2.QRCodeDetector()

# Initialize webcam (met CAP_DSHOW voor Windows)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    # Lees frame van webcam
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detecteer en decodeer meerdere QR codes
    ret_qr, decoded_info, points, straight_qr = qr_detector.detectAndDecodeMulti(frame)
    if ret_qr:
        # Loop door alle gedetecteerde QR codes
        for i in range(len(decoded_info)):
            # Controleer of de data niet leeg is
            if decoded_info[i]:
                # Converteer punten naar integers
                qr_points = np.array(points[i], dtype=np.int32)
                
                # Teken bounding box rond QR code
                cv2.polylines(frame, [qr_points], isClosed=True, color=(0, 255, 0), thickness=2)
                
                # Bereken middenpunt voor tekst
                center_x = int(qr_points[:, 0].mean())
                center_y = int(qr_points[:, 1].mean())
                
                # Plaats tekst in het midden
                cv2.putText(frame, decoded_info[i], 
                           (center_x , center_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 0, 255), 2)
    
    # Toon resultaat
    cv2.imshow('QR Code Tracker', frame)
    
    # Stop met 'q' toets
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Opruimen
cap.release()
cv2.destroyAllWindows()