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
            default_value="false",
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
            default_value="/ur",
            description="Namespace for the hardware robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "controller_prefix",
            default_value="/ur/",
            description="Namespace for the hardware robot",
        )
    )

    # Initialize Arguments
    sim_ignition = LaunchConfiguration("sim_ignition")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    tf_prefix = LaunchConfiguration("tf_prefix")
    ns = LaunchConfiguration("ns")  # this gets used in the
    # controller_prefix = LaunchConfiguration("controller_prefix")  # this gets used in the

    # Each controller manager node will need a slightly different robot description to ensure that the
    # manager only loads hardware resources for _exactly_ what it needs at construction time. This is
    # due to the fact that the controller managers's resource manager is not paramerizable in Humble,
    # so by default it will attempt to load all hardware interfaces defined in the ros2 control xacro.
    # In this case the full robot description is used

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare("wilbur_description"), "urdf", "wilbur_ur10e.urdf.xacro"]),
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
        ]
    )
    robot_description = {"robot_description": ParameterValue(value=robot_description_content, value_type=str)}

    # helper function to get controllers files that we might need
    def GetControllersFile(file_name):
        return PathJoinSubstitution(
            [
                get_package_share_directory("wilbur_deploy"),
                "config",
                file_name,
            ]
        )

    # contains update rate
    controllers_common = GetControllersFile("controllers_common.yaml")
    # controllers for the warthog
    controllers_ur = GetControllersFile("controllers_ur.yaml")
    # controllers for the gripper
    controllers_hande = GetControllersFile("controllers_hande.yaml")

    # Declare nodes
    nodes = []

    # start the controller manager node with all of the controller config files
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        namespace=ns,
        parameters=[
            robot_description,
            ParameterFile(controllers_common, allow_substs=True),
            ParameterFile(controllers_ur, allow_substs=True),
            ParameterFile(controllers_hande, allow_substs=True),
        ],
        output="both",
    )
    nodes.append(control_node)

    # Add a topic republisher for the joint states topic, since there is no support for remapping spawned
    # controller's topics in Humble. Note this only runs when we are running two control computers
    republisher_node = Node(
        package="topic_tools",
        executable="relay",
        name="ur_joint_states_relay",
        output="both",
        arguments=[
            PathJoinSubstitution([ns, "joint_states"]),
            "/joint_states",
        ],
    )
    nodes.append(republisher_node)

    return LaunchDescription(declared_arguments + nodes)
