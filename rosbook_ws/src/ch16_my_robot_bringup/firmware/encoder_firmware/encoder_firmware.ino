#include <Arduino.h>

// 아두이노 우노 외부 인터럽트 지원 핀 매핑
const uint8_t PIN_ENC_LEFT  = 2;  // INT0 (좌측 바퀴 엔코더)
const uint8_t PIN_ENC_RIGHT = 3;  // INT1 (우측 바퀴 엔코더)

// 인터럽트 서비스 루틴(ISR)에서 실시간 갱신되는 휘발성 누적 틱 변수
volatile int32_t g_left_ticks = 0;
volatile int32_t g_right_ticks = 0;

// 좌측 바퀴 인터럽트 서비스 루틴 (1핀 간이 펄스 카운팅)
void isrEncoderLeft() {
  g_left_ticks++;
}

// 우측 바퀴 인터럽트 서비스 루틴 (1핀 간이 펄스 카운팅)
void isrEncoderRight() {
  g_right_ticks++;
}

void setup() {
  // 고속 직렬 통신 초기화
  Serial.begin(115200);
  
  // 엔코더 센서 입력 핀 설정 (내부 풀업 저항 활성화)
  pinMode(PIN_ENC_LEFT, INPUT_PULLUP);
  pinMode(PIN_ENC_RIGHT, INPUT_PULLUP);

  // 2번, 3번 핀에 외부 인터럽트 등록 (신호가 LOW에서 HIGH로 바뀔 때 감지)
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_LEFT), isrEncoderLeft, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_RIGHT), isrEncoderRight, RISING);
}

void loop() {
  static unsigned long last_send_time = 0;
  const unsigned long interval_ms = 20; // 50Hz 주기 (20ms)

  if (millis() - last_send_time >= interval_ms) {
    last_send_time = millis();

    // 4바이트 정수 읽기 중 인터럽트에 의한 데이터 왜곡 방지 (원자적 복사)
    noInterrupts();
    int32_t current_l = g_left_ticks;
    int32_t current_r = g_right_ticks;
    interrupts();

    // 12바이트 패킷 버퍼 구성
    uint8_t packet[12];
    packet[0] = 0xAA; // Header 1
    packet[1] = 0x55; // Header 2
    packet[2] = 0x08; // Payload Length (8 Bytes)

    // int32_t 데이터를 4바이트 Little-Endian 형태로 복사
    memcpy(&packet[3], &current_l, sizeof(int32_t));
    memcpy(&packet[7], &current_r, sizeof(int32_t));

    // Checksum 연산 (Byte 2부터 Byte 10까지의 XOR 합)
    uint8_t checksum = 0;
    for (int i = 2; i < 11; i++) {
      checksum ^= packet[i];
    }
    packet[11] = checksum;

    // 직렬 포트로 바이너리 패킷 송출
    Serial.write(packet, sizeof(packet));
  }
}
