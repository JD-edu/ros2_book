from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    arguments = [
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyACM0'),
        DeclareLaunchArgument('baud_rate', default_value='115200'),
        DeclareLaunchArgument('wheel_separation', default_value='0.20'),
        DeclareLaunchArgument('max_linear_speed', default_value='0.5'),
        DeclareLaunchArgument('max_pwm', default_value='255'),
    ]
    motor_node = Node(
        package='ch15_motor_control',
        executable='motor_serial_node',
        name='motor_serial_node',
        output='screen',
        parameters=[{
            'serial_port': LaunchConfiguration('serial_port'),
            'baud_rate': LaunchConfiguration('baud_rate'),
            'wheel_separation': LaunchConfiguration('wheel_separation'),
            'max_linear_speed': LaunchConfiguration('max_linear_speed'),
            'max_pwm': LaunchConfiguration('max_pwm'),
        }],
    )
    return LaunchDescription(arguments + [motor_node])
