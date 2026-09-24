import struct
import threading
import time
import serial

# 포트 및 속도 설정 (환경에 맞게 포트명 수정: '/dev/ttyACM0', 'COM3' 등)
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

# 프로토콜 상수 정의
STX = 0xAA
ETX = 0x55
CMD_VEL = 0x01
ENCODER = 0x02
ACK = 0x03


class MotorControllerTest:
    def __init__(self, port: str, baudrate: int):
        self.ser = serial.Serial(port, baudrate, timeout=0.05)
        self.seq = 0
        self.running = True
        self.rx_buffer = bytearray()
        
        # 수신 스레드 시작
        self.rx_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.rx_thread.start()

    def _calc_checksum(self, packet_type: int, payload: bytes) -> int:
        """Type, Length, Payload 바이트들의 XOR 체크섬을 계산합니다."""
        checksum = packet_type ^ len(payload)
        for b in payload:
            checksum ^= b
        return checksum

    def send_cmd_vel(self, left_rpm: int, right_rpm: int):
        """속도 제어 프레임을 생성하여 아두이노로 송신합니다."""
        self.seq = (self.seq + 1) & 0xFF
        # int16(2바이트 리틀엔디언) x 2 + uint8(1바이트 SEQ) = 총 5바이트
        payload = struct.pack('<hhB', left_rpm, right_rpm, self.seq)
        checksum = self._calc_checksum(CMD_VEL, payload)
        
        frame = bytearray([STX, CMD_VEL, len(payload)]) + payload + bytearray([checksum, ETX])
        self.ser.write(frame)

    def _receive_loop(self):
        """아두이노로부터 들어오는 직렬 패킷을 파싱합니다."""
        while self.running:
            try:
                data = self.ser.read(self.ser.in_waiting or 1)
                if not data:
                    continue
                self.rx_buffer.extend(data)

                while len(self.rx_buffer) >= 5:  # 최소 프레임 길이(STX, TYPE, LEN, CHK, ETX)
                    # STX 동기화
                    if self.rx_buffer[0] != STX:
                        self.rx_buffer.pop(0)
                        continue

                    pkt_type = self.rx_buffer[1]
                    pkt_len = self.rx_buffer[2]
                    expected_frame_len = pkt_len + 5

                    if len(self.rx_buffer) < expected_frame_len:
                        break  # 패킷이 아직 덜 도착함

                    frame = self.rx_buffer[:expected_frame_len]
                    self.rx_buffer = self.rx_buffer[expected_frame_len:]

                    payload = frame[3:3 + pkt_len]
                    recv_chk = frame[3 + pkt_len]
                    recv_etx = frame[4 + pkt_len]

                    # ETX 및 Checksum 검증
                    if recv_etx != ETX or recv_chk != self._calc_checksum(pkt_type, payload):
                        continue

                    # 패킷 타입별 처리
                    if pkt_type == ENCODER and pkt_len == 8:
                        ticks_l, ticks_r = struct.unpack('<ii', payload)
                        print(f"\r[FEEDBACK] Encoders -> Left: {ticks_l:7d} | Right: {ticks_r:7d}", end='', flush=True)
                    elif pkt_type == ACK and pkt_len == 1:
                        ack_seq = payload[0]
                        # 필요 시 ACK 확인 로깅 가능

            except Exception:
                break

    def close(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()


def run_test():
    try:
        print(f"포트 연결 중: {SERIAL_PORT} @ {BAUD_RATE}bps...")
        tester = MotorControllerTest(SERIAL_PORT, BAUD_RATE)
        time.sleep(2.0)  # 아두이노 리셋 대기
        print("연결 완료! 테스트 시퀀스를 시작합니다.\n")

        # 테스트 시나리오: (좌측 RPM, 우측 RPM, 지속시간 초, 동작명)
        # 아두이노 제한 범위: -120 ~ 120 RPM
        scenarios = [
            (50, 50, 2.0, "전진 (Forward 50 RPM)"),
            (0, 0, 1.0, "정지 (Stop)"),
            (-50, -50, 2.0, "후진 (Backward 50 RPM)"),
            (0, 0, 1.0, "정지 (Stop)"),
            (-40, 40, 2.0, "제자리 좌회전 (Turn Left)"),
            (40, -40, 2.0, "제자리 우회전 (Turn Right)"),
            (0, 0, 1.0, "최종 정지 (Stop)")
        ]

        for left, right, duration, desc in scenarios:
            print(f"\n\n>> 동작 수행: {desc}")
            start = time.time()
            # 500ms 세이프티 타임아웃 방지를 위해 20ms(50Hz) 주기로 지속 전송
            while time.time() - start < duration:
                tester.send_cmd_vel(left, right)
                time.sleep(0.02)

        tester.send_cmd_vel(0, 0)
        print("\n\n모든 테스트 시퀀스가 정상 완료되었습니다.")

    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다. 모터를 정지합니다.")
    except serial.SerialException as e:
        print(f"\n시리얼 통신 에러: {e}")
    finally:
        if 'tester' in locals():
            tester.send_cmd_vel(0, 0)
            time.sleep(0.1)
            tester.close()


if __name__ == '__main__':
    run_test()