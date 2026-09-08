import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'ch15_motor_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='ROS 2 Book',
    maintainer_email='examples@example.com',
    description='Chapter 15 ROS 2 to Arduino motor serial controller.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'motor_serial_node = ch15_motor_control.motor_serial_node:main',
        ],
    },
)
