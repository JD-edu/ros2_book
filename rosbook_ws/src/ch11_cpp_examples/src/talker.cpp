#include <chrono>
#include <memory>
#include <string>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class Talker : public rclcpp::Node
{
public:
  Talker() : Node("ch11_cpp_talker"), count_(0)
  {
    publisher_ = create_publisher<std_msgs::msg::String>("ch11_chatter", 10);
    timer_ = create_wall_timer(std::chrono::milliseconds(500), [this]() {
      std_msgs::msg::String message;
      message.data = "Hello ROS 2 from C++: " + std::to_string(++count_);
      publisher_->publish(message);
    });
  }

private:
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  int count_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Talker>());
  rclcpp::shutdown();
  return 0;
}
