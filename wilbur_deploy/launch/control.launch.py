#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
)
from ament_index_python.packages import get_package_share_directory


def launch_setup(context, *args, **kwargs):

    # Initialize Arguments
    platform = LaunchConfiguration("platform")
    separate_controls_pcs = LaunchConfiguration("separate_controls_pcs")
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")

    platform_string = platform.perform(context)
    separate_controls_pcs_string = separate_controls_pcs.perform(context)

    sim_ignition = platform_string == "sim_ignition"
    sim_ignition_bool = "true" if sim_ignition else "false"
    use_fake_hardware = platform_string == "mock_hardware"
    use_fake_hardware_bool = "true" if use_fake_hardware else "false"

    separate_controls_pcs_bool = separate_controls_pcs_string == "true"

    common_launch_args = {
        "sim_ignition": sim_ignition_bool,
        "use_fake_hardware": use_fake_hardware_bool,
        "tf_prefix": tf_prefix,
        "ns": ns,
    }.items()

    # helper function to organize launch description objects with the same launch args and package names
    def AddLaunchDescriptions(package_name, launch_file_names, launch_args):
        launch_files_list = []
        for launch_file_name in launch_file_names:
            launch_files_list.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(get_package_share_directory(package_name), "launch", launch_file_name)
                    ),
                    launch_arguments=launch_args,
                )
            )

        return launch_files_list

    # This is the "definitive" robot state publisher.
    # This should be launched on whatever machine has the most resources, which
    # along with whichever controller manager we think should com up first.
    launch_file_names = ["robot_state_publisher.launch.py"]

    if not separate_controls_pcs_bool:
        # ignition has its own controller manager plugin
        if not sim_ignition:
            launch_file_names.append("controller_manager.launch.py")
        launch_file_names.append("spawn_controllers.launch.py")
    else:
        launch_file_names.append("controller_manager_w200.launch.py")
        launch_file_names.append("spawn_controllers_w200.launch.py")
        # launch_file_names.append("spawn_controllers_ur.launch.py") (prefix ur)
        # launch_file_names.append("spawn_controllers_hande.launch.py") (prefix ur)
        # launch_file_names.append("controller_manager_ur_gripper.launch.py") (launched remotely)

    launch_files = AddLaunchDescriptions(
        package_name="wilbur_deploy", launch_file_names=launch_file_names, launch_args=common_launch_args
    )
    return launch_files


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "platform",
            default_value="hardware",
            description="Whether to run the robot on hardware, mock_hardware, or sim_ignition.",
            choices=["hardware", "mock_hardware", "sim_ignition"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "separate_controls_pcs",
            default_value="false",
            description="Whether you want to run the controller managers on two separate pcs.",
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

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
