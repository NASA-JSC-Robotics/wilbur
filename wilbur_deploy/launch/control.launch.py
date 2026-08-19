#!/usr/bin/env python3
#
# Copyright (c) 2026, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
#
# All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from wilbur_deploy.pig_warnings import (
    pig_hardware,
    pig_mockhardware,
    pig_gazebo,
    pig_mujoco,
)
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node

from wilbur_deploy.launch_utils import AddLaunchDescriptions


def launch_setup(context, *args, **kwargs):
    # Initialize Arguments
    robot_description_package = LaunchConfiguration("robot_description_package")
    robot_description_file = LaunchConfiguration("robot_description_file")
    platform = LaunchConfiguration("platform").perform(context)
    include_ur = LaunchConfiguration("include_ur").perform(context)
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")
    extra_xacro_args = LaunchConfiguration("extra_xacro_args").perform(context)

    sim_gazebo = "false"
    use_mock_hardware = "false"


    pkg_deploy = get_package_share_directory("wilbur_deploy")

    # Decide which platform we are using
    match platform:
        case "sim_gazebo":
            print("Gazebo sim")
            sim_gazebo = "true"
            pig_gazebo()
        case "mock_hardware":
            print("Mock hardware")
            use_mock_hardware = "true"
            pig_mockhardware()
        case "hardware":
            print("Launching hardware")
            pig_hardware()
        case "sim_mujoco":
            pig_mujoco()
        case _:
            raise AttributeError

    launch_files = []

    # This is the main robot description for Wilbur.
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare(robot_description_package), "urdf", robot_description_file]),
            " ",
            "tf_prefix:=",
            tf_prefix,
            " ",
            "ns:=",
            ns,
            " ",
            "include_ur:=",
            include_ur,
            " ",
            extra_xacro_args,
        ]
    )

    # common launch args shared across different nodes
    common_launch_args = {
        "sim_ignition": sim_gazebo,
        "sim_gazebo": sim_gazebo,
        "abs_mesh_paths": sim_gazebo,
        "use_fake_hardware": use_mock_hardware,
        "include_ur": include_ur,
        "tf_prefix": tf_prefix,
        "ns": ns,
    }

    # List to keep track of launch file names to start
    launch_file_names = []
    # Gazebo handles it's own controller_manager
    if platform != "sim_gazebo":
        launch_file_names.append("controller_manager.launch.py")

#    launch_file_names.append("spawn_controllers.launch.py")


    ## Generate the launch files based on launch_file_names which has been configured
    launch_files = AddLaunchDescriptions(
        package_name="wilbur_deploy",
        launch_file_names=launch_file_names,
        launch_args=common_launch_args.items(),
    )

    spawn_launch_args = common_launch_args
    spawn_launch_args.update({"wheel_separation_multiplier": LaunchConfiguration("wheel_separation_multiplier")})

    launch_files.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_deploy, "launch", "spawn_controllers.launch.py")),
            launch_arguments=
                spawn_launch_args.items()
        )
    )

    if platform != "sim_mujoco":
        robot_description = {"robot_description": ParameterValue(value=robot_description_content, value_type=str)}
        robot_state_publisher_node = Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="both",
            parameters=[robot_description],
        )
        launch_files.append(robot_state_publisher_node)

    return launch_files


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_description_package",
            default_value="wilbur_description",
            description="The package to find the robot description.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_description_file",
            default_value="wilbur.urdf.xacro",
            description="The name of the robot description file. "
            "Must be in the 'urdf' folder of the description package.",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "platform",
            default_value="hardware",
            description="Whether to run the robot on hardware, mock_hardware, or sim_gazebo.",
            choices=["hardware", "mock_hardware", "sim_gazebo", "sim_mujoco"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "include_ur",
            default_value="true",
            description="If running with separate_controls_pcs, set to true to launch the UR in a standalone config.",
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
    declared_arguments.append(
        DeclareLaunchArgument(
            "wheel_separation_multiplier",
            default_value="",
            description="Multiplier for the velocity_controller effective wheel separation",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "extra_xacro_args",
            default_value="",
            description="Extra args to add for making a robot description. "
            "Should be in the format of 'arg1:=value1 arg2:=value2'",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
