#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the hardware robot",
        )
    )

    ns = LaunchConfiguration("ns")

    # namespace the controller manager based on ns argument
    controller_manager_name = PathJoinSubstitution([ns, "controller_manager"])

    nodes = []

    # helper function to make controller nodes
    def MakeControllerNode(controller_name):
        return Node(
            package="controller_manager",
            executable="spawner",
            name=controller_name,
            arguments=[
                "--controller-manager",
                controller_manager_name,
                controller_name,
                "--controller-manager-timeout",
                "300",
            ],
            output="screen",
        )

    nodes.append(MakeControllerNode("velocity_controller"))
    nodes.append(MakeControllerNode("w200_joint_state_broadcaster"))

    return LaunchDescription(declared_arguments + nodes)
