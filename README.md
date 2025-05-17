# Autonomous Lane-Keeping System using Image Processing  
**Team-08**: **Nabil Hassan, Yassin Eissa**
---
**Mechatronics Department, German University in Cairo**  

---

## 📑 Abstract  
This project implements a lane detection and control system for autonomous vehicles using Raspberry Pi, Arduino, and image processing techniques. Key methodologies include color masking, edge detection, polynomial fitting, and real-time steering angle computation. The system ensures robust lane-keeping under varying conditions and demonstrates adaptability through hardware-in-the-loop validation.  

---

## 🛠️ Features & Components  
### Hardware  
- **Raspberry Pi 4B**: Processes images and computes steering commands.  
- **Arduino Nano**: Translates steering angles into servo signals.  
- **MG95R Servo Motor**: Controls front wheels for steering.  
- **BLDC Motor (1100KV)**: Powers rear wheels via an ESC.  
- **Camera Module**: Captures lane images (adjusted tilt for perspective correction).  
- **LiPo Battery & Power Bank**: Supplies power to components.  

### Software  
- **OpenCV**: Image processing (grayscale conversion, edge detection, warping).  
- **NumPy**: Polynomial fitting for lane trajectory estimation.  
- **PySerial**: Raspberry Pi-Arduino communication.  
- **Canny Edge Detection**: Identifies lane boundaries.  
- **Inverse Binary Thresholding**: Enhances lane visibility.  

---

## 🚀 Installation & Setup  
1. **Hardware Connections**:  
   - Connect Raspberry Pi to Arduino Nano via USB.  
   - Attach servo motor to Arduino (PWM pin) and BLDC motor to ESC.  
   - Mount the camera on the vehicle with a slight tilt for perspective correction.  

2. **Software Dependencies**:  
   ```bash
   pip install opencv-python numpy pyserial
