import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, RegisterEventHandler, DeclareLaunchArgument
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch.actions import RegisterEventHandler, EmitEvent
from launch_ros.actions import Node
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():

    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "x_dot",
            default_value="0.0",
            description="Command x velocity in m/s",
        ),
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "theta_dot",
            default_value="0.0",
            description="Command theta velocity in rad/s",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "count",
            default_value="100",
            description="Number of commands to send",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'separate',
            default_value='true',
            description="log topics in separate files",
        )
    )

    x_dot = LaunchConfiguration("x_dot")
    theta_dot = LaunchConfiguration("theta_dot")
    count = LaunchConfiguration("count")
    sep = LaunchConfiguration('separate')

    log_odom = Node(
        package="wilbur_testing",
        executable="log_odom",
        output="screen",
        parameters=[{'x_dot': x_dot},
                    {'theta_dot': theta_dot},
                    {'separate': sep}],
    )
    send_cmd = Node(
        package="wilbur_testing",
        executable="send_cmd",
        output="screen",
        parameters=[{'x_dot': x_dot},
                    {'theta_dot': theta_dot},
                    {'count': count}],
    )

    return LaunchDescription(declared_arguments + [
        log_odom, send_cmd
    ])