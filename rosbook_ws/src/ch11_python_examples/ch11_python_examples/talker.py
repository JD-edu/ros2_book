import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    def __init__(self):
        super().__init__('ch11_python_talker')
        self.publisher = self.create_publisher(String, 'ch11_chatter', 10)
        self.count = 0
        self.timer = self.create_timer(0.5, self.publish_message)

    def publish_message(self):
        self.count += 1
        self.publisher.publish(String(data=f'Hello ROS 2: {self.count}'))


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
