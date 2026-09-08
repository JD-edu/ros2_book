#!/usr/bin/env python3
import math
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray


class MotorNode(Node):
    def __init__(self):
        super().__init__('motor_node')
        self.declare_parameter('wheel_radius', 0.033)
        self.declare_parameter('wheel_base', 0.160)
        self.declare_parameter('max_rpm', 120.0)
        self.declare_parameter('command_timeout', 0.5)
        self.radius = float(self.get_parameter('wheel_radius').value)
        self.wheel_base = float(self.get_parameter('wheel_base').value)
        self.max_rpm = float(self.get_parameter('max_rpm').value)
        self.command_timeout = float(self.get_parameter('command_timeout').value)
        self.left_rpm = 0
        self.right_rpm = 0
        self.heartbeat = 0
        self.last_command_time = self.get_clock().now()
        self.sub = self.create_subscription(Twist, '/cmd_vel', self.on_cmd_vel, 10)
        self.pub = self.create_publisher(Int16MultiArray, '/wheel_commands', 10)
        self.timer = self.create_timer(0.05, self.send_periodic)

    def on_cmd_vel(self, msg):
        self.last_command_time = self.get_clock().now()
        left = msg.linear.x - msg.angular.z * self.wheel_base / 2.0
        right = msg.linear.x + msg.angular.z * self.wheel_base / 2.0
        scale = 60.0 / (2.0 * math.pi * self.radius)
        limit = abs(self.max_rpm)
        self.left_rpm = round(max(-limit, min(limit, left * scale)))
        self.right_rpm = round(max(-limit, min(limit, right * scale)))

    def send_periodic(self):
        elapsed = (self.get_clock().now() - self.last_command_time).nanoseconds / 1e9
        if elapsed > self.command_timeout:
            self.left_rpm = 0
            self.right_rpm = 0
        msg = Int16MultiArray()
        msg.data = [self.left_rpm, self.right_rpm, self.heartbeat]
        self.pub.publish(msg)
        self.heartbeat = (self.heartbeat + 1) & 0xFF


def main(args=None):
    rclpy.init(args=args)
    node = MotorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
