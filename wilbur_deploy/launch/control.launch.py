#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
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

from wilbur_deploy.launch_utils import AddLaunchDescriptions


def launch_setup(context, *args, **kwargs):

    # Initialize Arguments
    platform = LaunchConfiguration("platform").perform(context)
    separate_controls_pcs = (
        LaunchConfiguration("separate_controls_pcs").perform(context).lower() == "true"
    )
    include_ur = LaunchConfiguration("include_ur").perform(context)
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")

    sim_ignition = "false"
    mock_hardware = "false"
    use_fake_hardware = "false"

    # Decide which platfrom we are using
    match platform:
        case "sim_ignition":
            print("Ignition sim")
            sim_ignition = "true"
            pig_gazebo()
        case "mock_hardware":
            print("Mock hardware")
            mock_hardware = "true"
            use_fake_hardware = "true"
            pig_mockhardware(separate_controls_pcs)
        case "hardware":
            print("Launching hardware")
            pig_hardware(separate_controls_pcs)
        case _:
            raise AttributeError

    # common launch args shared across different nodes
    common_launch_args = {
        "sim_ignition": sim_ignition,
        "abs_mesh_paths": sim_ignition,
        "use_fake_hardware": use_fake_hardware,
        "include_ur": include_ur,
        "tf_prefix": tf_prefix,
        "ns": ns,
    }.items()

    # List to keep track of launch file names to start
    launch_file_names = []

    # Extra launch files that will be run if we are separating out controls pcs
    ur_specific_launch_files = []

    # This is the "definitive" robot state publisher.
    # This should be launched on whatever machine has the most resources, which
    # along with whichever controller manager we think should come up first.
    launch_file_names.append("robot_state_publisher.launch.py")
    launch_file_names.append("spawn_controllers.launch.py")

    # # if we are running on a single controls pc, we just run default controller manager
    # # and controller spawners.
    # if not separate_controls_pcs:
    #     # ignition has its own controller manager plugin, so we don't spawn it
    #     if sim_ignition != "true":
    #         launch_file_names.append("controller_manager.launch.py")
    #     launch_file_names.append("spawn_controllers.launch.py")
    # # if we are running on different controls pcs, we just launch the w200 components by default,
    # # and can conditionally launch namespaced ur components separately
    # else:
    #     if include_ur.lower() == "true":
    #         ur_cm_launch = IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource(
    #                 os.path.join(
    #                     get_package_share_directory("wilbur_deploy"),
    #                     "launch",
    #                     "controller_manager",
    #                     "controller_manager_ur_gripper.launch.py",
    #                 )
    #             ),
    #             launch_arguments={
    #                 "ns": "/ur",
    #                 "controller_prefix": "/ur/",
    #             }.items(),
    #         )
    #         ur_spawn_controllers = IncludeLaunchDescription(
    #             PythonLaunchDescriptionSource(
    #                 os.path.join(
    #                     get_package_share_directory("wilbur_deploy"),
    #                     "launch",
    #                     "spawn_controllers",
    #                     "spawn_controllers_ur.launch.py",
    #                 )
    #             ),
    #             launch_arguments={
    #                 "sim_ignition": sim_ignition,
    #                 "use_fake_hardware": use_fake_hardware,
    #                 "tf_prefix": tf_prefix,
    #                 "ns": "/ur",
    #             }.items(),
    #         )
    #         ur_specific_launch_files.append(ur_cm_launch)
    #         ur_specific_launch_files.append(ur_spawn_controllers)
    #     else:
    #         # controllers for warthog
    #         launch_file_names.append(
    #             "controller_manager/controller_manager_w200.launch.py"
    #         )
    #         launch_file_names.append(
    #             "spawn_controllers/spawn_controllers_w200.launch.py"
    #         )

    # Generate the launch files based on launch_file_names which has been configured
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
            "include_ur",
            default_value="true",
            description="If running with separate_controls_pcs, set to true to launch the UR in a standalone config.",
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

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
