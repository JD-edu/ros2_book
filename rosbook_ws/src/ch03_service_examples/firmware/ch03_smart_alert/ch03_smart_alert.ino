const unsigned long WARNING_MS = 400;
const unsigned long EMERGENCY_MS = 100;
int mode = 1;
bool ledState = false;
unsigned long lastToggle = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command.length() == 2 && command[0] == 'M' &&
        command[1] >= '1' && command[1] <= '3') {
      mode = command[1] - '0';
      Serial.print("OK,M");
      Serial.println(mode);
    }
  }
  if (mode == 1) {
    ledState = false;
  } else {
    unsigned long interval = mode == 2 ? WARNING_MS : EMERGENCY_MS;
    if (millis() - lastToggle >= interval) {
      lastToggle = millis();
      ledState = !ledState;
    }
  }
  digitalWrite(LED_BUILTIN, ledState ? HIGH : LOW);
}
