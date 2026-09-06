import time
import rclpy
import serial
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node


class ArduinoParameterNode(Node):
    def __init__(self):
        super().__init__('ch05_arduino_parameter_node')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('led_blink_rate', 1)
        self.declare_parameter('warning_mode', False)
        self.serial = serial.Serial(self.get_parameter('port').value, 115200, timeout=0.2)
        time.sleep(2.0)
        self.add_on_set_parameters_callback(self.on_parameters)

    def on_parameters(self, parameters):
        for parameter in parameters:
            if parameter.name == 'led_blink_rate':
                if not isinstance(parameter.value, int) or not 1 <= parameter.value <= 10:
                    return SetParametersResult(successful=False, reason='rate must be 1..10')
            if parameter.name == 'warning_mode' and not isinstance(parameter.value, bool):
                return SetParametersResult(successful=False, reason='warning_mode must be bool')
        for parameter in parameters:
            if parameter.name == 'led_blink_rate':
                self.serial.write(f'RATE,{parameter.value}\n'.encode())
            elif parameter.name == 'warning_mode':
                self.serial.write(f'WARN,{int(parameter.value)}\n'.encode())
        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoParameterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.serial.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
