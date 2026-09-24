"""Non-blocking, teach-and-playback Pick & Place example."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from .joint_mapper import JOINT_NAMES


class PickAndPlace(Node):
    def __init__(self):
        super().__init__('pick_and_place')
        self.declare_parameter('publish_rate', 30.0)
        self.declare_parameter('move_duration', 1.5)
        self.declare_parameter('pause_duration', 0.5)
        defaults = {
            'home': [0.0, 0.0, 0.0, 0.0, 0.0],
            'pick_up': [0.0, 0.35, -0.62, 0.28, 0.0],
            'pick': [0.0, 0.65, -0.95, 0.30, 0.0],
            'grip': [0.0, 0.65, -0.95, 0.30, 3.1416],
            'place_up': [1.20, 0.35, -0.62, 0.28, 3.1416],
            'place': [1.20, 0.65, -0.95, 0.30, 3.1416],
            'release': [1.20, 0.65, -0.95, 0.30, 0.0],
        }
        self.poses = {}
        for name, value in defaults.items():
            self.declare_parameter(f'poses.{name}', value)
            pose = list(self.get_parameter(f'poses.{name}').value)
            if len(pose) != len(JOINT_NAMES):
                raise ValueError(f'pose {name} must contain five positions')
            self.poses[name] = pose

        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        rate = float(self.get_parameter('publish_rate').value)
        duration = float(self.get_parameter('move_duration').value)
        if rate <= 0.0 or duration <= 0.0:
            raise ValueError('publish_rate and move_duration must be positive')
        self.steps_per_move = max(1, round(rate * duration))
        self.pause_steps = max(0, round(rate * float(
            self.get_parameter('pause_duration').value)))
        self.sequence = [
            'home', 'pick_up', 'pick', 'grip', 'pick_up',
            'place_up', 'place', 'release', 'place_up', 'home',
        ]
        self.current = list(self.poses['home'])
        self.start = list(self.current)
        self.target_index = 0
        self.step = 0
        self.pause = self.pause_steps
        self.finished = False
        self.timer = self.create_timer(1.0 / rate, self.update)
        self.get_logger().info('Pick & Place sequence ready')

    def publish(self, positions):
        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = list(JOINT_NAMES)
        message.position = list(positions)
        self.publisher.publish(message)

    def update(self):
        if self.finished:
            return
        if self.pause > 0:
            self.pause -= 1
            self.publish(self.current)
            return

        target_name = self.sequence[self.target_index]
        target = self.poses[target_name]
        self.step += 1
        ratio = min(1.0, self.step / self.steps_per_move)
        self.current = [
            start + (goal - start) * ratio
            for start, goal in zip(self.start, target)
        ]
        self.publish(self.current)

        if ratio >= 1.0:
            self.get_logger().info(f'Reached pose: {target_name}')
            self.target_index += 1
            if self.target_index >= len(self.sequence):
                self.finished = True
                self.get_logger().info('Pick & Place sequence complete')
                return
            self.start = list(self.current)
            self.step = 0
            self.pause = self.pause_steps


def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlace()
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
