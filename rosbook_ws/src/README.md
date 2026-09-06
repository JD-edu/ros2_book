# ROS 2 Book examples (Chapters 0-11)

Packages are prefixed with the chapter number so that their source chapter is
immediately visible. Chapters 0 and 1 contain no package source. Arduino examples
use only the Uno's built-in LED and USB serial port, so no external circuit is needed.

| Chapter | Package | Example |
|---|---|---|
| 2 | `ch02_robot_interfaces` | `RobotStatus.msg` |
| 2 | `ch02_topic_examples` | custom-message publisher/subscriber |
| 3 | `ch03_service_interfaces` | `SmartAlert.srv` |
| 3 | `ch03_service_examples` | hardware-free service server/client |
| 4 | `ch04_action_interfaces` | `LedBlink.action` |
| 4 | `ch04_action_examples` | hardware-free action server/client |
| 5 | `ch05_parameter_examples` | validated dynamic parameters |
| 6 | `ch06_launch_examples` | talker/listener launch |
| 7-9 | `ch07_09_robot_description` | URDF, TF and RViz launch |
| 10 | `ch10_serial_bridge` | Uno virtual sensors and bidirectional serial bridge |
| 11 | `ch11_python_examples` | Python talker |
| 11 | `ch11_cpp_examples` | C++ talker |

Build and test:

```bash
cd ~/ros2_book_codex/rosbook_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
colcon test
colcon test-result --verbose
```

## Arduino Uno R3 examples

All sketches target `arduino:avr:uno`, use `/dev/ttyACM0` at 115200 baud,
and require no external circuit. Only one program can be installed on the Uno
at a time.

```bash
# Chapter 03 firmware (use the corresponding path for chapters 04, 05, or 10)
arduino-cli compile --fqbn arduino:avr:uno \
  src/ch03_service_examples/firmware/ch03_smart_alert
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno \
  src/ch03_service_examples/firmware/ch03_smart_alert

# Chapter 03 service
ros2 run ch03_service_examples arduino_alert_server
ros2 run ch03_service_examples smart_alert_client 2 1.0

# Chapter 04 action
ros2 run ch04_action_examples arduino_blink_server
ros2 run ch04_action_examples blink_client

# Chapter 05 parameters
ros2 run ch05_parameter_examples arduino_parameter_node
ros2 param set /ch05_arduino_parameter_node led_blink_rate 5
ros2 param set /ch05_arduino_parameter_node warning_mode true

# Chapter 10 bridge (the final firmware left on the test board)
ros2 run ch10_serial_bridge serial_bridge
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.2}}"
ros2 topic echo /encoder_left
ros2 topic echo /imu/data
ros2 topic echo /battery_voltage
```
