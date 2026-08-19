import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, RegisterEventHandler, DeclareLaunchArgument
from launch.event_handlers import OnProcessStart, OnProcessExit
from launch.actions import RegisterEventHandler, EmitEvent, LogInfo
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
            "time_ms",
            default_value="1000",
            description="Length of time to send commands (sec)",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'separate',
            default_value='false',
            description="log topics in separate files",
        )
    )

    x_dot = LaunchConfiguration("x_dot")
    theta_dot = LaunchConfiguration("theta_dot")
    time = LaunchConfiguration("time_ms")
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
                    {'time': time}],
    )

    # Create the event handler to shutdown everything when critical_node exits
    shutdown_handler = RegisterEventHandler(
        OnProcessExit(
            target_action=send_cmd,
            on_exit=[
                LogInfo(msg=['Critical node died! Shutting down launch description...']),
                EmitEvent(event=Shutdown())
            ]
        )
    )

    return LaunchDescription(declared_arguments + [
        log_odom, send_cmd, shutdown_handler
    ])