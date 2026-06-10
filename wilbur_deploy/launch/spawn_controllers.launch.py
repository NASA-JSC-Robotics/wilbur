#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition, UnlessCondition

from wilbur_deploy.launch_utils import AddLaunchDescriptions
from wilbur_deploy.launch_utils import SpawnController


def generate_launch_description():

    declared_arguments = []

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
    declared_arguments.append(
        DeclareLaunchArgument(
            "include_ur",
            default_value="true",
            description="Start robot with simulated hardware mirroring command to its states.",
        )
    )

    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")
    include_ur = LaunchConfiguration("include_ur")

    controller_manager_name = PathJoinSubstitution([ns, "controller_manager"])

    controllers_to_spawn = []
    controllers_to_spawn.append(
        SpawnController(controller_manager_name, "velocity_controller")
    )
    controllers_to_spawn.append(
        SpawnController(controller_manager_name, "joint_state_broadcaster")
    )

    controllers_to_spawn.append(
        SpawnController(
            controller_manager_name,
            "joint_trajectory_controller",
            condition=IfCondition(include_ur),
        )
    )
    controllers_to_spawn.append(
        SpawnController(
            controller_manager_name,
            "robotiq_gripper_hande_controller",
            condition=IfCondition(include_ur),
        )
    )

    return LaunchDescription(declared_arguments + controllers_to_spawn)
