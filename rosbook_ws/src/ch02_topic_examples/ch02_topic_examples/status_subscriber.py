import rclpy
from rclpy.node import Node
from ch02_robot_interfaces.msg import RobotStatus


class StatusSubscriber(Node):
    def __init__(self):
        super().__init__('ch02_status_subscriber')
        self.subscription = self.create_subscription(
            RobotStatus, 'robot_status', self.on_status, 10)

    def on_status(self, msg):
        self.get_logger().info(
            f'{msg.robot_id}: battery={msg.battery_level}%, '
            f'temperature={msg.temperature:.1f}, emergency={msg.is_emergency}')


def main(args=None):
    rclpy.init(args=args)
    node = StatusSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
