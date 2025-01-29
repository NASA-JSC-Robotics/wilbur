#!/usr/bin/env python3


import os
import launch
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, OpaqueFunction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


arguments = []

arguments.append(DeclareLaunchArgument(
    "tf_prefix",
    default_value='""',
    description="tf_prefix of the joint names, useful for \
    multi-robot setup. If changed, also joint names in the controllers' configuration \
    have to be updated.",
    
))
arguments.append(DeclareLaunchArgument(
    "is_sim",
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

arguments.append(DeclareLaunchArgument('control_config_filepath', default_value=[
        launch.substitutions.TextSubstitution(text=os.path.join(
            get_package_share_directory('wilber_deploy'), 'config', '')),
        'control', launch.substitutions.TextSubstitution(text='.yaml')]))

def launch_setup(context):
    
    
    # Initialize Arguments
    tf_prefix = LaunchConfiguration("tf_prefix").perform(context)
    tf_prefix_arg = LaunchConfiguration("tf_prefix")
    namespace = LaunchConfiguration("ns").perform(context)
    is_sim = LaunchConfiguration("is_sim")
    headless_mode = LaunchConfiguration("headless_mode")
    config_filepath = LaunchConfiguration('control_config_filepath')
    
    if not tf_prefix:
        tf_frame_prefix_enable = "False"
    else:
        tf_frame_prefix_enable = "True"

        
    
    pkg_deploy = get_package_share_directory('wilber_deploy')
    pkg_description = get_package_share_directory('wilber_description')
    
    
    robot_controllers = PathJoinSubstitution(
        [
            pkg_deploy,
            "config",
            "control.yaml",
        ]
    )
    urdf_model_path = os.path.join(pkg_description, 'urdf/wilber.urdf.xacro')
    
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_state_broadcaster_control",
        parameters=[urdf_model_path, 
                    robot_controllers,],
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager-timeout',
            '300',
        ],
        additional_env={'ROS_SUPER_CLIENT': 'True'},
    )
    
    print("*********************************************************")
    print(left_wheel_names)
    print("*********************************************************")

    # Add Velocity Controller
    velocity_controller = Node(
        package='controller_manager',
        executable='spawner',
        name="velocity_controller",
#        parameters=[{"odom_frame_id": "wilber_odom",
#                     "left_wheel_names": left_wheel_names,
#                     "right_wheel_names": right_wheel_names}
#                ],
        arguments=['velocity_controller', 
                   '--controller-manager-timeout', '300',
                   ],
        output='screen',
        additional_env={'ROS_SUPER_CLIENT': 'True'},
    )

    nodes = (joint_state_broadcaster, velocity_controller)
    
    return nodes
    
    
def generate_launch_description():
    n = OpaqueFunction(function=launch_setup)
    ld = LaunchDescription(arguments)
    ld.add_action(n)
    return ld