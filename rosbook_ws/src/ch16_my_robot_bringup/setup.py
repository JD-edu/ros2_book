from setuptools import find_packages, setup

package_name = 'ch16_my_robot_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Book',
    maintainer_email='examples@example.com',
    description='Chapter 16 Arduino encoder and odometry example.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'differential_odom_node = my_robot_bringup.differential_odom_node:main',
        ],
    },
)
