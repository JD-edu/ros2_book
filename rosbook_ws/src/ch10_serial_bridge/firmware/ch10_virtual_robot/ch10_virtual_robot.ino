#include <math.h>
#include <string.h>
#include <stdlib.h>

long leftTicks = 0;
long rightTicks = 0;
float yaw = 0.0f;
float targetLinear = 0.0f;
float targetAngular = 0.0f;
char receiveBuffer[64];
byte receiveIndex = 0;
unsigned long lastSensor = 0;
unsigned long lastCommand = 0;
const unsigned long SENSOR_INTERVAL_MS = 20;
const unsigned long COMMAND_TIMEOUT_MS = 500;

void parseCommand(char *command) {
  char *header = strtok(command, ",");
  char *linear = strtok(NULL, ",");
  char *angular = strtok(NULL, ",");
  if (header && linear && angular && strcmp(header, "CMD") == 0) {
    targetLinear = atof(linear);
    targetAngular = atof(angular);
    lastCommand = millis();
  }
}

void receiveCommands() {
  while (Serial.available()) {
    char value = Serial.read();
    if (value == '\n' || value == '\r') {
      if (receiveIndex) {
        receiveBuffer[receiveIndex] = '\0';
        parseCommand(receiveBuffer);
        receiveIndex = 0;
      }
    } else if (receiveIndex < sizeof(receiveBuffer) - 1) {
      receiveBuffer[receiveIndex++] = value;
    } else {
      receiveIndex = 0;
    }
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  lastSensor = lastCommand = millis();
}

void loop() {
  unsigned long now = millis();
  receiveCommands();
  if (now - lastCommand > COMMAND_TIMEOUT_MS) {
    targetLinear = 0.0f;
    targetAngular = 0.0f;
  }
  digitalWrite(LED_BUILTIN, (targetLinear != 0.0f || targetAngular != 0.0f));
  if (now - lastSensor < SENSOR_INTERVAL_MS) return;
  lastSensor = now;
  leftTicks += (long)((targetLinear - targetAngular * 0.1f) * 100.0f);
  rightTicks += (long)((targetLinear + targetAngular * 0.1f) * 100.0f);
  float roll = 0.01f * sin(now * 0.002f);
  float pitch = 0.02f * cos(now * 0.002f);
  yaw += targetAngular * 0.02f;
  if (yaw > PI) yaw -= TWO_PI;
  if (yaw < -PI) yaw += TWO_PI;
  Serial.print("ENC,"); Serial.print(leftTicks); Serial.print(','); Serial.println(rightTicks);
  Serial.print("IMU,"); Serial.print(roll, 4); Serial.print(',');
  Serial.print(pitch, 4); Serial.print(','); Serial.println(yaw, 4);
  Serial.println("BAT,5.00");
}
