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
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.event_handlers import OnShutdown
from launch.substitutions import (
    PathJoinSubstitution,
    LaunchConfiguration,
    Command,
    FindExecutable,
)
from launch_ros.substitutions import FindPackageShare
from launch.conditions import UnlessCondition, IfCondition
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "launch_rviz",
            default_value="true",
            description="Launch rviz or nah",
        ),
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_pregenerated_mjcf",
            default_value="false",
            description="Use pre-generated mjcf instead of converting it on the fly.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_speed",
            default_value="1.0",
            description="Percentage speed to run the simulation at. 1.0 is 100 percent speed.",
        )
    )

    use_pregenerated_mjcf = LaunchConfiguration("use_pregenerated_mjcf")
    sim_speed = LaunchConfiguration("sim_speed")

    wilbur_mujoco_package_name = "wilbur_mujoco_config"
    wilbur_mujoco_description_file = "wilbur_mujoco_xacro.urdf"
    rviz_config_file = os.path.join(get_package_share_directory("wilbur_mujoco_config"), "rviz", "mujoco.rviz")

    mjcf_robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(wilbur_mujoco_package_name), "urdf", wilbur_mujoco_description_file]
            ),
            " base_joint_type:=floating",
        ]
    )

    # Using an inline opaque function to write the URDF for mujoco to a tempfile...
    # This prevents it from being dumped into the console on conversion errors.
    def launch_mjcf_node(context):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".urdf", delete=False)
        tmp.write(mjcf_robot_description_content.perform(context))
        tmp.close()

        # Ensure the file gets deleted
        def cleanup(event, context):
            if os.path.exists(tmp.name):
                os.remove(tmp.name)

        return [
            Node(
                package="mujoco_ros2_control",
                executable="make_mjcf_from_robot_description.py",
                output="both",
                emulate_tty=True,
                arguments=[
                    "--publish_topic",
                    "/mujoco_robot_description",
                    "--urdf",
                    tmp.name,
                ],
                condition=UnlessCondition(use_pregenerated_mjcf),
            ),
            RegisterEventHandler(OnShutdown(on_shutdown=cleanup)),
        ]

    generate_mjcf = OpaqueFunction(function=launch_mjcf_node)

    extra_xacro_args = [" use_pregenerated_mjcf:=", use_pregenerated_mjcf, " sim_speed:=", sim_speed]
    extra_controller_params_file = PathJoinSubstitution(
        [FindPackageShare(wilbur_mujoco_package_name), "config", "mujoco_plugins.yaml"]
    )
    # Include the control launch file with relevant configuration
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
            "robot_description_file": "wilbur_mujoco_xacro.urdf",
            "use_sim_time": "true",
            "extra_xacro_args": extra_xacro_args,
            "extra_controller_params_file": extra_controller_params_file,
        }.items(),
    )
    rviz_launch = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="log",
            arguments=["-d", rviz_config_file],
        )
    return LaunchDescription(declared_arguments + [generate_mjcf, control_launch])
