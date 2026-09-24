from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = Path(get_package_share_directory('ch18_22_robot_arm'))

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_hardware',
            default_value='false',
            description='false: RViz simulation, true: RViz and physical robot.',
        ),
        DeclareLaunchArgument(
            'port',
            default_value='/dev/ttyACM0',
            description='Arduino serial port used when use_hardware is true.',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Start RViz.',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(share / 'launch' / 'robot_arm.launch.py')
            ),
            launch_arguments={
                'port': LaunchConfiguration('port'),
                'use_hardware': LaunchConfiguration('use_hardware'),
                'use_gui': 'false',
                'use_rviz': LaunchConfiguration('use_rviz'),
            }.items(),
        ),
        Node(
            package='ch18_22_robot_arm',
            executable='pick_and_place',
            name='pick_and_place',
            parameters=[str(share / 'config' / 'poses.yaml')],
            output='screen',
        ),
    ])
