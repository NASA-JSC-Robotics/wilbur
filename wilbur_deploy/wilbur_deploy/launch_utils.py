import os

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition


# helper function to organize launch description objects with the same launch args and package names
def AddLaunchDescriptions(package_name, launch_file_names, launch_args):
    launch_files_list = []
    for launch_file_name in launch_file_names:
        launch_files_list.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory(package_name),
                        "launch",
                        launch_file_name,
                    )
                ),
                launch_arguments=launch_args,
            )
        )

    return launch_files_list


# helper function to get controllers files that we might need
def GetControllersFile(package_name, file_name):
    return PathJoinSubstitution(
        [
            get_package_share_directory(package_name),
            "config",
            file_name,
        ]
    )


# Helper function to make controller nodes
def SpawnController(
    controller_manager_name: str,
    controller_name: str,
    controller_manager_timeout: str = "300",
    **kwargs
) -> Node:
    return Node(
        package="controller_manager",
        executable="spawner",
        name=controller_name,
        arguments=[
            "--controller-manager",
            controller_manager_name,
            "--controller-manager-timeout",
            controller_manager_timeout,
            "--controller",
            controller_name,
        ],
        output="screen",
        **kwargs
    )
