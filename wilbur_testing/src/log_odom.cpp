#include <memory>
#include <cstdio>
#include <string>
#include <format>

#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>
#include <tf2/LinearMath/Quaternion.hpp>
#include <tf2/utils.hpp>
#include <angles/angles.h>

#include "navigation_testing/utils.hpp"

using std::placeholders::_1;
using namespace std::chrono_literals;

#define SQ(x)((x)*(X))

template <typename T>
std::string to_string_with_precision(const T value, const int precision = 2) {
    std::ostringstream out;
    out << std::fixed << std::setprecision(precision) << value;
    return out.str();
}


class OdomSubscriber : public rclcpp::Node
{
  public:
    OdomSubscriber()
    : Node("odom_subscriber")
    , gtInit_(false)
    , odInit_(false)
    , sep_(false)
    {
      this->declare_parameter("x_dot", 0.0);
      this->declare_parameter("theta_dot", 0.0);
      this->declare_parameter<bool>("separate", false);
      fptr[GT] = nullptr;
      fptr[OD] = nullptr;

      memset(gtState_, 0, NUM_STATE*sizeof(double));
      memset(odState_, 0, NUM_STATE*sizeof(double));

      std::string x_dot_str = to_string_with_precision<double>(this->get_parameter("x_dot").as_double(), 2);
      std::string theta_dot_str = to_string_with_precision<double>(this->get_parameter("theta_dot").as_double(), 2);
      
      sep_ = this->get_parameter("separate").as_bool();;

       gtSubscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/simulator/floating_base_state", 10, std::bind(&OdomSubscriber::ground_truth_callback, this, _1));
       odSubscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/velocity_controller/odom", 10, std::bind(&OdomSubscriber::odom_callback, this, _1));

      if(sep_)
      {
        std::string basefilename = "gt_" + x_dot_str + "_theta_" + theta_dot_str + "_";
        std::string filename = generate_timestamp_filename(basefilename, "csv");
        fptr[GT] = fopen(filename.c_str(), "w");
        fprintf(fptr[GT],"time, gt_x, gt_y, gt_theta, gt_x_rate, gt_theta_rate, gt_total_x, gt_total_theta\n");
        
        basefilename = "od_" + x_dot_str + "_theta_" + theta_dot_str + "_";
        filename = generate_timestamp_filename(basefilename, "csv");
        fptr[OD] = fopen(filename.c_str(), "w");
        fprintf(fptr[OD],"time, od_x, od_y, od_theta, od_x_rate, od_theta_rate, od_total_x, od_total_theta\n");
      }
      else
      {
        std::string basefilename = "gt_od_x_" + x_dot_str + "_theta_" + theta_dot_str + "_";
        std::string filename = generate_timestamp_filename(basefilename, "csv");
        fptr[0] = fopen(filename.c_str(), "w");
        fprintf(fptr[0],"time, gt_x, gt_y, gt_theta, gt_x_rate, gt_theta_rate, gt_total_x, gt_total_theta, od_x, od_y, od_theta, od_x_rate, od_theta_rate, od_total_x, od_total_theta\n");

      }
    }

    ~OdomSubscriber()
    {
        double xErr = std::abs(gtState_[TOTAL_X] - odState_[TOTAL_X]);
        double thetaErr = std::abs(gtState_[TOTAL_THETA] - odState_[TOTAL_THETA]);
        RCLCPP_INFO(this->get_logger(), "X error = %0.3lf, -- %0.2lf %%", xErr, xErr/std::abs(gtState_[TOTAL_X])*100.0);
        RCLCPP_INFO(this->get_logger(), "Theta error = %0.3lf, -- %0.2lf %%", thetaErr, thetaErr/std::abs(gtState_[TOTAL_THETA])*100.0);

        if(fptr[0]) 
        {
            fclose(fptr[0]);
            fptr[0] = nullptr;
        }
        if(fptr[1]) 
        {
            fclose(fptr[1]);
            fptr[1] = nullptr;
        }
    }

  private:
  
    enum {X = 0, Y, YAW, X_RATE, YAW_RATE, TOTAL_X, TOTAL_THETA, LAST_TIME, NUM_STATE};
    enum{GT = 0, OD, BOTH};

    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr gtSubscription_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odSubscription_;
    
    int32_t sep_;
    double gtState_[NUM_STATE];
    double odState_[NUM_STATE];
    bool gtInit_;
    bool odInit_;
    double gtLastTime_;
    double odLastTime_;
    FILE* fptr[2];

    void ground_truth_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
      
      rclcpp::Time timeObj(msg->header.stamp);
      double timeVal = timeObj.seconds();

      compute(msg, gtState_, gtInit_);
      if(sep_ && gtInit_)
      {
        log(timeVal, GT);
      }
      gtInit_ = true;
    }

    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {

      rclcpp::Time timeObj(msg->header.stamp);
      double timeVal = timeObj.seconds();

      compute(msg, odState_, odInit_);
      if(sep_ && odInit_)
      {
        log(timeVal, OD);
      }
      else if(!sep_ && odInit_ && gtInit_)
      {
        log(timeVal, BOTH);
      }
      odInit_ = true;
    }

    void compute(const nav_msgs::msg::Odometry::SharedPtr msg, double state[NUM_STATE], bool& init)
    {
      rclcpp::Time timeObj(msg->header.stamp);
      double timeVal = timeObj.seconds();
      double dt = timeVal - state[LAST_TIME];

      tf2::Quaternion q(msg->pose.pose.orientation.x, msg->pose.pose.orientation.y, msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
      if(init)
      {
         double xDiff = std::sqrt(std::pow((msg->pose.pose.position.x - state[X]),2) + std::pow((msg->pose.pose.position.y - state[Y]),2));
         double yawDiff = angles::shortest_angular_distance(state[YAW], tf2::getYaw(q));
         state[YAW_RATE] = std::abs(yawDiff)/dt;
         state[X_RATE] = xDiff/dt;
         state[TOTAL_X] += xDiff;
         state[TOTAL_THETA] += yawDiff;
      }
      state[X] = msg->pose.pose.position.x;
      state[Y] = msg->pose.pose.position.y;
      state[YAW] = tf2::getYaw(q);
      state[LAST_TIME] = timeVal;
      init = true;
    }

    void log(double timeA, int type = BOTH)
    {
      switch(type)
      {
        case BOTH:
          fprintf(fptr[0], "%lf,", timeA);
          fprintf(fptr[0], "%lf, %lf, %lf, %lf, %lf, %lf, %lf,",  gtState_[0], gtState_[1], gtState_[2], gtState_[X_RATE], gtState_[YAW_RATE], gtState_[TOTAL_X], gtState_[TOTAL_THETA]);
          fprintf(fptr[0], "%lf, %lf, %lf, %lf, %lf, %lf, %lf\n", odState_[0], odState_[1], odState_[2], odState_[X_RATE], odState_[YAW_RATE], odState_[TOTAL_X], odState_[TOTAL_THETA]);
          break;
        case GT:
          fprintf(fptr[GT], "%lf,", timeA);
          fprintf(fptr[GT], "%lf, %lf, %lf, %lf, %lf, %lf, %lf\n", gtState_[0], gtState_[1], gtState_[2], gtState_[X_RATE], gtState_[YAW_RATE], gtState_[TOTAL_X], gtState_[TOTAL_THETA]);
          break;
        case OD:
          fprintf(fptr[OD], "%lf,", timeA);
          fprintf(fptr[OD], "%lf, %lf, %lf, %lf, %lf, %lf, %lf\n", odState_[0], odState_[1], odState_[2], odState_[X_RATE], odState_[YAW_RATE], odState_[TOTAL_X], odState_[TOTAL_THETA]);
          break;
      }
    }

};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<OdomSubscriber>());
  rclcpp::shutdown();
  return 0;
}