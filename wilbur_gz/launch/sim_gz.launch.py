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

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    GroupAction,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from launch.conditions import IfCondition


def launch_setup(context, *args, **kwargs):
    # Initialize Arguments
    tf_prefix = LaunchConfiguration("tf_prefix")
    namespace = LaunchConfiguration("ns")

    x = LaunchConfiguration("robot_x")
    y = LaunchConfiguration("robot_y")
    z = LaunchConfiguration("robot_z")

    include_ur = LaunchConfiguration("include_ur")

    if namespace.perform(context) == "":
        use_namespace = "False"
    else:
        use_namespace = "True"

    pkg_deploy = get_package_share_directory("wilbur_deploy")
    pkg_gazebo = get_package_share_directory("wilbur_gz")

    nodes = []

    # Start gazebo with the selected World
    world_group = GroupAction(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(pkg_gazebo, "launch", "start_world.launch.py"))
            )
        ]
    )
    nodes.append(world_group)

    # add the robot to the world
    robot_group = GroupAction(
        [
            PushRosNamespace(condition=IfCondition([use_namespace]), namespace=namespace),
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-entity",
                    "wilbur",
                    "-name",
                    "wilbur",
                    "-topic",
                    "robot_description",
                    "-x",
                    x,
                    "-y",
                    y,
                    "-z",
                    z,
                    "-controller_manager",
                    "controller_manager",
                ],
                output="screen",
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="sim_bridge",
                parameters=[
                    {
                        "config_file": os.path.join(pkg_gazebo, "config", "bridge.yaml"),
                        "qos_overrides./tf_static.publisher.durability": "transient_local",
                    }
                ],
                output="screen",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(pkg_deploy, "launch", "control.launch.py")),
                launch_arguments={
                    "robot_description_package": "wilbur_gz",
                    "robot_description_file": "wilbur_gz.urdf.xacro",
                    "platform": "sim_ignition",
                    "tf_prefix": tf_prefix,
                    "ns": namespace,
                    "include_ur": include_ur,
                    "extra_xacro_args": "abs_mesh_paths:=true",
                }.items(),
            ),
        ]
    )
    nodes.append(robot_group)

    return nodes


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "tf_prefix",
            default_value='""',
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, also joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(DeclareLaunchArgument("ns", default_value=""))
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_x",
            default_value="0.0",
            description="X position of the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_y",
            default_value="0.0",
            description="Y position of the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_z",
            default_value="0.2",
            description="Z position of the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="namespace of the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "include_ur",
            default_value="true",
            description="Adds/removes the UR10e arm from the configuration.",
            choices=["true", "false"],
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
