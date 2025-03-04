#!/usr/bin/python 3
import cv2
import time
import os

# Choose camera type: 'picamera' for Raspberry Pi Camera, 'usb' for USB webcam
CAMERA_TYPE = "usb"  # Change to "picamera" if using Raspberry Pi Camera Module

# Define save path
SAVE_PATH = "/home/pi/captured_image.jpg"

def capture_with_usb():
    """ Captures an image using a USB webcam and saves it. """
    cap = cv2.VideoCapture(0)  # Open default camera (index 0)
    time.sleep(2)  # Give the camera time to adjust

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    ret, frame = cap.read()  # Capture a frame
    if ret:
        cv2.imwrite(SAVE_PATH, frame)  # Save image
        print(f"Image saved at {SAVE_PATH}")
    else:
        print("Error: Failed to capture image.")

    cap.release()
    cv2.destroyAllWindows()

def capture_with_picamera():
    """ Captures an image using the Raspberry Pi Camera Module and saves it. """
    from picamera2 import Picamera2
    picam = Picamera2()
    picam.start()
    time.sleep(2)  # Allow camera to adjust
    picam.capture_file(SAVE_PATH)
    print(f"Image saved at {SAVE_PATH}")

# Choose camera method
if CAMERA_TYPE == "usb":
    capture_with_usb()
else:
    capture_with_picamera()
