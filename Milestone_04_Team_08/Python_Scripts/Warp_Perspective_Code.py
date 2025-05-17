#!/usr/bin/env python3
import cv2
import numpy as np
import serial
import time
import math
import warnings
from collections import deque

cap = cv2.VideoCapture(0)

# Keep history of directions to reduce sensitivity
direction_history = deque(maxlen=10)
# Setup Arduino serial (adjust COM port and baud rate)
# wait for serial connection

def calculate_steering_angle(left_fit, right_fit, frame_shape , k=0.5, velocity=1.0):
    height, width = frame_shape[:2]
    y_eval = height

    if left_fit is None or right_fit is None:
        return 0  # Default to straight
    
    left_x = left_fit[0] * y_eval**2 + left_fit[1] * y_eval + left_fit[2]
    right_x = right_fit[0] * y_eval**2 + right_fit[1] * y_eval + right_fit[2]
    lane_center = (left_x + right_x) / 2
    car_center = width / 2
    cte = lane_center - car_center

    dy = 1
    left_dx = 2 * left_fit[0] * y_eval + left_fit[1]
    right_dx = 2 * right_fit[0] * y_eval + right_fit[1]
    lane_dx = (left_dx + right_dx) / 2
    heading_error = math.atan2(lane_dx, dy)

    steering_angle = heading_error + math.atan2(k * cte, velocity)
    steering_angle_deg = math.degrees(steering_angle)
    steering_angle_deg = max(min(steering_angle_deg, 30), -30)

    return steering_angle_deg

def map_angle_to_servo_command(steering_angle_deg):
    # Map from [-30, 30] to [90, 140]
    servo_angle = int((steering_angle_deg + 30) * (50 / 60) + 90)
    return f"{servo_angle}\n"
def warp_perspective(img):
    height, width = img.shape[:2]
    src = np.float32([
        [width * 0.45, height * 0.6],
        [width * 0.55, height * 0.6],
        [width * 0.9, height],
        [width * 0.1, height]
    ])
    dst = np.float32([
        [width * 0.2, 0],
        [width * 0.8, 0],
        [width * 0.8, height],
        [width * 0.2, height]
    ])
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, matrix, (width, height))
    return warped

def fit_polynomial(binary_img):
    histogram = np.sum(binary_img[binary_img.shape[0]//2:,:], axis=0)
    midpoint = int(histogram.shape[0] / 2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    nwindows = 9
    window_height = binary_img.shape[0] // nwindows
    nonzero = binary_img.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    leftx_current = leftx_base
    rightx_current = rightx_base
    margin = 100
    minpix = 50
    left_lane_inds = []
    right_lane_inds = []
    
    for window in range(nwindows):
        win_y_low = binary_img.shape[0] - (window + 1) * window_height
        win_y_high = binary_img.shape[0] - window * window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin

        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                          (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                           (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]

        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)

        if len(good_left_inds) > minpix:
            leftx_current = int(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = int(np.mean(nonzerox[good_right_inds]))

    left_lane_inds = np.concatenate(left_lane_inds)
    right_lane_inds = np.concatenate(right_lane_inds)

    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    if len(leftx) == 0 or len(rightx) == 0:
        return None, None
    
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    return left_fit, right_fit

def curvature_direction(angle):
    #if left_fit is None or right_fit is None:
        #return "No Lane"

    #avg_curve = (left_fit[0] + right_fit[0]) / 2

    #if avg_curve < -5e-4:
        #return "Curve Right"
    #elif avg_curve > 5e-4:
        #return "Curve Left"
    #else:
        #return "Straight"
    if abs(angle) < 15:
        return "Straight"
    elif angle < 0:
        return "Curve Left"
    else:
        return "Curve Right"

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Threshold to highlight black areas (black lanes)
    # You can adjust 60 → try 50, 70 depending on the actual black level
    _, mask_black = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Region of Interest (ROI) to keep only the lane area
    height, width = mask_black.shape
    roi_mask = np.zeros_like(mask_black)
    polygon = np.array([[(0, height), (width, height), (width, int(height * 0.6)), (0, int(height * 0.6))]], np.int32)
    cv2.fillPoly(roi_mask, polygon, 255)

    # Apply ROI to the binary black mask
    masked = cv2.bitwise_and(mask_black, roi_mask)
    blurred = cv2.GaussianBlur(masked , (5,5), 0)
    edges = cv2.Canny(blurred , 50 , 150)
    # For debugging: show intermediate results
    cv2.imshow("binary", masked)
    cv2.imshow("edges", edges)
    cv2.imshow("Masked ROI", edges)

    

    # Perspective Transform
    warped = warp_perspective(edges)
    
    # Polynomial Fitting
    left_fit, right_fit = fit_polynomial(warped)
    
    
    


    # Determine Lane Direction
    steering_angle = calculate_steering_angle(left_fit, right_fit, frame.shape)
    current_direction = curvature_direction(steering_angle)
    servo_command = map_angle_to_servo_command(steering_angle)
    
    direction_history.append(current_direction)
    smoothed_direction = max(set(direction_history), key=direction_history.count)
    # Visual feedback (optional)
    cv2.putText(frame, f"Angle: {steering_angle:.2f} deg", (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    # Overlay Text
    cv2.putText(frame, f"Direction: {smoothed_direction}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Show Detection Mask (for debugging)
    lane_overlay = cv2.cvtColor(warped, cv2.COLOR_GRAY2BGR)
    cv2.imshow("Warped Lane", lane_overlay)
    cv2.imshow("Lane Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


