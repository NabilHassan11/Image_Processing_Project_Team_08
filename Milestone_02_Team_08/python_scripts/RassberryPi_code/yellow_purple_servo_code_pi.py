import cv2
import numpy as np
import serial
import time

# Initialize serial connection with Arduino
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Change port as needed
time.sleep(2)  # Wait for Arduino to initialize

# Define HSV color ranges
purple_lower = np.array([125, 50, 50])
purple_upper = np.array([155, 255, 255])

yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([35, 255, 255])

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks
    mask_purple = cv2.inRange(hsv, purple_lower, purple_upper)
    mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)

    # Count number of pixels detected
    purple_pixels = cv2.countNonZero(mask_purple)
    yellow_pixels = cv2.countNonZero(mask_yellow)

    # Send command to Arduino
    if purple_pixels > 500:  # adjust threshold as needed
        arduino.write(b"RIGHT\n")  # Go to 140
        print("Purple detected → RIGHT")
    elif yellow_pixels > 500:
        arduino.write(b"LEFT\n")   # Go to 90
        print("Yellow detected → LEFT")
    else:
        arduino.write(b"CENTER\n") # Go to 120
        print("No significant color → CENTER")

    # Show masks for debug
    cv2.imshow("Purple Mask", mask_purple)
    cv2.imshow("Yellow Mask", mask_yellow)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()