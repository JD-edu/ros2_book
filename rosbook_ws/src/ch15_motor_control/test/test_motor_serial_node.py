import time
import serial

# ==========================================
# 1. 시리얼 포트 및 통신 설정
# ==========================================
# Windows: 'COM3', 'COM4' 등
# Linux / Ubuntu: '/dev/ttyACM0' 또는 '/dev/ttyUSB0'
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200


def encode_motor_frame(left_speed: int, right_speed: int) -> bytes:
    """모터 속도(-255 ~ 255)를 아두이노 수신 규격($M,LLLL,RRRR#\\n)에 맞게 16진수 포맷으로 인코딩합니다."""
    # -255 ~ 255 범위로 제한
    left_clamped = max(-255, min(255, left_speed))
    right_clamped = max(-255, min(255, right_speed))

    # int16(2의 보수)을 4자리 16진수 대문자로 변환 (음수 처리: & 0xFFFF)
    left_hex = f"{left_clamped & 0xFFFF:04X}"
    right_hex = f"{right_clamped & 0xFFFF:04X}"

    # 아두이노 프레임 규격: $M,LLLL,RRRR#\n
    frame_str = f"$M,{left_hex},{right_hex}#\n"
    return frame_str.encode('ascii')


def send_motor_command(ser: serial.Serial, left_speed: int, right_speed: int):
    """시리얼 포트로 모터 명령 프레임을 전송합니다."""
    packet = encode_motor_frame(left_speed, right_speed)
    ser.write(packet)
    ser.flush()
    print(f"[TX] Left: {left_speed:4d}, Right: {right_speed:4d} -> {packet.decode('ascii').strip()}")


def run_motor_test():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print(f"Connected to {SERIAL_PORT} @ {BAUD_RATE} bps")
        
        # 아두이노는 시리얼 연결 직후 리셋되므로 부팅 대기 (약 2초)
        time.sleep(2.0)

        # 테스트 시퀀스: (좌측 속도, 우측 속도, 지속 시간(초), 동작 설명)
        test_sequence = [
            (150, 150, 2.0, "전진 (Forward)"),
            (0, 0, 1.0, "정지 (Stop)"),
            (-150, -150, 2.0, "후진 (Backward)"),
            (0, 0, 1.0, "정지 (Stop)"),
         #   (-120, 120, 2.0, "제자리 좌회전 (Turn Left)"),
         #   (120, -120, 2.0, "제자리 우회전 (Turn Right)"),
         #   (0, 0, 1.0, "최종 정지 (Stop)")
        ]

        print("\n=== 모터 구동 테스트 시작 ===")
        for left, right, duration, desc in test_sequence:
            print(f"\n>> 동작: {desc} (지속시간: {duration}초)")
            start_time = time.time()
            
            # 아두이노 타임아웃(COMMAND_TIMEOUT_MS = 500ms)을 방지하기 위해 50Hz(20ms) 주기로 반복 송신
            while time.time() - start_time < duration:
                send_motor_command(ser, left, right)
                time.sleep(0.02)

        # 안전을 위한 최종 정지 명령 송신
        send_motor_command(ser, 0, 0)
        print("\n=== 모든 테스트 완료 ===")

    except serial.SerialException as e:
        print(f"\n[오류] 시리얼 포트를 열 수 없습니다: {e}")
        print("포트 이름(SERIAL_PORT) 및 권한(sudo usermod -a -G dialout $USER)을 확인하세요.")
    except KeyboardInterrupt:
        print("\n[중단] 사용자에 의해 중단되었습니다. 모터를 정지합니다.")
        if 'ser' in locals() and ser.is_open:
            send_motor_command(ser, 0, 0)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("시리얼 포트가 닫혔습니다.")


if __name__ == "__main__":
    run_motor_test()