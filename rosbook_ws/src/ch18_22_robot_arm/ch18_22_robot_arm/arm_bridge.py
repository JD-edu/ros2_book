"""Bridge JointState commands to a five-channel Arduino servo controller."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from .joint_mapper import JointMapper, encode_command


class ArmBridge(Node):
    def __init__(self):
        super().__init__('arm_bridge')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('offsets', [90.0] * 5)
        self.declare_parameter('directions', [1, -1, 1, -1, 1])
        self.declare_parameter('min_angles', [10.0, 15.0, 10.0, 20.0, 10.0])
        self.declare_parameter('max_angles', [170.0, 165.0, 170.0, 160.0, 80.0])

        self.mapper = JointMapper(
            self.get_parameter('offsets').value,
            self.get_parameter('directions').value,
            self.get_parameter('min_angles').value,
            self.get_parameter('max_angles').value,
        )
        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value

        try:
            import serial
            self.serial = serial.Serial(port, baudrate, timeout=0.1)
        except (ImportError, OSError) as exc:
            raise RuntimeError(f'could not open serial port {port}: {exc}') from exc

        self.sequence = 0
        self.subscription = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10)
        self.get_logger().info(f'Serial port opened: {port} @ {baudrate}')

    def joint_state_callback(self, message):
        try:
            positions = self.mapper.positions_from_message(message.name, message.position)
            angles = self.mapper.to_servo_degrees(positions)
        except ValueError as exc:
            self.get_logger().warning(f'Ignored invalid JointState: {exc}')
            return

        command = encode_command(self.sequence, angles)
        self.serial.write(command.encode('ascii'))
        self.sequence = (self.sequence + 1) % 65536

    def destroy_node(self):
        if getattr(self, 'serial', None) is not None:
            self.serial.close()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ArmBridge()
        rclpy.spin(node)
    except (RuntimeError, KeyboardInterrupt) as exc:
        if node is None:
            print(exc)
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
