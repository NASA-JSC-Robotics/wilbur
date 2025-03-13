#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
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
            "tf_prefix",
            default_value="",
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, also joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_ignition",
            default_value="false",
            description="Start robot with simulated hardware mirroring command to its states.",
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
            "parent",
            default_value="world",
            description="Namespace for the hardware robot",
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
            "controller_file",
            default_value="control.yaml",
            description="Name of the defined controllers.yaml file defined in wilbur_deploy/config",
        )
    )

    # Initialize Arguments
    sim_ignition = LaunchConfiguration("sim_ignition")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    controller_file = LaunchConfiguration("controller_file")

    # This is the "definitive" robot state publisher.
    # This should be launched on whatever machine has the most resources, which
    # along with whichever controller manager we think should com up first.
    warthog_robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("wilbur_deploy"), "launch", "robot_state_publisher.launch.py")
        ),
        launch_arguments={
            "sim_ignition": sim_ignition,
            "use_fake_hardware": use_fake_hardware,
        }.items(),
    )

    robot_controllers = PathJoinSubstitution(
        [
            get_package_share_directory("wilbur_deploy"),
            "config",
            controller_file,
        ]
    )

    # Each controller manager node will need a slightly different robot description to ensure that the
    # manager only loads hardware resources for _exactly_ what it needs at construction time. This is
    # due to the fact that the controller managers's resource manager is not paramerizable in Humble,
    # so by default it will attempt to load all hardware interfaces defined in the ros2 control xacro.
    # In this case the UR's ros2 controllers are not loaded, but the
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare("wilbur_description"), "urdf", "wilbur.urdf.xacro"]),
            " ",
            "sim_ignition:=",
            sim_ignition,
            " ",
            "use_fake_hardware:=",
            use_fake_hardware,
            " ",
            "generate_ros2_control_tag:=",
            # Only include ROS 2 control here so that gazebo launches the UR HW interface.
            sim_ignition,
            " ",
            "use_w200_controllers:=",
            "true",
            " ",
        ]
    )
    robot_description = {"robot_description": ParameterValue(value=robot_description_content, value_type=str)}

    # Declare nodes
    nodes = []

    # Only launch the control node if using mock hardware, for now
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            ParameterFile(robot_controllers, allow_substs=True),
        ],
        output="both",
        condition=IfCondition(use_fake_hardware),
    )
    nodes.append(control_node)

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_state_broadcaster_control",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager-timeout",
            "300",
        ],
        additional_env={"ROS_SUPER_CLIENT": "True"},
    )
    nodes.append(joint_state_broadcaster)

    velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        name="velocity_controller",
        arguments=[
            "velocity_controller",
            "--controller-manager-timeout",
            "300",
        ],
        output="screen",
        additional_env={"ROS_SUPER_CLIENT": "True"},
    )
    nodes.append(velocity_controller)

    # When using Gazebo we do not rely on the UR launcher's controller spawners, so
    # we must manually spawn the joint trajectory controller, etc.
    joint_trajectory_controller = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_trajectory_controller",
        arguments=[
            "joint_trajectory_controller",
            "--controller-manager-timeout",
            "300",
        ],
        output="screen",
        condition=IfCondition(sim_ignition),
    )
    nodes.append(joint_trajectory_controller)

    return LaunchDescription([warthog_robot_state_publisher] + declared_arguments + nodes)
