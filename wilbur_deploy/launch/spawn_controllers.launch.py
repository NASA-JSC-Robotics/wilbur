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
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction
)
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression
)
from launch_ros.actions import Node
from wilbur_deploy.launch_utils import spawn_controller
from launch.conditions import IfCondition

def launch_setup(context, *args, **kwargs):
    # Initialize Arguments

    ns = LaunchConfiguration("ns")
    include_ur = LaunchConfiguration("include_ur")
    wheel_separation_multiplier = LaunchConfiguration("wheel_separation_multiplier").perform(context)
    use_sim_time = LaunchConfiguration("use_sim_time").perform(context)

    velocity_controller_args = "--ros-args -p wheel_separation_multiplier:=" + wheel_separation_multiplier + " -p use_sim_time:=" + use_sim_time
    joint_state_broadcaster_args = "--ros-args -p use_sim_time:=" + use_sim_time
    imu_broadcaster_args = "--ros-args --remap /imu_broadcaster/imu:=/sensors/imu_0/data_raw -p use_sim_time:=" + use_sim_time

    controller_manager_name = PathJoinSubstitution([ns, "controller_manager"])

    controllers_to_spawn = []
    controllers_to_spawn.append(
        spawn_controller(
            "velocity_controller",
            controller_manager_name=controller_manager_name, 
            controller_ros_args=velocity_controller_args
        )
    )

    controllers_to_spawn.append(
        spawn_controller(
            "joint_state_broadcaster", 
            controller_manager_name=controller_manager_name, 
            controller_ros_args=joint_state_broadcaster_args
        )
    )

    controllers_to_spawn.append(
        spawn_controller(
            "imu_broadcaster",
             controller_manager_name=controller_manager_name,
             controller_ros_args=imu_broadcaster_args
        )
    )
    return(controllers_to_spawn)

def generate_launch_description():

    declared_arguments = []

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
    declared_arguments.append(
        DeclareLaunchArgument(
            "wheel_separation_multiplier",
            default_value="1.0",
            description="Multiplier for the velocity_controller effective wheel separation",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Flag to use simulation clock",
        )
    )
    
    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
