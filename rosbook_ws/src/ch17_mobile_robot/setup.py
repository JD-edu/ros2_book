import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'ch17_mobile_robot'
setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'firmware', 'mobile_robot_firmware'),
         glob('firmware/mobile_robot_firmware/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Book', maintainer_email='examples@example.com',
    description='Chapter 17 complete two-wheel mobile robot.',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'motor_node = ch17_mobile_robot.motor_node:main',
        'encoder_node = ch17_mobile_robot.encoder_node:main',
        'odom_node = ch17_mobile_robot.odom_node:main',
    ]},
)
