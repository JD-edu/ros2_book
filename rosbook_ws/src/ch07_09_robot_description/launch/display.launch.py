import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('ch07_09_robot_description')
    with open(os.path.join(share, 'urdf', 'four_wheel_robot.urdf')) as stream:
        description = stream.read()
    use_gui = LaunchConfiguration('use_gui')
    use_rviz = LaunchConfiguration('use_rviz')
    return LaunchDescription([
        DeclareLaunchArgument('use_gui', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': description}]),
        Node(package='joint_state_publisher', executable='joint_state_publisher',
             condition=UnlessCondition(use_gui)),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui',
             condition=IfCondition(use_gui)),
        Node(package='rviz2', executable='rviz2', condition=IfCondition(use_rviz),
             arguments=['-d', os.path.join(share, 'rviz', 'robot.rviz')]),
    ])
