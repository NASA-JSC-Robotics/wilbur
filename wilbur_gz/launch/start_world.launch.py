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


from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    world_arg = DeclareLaunchArgument(
        "world",
        default_value="empty_world.sdf",
        description="name of the world file",
    )

    world_pkg_arg = DeclareLaunchArgument(
        "world_pkg",
        default_value="wilbur_gz",
        description="name of the package that has the world file",
    )

    world_file = PathJoinSubstitution(
        [FindPackageShare(LaunchConfiguration("world_pkg")), "worlds", LaunchConfiguration("world")]
    )

    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    gz_launch_path = PathJoinSubstitution([pkg_ros_gz_sim, "launch", "gz_sim.launch.py"])

    # TODO: Add an option for gazebo headless?
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch_path),
        launch_arguments={
            "gz_args": ["-r -v 4 ", world_file],
            "on_exit_shutdown": "True",
        }.items(),
    )

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"],
        output="screen",
    )

    return LaunchDescription([world_arg, world_pkg_arg, gz_sim, clock_bridge])
