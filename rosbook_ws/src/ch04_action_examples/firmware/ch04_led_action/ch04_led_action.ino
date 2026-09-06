void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  if (!Serial.available()) return;
  String command = Serial.readStringUntil('\n');
  command.trim();
  if (command == "LED,1") {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("OK,1");
  } else if (command == "LED,0") {
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("OK,0");
  }
}
