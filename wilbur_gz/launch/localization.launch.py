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

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


import os
from ament_index_python.packages import get_package_share_directory


def launch_setup(context, *args, **kwargs):
    # ======================================
    # Initialize Arguments
    # ======================================
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")

    config_file = os.path.join(
        get_package_share_directory("wilbur_gz"), "config", "localization.yaml"
    )

    ekf_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_node",
        parameters=[config_file],
        remappings=[
            ("odometry/filtered", "odom/filtered"),
            ("/diagnostics", "diagnostics"),
            ("/tf", "tf"),
            ("/tf_static", "tf_static"),
        ],
        output="screen",
    )
    return [ekf_node]


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

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
