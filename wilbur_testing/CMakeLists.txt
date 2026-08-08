cmake_minimum_required(VERSION 3.5)
project(wilbur_testing)

find_package(ament_cmake REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(angles REQUIRED)
find_package(geometry_msgs)

include_directories(
  include
)


# Add the executable node
add_executable(log_odom src/log_odom.cpp src/utils.cpp)
ament_target_dependencies(log_odom rclcpp nav_msgs tf2 tf2_geometry_msgs angles)

add_executable(log_odom_gz src/log_odom_gz.cpp src/utils.cpp)
ament_target_dependencies(log_odom_gz rclcpp nav_msgs tf2 geometry_msgs angles)

add_executable(send_cmd src/send_cmd.cpp)
ament_target_dependencies(send_cmd rclcpp nav_msgs tf2 tf2_geometry_msgs)


# Install the executable so 'ros2 run' can locate it
install(TARGETS
  log_odom
  send_cmd
  log_odom_gz
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(${THIS_PACKAGE_INCLUDE_DEPENDS})

ament_package()

