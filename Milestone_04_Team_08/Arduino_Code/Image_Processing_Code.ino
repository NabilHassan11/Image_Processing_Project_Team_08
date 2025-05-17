#include <Servo.h>  // Include Servo library to control ESC and steering

// --- Pin Definitions ---
#define SERVO_PIN 10  // Pin connected to the steering servo
#define ESC_PIN 9     // Pin connected to the ESC (Electronic Speed Controller)

// --- Steering Angle Definitions ---
#define CENTER 120     // Neutral steering angle (straight)
#define MAX_LEFT 90    // Maximum left turn
#define MAX_RIGHT 140  // Maximum right turn

// --- ESC PWM Values (microseconds) ---
#define ESC_MIN 1000       // 0% throttle (stop signal)
#define ESC_THROTTLE 1040  // ~4% throttle to just start motor

// --- Create Servo Objects ---
Servo steering_servo;  // Servo for steering control
Servo esc;             // Servo object used for ESC (motor control)

void setup() {
  Serial.begin(9600);  // Start serial communication with host (e.g., Raspberry Pi or PC)

  // --- Attach servos to respective pins ---
  steering_servo.attach(SERVO_PIN);  // Attach steering servo to pin 10
  esc.attach(ESC_PIN);               // Attach ESC to pin 9

  // --- ESC Initialization Sequence ---
  // Required to safely arm the ESC before sending throttle signals
  esc.writeMicroseconds(ESC_MIN);    // Send minimum throttle to ensure motor is off
  delay(3000);                       // Wait for ESC to initialize (important for safety)

  esc.writeMicroseconds(ESC_THROTTLE);  // Set a low throttle value (e.g., 4%) to start the motor slowly
  delay(500);                           // Allow some time for throttle to settle

  // --- Center the Steering Servo ---
  steering_servo.write(CENTER);  // Set steering to center position
  delay(500);                    // Allow servo time to move to position
}

void loop() {
  // Check if a character was received via serial
  if (Serial.available() > 0) {
    char command = Serial.read();  // Read the incoming character

    // --- Interpret Command ---
    switch(command) {
      case 'LEFT':  // Turn Left
        steering_servo.write(MAX_LEFT);
        break;

      case 'RIGHT':  // Turn Right
        steering_servo.write(MAX_RIGHT);
        break;

      case 'CENTER':  // Center Steering
        steering_servo.write(CENTER);
        break;

      // Optionally add default to handle unexpected input
    }
  }
 
}
// --- Note: The ESC and steering servo are controlled using PWM signals.
// The ESC requires a specific initialization sequence to ensure safe operation.
// The steering servo is controlled by sending specific angles to it.
// The code is designed to be simple and effective for basic steering control.
// --- Ensure to test the system in a safe environment to avoid accidents.
// --- Adjust the ESC_MIN and ESC_THROTTLE values based on your specific ESC and motor setup.
// --- The steering angles (CENTER, MAX_LEFT, MAX_RIGHT) may need to be calibrated