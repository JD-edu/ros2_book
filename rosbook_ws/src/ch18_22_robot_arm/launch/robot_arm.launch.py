from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = Path(get_package_share_directory('ch18_22_robot_arm'))
    robot_description = (share / 'urdf' / 'robot_arm.urdf').read_text()

    return LaunchDescription([
        DeclareLaunchArgument('port', default_value='/dev/ttyACM0'),
        DeclareLaunchArgument(
            'use_hardware',
            default_value='true',
            description='Start the serial bridge for the physical robot.',
        ),
        DeclareLaunchArgument(
            'use_gui',
            default_value='true',
            description='Start Joint State Publisher GUI so movable-joint TF is available.',
        ),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            condition=IfCondition(LaunchConfiguration('use_gui')),
        ),
        Node(
            package='ch18_22_robot_arm',
            executable='arm_bridge',
            parameters=[str(share / 'config' / 'servo.yaml'), {
                'port': LaunchConfiguration('port'),
            }],
            condition=IfCondition(LaunchConfiguration('use_hardware')),
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', str(share / 'rviz' / 'robot_arm.rviz')],
            condition=IfCondition(LaunchConfiguration('use_rviz')),
        ),
    ])
