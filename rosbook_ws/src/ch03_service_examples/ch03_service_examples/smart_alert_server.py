import rclpy
from rclpy.node import Node
from ch03_service_interfaces.srv import SmartAlert


class SmartAlertServer(Node):
    def __init__(self):
        super().__init__('ch03_smart_alert_server')
        self.srv = self.create_service(
            SmartAlert, 'set_smart_alert', self.handle_request)

    def handle_request(self, request, response):
        if request.mode not in (1, 2, 3) or request.duration < 0.0:
            response.success = False
            response.message = 'mode must be 1..3 and duration must be non-negative'
            return response
        response.success = True
        response.message = (
            f'simulated alert mode {request.mode} for {request.duration:.1f}s')
        self.get_logger().info(response.message)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SmartAlertServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
