import time
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from ch04_action_interfaces.action import LedBlink


class BlinkServer(Node):
    def __init__(self):
        super().__init__('ch04_blink_server')
        self.server = ActionServer(self, LedBlink, 'blink_led', self.execute)

    def execute(self, goal_handle):
        seconds = goal_handle.request.target_seconds
        interval_ms = goal_handle.request.blink_interval_ms
        result = LedBlink.Result()
        if seconds <= 0 or interval_ms <= 0:
            goal_handle.abort()
            return result
        start = time.monotonic()
        count = 0
        feedback = LedBlink.Feedback()
        while time.monotonic() - start < seconds:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.total_blinks = count
                return result
            time.sleep(interval_ms / 1000.0)
            count += 1
            elapsed = time.monotonic() - start
            feedback.remaining_seconds = max(0, int(seconds - elapsed))
            feedback.progress_percent = min(100.0, elapsed / seconds * 100.0)
            goal_handle.publish_feedback(feedback)
        goal_handle.succeed()
        result.is_completed = True
        result.total_blinks = count
        return result


def main(args=None):
    rclpy.init(args=args)
    node = BlinkServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
