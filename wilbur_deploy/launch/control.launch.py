#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
)
from ament_index_python.packages import get_package_share_directory
from wilbur_deploy.pig_warnings import (
    pig_hardware,
    pig_mockhardware,
    pig_gazebo,
)


def launch_setup(context, *args, **kwargs):

    # Initialize Arguments
    platform = LaunchConfiguration("platform")
    separate_controls_pcs = LaunchConfiguration("separate_controls_pcs")
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")

    # convert platform type to string so that we can evaluate different options
    platform_string = platform.perform(context)
    sim_ignition = "true" if platform_string == "sim_ignition" else "false"
    use_fake_hardware = "true" if platform_string == "mock_hardware" else "false"

    # convert separate controls pc option to bool to figure out what components to launch
    separate_controls_pcs_string = separate_controls_pcs.perform(context)
    separate_controls_pcs_bool = separate_controls_pcs_string == "true"

    # print warning about system type
    if sim_ignition == "true":
        pig_gazebo()
    elif use_fake_hardware == "true":
        pig_mockhardware(separate_controls_pcs_bool)
    else:
        pig_hardware(separate_controls_pcs)

    # common launch args shared across different nodes
    common_launch_args = {
        "sim_ignition": sim_ignition,
        "use_fake_hardware": use_fake_hardware,
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

    # list to keep track of launch file names to start
    launch_file_names = []

    # extra launch files that will be run if we are separating out controls pcs
    ur_specific_launch_files = []

    # This is the "definitive" robot state publisher.
    # This should be launched on whatever machine has the most resources, which
    # along with whichever controller manager we think should com up first.
    launch_file_names.append("robot_state_publisher.launch.py")

    # if we are running on a single controls pc, we just run default controller manager
    # and controller spawners.
    if not separate_controls_pcs_bool:
        # ignition has its own controller manager plugin, so we don't spawn it
        if sim_ignition != "true":
            launch_file_names.append("controller_manager.launch.py")
        launch_file_names.append("spawn_controllers.launch.py")
    # if we are running on different controls pcs, we just launch the w200 components,
    # and the other pc will launch the ur and gripper controller manager and spawners
    else:
        # controllers for warthog
        launch_file_names.append("controller_manager/controller_manager_w200.launch.py")
        launch_file_names.append("spawn_controllers/spawn_controllers_w200.launch.py")

        ur_cm_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("wilbur_deploy"),
                    "launch",
                    "controller_manager",
                    "controller_manager_ur_gripper.launch.py",
                )
            ),
            launch_arguments={
                "ns": "/ur",
                "controller_prefix": "/ur/",
            }.items(),
        )

        ur_spawn_controllers = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("wilbur_deploy"),
                    "launch",
                    "spawn_controllers",
                    "spawn_controllers_ur.launch.py",
                )
            ),
            launch_arguments={
                "sim_ignition": sim_ignition,
                "use_fake_hardware": use_fake_hardware,
                "tf_prefix": tf_prefix,
                "ns": "/ur",
            }.items(),
        )

        ur_specific_launch_files.append(ur_cm_launch)
        ur_specific_launch_files.append(ur_spawn_controllers)

    # generate the launch files based on launch_file_names which has been configured
    launch_files = AddLaunchDescriptions(
        package_name="wilbur_deploy",
        launch_file_names=launch_file_names,
        launch_args=common_launch_args,
    )

    return launch_files + ur_specific_launch_files


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
