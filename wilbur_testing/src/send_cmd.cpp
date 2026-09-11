#include <memory>
#include <cstdio>
#include <string>

#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>
#include <tf2/LinearMath/Quaternion.hpp>
#include <tf2/utils.hpp>

#include "navigation_testing/utils.hpp"

using std::placeholders::_1;
using namespace std::chrono_literals;

class CmdPublisher : public rclcpp::Node
{
  public:
    CmdPublisher()
      : Node("cmd_publisher")
    {
      this->declare_parameter("x_dot", 0.0);
      this->declare_parameter("theta_dot", 0.0);
      this->declare_parameter("time", 1000);

      x_dot_ = this->get_parameter("x_dot").as_double();
      theta_dot_ = this->get_parameter("theta_dot").as_double();
      max_time_ = this->get_parameter("time").as_int();

      std::string topic = "/velocity_controller/cmd_vel";
      publisher_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(topic, 10);
      timer_ = this->create_wall_timer(100ms, std::bind(&CmdPublisher::timer_callback, this));

      shutdownTimer_ = this->create_wall_timer(
            std::chrono::milliseconds(max_time_),
            std::bind(&CmdPublisher::time_out_callback, this));
    }
    ~CmdPublisher()
    {
        publish_stop();
    }

  private:
    void timer_callback()
    {
      geometry_msgs::msg::TwistStamped msg;
      msg.header.stamp = this->now();
      msg.header.frame_id = "base_link";
      msg.twist.linear.x = x_dot_;
      msg.twist.linear.y = 0.0;
      msg.twist.linear.z = 0.0;
      msg.twist.angular.x = 0.0;
      msg.twist.angular.y = 0.0;
      msg.twist.angular.z = theta_dot_;

      publisher_->publish(msg);
    }

    void time_out_callback() 
    {
        RCLCPP_INFO(this->get_logger(), "Time limit reached. Shutting down node. Done!");
        timer_->cancel();
        publish_stop();
        rclcpp::shutdown();
    }

    void publish_stop()
    {
      geometry_msgs::msg::TwistStamped msg;
      msg.header.stamp = this->now();
      msg.header.frame_id = "base_link";
      msg.twist.linear.x = 0.0;
      msg.twist.linear.y = 0.0;
      msg.twist.linear.z = 0.0;
      msg.twist.angular.x = 0.0;
      msg.twist.angular.y = 0.0;
      msg.twist.angular.z = 0.0;

      publisher_->publish(msg);
    }
  
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::TimerBase::SharedPtr shutdownTimer_;
    rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr publisher_;
    double x_dot_;
    double theta_dot_;
    int32_t max_time_;
};




int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CmdPublisher>());
  rclcpp::shutdown();
  return 0;
}