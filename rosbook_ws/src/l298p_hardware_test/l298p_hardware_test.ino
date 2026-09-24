// Safe, command-triggered test for the Arduino Motor Shield Rev3 (L298P).
// Send 't' at 115200 baud to run one short test cycle; send 's' to stop.

const uint8_t DIR_A = 12;
const uint8_t PWM_A = 3;
const uint8_t BRAKE_A = 9;
const uint8_t DIR_B = 13;
const uint8_t PWM_B = 11;
const uint8_t BRAKE_B = 8;

const uint8_t TEST_PWM = 64;       // 25% duty cycle
const unsigned long RUN_MS = 700;
const unsigned long PAUSE_MS = 500;

void stopAll() {
  analogWrite(PWM_A, 0);
  analogWrite(PWM_B, 0);
  digitalWrite(BRAKE_A, HIGH);
  digitalWrite(BRAKE_B, HIGH);
}

bool waitOrStop(unsigned long durationMs) {
  const unsigned long started = millis();
  while (millis() - started < durationMs) {
    if (Serial.available() && Serial.read() == 's') {
      stopAll();
      Serial.println(F("STOPPED_BY_USER"));
      return false;
    }
  }
  return true;
}

bool runStep(const __FlashStringHelper* label, uint8_t dirPin,
             uint8_t pwmPin, uint8_t brakePin, bool forward) {
  stopAll();
  delay(PAUSE_MS);
  digitalWrite(dirPin, forward ? HIGH : LOW);
  digitalWrite(brakePin, LOW);
  Serial.println(label);
  analogWrite(pwmPin, TEST_PWM);
  const bool completed = waitOrStop(RUN_MS);
  stopAll();
  return completed;
}

void runTest() {
  Serial.println(F("TEST_BEGIN"));
  if (!runStep(F("A_FORWARD"), DIR_A, PWM_A, BRAKE_A, true)) return;
  if (!runStep(F("A_REVERSE"), DIR_A, PWM_A, BRAKE_A, false)) return;
  if (!runStep(F("B_FORWARD"), DIR_B, PWM_B, BRAKE_B, true)) return;
  if (!runStep(F("B_REVERSE"), DIR_B, PWM_B, BRAKE_B, false)) return;
  stopAll();
  Serial.println(F("TEST_COMPLETE_MOTORS_STOPPED"));
}

void setup() {
  pinMode(DIR_A, OUTPUT);
  pinMode(PWM_A, OUTPUT);
  pinMode(BRAKE_A, OUTPUT);
  pinMode(DIR_B, OUTPUT);
  pinMode(PWM_B, OUTPUT);
  pinMode(BRAKE_B, OUTPUT);
  stopAll();
  Serial.begin(115200);
  Serial.println(F("L298P_READY_SEND_t_TO_TEST_s_TO_STOP"));
}

void loop() {
  if (Serial.available()) {
    const char command = Serial.read();
    if (command == 't') runTest();
    if (command == 's') {
      stopAll();
      Serial.println(F("MOTORS_STOPPED"));
    }
  }
}
