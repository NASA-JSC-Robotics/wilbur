#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile, ParameterValue
from ament_index_python.packages import get_package_share_directory
from launch_ros.substitutions import FindPackageShare

from wilbur_deploy.launch_utils import GetControllersFile


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_ignition",
            default_value="false",
            description="Start robot in ignition simulator.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="true",
            description="Start robot with simulated hardware mirroring command to its states.",
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
    declared_arguments.append(
        DeclareLaunchArgument(
            "controller_prefix",
            default_value="",
            description="prefix used in the yaml controllers files",
        )
    )

    # Initialize Arguments
    sim_ignition = LaunchConfiguration("sim_ignition")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")

    # Each controller manager node will need a slightly different robot description to ensure that the
    # manager only loads hardware resources for _exactly_ what it needs at construction time. This is
    # due to the fact that the controller managers's resource manager is not paramerizable in Humble,
    # so by default it will attempt to load all hardware interfaces defined in the ros2 control xacro.
    # In this case the full robot description is used

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare("wilbur_description"), "urdf", "w200.urdf.xacro"]),
            " ",
            "sim_ignition:=",
            sim_ignition,
            " ",
            "use_fake_hardware:=",
            use_fake_hardware,
            " ",
            "tf_prefix:=",
            tf_prefix,
            " ",
            "ns:=",
            ns,
            " ",
        ]
    )
    # Controller files

    # contains update rate
    controllers_common = GetControllersFile("wilbur_deploy", "controllers_common.yaml")
    # controllers for the warthog
    controllers_w200 = GetControllersFile("wilbur_deploy", "controllers_w200.yaml")

    # Declare nodes
    nodes = []

    # start the controller manager node with all of the controller config files
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            ParameterFile(controllers_common, allow_substs=True),
            ParameterFile(controllers_w200, allow_substs=True),
        ],
        output="both",
    )
    nodes.append(control_node)

    return LaunchDescription(declared_arguments + nodes)
