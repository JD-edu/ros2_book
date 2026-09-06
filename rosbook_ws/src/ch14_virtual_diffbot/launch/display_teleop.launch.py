import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('ch14_virtual_diffbot')
    urdf_path = os.path.join(package_share, 'urdf', 'ch14_diffbot.urdf')
    rviz_path = os.path.join(package_share, 'rviz', 'ch14_diffbot.rviz')

    with open(urdf_path, encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    use_rviz = LaunchConfiguration('use_rviz')

    return LaunchDescription([
        DeclareLaunchArgument('use_rviz', default_value='true'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),
        Node(
            package='ch14_virtual_diffbot',
            executable='diff_drive_simulator',
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
