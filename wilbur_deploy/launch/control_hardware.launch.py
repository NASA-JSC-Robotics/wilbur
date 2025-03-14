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
            "separate_controls_pcs",
            default_value="false",
            description="Whether you want to run the controller managers on two separate pcs.",
            choices=["true", "false"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "tf_prefix",
            default_value="",
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, also joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the hardware robot",
        )
    )

    # Initialize Arguments
    separate_controls_pcs = LaunchConfiguration("separate_controls_pcs")
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")

    # launch main control launch with hardware
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("wilbur_deploy"), "launch", "control.launch.py")
        ),
        launch_arguments={
            "platform": "hardware",
            "separate_controls_pcs": separate_controls_pcs,
            "tf_prefix": tf_prefix,
            "ns": ns,
        }.items(),
    )

    return LaunchDescription(declared_arguments + [control_launch])
