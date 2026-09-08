#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Quaternion
from tf2_ros import TransformBroadcaster
import serial
import struct
import math

class DifferentialOdomNode(Node):
    def __init__(self):
        super().__init__('differential_odom_node')

        # 파라미터 선언 및 취득
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('wheel_radius', 0.033)
        self.declare_parameter('wheel_base', 0.160)
        self.declare_parameter('ticks_per_rev', 1496)

        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value
        self.r = self.get_parameter('wheel_radius').value
        self.L = self.get_parameter('wheel_base').value
        self.N = self.get_parameter('ticks_per_rev').value

        # 직렬 통신 초기화
        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.05)
            self.get_logger().info(f"Opened serial port: {port} at {baudrate} baud")
        except serial.SerialException as e:
            self.get_logger().error(f"Failed to open serial port: {e}")
            raise SystemExit

        # 퍼블리셔 및 TF 브로드캐스터
        self.odom_pub = self.create_publisher(Odometry, '/odom', 20)
        self.tf_broadcaster = TransformBroadcaster(self)

        # 로봇 글로벌 상태 변수
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        # 직전 엔코더 틱 변수
        self.last_tick_l = None
        self.last_tick_r = None
        self.last_time = self.get_clock().now()

        # 수신 버퍼
        self.rx_buffer = bytearray()

        # 주기적 수신 타이머 (100Hz로 폴링)
        self.timer = self.create_timer(0.01, self.process_serial_data)

    def process_serial_data(self):
        # 가용한 바이트 읽기
        bytes_to_read = self.ser.in_waiting
        if bytes_to_read > 0:
            self.rx_buffer.extend(self.ser.read(bytes_to_read))

        # 패킷 파싱 루프 (고정 길이 12바이트)
        while len(self.rx_buffer) >= 12:
            # 헤더 검사
            if self.rx_buffer[0] != 0xAA or self.rx_buffer[1] != 0x55:
                # 헤더가 일치하지 않으면 1바이트 버리고 다음 위치 탐색
                self.rx_buffer.pop(0)
                continue

            # 길이 검사
            length = self.rx_buffer[2]
            if length != 8:
                self.rx_buffer.pop(0)
                continue

            # 체크섬 검증
            calculated_checksum = 0
            for i in range(2, 11):
                calculated_checksum ^= self.rx_buffer[i]
        
            received_checksum = self.rx_buffer[11]

            if calculated_checksum != received_checksum:
                self.get_logger().warn("Checksum mismatch. Discarding invalid packet.")
                self.rx_buffer.pop(0)
                continue

            # 패킷 디코딩 (int32_t Little-Endian: <ii)
            payload = self.rx_buffer[3:11]
            left_ticks, right_ticks = struct.unpack('<ii', payload)

            # 정상 패킷 12바이트 제거
            del self.rx_buffer[0:12]

            # 오도메트리 연산 수행
            self.update_odometry(left_ticks, right_ticks)

    def update_odometry(self, tick_l, tick_r):
        current_time = self.get_clock().now()
    
        if self.last_tick_l is None or self.last_tick_r is None:
            self.last_tick_l = tick_l
            self.last_tick_r = tick_r
            self.last_time = current_time
            return

        dt = (current_time - self.last_time).nanoseconds / 1e9
        if dt <= 0.0:
            return

        # 틱 차분 계산
        delta_l_ticks = tick_l - self.last_tick_l
        delta_r_ticks = tick_r - self.last_tick_r

        self.last_tick_l = tick_l
        self.last_tick_r = tick_r
        self.last_time = current_time

        # 물리적 이동 거리 환산
        d_left = (2.0 * math.pi * self.r * delta_l_ticks) / self.N
        d_right = (2.0 * math.pi * self.r * delta_r_ticks) / self.N

        # 미소 선형 변위 및 회전 각도
        delta_s = (d_right + d_left) / 2.0
        delta_theta = (d_right - d_left) / self.L

        # 글로벌 좌표 갱신 (Mid-point Runge-Kutta 근사)
        self.x += delta_s * math.cos(self.yaw + (delta_theta / 2.0))
        self.y += delta_s * math.sin(self.yaw + (delta_theta / 2.0))
        self.yaw += delta_theta
    
        # 각도 정규화 (-pi ~ pi)
        self.yaw = math.atan2(math.sin(self.yaw), math.cos(self.yaw))

        # 선속도 및 각속도
        v = delta_s / dt
        w = delta_theta / dt

        # 쿼터니언 계산
        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        # 1. nav_msgs/msg/Odometry 메시지 발행
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0
        odom_msg.pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=qz, w=qw)

        # 공분산 행렬 설정
        odom_msg.pose.covariance[0] = 0.001   # x
        odom_msg.pose.covariance[7] = 0.001   # y
        odom_msg.pose.covariance[35] = 0.005  # yaw

        odom_msg.twist.twist.linear.x = v
        odom_msg.twist.twist.angular.z = w
        odom_msg.twist.covariance[0] = 0.001
        odom_msg.twist.covariance[35] = 0.005

        self.odom_pub.publish(odom_msg)

        # 2. TF (odom -> base_link) 브로드캐스팅
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        t.transform.rotation = Quaternion(x=0.0, y=0.0, z=qz, w=qw)

        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = DifferentialOdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(node, 'ser') and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
