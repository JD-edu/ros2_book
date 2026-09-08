#!/usr/bin/env python3
"""Convert ROS 2 velocity commands to the Chapter 15 serial protocol."""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
import serial

from ch15_motor_control.protocol import encode_motor_command, velocity_to_pwm


class MotorSerialNode(Node):
    def __init__(self) -> None:
        super().__init__('motor_serial_node')
        self.declare_parameter('wheel_separation', 0.20)
        self.declare_parameter('max_linear_speed', 0.5)
        self.declare_parameter('max_pwm', 255)
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)

        self.wheel_separation = float(self.get_parameter('wheel_separation').value)
        self.max_linear_speed = float(self.get_parameter('max_linear_speed').value)
        self.max_pwm = int(self.get_parameter('max_pwm').value)
        port = str(self.get_parameter('serial_port').value)
        baud_rate = int(self.get_parameter('baud_rate').value)

        if self.wheel_separation <= 0.0:
            raise ValueError('wheel_separation must be greater than zero')
        if self.max_linear_speed <= 0.0:
            raise ValueError('max_linear_speed must be greater than zero')
        if not 1 <= self.max_pwm <= 255:
            raise ValueError('max_pwm must be between 1 and 255')

        self.serial_port = serial.Serial(port, baud_rate, timeout=0.05)
        self.subscription = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.get_logger().info(f'Serial opened: {port} @ {baud_rate}')

    def cmd_vel_callback(self, msg: Twist) -> None:
        left_pwm, right_pwm = velocity_to_pwm(
            msg.linear.x,
            msg.angular.z,
            self.wheel_separation,
            self.max_linear_speed,
            self.max_pwm,
        )
        frame = encode_motor_command(left_pwm, right_pwm)
        try:
            self.serial_port.write(frame)
        except serial.SerialException as error:
            self.get_logger().error(f'Serial write failed: {error}')

    def destroy_node(self) -> None:
        try:
            if self.serial_port.is_open:
                self.serial_port.write(encode_motor_command(0, 0))
                self.serial_port.close()
        except serial.SerialException as error:
            self.get_logger().warning(f'Could not send the final stop command: {error}')
        super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = None
    try:
        node = MotorSerialNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
