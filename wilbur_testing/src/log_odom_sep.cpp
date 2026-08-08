#include <memory>
#include <cstdio>
#include <string>
#include <format>

#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <tf2/LinearMath/Quaternion.hpp>
#include <tf2/utils.hpp>
#include <angles/angles.h>

#include "navigation_testing/utils.hpp"

using std::placeholders::_1;
using namespace std::chrono_literals;

template <typename T>
std::string to_string_with_precision(const T value, const int precision = 2) {
    std::ostringstream out;
    out << std::fixed << std::setprecision(precision) << value;
    return out.str();
}


class DataSubscriber : public rclcpp::Node
{
  public:
    DataSubscriber()
    : Node("data_subscriber")
    , gtInit_(false)
    , odInit_(false)
    {
      this->declare_parameter("x_dot", 0.0);
      this->declare_parameter("theta_dot", 0.0);

      memset(gtState_, 0, NUM_STATE*sizeof(double));
      memset(odState_, 0, NUM_STATE*sizeof(double));

      std::string x_dot_str = to_string_with_precision<double>(this->get_parameter("x_dot").as_double(), 2);
      std::string theta_dot_str = to_string_with_precision<double>(this->get_parameter("theta_dot").as_double(), 2);

       gtSubscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/simulator/floating_base_state", 10, std::bind(&DataSubscriber::ground_truth_callback, this, _1));
       odSubscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/velocity_controller/odom", 10, std::bind(&DataSubscriber::odom_callback, this, _1));

      std::string basefilename = "odom_" + x_dot_str + "_theta_" + theta_dot_str + "_";
      std::string filename = generate_timestamp_filename(basefilename, "csv");
      odFptr_ = fopen(filename.c_str(), "w");
      fprintf(odFptr_,"time, od_x, od_y, od_theta, od_x_rate, od_theta_rate\n");

      basefilename = "gt_" + x_dot_str + "_theta_" + theta_dot_str + "_";
      filename = generate_timestamp_filename(basefilename, "csv");
      gtFptr_ = fopen(filename.c_str(), "w");
      fprintf(gtFptr_,"time, gt_x, gt_y, gt_theta, gt_x_rate, gt_theta_rate\n");
    }

    ~DataSubscriber()
    {
        if(gtFptr_) 
        {
            fclose(gtFptr_);
            gtFptr_ = nullptr;
        }
        if(odFptr_) 
        {
            fclose(odFptr_);
            odFptr_ = nullptr;
        }
    }

  private:
  
    enum {X = 0, Y, YAW, X_RATE, YAW_RATE, LAST_TIME, NUM_STATE};

    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr gtSubscription_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odSubscription_;
    
    double gtState_[NUM_STATE];
    double odState_[NUM_STATE];
    bool gtInit_;
    bool odInit_;
    double gtLastTime_;
    double odLastTime_;
    FILE* odFptr_;
    FILE* gtFptr_;

    void ground_truth_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
    {
      rclcpp::Time timeObj(msg->header.stamp);
      double timeVal = timeObj.seconds();
      double dt = timeVal - gtState_[LAST_TIME];

      tf2::Quaternion q(msg->pose.orientation.x, msg->pose.orientation.y, msg->pose.orientation.z, msg->pose.orientation.w);
      if(gtInit_)
      {
         gtState_[X_RATE]= (msg->pose.position.x - gtState_[X])/dt;
         double yawDiff = angles::shortest_angular_distance(tf2::getYaw(q), gtState_[YAW]);
         gtState_[YAW_RATE]= std::abs(yawDiff)/dt;
      }
      gtState_[X] = msg->pose.position.x;
      gtState_[Y] = msg->pose.position.y;
      gtState_[YAW] = tf2::getYaw(q);
      gtState_[LAST_TIME] = timeVal;
      if(gtInit_)
      {
        fprintf(gtFptr_, "%lf,", timeVal);
        fprintf(gtFptr_, "%lf, %lf, %lf, %lf, %lf,", gtState_[0], gtState_[1], gtState_[2], gtState_[X_RATE], gtState_[YAW_RATE]);
      }
      gtInit_ = true;


    }

    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
      rclcpp::Time timeObj(msg->header.stamp);
      double timeVal = timeObj.seconds();
      double dt = timeVal - odState_[LAST_TIME];

      tf2::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
      if(odInit_)
      {
         odState_[X_RATE]= (msg->pose.pose.position.x - odState_[X])/dt;
         double yawDiff = angles::shortest_angular_distance(tf2::getYaw(q), odState_[YAW]);
         odState_[YAW_RATE]= std::abs(yawDiff)/dt;
      }
      odState_[X] = msg->pose.pose.position.x;
      odState_[Y] = msg->pose.pose.position.y;
      odState_[YAW] = tf2::getYaw(q);
      odState_[LAST_TIME] = timeVal;

      if(odInit_)
      {
        fprintf(odFptr_, "%lf,", timeVal);
        fprintf(odFptr_, "%lf, %lf, %lf, %lf, %lf,", odState_[0], odState_[1], odState_[2], odState_[X_RATE], odState_[YAW_RATE]);
      }
      odInit_ = true;

      
    }

    void log(double timeA)
    {
      fprintf(odFptr_, "%lf,", timeA);
      fprintf(odFptr_, "%lf, %lf, %lf, %lf, %lf,", gtState_[0], gtState_[1], gtState_[2], gtState_[X_RATE], gtState_[YAW_RATE]);
      fprintf(odFptr_, "%lf, %lf, %lf, %lf, %lf\n", odState_[0], odState_[1], odState_[2], odState_[X_RATE], odState_[YAW_RATE]);
    }

};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DataSubscriber>());
  rclcpp::shutdown();
  return 0;
}