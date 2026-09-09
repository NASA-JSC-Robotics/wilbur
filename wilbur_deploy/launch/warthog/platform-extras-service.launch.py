from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Include Packages
    pkg_clearpath_common = FindPackageShare('clearpath_common')
    pkg_jaco03_bringup = FindPackageShare('jaco03_bringup')

    # Declare launch files
    launch_file_platform_extras = PathJoinSubstitution([
        pkg_clearpath_common, 'launch', 'platform_extras.launch.py'])
    launch_file_numato_relay = PathJoinSubstitution([
        pkg_jaco03_bringup, 'launch', 'numato_relay.launch.py'])

    # Include launch files
    launch_platform_extras = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_platform_extras]),
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
            ]
    )

    launch_numato_relay = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_numato_relay]),
        launch_arguments=
            [
            ]
    )

    # Create LaunchDescription
    ld = LaunchDescription()
    ld.add_action(launch_platform_extras)
    ld.add_action(launch_numato_relay)
    return ld
