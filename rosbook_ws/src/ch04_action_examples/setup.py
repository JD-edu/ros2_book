from setuptools import setup

package_name = 'ch04_action_examples'

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
    description='Chapter 04 action examples',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'blink_server = ch04_action_examples.blink_server:main',
            'arduino_blink_server = ch04_action_examples.arduino_blink_server:main',
            'blink_client = ch04_action_examples.blink_client:main',
        ],
    },
)
