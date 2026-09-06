import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node


class ParameterNode(Node):
    def __init__(self):
        super().__init__('ch05_parameter_node')
        self.declare_parameter('led_blink_rate', 1)
        self.declare_parameter('warning_mode', False)
        self.add_on_set_parameters_callback(self.validate)

    def validate(self, parameters):
        for parameter in parameters:
            if parameter.name == 'led_blink_rate' and not 1 <= parameter.value <= 10:
                return SetParametersResult(
                    successful=False, reason='led_blink_rate must be from 1 to 10')
            if parameter.name == 'warning_mode' and not isinstance(parameter.value, bool):
                return SetParametersResult(
                    successful=False, reason='warning_mode must be boolean')
        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = ParameterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
