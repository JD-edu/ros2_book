cmake_minimum_required(VERSION 3.8)
project(ch11_cpp_examples)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(talker src/talker.cpp)
ament_target_dependencies(talker rclcpp std_msgs)

install(
  TARGETS talker
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
