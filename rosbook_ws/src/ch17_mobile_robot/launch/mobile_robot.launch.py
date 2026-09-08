import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    share = get_package_share_directory('ch17_mobile_robot')
    config = os.path.join(share, 'config', 'robot.yaml')
    urdf_path = os.path.join(share, 'urdf', 'mobile_robot.urdf')
    with open(urdf_path, encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()
    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyACM0'),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description}]),
        Node(package='joint_state_publisher', executable='joint_state_publisher'),
        Node(package='ch17_mobile_robot', executable='motor_node',
             parameters=[config], output='screen'),
        Node(package='ch17_mobile_robot', executable='encoder_node',
             parameters=[config, {'serial_port': LaunchConfiguration('serial_port')}],
             output='screen'),
        Node(package='ch17_mobile_robot', executable='odom_node',
             parameters=[config], output='screen'),
    ])
