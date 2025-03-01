cmake_minimum_required(VERSION 3.5)
project(wilbur_gz)

find_package(ament_cmake REQUIRED)
#find_package(ament_cmake_python REQUIRED)
#find_package(rclpy REQUIRED)

install(
  DIRECTORY urdf config
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(${THIS_PACKAGE_INCLUDE_DEPENDS})

ament_package()
