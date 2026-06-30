#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
)
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import PushRosNamespace


def generate_launch_description():

    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("wilbur_deploy"),
                "launch",
                "control.launch.py",
            )
        ),
        launch_arguments={
            "platform": "mock_hardware",
            "robot_description_package": "wilbur_mujoco_config",
            "robot_description_file": "wilbur_xacro.urdf",
            "use_sim_time": "true",
        }.items(),
    )

    return LaunchDescription([control_launch])
