import time
import rclpy
import serial
from rclpy.node import Node
from ch03_service_interfaces.srv import SmartAlert


class ArduinoAlertServer(Node):
    def __init__(self):
        super().__init__('ch03_arduino_alert_server')
        self.declare_parameter('port', '/dev/ttyACM0')
        port = self.get_parameter('port').value
        self.serial = serial.Serial(port, 115200, timeout=1.0)
        time.sleep(2.0)
        self.service = self.create_service(
            SmartAlert, 'set_smart_alert', self.handle_request)
        self.get_logger().info(f'Arduino connected: {port}')

    def handle_request(self, request, response):
        if request.mode not in (1, 2, 3) or request.duration < 0.0:
            response.success = False
            response.message = 'mode must be 1..3 and duration must be non-negative'
            return response
        self.serial.write(f'M{request.mode}\n'.encode())
        acknowledgement = self.serial.readline().decode(errors='replace').strip()
        time.sleep(request.duration)
        self.serial.write(b'M1\n')
        self.serial.readline()
        response.success = acknowledgement == f'OK,M{request.mode}'
        response.message = acknowledgement or 'no Arduino acknowledgement'
        return response


def main(args=None):
    rclpy.init(args=args)
    node = ArduinoAlertServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.serial.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
