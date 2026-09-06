from setuptools import setup

package_name = 'ch05_parameter_examples'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Book',
    maintainer_email='examples@example.com',
    description='Chapter 05 parameters',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'parameter_node = ch05_parameter_examples.parameter_node:main',
            'arduino_parameter_node = ch05_parameter_examples.arduino_parameter_node:main',
        ],
    },
)
