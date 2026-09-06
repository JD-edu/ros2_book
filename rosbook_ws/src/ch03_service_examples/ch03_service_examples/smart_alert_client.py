import sys
import rclpy
from rclpy.node import Node
from ch03_service_interfaces.srv import SmartAlert


def main(args=None):
    rclpy.init(args=args)
    node = Node('ch03_smart_alert_client')
    client = node.create_client(SmartAlert, 'set_smart_alert')
    if not client.wait_for_service(timeout_sec=5.0):
        node.get_logger().error('service not available')
        node.destroy_node()
        rclpy.shutdown()
        return
    request = SmartAlert.Request()
    request.mode = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    request.duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    node.get_logger().info(future.result().message)
    node.destroy_node()
    rclpy.shutdown()
