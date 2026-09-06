import math

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster


def yaw_to_quaternion(yaw):
    """Return the z and w components of a planar yaw quaternion."""
    return math.sin(yaw / 2.0), math.cos(yaw / 2.0)


class DiffDriveSimulator(Node):
    def __init__(self):
        super().__init__('ch14_diff_drive_simulator')

        self.declare_parameter('wheel_base', 0.24)
        self.declare_parameter('wheel_radius', 0.05)
        self.declare_parameter('update_rate', 30.0)

        self.wheel_base = float(self.get_parameter('wheel_base').value)
        self.wheel_radius = float(self.get_parameter('wheel_radius').value)
        update_rate = float(self.get_parameter('update_rate').value)
        if self.wheel_base <= 0.0 or self.wheel_radius <= 0.0 or update_rate <= 0.0:
            raise ValueError('wheel_base, wheel_radius, and update_rate must be positive')

        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.left_wheel_position = 0.0
        self.right_wheel_position = 0.0
        self.last_time = self.get_clock().now()

        self.create_subscription(Twist, 'cmd_vel', self.on_cmd_vel, 10)
        self.joint_state_publisher = self.create_publisher(
            JointState, 'joint_states', 10)
        self.odometry_publisher = self.create_publisher(Odometry, 'odom', 10)
        self.transform_broadcaster = TransformBroadcaster(self)
        self.create_timer(1.0 / update_rate, self.update)

        self.get_logger().info(
            f'Ready: wheel_base={self.wheel_base:.3f} m, '
            f'wheel_radius={self.wheel_radius:.3f} m')

    def on_cmd_vel(self, message):
        self.linear_velocity = message.linear.x
        self.angular_velocity = message.angular.z

    def update(self):
        current_time = self.get_clock().now()
        delta_time = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time
        if delta_time <= 0.0:
            return

        half_track = self.wheel_base / 2.0
        left_linear = self.linear_velocity - self.angular_velocity * half_track
        right_linear = self.linear_velocity + self.angular_velocity * half_track
        left_angular = left_linear / self.wheel_radius
        right_angular = right_linear / self.wheel_radius

        self.left_wheel_position += left_angular * delta_time
        self.right_wheel_position += right_angular * delta_time

        delta_distance = self.linear_velocity * delta_time
        delta_yaw = self.angular_velocity * delta_time
        middle_yaw = self.yaw + delta_yaw / 2.0
        self.x += delta_distance * math.cos(middle_yaw)
        self.y += delta_distance * math.sin(middle_yaw)
        self.yaw = math.atan2(
            math.sin(self.yaw + delta_yaw),
            math.cos(self.yaw + delta_yaw),
        )
        quaternion_z, quaternion_w = yaw_to_quaternion(self.yaw)

        joint_state = JointState()
        joint_state.header.stamp = current_time.to_msg()
        joint_state.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_state.position = [
            self.left_wheel_position,
            self.right_wheel_position,
        ]
        joint_state.velocity = [left_angular, right_angular]
        self.joint_state_publisher.publish(joint_state)

        transform = TransformStamped()
        transform.header.stamp = current_time.to_msg()
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_footprint'
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.rotation.z = quaternion_z
        transform.transform.rotation.w = quaternion_w
        self.transform_broadcaster.sendTransform(transform)

        odometry = Odometry()
        odometry.header.stamp = current_time.to_msg()
        odometry.header.frame_id = 'odom'
        odometry.child_frame_id = 'base_footprint'
        odometry.pose.pose.position.x = self.x
        odometry.pose.pose.position.y = self.y
        odometry.pose.pose.orientation.z = quaternion_z
        odometry.pose.pose.orientation.w = quaternion_w
        odometry.twist.twist.linear.x = self.linear_velocity
        odometry.twist.twist.angular.z = self.angular_velocity
        self.odometry_publisher.publish(odometry)


def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
