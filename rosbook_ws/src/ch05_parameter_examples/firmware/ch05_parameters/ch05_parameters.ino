int blinkRate = 1;
bool warningMode = false;
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
    if (command.startsWith("RATE,")) {
      int value = command.substring(5).toInt();
      if (value >= 1 && value <= 10) blinkRate = value;
      Serial.println("OK,RATE");
    } else if (command == "WARN,1" || command == "WARN,0") {
      warningMode = command.endsWith("1");
      Serial.println("OK,WARN");
    }
  }
  int effectiveRate = warningMode ? 10 : blinkRate;
  unsigned long interval = 500UL / effectiveRate;
  if (millis() - lastToggle >= interval) {
    lastToggle = millis();
    ledState = !ledState;
    digitalWrite(LED_BUILTIN, ledState ? HIGH : LOW);
  }
}
