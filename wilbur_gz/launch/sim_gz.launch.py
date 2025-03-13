#!/usr/bin/python3
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from launch.conditions import IfCondition


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "tf_prefix",
            default_value='""',
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, also joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_ignition",
            default_value="true",
            description="Start robot with simulated hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "headless_mode",
            default_value="false",
            description="Enable headless mode for robot control",
        )
    )
    declared_arguments.append(DeclareLaunchArgument("ns", default_value=""))
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_x",
            default_value="0.0",
            description="X position of the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_y",
            default_value="0.0",
            description="Y position of the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_z",
            default_value="6.0",
            description="Z position of the robot",
        )
    )

    # Initialize Arguments
    tf_prefix = LaunchConfiguration("tf_prefix")
    sim_ignition = LaunchConfiguration("sim_ignition")
    namespace = LaunchConfiguration("ns")

    x = LaunchConfiguration("robot_x")
    y = LaunchConfiguration("robot_y")
    z = LaunchConfiguration("robot_z")

    # Todo: fix this - does not work as expected
    # https://robotics.stackexchange.com/questions/103310/can-i-programmatically-call-a-launch-file-with-arguments-that-can-be-used-as-a-v
    if not namespace:
        use_namespace = "False"
    else:
        use_namespace = "True"

    pkg_deploy = get_package_share_directory("wilbur_deploy")
    pkg_gazebo = get_package_share_directory("wilbur_gz")

    nodes = []

    # Start gazebo with the selected World
    world_group = GroupAction(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(pkg_gazebo, "launch", "start_world.launch.py"))
            )
        ]
    )
    nodes.append(world_group)

    # add the robot to the world
    robot_group = GroupAction(
        [
            PushRosNamespace(condition=IfCondition([use_namespace]), namespace=namespace),
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-entity",
                    "wilbur",
                    "-name",
                    "wilbur",
                    "-topic",
                    "robot_description",
                    "-x",
                    x,
                    "-y",
                    y,
                    "-z",
                    z,
                    "-controller_manager",
                    "controller_manager",
                ],
                output="screen",
            ),
            Node(
                package="ros_gz_bridge",
                executable="parameter_bridge",
                name="sim_bridge",
                parameters=[
                    {
                        "config_file": os.path.join(pkg_gazebo, "config", "bridge.yaml"),
                        "qos_overrides./tf_static.publisher.durability": "transient_local",
                    }
                ],
                output="screen",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(pkg_deploy, "launch", "control.launch.py")),
                launch_arguments={
                    "sim_ignition": sim_ignition,
                    "use_fake_hardware": "false",
                    "tf_prefix": tf_prefix,
                    "namespace": namespace,
                    "controller_file": "gazebo_controllers.yaml",
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(os.path.join(pkg_deploy, "launch", "ur_control.launch.py")),
                launch_arguments={
                    "sim_ignition": sim_ignition,
                    "use_fake_hardware": "false",
                    "tf_prefix": tf_prefix,
                    "namespace": namespace,
                }.items(),
            ),
        ]
    )
    nodes.append(robot_group)

    return LaunchDescription(declared_arguments + nodes)
