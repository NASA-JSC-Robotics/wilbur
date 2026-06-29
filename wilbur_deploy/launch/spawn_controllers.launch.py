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
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from wilbur_deploy.launch_utils import SpawnController
from launch.conditions import IfCondition


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
    ns = LaunchConfiguration("ns")
    include_ur = LaunchConfiguration("include_ur")

    controller_manager_name = PathJoinSubstitution([ns, "controller_manager"])

    controllers_to_spawn = []
    controllers_to_spawn.append(SpawnController(controller_manager_name, "velocity_controller"))
    controllers_to_spawn.append(SpawnController(controller_manager_name, "joint_state_broadcaster"))

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
