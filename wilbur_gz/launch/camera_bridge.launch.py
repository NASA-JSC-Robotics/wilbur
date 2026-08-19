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


def launch_setup(context, *args, **kwargs):
    # ======================================
    # Initialize Arguments
    # ======================================
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")
    gazebo_camera_name = LaunchConfiguration("gazebo_camera_name").perform(context)
    ros_camera_name = LaunchConfiguration("ros_camera_name").perform(context)

    gz_image_bridge = Node(
        name="gz_image_bridge",
        executable="image_bridge",
        package="ros_gz_image",
        namespace="",
        output="screen",
        arguments=[gazebo_camera_name + "/image"],
        remappings=[
            (
                gazebo_camera_name + "/image",
                ros_camera_name + "/color/image",
            ),
            (
                gazebo_camera_name + "/image/compressed",
                ros_camera_name + "/color/compressed",
            ),
            (
                gazebo_camera_name + "/image/compressedDepth",
                ros_camera_name + "/color/compressedDepth",
            ),
            (
                gazebo_camera_name + "/image/theora",
                ros_camera_name + "/color/theora",
            ),
            (
                gazebo_camera_name + "/image/zstd",
                ros_camera_name + "/color/zstd",
            ),
        ],
        parameters=[{"use_sim_time": True}],
    )

    gz_depth_bridge = Node(
        name="gz_depth_bridge",
        executable="image_bridge",
        package="ros_gz_image",
        namespace="",
        output="screen",
        arguments=[gazebo_camera_name + "/depth_image"],
        remappings=[
            (
                gazebo_camera_name + "/depth_image",
                ros_camera_name + "/depth/image",
            ),
            (
                gazebo_camera_name + "/depth_image/compressed",
                ros_camera_name + "/depth/compressed",
            ),
            (
                gazebo_camera_name + "/depth_image/compressedDepth",
                ros_camera_name + "/depth/compressedDepth",
            ),
            (
                gazebo_camera_name + "/depth_image/theora",
                ros_camera_name + "/depth/theora",
            ),
            (
                gazebo_camera_name + "/depth_image/zstd",
                ros_camera_name + "/depth/zstd",
            ),
        ],
        parameters=[{"use_sim_time": True}],
    )

    return [gz_image_bridge, gz_depth_bridge]


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
            "gazebo_camera_name",
            default_value="/sensors/camera_0",
            description="Extra args to add for making a robot description. "
            "Should be in the format of 'arg1:=value1 arg2:=value2'",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ros_camera_name",
            default_value="/camera_0",
            description="Extra args to add for making a robot description. "
            "Should be in the format of 'arg1:=value1 arg2:=value2'",
        )
    )
    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
