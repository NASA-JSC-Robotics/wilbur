#!/usr/bin/env python3

# Software License Agreement (BSD)
#
# @author    Luis Camero <lcamero@clearpathrobotics.com>
# @copyright (c) 2024, Clearpath Robotics, Inc., All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of Clearpath Robotics nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Redistribution and use in source and binary forms, with or without
# modification, is not permitted without the express permission
# of Clearpath Robotics.
import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from clearpath_config.clearpath_config import ClearpathConfig

arguments = []

arguments.append(DeclareLaunchArgument(
    "tf_prefix",
    default_value='""',
    description="tf_prefix of the joint names, useful for \
    multi-robot setup. If changed, also joint names in the controllers' configuration \
    have to be updated.",
    
))


arguments.append(DeclareLaunchArgument(
    "use_sim_time",
    default_value="true",
    description="Start robot with simulated hardware mirroring command to its states.",
))

arguments.append(DeclareLaunchArgument(
    "ns",
    default_value=""
))


def launch_setup(context, *args, **kwargs):
    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Namespace
    namespace = LaunchConfiguration("ns").perform(context)
    pkg_deploy = get_package_share_directory('wilbur_deploy')
    pkg_description = get_package_share_directory('wilbur_description')

    # Robot Description
    robot_description = {
        'robot_description': xacro.process_file(
            os.path.join(pkg_description, 'urdf', 'wilbur.urdf.xacro')
        ).toxml()
    }

    # Semantic Robot Description
    robot_description_semantic = {
        'robot_description_semantic': xacro.process_file(
            os.path.join(pkg_description, 'urdf', 'wilbur.srdf')
        ).toxml()
    }

    nodes = []
    
    move_group = Node(package='moveit_ros_move_group',
                      executable='move_group',
                      output='log',
                      namespace=namespace,
                      parameters=[
                          os.path.join(pkg_deploy, 'config', 'moveit.yaml'),
                          robot_description,
                          robot_description_semantic,
                          {'use_sim_time': use_sim_time},
                      ],
                      remappings=[
                          ('/tf', 'tf'),
                          ('/tf_static', 'tf_static'),
                          ('joint_states', 'joint_states'),
                      ]
                    )
    nodes.append(move_group)
    
    return(nodes)


def generate_launch_description():
    n = OpaqueFunction(function=launch_setup)
    ld = LaunchDescription(arguments)
    ld.add_action(n)
    return ld