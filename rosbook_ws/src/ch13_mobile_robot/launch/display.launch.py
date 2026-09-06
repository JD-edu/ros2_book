import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('ch13_mobile_robot')
    urdf_path = os.path.join(package_share, 'urdf', 'ch13_mobile_robot.urdf')
    rviz_path = os.path.join(package_share, 'rviz', 'ch13_mobile_robot.rviz')

    with open(urdf_path, encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    use_gui = LaunchConfiguration('use_gui')
    use_rviz = LaunchConfiguration('use_rviz')

    return LaunchDescription([
        DeclareLaunchArgument('use_gui', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            condition=UnlessCondition(use_gui),
            output='screen',
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            condition=IfCondition(use_gui),
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_path],
            condition=IfCondition(use_rviz),
            output='screen',
        ),
    ])
