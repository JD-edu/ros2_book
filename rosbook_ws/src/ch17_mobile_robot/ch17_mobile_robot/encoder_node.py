#!/usr/bin/env python3
import struct
import rclpy
from rclpy.node import Node
import serial
from std_msgs.msg import Int16MultiArray, Int32MultiArray

from ch17_mobile_robot.protocol import ACK, CMD_VEL, ENCODER, ERROR, PacketParser, pack_packet


class EncoderNode(Node):
    def __init__(self):
        super().__init__('encoder_node')
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        port = str(self.get_parameter('serial_port').value)
        baudrate = int(self.get_parameter('baudrate').value)
        self.serial = serial.Serial(port, baudrate, timeout=0.0)
        self.parser = PacketParser()
        self.last_ack = None
        self.tick_pub = self.create_publisher(Int32MultiArray, '/wheel_ticks', 20)
        self.create_subscription(Int16MultiArray, '/wheel_commands', self.on_wheel_commands, 10)
        self.create_timer(0.01, self.poll_serial)
        self.get_logger().info(f'Opened serial port: {port} at {baudrate} baud')

    def on_wheel_commands(self, msg):
        if len(msg.data) < 3:
            return
        left_rpm, right_rpm, heartbeat = msg.data[:3]
        payload = struct.pack('<hhB', left_rpm, right_rpm, heartbeat & 0xFF)
        self.serial.write(pack_packet(CMD_VEL, payload))

    def poll_serial(self):
        waiting = self.serial.in_waiting
        if not waiting:
            return
        for packet_type, payload in self.parser.feed(self.serial.read(waiting)):
            if packet_type == ENCODER and len(payload) == 8:
                ticks = Int32MultiArray()
                ticks.data = list(struct.unpack('<ii', payload))
                self.tick_pub.publish(ticks)
            elif packet_type == ACK and len(payload) == 1:
                self.last_ack = payload[0]
            elif packet_type == ERROR:
                self.get_logger().error(f'MCU error packet: {payload.hex()}')

    def destroy_node(self):
        if self.serial.is_open:
            self.serial.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = EncoderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
