from setuptools import setup

package_name = 'ch03_service_examples'

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
    description='Chapter 03 service examples',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'smart_alert_server = ch03_service_examples.smart_alert_server:main',
            'arduino_alert_server = ch03_service_examples.arduino_alert_server:main',
            'smart_alert_client = ch03_service_examples.smart_alert_client:main',
        ],
    },
)
