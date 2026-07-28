#!/usr/bin/env python3
#
# Copyright (c) 2025, United States Government, as represented by the
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
import tempfile
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnShutdown
from launch.actions import RegisterEventHandler, DeclareLaunchArgument, OpaqueFunction


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_pregenerated_assets_dir",
            default_value="false",
            choices=["true", "false"],
            description="Use pre-generated assets dir. This is useful if you are just modifying an existing structure",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "include_ur",
            default_value="true",
            choices=["true", "false"],
            description="Whether or not to include the UR10e in the converted MCJF",
        )
    )

    wilbur_mujoco_package_name = "wilbur_mujoco_config"
    wilbur_mujoco_description_file = "wilbur_mujoco_xacro.urdf"

    use_pregenerated_assets_dir = LaunchConfiguration("use_pregenerated_assets_dir")
    include_ur = LaunchConfiguration("include_ur")

    # main robot description for wilbur
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare(wilbur_mujoco_package_name),
                    "urdf",
                    wilbur_mujoco_description_file,
                ]
            ),
            " base_joint_type:=floating",
            " include_ur:=",
            include_ur,
        ]
    )

    def launch_mjcf_node(context):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".urdf", delete=False)
        tmp.write(robot_description_content.perform(context))
        tmp.close()

        default_arguments = [
            "--urdf",
            tmp.name,
            "--save_only",
        ]

        if use_pregenerated_assets_dir.perform(context) == "true":
            default_arguments = default_arguments + [
                "--asset_dir",
                PathJoinSubstitution([FindPackageShare(wilbur_mujoco_package_name), "description", "assets"]),
            ]

        generate_mjcf = Node(
            package="mujoco_ros2_control",
            executable="make_mjcf_from_robot_description.py",
            output="both",
            emulate_tty=True,
            arguments=default_arguments,
        )

        # Ensure the file gets deleted
        def cleanup(event, context):
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

        return [
            generate_mjcf,
            RegisterEventHandler(OnShutdown(on_shutdown=cleanup)),
        ]

    generate_mjcf = OpaqueFunction(function=launch_mjcf_node)

    return LaunchDescription(
        declared_arguments
        + [
            generate_mjcf,
        ]
    )
