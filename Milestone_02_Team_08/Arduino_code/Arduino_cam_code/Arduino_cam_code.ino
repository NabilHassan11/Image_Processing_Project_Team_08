#include <Servo.h>

Servo myServo;
String command = "";

void setup() {
  Serial.begin(9600);
  myServo.attach(9);  // Attach to pin D9
  myServo.write(120); // Center position
}

void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');

    if (command == "LEFT") {
      myServo.write(90);
    } 
    else if (command == "RIGHT") {
      myServo.write(140);
    } 
    else if (command == "CENTER") {
      myServo.write(120);
    }
  }
}
