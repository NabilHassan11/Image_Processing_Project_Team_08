import cv2
import serial
import time
import numpy as np

# --- Setup serial communication with Arduino ---
try:
    # Initialize serial port to communicate with Arduino
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)  # Give the Arduino some time to reset
except serial.SerialException as e:
    print(f"Serial error: {e}")
    exit()

# --- Open USB camera ---
cap = cv2.VideoCapture(0)  # Use the first connected camera
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# --- Define HSV color range for detecting red ---
# Red in HSV has two ranges because it wraps around the hue circle
RED_LOWER1 = np.array([0, 100, 100])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([160, 100, 100])
RED_UPPER2 = np.array([179, 255, 255])

def get_red_mask(hsv_frame):
    """
    Create a binary mask where red areas are white and everything else is black.
    
    Parameters:
        hsv_frame (np.array): Image in HSV color space.
    
    Returns:
        mask (np.array): Combined mask of two red hue ranges.
    """
    mask1 = cv2.inRange(hsv_frame, RED_LOWER1, RED_UPPER1)
    mask2 = cv2.inRange(hsv_frame, RED_LOWER2, RED_UPPER2)
    return cv2.bitwise_or(mask1, mask2)

def get_line_centers(contours, min_area=300, max_lines=2):
    """
    Calculate the horizontal center of the largest red contours (presumed lines).
    
    Parameters:
        contours (list): Contours from the red mask.
        min_area (int): Minimum area threshold to ignore small noise.
        max_lines (int): Maximum number of largest contours to use.

    Returns:
        centers (list): List of x-coordinates of detected line centers.
    """
    # Filter and sort contours by size
    valid = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    valid = sorted(valid, key=cv2.contourArea, reverse=True)[:max_lines]
    centers = []

    # Calculate centroid x-position for each valid contour
    for cnt in valid:
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            centers.append(cx)

    return centers

def decide_direction(centers, frame_width):
    """
    Decide which direction the robot should go based on the line centers.

    Parameters:
        centers (list): x-coordinates of detected line centers.
        frame_width (int): Width of the video frame.

    Returns:
        direction (str): One of 'LEFT', 'RIGHT', or 'CENTER'.
    """
    if len(centers) == 2:
        lane_center = (centers[0] + centers[1]) // 2
        frame_center = frame_width // 2
        offset = lane_center - frame_center

        # Adjust direction based on how far the center is from the frame's center
        if offset < -30:
            return 'LEFT'
        elif offset > 30:
            return 'RIGHT'
        else:
            return 'CENTER'

    elif len(centers) == 1:
        # If only one line is visible, estimate the other side
        return 'RIGHT' if centers[0] < frame_width // 2 else 'LEFT'

    return 'CENTER'  # Default if no line is visible

# --- Main loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        continue  # Skip iteration if frame capture fails

    # Get frame dimensions and region of interest (ROI)
    height, width = frame.shape[:2]
    roi = frame[int(height * 0.6):, :]  # Focus on the bottom 40% of the frame

    # Convert ROI to HSV for better color filtering
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Create red color mask
    mask = get_red_mask(hsv_roi)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Get red line centers and compute direction
    centers = get_line_centers(contours)
    direction = decide_direction(centers, width)

    # Send computed direction to Arduino
    ser.write(direction.encode())
    print(f"Direction sent: {direction}")

    # --- Visualization for debugging ---
    # Draw circles on detected line centers
    for cx in centers:
        cv2.circle(roi, (cx, roi.shape[0] // 2), 10, (0, 255, 255), -1)

    # Show the ROI and red mask for debugging
    cv2.imshow("Region of Interest", roi)
    cv2.imshow("Red Mask", mask)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup on exit ---
cap.release()
cv2.destroyAllWindows()
ser.close()