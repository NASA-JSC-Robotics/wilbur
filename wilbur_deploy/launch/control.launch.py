#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
)
from launch.substitutions import (
    LaunchConfiguration,
)
from wilbur_deploy.pig_warnings import (
    pig_hardware,
    pig_mockhardware,
    pig_gazebo,
)

from wilbur_deploy.launch_utils import AddLaunchDescriptions


def launch_setup(context, *args, **kwargs):

    # Initialize Arguments
    platform = LaunchConfiguration("platform").perform(context)
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
            pig_mockhardware()
        case "hardware":
            print("Launching hardware")
            pig_hardware()
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

    # This is the "definitive" robot state publisher.
    # This should be launched on whatever machine has the most resources, which
    # along with whichever controller manager we think should come up first.
    launch_file_names.append("robot_state_publisher.launch.py")
    launch_file_names.append("spawn_controllers.launch.py")

    # Generate the launch files based on launch_file_names which has been configured
    launch_files = AddLaunchDescriptions(
        package_name="wilbur_deploy",
        launch_file_names=launch_file_names,
        launch_args=common_launch_args,
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
