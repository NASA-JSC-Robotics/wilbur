#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, OpaqueFunction, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, UnlessCondition


arguments = []

arguments.append(DeclareLaunchArgument(
    "tf_prefix",
    default_value='""',
    description="tf_prefix of the joint names, useful for \
    multi-robot setup. If changed, also joint names in the controllers' configuration \
    have to be updated.",

))
arguments.append(DeclareLaunchArgument(
    "sim_ignition",
    default_value="true",
    description="Start robot with simulated hardware mirroring command to its states.",
))
arguments.append(DeclareLaunchArgument(
    "headless_mode",
    default_value="false",
    description="Enable headless mode for robot control",
))
arguments.append(DeclareLaunchArgument(
    "ns",
    default_value=""
))

arguments.append(DeclareLaunchArgument(
    'robot_x',
    default_value="0.0",
    description="X position of the robot",
))
arguments.append(DeclareLaunchArgument(
    'robot_y',
    default_value="0.0",
    description="Y position of the robot",
))
arguments.append(DeclareLaunchArgument(
    'robot_z',
    default_value="6.0",
    description="Z position of the robot",
))

def launch_setup(context):


    # Initialize Arguments
    tf_prefix = LaunchConfiguration("tf_prefix")
    sim_ignition = LaunchConfiguration("sim_ignition")
    headless_mode = LaunchConfiguration("headless_mode")
    namespace = LaunchConfiguration("ns").perform(context)


    x = LaunchConfiguration('robot_x')
    y = LaunchConfiguration('robot_y')
    z = LaunchConfiguration('robot_z')

    if not namespace:
        use_namespace = "False"
    else:
        use_namespace = "True"

    if use_namespace == "True":
        print("*************************", namespace, "**********************************")

    pkg_deploy = get_package_share_directory('wilbur_deploy')
    pkg_description = get_package_share_directory('wilbur_description')


    # Start gazebo with the selected World
    world_group = GroupAction([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_deploy, 'launch', 'start_world.launch.py')
            )
        )])

    # add the robot to the world

    robot_group = GroupAction([
        PushRosNamespace(
           condition=IfCondition([use_namespace]),
            namespace=namespace),


        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_description, 'launch', 'spawn_robot.launch.py')),
            launch_arguments = {'sim_ignition' : sim_ignition,
                                'tf_prefix' : tf_prefix,
                                'x' : x,
                                'y' : y,
                                'z' : z,
#                                'namespace' : namespace
            }.items()
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_deploy, 'launch', 'control.launch.py')),
            launch_arguments={'sim_ignition': sim_ignition,
                              'tf_prefix' : tf_prefix,
                              'namespace': namespace,
            }.items()
        ),
    ])
    nodes = [world_group, robot_group]

    return nodes

def generate_launch_description():
    n = OpaqueFunction(function=launch_setup)
    ld = LaunchDescription(arguments)
    ld.add_action(n)
    return ld
