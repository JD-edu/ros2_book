import rclpy
from rclpy.node import Node
from ch02_robot_interfaces.msg import RobotStatus


class StatusPublisher(Node):
    def __init__(self):
        super().__init__('ch02_status_publisher')
        self.publisher = self.create_publisher(RobotStatus, 'robot_status', 10)
        self.timer = self.create_timer(1.0, self.publish_status)

    def publish_status(self):
        msg = RobotStatus()
        msg.stamp = self.get_clock().now().to_msg()
        msg.robot_id = 'ROBOT_01'
        msg.battery_level = 85
        msg.temperature = 36.5
        msg.is_emergency = False
        self.publisher.publish(msg)
        self.get_logger().info(f'published status for {msg.robot_id}')


def main(args=None):
    rclpy.init(args=args)
    node = StatusPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
