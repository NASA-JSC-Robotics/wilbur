import os

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

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
def spawn_controller(
    controller_name,
    inactive=False,
    controller_manager_name="controller_manager",
    timeout=300,
    namespace: LaunchConfiguration = "",
    condition=None,
    controller_ros_args=None,
):
    """
    Create a spawn controller node action for the specified controller and arguments.
    """
    inactive_flags = ["--inactive"] if inactive else []
    ros_args = ["--controller-ros-args", f"{controller_ros_args}"] if controller_ros_args is not None else []

    return Node(
        package="controller_manager",
        executable="spawner",
        name=controller_name,
        namespace=namespace,
        arguments=[
            controller_name,
            "--controller-manager",
            controller_manager_name,
            "--controller-manager-timeout",
            str(timeout),
        ]
        + ros_args
        + inactive_flags,
        output="both",
        condition=condition,
    )