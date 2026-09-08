/* Chapter 15: TB6612FNG motor controller for Arduino Uno.
 * Protocol: $M,LLLL,RRRR# followed by a newline.
 * Wiring from Section 15.2:
 *   Left:  PWMA=D11, AIN1=D5, AIN2=D4
 *   Right: PWMB=D9,  BIN1=D7, BIN2=D8
 *   Standby: STBY=D6
 */

#include <Arduino.h>

constexpr uint8_t PIN_PWMA = 11;
constexpr uint8_t PIN_AIN1 = 5;
constexpr uint8_t PIN_AIN2 = 4;
constexpr uint8_t PIN_PWMB = 9;
constexpr uint8_t PIN_BIN1 = 7;
constexpr uint8_t PIN_BIN2 = 8;
constexpr uint8_t PIN_STBY = 6;

constexpr uint8_t FRAME_LENGTH = 13;
constexpr unsigned long COMMAND_TIMEOUT_MS = 500;

char frame[FRAME_LENGTH + 1];
uint8_t frame_index = 0;
unsigned long last_command_ms = 0;

// ASCII '0'..'9','A'..'F' 한 글자를 0..15로 변환합니다.
int8_t hexDigit(char value) {
  if (value >= '0' && value <= '9') return value - '0';
  if (value >= 'A' && value <= 'F') return value - 'A' + 10;
  if (value >= 'a' && value <= 'f') return value - 'a' + 10;
  return -1;
}

bool parseHex16(const char* text, int16_t& result) {
  uint16_t value = 0;
  for (uint8_t i = 0; i < 4; ++i) {
    const int8_t digit = hexDigit(text[i]);
    if (digit < 0) return false;
    value = static_cast<uint16_t>((value << 4) | digit);
  }
  result = static_cast<int16_t>(value);
  return true;
}

void driveMotor(uint8_t pwm_pin, uint8_t in1, uint8_t in2, int16_t command) {
  command = constrain(command, -255, 255);
  if (command > 0) {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  } else if (command < 0) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  } else {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
  }
  analogWrite(pwm_pin, abs(command));
}

void stopMotors() {
  driveMotor(PIN_PWMA, PIN_AIN1, PIN_AIN2, 0);
  driveMotor(PIN_PWMB, PIN_BIN1, PIN_BIN2, 0);
}

bool applyFrame(const char* data) {
  if (data[0] != '$' || data[1] != 'M' || data[2] != ',' ||
      data[7] != ',' || data[12] != '#') {
    return false;
  }
  int16_t left = 0;
  int16_t right = 0;
  if (!parseHex16(data + 3, left) || !parseHex16(data + 8, right)) {
    return false;
  }
  driveMotor(PIN_PWMA, PIN_AIN1, PIN_AIN2, left);
  driveMotor(PIN_PWMB, PIN_BIN1, PIN_BIN2, right);
  last_command_ms = millis();
  return true;
}

void setup() {
  pinMode(PIN_PWMA, OUTPUT);
  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_AIN2, OUTPUT);
  pinMode(PIN_PWMB, OUTPUT);
  pinMode(PIN_BIN1, OUTPUT);
  pinMode(PIN_BIN2, OUTPUT);
  pinMode(PIN_STBY, OUTPUT);

  digitalWrite(PIN_STBY, HIGH);
  stopMotors();
  Serial.begin(115200);
  last_command_ms = millis();
}

void loop() {
  while (Serial.available() > 0) {
    const char incoming = static_cast<char>(Serial.read());
    if (incoming == '$') {
      frame_index = 0;
      frame[frame_index++] = incoming;
    } else if (frame_index > 0 && frame_index < FRAME_LENGTH) {
      frame[frame_index++] = incoming;
      if (frame_index == FRAME_LENGTH) {
        frame[FRAME_LENGTH] = '\0';
        applyFrame(frame);
        frame_index = 0;
      }
    }
  }

  if (millis() - last_command_ms > COMMAND_TIMEOUT_MS) {
    stopMotors();
  }
}
