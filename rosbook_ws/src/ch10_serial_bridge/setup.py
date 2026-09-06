from setuptools import setup

package_name = 'ch10_serial_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Book',
    maintainer_email='examples@example.com',
    description='Chapter 10 Arduino serial bridge',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'serial_bridge = ch10_serial_bridge.serial_bridge:main',
        ],
    },
)
