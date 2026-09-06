import math
import time
import rclpy
import serial
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32, Int64


class SerialBridge(Node):
    def __init__(self):
        super().__init__('ch10_serial_bridge')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('imu_frame_id', 'imu_link')
        self.frame_id = self.get_parameter('imu_frame_id').value
        self.serial = serial.Serial(self.get_parameter('port').value,
                                    self.get_parameter('baudrate').value,
                                    timeout=0.01)
        time.sleep(2.0)
        self.serial.reset_input_buffer()
        self.left_pub = self.create_publisher(Int64, 'encoder_left', 10)
        self.right_pub = self.create_publisher(Int64, 'encoder_right', 10)
        self.imu_pub = self.create_publisher(Imu, 'imu/data', 10)
        self.battery_pub = self.create_publisher(Float32, 'battery_voltage', 10)
        self.cmd_sub = self.create_subscription(Twist, 'cmd_vel', self.on_cmd_vel, 10)
        self.timer = self.create_timer(0.01, self.read_serial)
        self.get_logger().info(f'Arduino serial bridge ready: {self.serial.port}')

    def on_cmd_vel(self, message):
        command = f'CMD,{message.linear.x:.3f},{message.angular.z:.3f}\n'
        self.serial.write(command.encode())

    def read_serial(self):
        while self.serial.in_waiting:
            line = self.serial.readline().decode(errors='replace').strip()
            fields = line.split(',')
            try:
                if len(fields) == 3 and fields[0] == 'ENC':
                    self.left_pub.publish(Int64(data=int(fields[1])))
                    self.right_pub.publish(Int64(data=int(fields[2])))
                elif len(fields) == 4 and fields[0] == 'IMU':
                    self.publish_imu(*(float(value) for value in fields[1:]))
                elif len(fields) == 2 and fields[0] == 'BAT':
                    self.battery_pub.publish(Float32(data=float(fields[1])))
            except ValueError:
                self.get_logger().warning(f'Invalid serial frame: {line}')

    def publish_imu(self, roll, pitch, yaw):
        cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
        cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
        cr, sr = math.cos(roll / 2), math.sin(roll / 2)
        message = Imu()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = self.frame_id
        message.orientation.w = cr * cp * cy + sr * sp * sy
        message.orientation.x = sr * cp * cy - cr * sp * sy
        message.orientation.y = cr * sp * cy + sr * cp * sy
        message.orientation.z = cr * cp * sy - sr * sp * cy
        message.orientation_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        self.imu_pub.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.serial.write(b'CMD,0.000,0.000\n')
        node.serial.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
