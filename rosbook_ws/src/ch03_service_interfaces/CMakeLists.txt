cmake_minimum_required(VERSION 3.8)
project(ch03_service_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(
  ${PROJECT_NAME}
  "srv/SmartAlert.srv"
)

ament_package()
