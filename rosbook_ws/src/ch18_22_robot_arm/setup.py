import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'ch18_22_robot_arm'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (
            os.path.join('share', package_name, 'firmware', 'robot_arm_firmware'),
            glob('firmware/robot_arm_firmware/*.ino'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Book',
    maintainer_email='examples@example.com',
    description='Five-servo educational robot arm for Chapters 18 through 22.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'arm_bridge = ch18_22_robot_arm.arm_bridge:main',
            'pick_and_place = ch18_22_robot_arm.pick_and_place:main',
        ],
    },
)
