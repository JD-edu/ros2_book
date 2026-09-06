import time
import rclpy
import serial
from rclpy.action import ActionServer
from rclpy.node import Node
from ch04_action_interfaces.action import LedBlink


class ArduinoBlinkServer(Node):
    def __init__(self):
        super().__init__('ch04_arduino_blink_server')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.serial = serial.Serial(self.get_parameter('port').value, 115200, timeout=0.2)
        time.sleep(2.0)
        self.server = ActionServer(self, LedBlink, 'blink_led', self.execute)

    def set_led(self, enabled):
        self.serial.write(b'LED,1\n' if enabled else b'LED,0\n')

    def execute(self, goal_handle):
        duration = goal_handle.request.target_seconds
        interval = goal_handle.request.blink_interval_ms / 1000.0
        result = LedBlink.Result()
        if duration <= 0 or interval <= 0:
            goal_handle.abort()
            return result
        started = time.monotonic()
        count = 0
        feedback = LedBlink.Feedback()
        while time.monotonic() - started < duration:
            if goal_handle.is_cancel_requested:
                self.set_led(False)
                goal_handle.canceled()
                result.total_blinks = count
                return result
            self.set_led(True)
            time.sleep(interval)
            self.set_led(False)
            count += 1
            elapsed = time.monotonic() - started
            feedback.remaining_seconds = max(0, int(duration - elapsed))
            feedback.progress_percent = min(100.0, elapsed / duration * 100.0)
            goal_handle.publish_feedback(feedback)
        goal_handle.succeed()
        result.is_completed = True
        result.total_blinks = count
        return result


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoBlinkServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.set_led(False)
        node.serial.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
