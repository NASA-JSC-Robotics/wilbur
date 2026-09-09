from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Include Packages
    pkg_clearpath_manipulators = FindPackageShare('clearpath_manipulators')

    # Declare launch files
    launch_file_manipulators = PathJoinSubstitution([
        pkg_clearpath_manipulators, 'launch', 'manipulators.launch.py'])

    # Include launch files
    launch_manipulators = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_manipulators]),
        launch_arguments=
            [
                (
                    'setup_path'
                    ,
                    '/etc/clearpath'
                )
                ,
                (
                    'use_sim_time'
                    ,
                    'false'
                )
                ,
                (
                    'namespace'
                    ,
                    'w200_0095'
                )
                ,
                (
                    'launch_moveit'
                    ,
                    'false'
                )
                ,
                (
                    'delay_moveit'
                    ,
                    '5.0'
                )
                ,
                (
                    'control_delay'
                    ,
                    '1.0'
                )
                ,
            ]
    )

    # Nodes
    node_arm_0_ur_tool_comm = Node(
        name='arm_0_ur_tool_comm',
        executable='tool_communication.py',
        package='ur_robot_driver',
        namespace='w200_0095',
        output='screen',
        parameters=
            [
                {
                    'robot_ip': '192.168.131.40'
                    ,
                    'tcp_port': 54321
                    ,
                    'device_name': '/tmp/arm_0_gripper'
                    ,
                }
                ,
            ]
        ,
    )

    # Create LaunchDescription
    ld = LaunchDescription()
    ld.add_action(launch_manipulators)
    ld.add_action(node_arm_0_ur_tool_comm)
    return ld
