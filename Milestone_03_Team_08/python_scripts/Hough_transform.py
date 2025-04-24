#!/usr/bin/env python3
import cv2
import numpy as np
import serial
import time
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Image processing pipeline (grayscale, blur, edges, ROI, etc.)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    height, width = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[
        (0, height),
        (width, height),
        (width, int(height * 0.6)),
        (0, int(height * 0.6))
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    masked = cv2.bitwise_and(edges, mask)
    # Hough Lines
    lines = cv2.HoughLinesP(masked, 1, np.pi / 180, 50, minLineLength=40, maxLineGap=150)
    left_lines = []
    right_lines = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

            if angle < -60:
                left_lines.append(line)
            elif angle > 60:
                right_lines.append(line)

            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
 
    
 
    # Detect Lane Direction
    if len(left_lines) < len(right_lines):
        direction = "Curve Left"
    elif len(right_lines) < len(left_lines):
        direction = "Curve Right"
    else:
        direction = "Straight"

    cv2.putText(frame, f"Direction: {direction}", (30,40),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    cv2.imshow("Lane Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
