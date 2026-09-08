#!/usr/bin/env python3
import math
import rclpy
from geometry_msgs.msg import Quaternion, TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from tf2_ros import TransformBroadcaster


class OdomNode(Node):
    def __init__(self):
        super().__init__('odom_node')
        self.declare_parameter('wheel_radius', 0.033)
        self.declare_parameter('wheel_base', 0.160)
        self.declare_parameter('ticks_per_rev', 1496)
        self.radius = float(self.get_parameter('wheel_radius').value)
        self.wheel_base = float(self.get_parameter('wheel_base').value)
        self.ticks_per_rev = int(self.get_parameter('ticks_per_rev').value)
        self.x = self.y = self.yaw = 0.0
        self.last_ticks = None
        self.last_time = None
        self.pub = self.create_publisher(Odometry, '/odom', 20)
        self.broadcaster = TransformBroadcaster(self)
        self.create_subscription(Int32MultiArray, '/wheel_ticks', self.on_ticks, 20)

    def on_ticks(self, msg):
        if len(msg.data) < 2:
            return
        now = self.get_clock().now()
        current = (int(msg.data[0]), int(msg.data[1]))
        if self.last_ticks is None:
            self.last_ticks, self.last_time = current, now
            return
        dt = (now - self.last_time).nanoseconds / 1e9
        if dt <= 0.0:
            return
        dl_ticks = ((current[0] - self.last_ticks[0] + 2**31) % 2**32) - 2**31
        dr_ticks = ((current[1] - self.last_ticks[1] + 2**31) % 2**32) - 2**31
        self.last_ticks, self.last_time = current, now
        meters_per_tick = 2.0 * math.pi * self.radius / self.ticks_per_rev
        dl, dr = dl_ticks * meters_per_tick, dr_ticks * meters_per_tick
        distance = (dl + dr) / 2.0
        dyaw = (dr - dl) / self.wheel_base
        self.x += distance * math.cos(self.yaw + dyaw / 2.0)
        self.y += distance * math.sin(self.yaw + dyaw / 2.0)
        self.yaw = math.atan2(math.sin(self.yaw + dyaw), math.cos(self.yaw + dyaw))
        q = Quaternion(z=math.sin(self.yaw / 2.0), w=math.cos(self.yaw / 2.0))
        odom = Odometry()
        odom.header.stamp, odom.header.frame_id = now.to_msg(), 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x, odom.pose.pose.position.y = self.x, self.y
        odom.pose.pose.orientation = q
        odom.twist.twist.linear.x = distance / dt
        odom.twist.twist.angular.z = dyaw / dt
        odom.pose.covariance[0] = odom.pose.covariance[7] = 0.001
        odom.pose.covariance[35] = 0.005
        self.pub.publish(odom)
        tf = TransformStamped()
        tf.header, tf.child_frame_id = odom.header, 'base_footprint'
        tf.transform.translation.x, tf.transform.translation.y = self.x, self.y
        tf.transform.rotation = q
        self.broadcaster.sendTransform(tf)


def main(args=None):
    rclpy.init(args=args)
    node = OdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
