#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
)
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the hardware robot",
        )
    )

    # Initialize Arguments
    ns = LaunchConfiguration("ns")

    # launch main control launch with hardware
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("wilbur_deploy"), "launch", "control.launch.py")
        ),
        launch_arguments={
            "platform": "hardware",
            "ns": ns,
        }.items(),
    )

    return LaunchDescription(declared_arguments + [control_launch])
