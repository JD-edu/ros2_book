import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from ch04_action_interfaces.action import LedBlink


def main(args=None):
    rclpy.init(args=args)
    node = Node('ch04_blink_client')
    client = ActionClient(node, LedBlink, 'blink_led')
    client.wait_for_server()
    goal = LedBlink.Goal(target_seconds=1, blink_interval_ms=100)
    send_future = client.send_goal_async(goal)
    rclpy.spin_until_future_complete(node, send_future)
    result_future = send_future.result().get_result_async()
    rclpy.spin_until_future_complete(node, result_future)
    result = result_future.result().result
    node.get_logger().info(f'completed={result.is_completed}, blinks={result.total_blinks}')
    node.destroy_node()
    rclpy.shutdown()
