#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray
import math

class MockEncoderNode(Node):
    def __init__(self):
        super().__init__('mock_encoder_node')
    
        self.declare_parameter('wheel_radius', 0.033)
        self.declare_parameter('wheel_base', 0.160)
        self.declare_parameter('ticks_per_rev', 1496)
        self.declare_parameter('publish_rate', 50.0)

        self.r = self.get_parameter('wheel_radius').value
        self.L = self.get_parameter('wheel_base').value
        self.N = self.get_parameter('ticks_per_rev').value
        self.rate = self.get_parameter('publish_rate').value

        self.sub_cmd_vel = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )
        self.pub_ticks = self.create_publisher(Int32MultiArray, '/wheel_ticks', 10)

        self.target_linear_v = 0.0
        self.target_angular_w = 0.0
        self.left_accumulated_ticks = 0.0
        self.right_accumulated_ticks = 0.0

        self.timer = self.create_timer(1.0 / self.rate, self.timer_callback)
        self.get_logger().info('Mock Encoder Node Initialized.')

    def cmd_vel_callback(self, msg: Twist):
        self.target_linear_v = msg.linear.x
        self.target_angular_w = msg.angular.z

    def timer_callback(self):
        dt = 1.0 / self.rate
    
        # 2륜 차동 기구학 역변환: 속도 -> 좌우 바퀴 선속도
        v_left = self.target_linear_v - (self.target_angular_w * self.L / 2.0)
        v_right = self.target_linear_v + (self.target_angular_w * self.L / 2.0)

        # 미소 시간 동안의 바퀴 이동 거리
        delta_dist_l = v_left * dt
        delta_dist_r = v_right * dt

        # 이동 거리를 엔코더 틱 차분으로 변환
        delta_tick_l = (delta_dist_l / (2.0 * math.pi * self.r)) * self.N
        delta_tick_r = (delta_dist_r / (2.0 * math.pi * self.r)) * self.N

        self.left_accumulated_ticks += delta_tick_l
        self.right_accumulated_ticks += delta_tick_r

        msg = Int32MultiArray()
        msg.data = [int(self.left_accumulated_ticks), int(self.right_accumulated_ticks)]
        self.pub_ticks.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MockEncoderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
