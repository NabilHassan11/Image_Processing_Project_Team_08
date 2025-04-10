import cv2
import numpy as np
import serial
import time


arduino = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)

purple_lower = np.array([115, 100, 100])  # Shifted toward blue
purple_upper = np.array([135, 255, 255])  # Narrower range


yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([35, 255, 255])

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_purple = cv2.inRange(hsv, purple_lower, purple_upper)
    mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)

    purple_pixels = cv2.countNonZero(mask_purple)
    yellow_pixels = cv2.countNonZero(mask_yellow)

    label = "None"

    if purple_pixels > 500:
        arduino.write(b"RIGHT\n")
        label = "Purple Detected → RIGHT (140°)"
    elif yellow_pixels > 500:
        arduino.write(b"LEFT\n")
        label = "Yellow Detected → LEFT (90°)"
    else:
        arduino.write(b"CENTER\n")
        label = "Center (120°)"

    # Add label to frame
    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Show everything
    cv2.imshow("Frame", frame)
    cv2.imshow("Purple Mask", mask_purple)
    cv2.imshow("Yellow Mask", mask_yellow)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
