import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'ch14_virtual_diffbot'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Book',
    maintainer_email='examples@example.com',
    description='Chapter 14 differential-drive simulator',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'diff_drive_simulator = ch14_virtual_diffbot.diff_drive_simulator:main',
        ],
    },
)
