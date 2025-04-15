import cv2
import numpy as np

def translate_image(img, x_shift, y_shift):
    height, width = img.shape[:2]
    trans_matrix = np.float32([[1, 0, x_shift], [0, 1, y_shift]])
    return cv2.warpAffine(img, trans_matrix, (width, height))

def scale_image(img, scale_factor):
    return cv2.resize(img, None, fx=scale_factor, fy=scale_factor)

def brighten_image(img, value=50):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v + value, 0, 255)
    bright_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(bright_hsv, cv2.COLOR_HSV2BGR)

def adjust_contrast(img, alpha=1.5):
    return cv2.convertScaleAbs(img, alpha=alpha, beta=0)

def gaussian_blur(img):
    return cv2.GaussianBlur(img, (5, 5), 0)

def edge_detection(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(gray, 100, 200)

cap = cv2.VideoCapture(1)  #0 for the PC camera 1 for the external camera

if not cap.isOpened():
    print("Camera could not be opened.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply transformations
    translated = translate_image(frame, x_shift=50, y_shift=30)
    scaled = scale_image(translated, 0.75)
    bright = brighten_image(scaled)
    contrast = adjust_contrast(bright)
    smoothed = gaussian_blur(contrast)
    edges = edge_detection(smoothed)

    # Display outputs
    cv2.imshow("Original", frame)
    cv2.imshow("Processed - Contrast + Blur", smoothed)
    cv2.imshow("Edges", edges)
    cv2.imshow("Scaled", scaled)
    cv2.imshow("Translated", translated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()