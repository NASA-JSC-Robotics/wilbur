#!/usr/bin/env python3
#
# Copyright (c) 2026, United States Government, as represented by the
# Administrator of the National Aeronautics and Space Administration.
#
# All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():

    declared_arguments = [
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the hardware robot",
        ),

        DeclareLaunchArgument(
            'use_sim_time',
            choices=['true', 'false'],
            default_value='false',
            description='Use simulation time'
        ),

        DeclareLaunchArgument(
            'tf_prefix',
            default_value='',
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, also joint names in the controllers' configuration \
        have to be updated.",
        ),                

        DeclareLaunchArgument(
            'controller_prefix',
            default_value='',
            description='prefix used in the yaml controllers files',
        ),

        DeclareLaunchArgument(
            'enable_ekf',
            default_value='true',
            choices=['true', 'false'],
            description='Enable localization via EKF node'
        )
    ]

    # Initialize Arguments
    ns = LaunchConfiguration("ns")
    use_sim_time = LaunchConfiguration("use_sim_time")
    tf_prefix = LaunchConfiguration("tf_prefix")
    controller_prefix = LaunchConfiguration("controller_prefix")
    enable_ekf = LaunchConfiguration("enable_ekf")
    pkg_clearpath_control = FindPackageShare('clearpath_control')
    pkg_wilbur_deploy = FindPackageShare('wilbur_deploy')


    # launch main control launch with hardware
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([pkg_wilbur_deploy, 
                                   "launch", 
                                   "control.launch.py"])]
        ),
        launch_arguments={
            "platform": "hardware",
            "ns": ns,
        }.items(),
    )

    # launch_file_localization = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         [PathJoinSubstitution([pkg_clearpath_control, 
    #                                'launch', 
    #                                'localization.launch.py'])]
    #     ),
    #     launch_arguments={
    #         'setup_path': pkg_wilbur_deploy, 
    #         'use_sim_time': use_sim_time,
    #         'enable_ekf': enable_ekf,

    #     }.items(),
    # )

    # Localization
    localization_config = [PathJoinSubstitution([pkg_wilbur_deploy,
                                                'config',
                                                'warthog']),
                           'localization.yaml']
    
    launch_file_teleop_base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([pkg_clearpath_control,
                                   'launch',
                                   'teleop_base.launch.py'])
            ]
        ),
        launch_arguments={
            "setup_path": PathJoinSubstitution([pkg_wilbur_deploy,
                                            'config',
                                            'warthog']),
            "use_sim_time": use_sim_time,        
        }.items(),
    )

    launch_file_teleop_joy = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([pkg_clearpath_control, 
                                   'launch',
                                   'teleop_joy.launch.py'])
            ]
        ),
        launch_arguments={
            "setup_path": PathJoinSubstitution([pkg_wilbur_deploy,
                                            'config',
                                            'warthog']),
            "use_sim_time": use_sim_time,
        }.items(),            
    )

    launch_controller_manager = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([pkg_wilbur_deploy, 
                                   'launch',
                                   'controller_manager.launch.py'])
            ]
        ),
        launch_arguments={
            'use_fake_hardware': 'false',
            'ns': ns,
            'tf_prefix': tf_prefix,
            'use_sim_time': use_sim_time,
            'controller_prefix': controller_prefix,
            'enable_ekf': enable_ekf,

        }.items(),        
    )

    node_localization = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[localization_config],
        remappings=[
            ('odometry/filtered', 'platform/odom/filtered'),
            ('/diagnostics', 'diagnostics'),
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
        ],
        condition=IfCondition(enable_ekf),
    )   

    launches = [
        control_launch,
        # launch_file_localization,
        launch_file_teleop_base,
        launch_file_teleop_joy,
        launch_controller_manager,
    ]

    nodes = [
        # node_localization,
    ]

    return LaunchDescription(declared_arguments + launches + nodes)
