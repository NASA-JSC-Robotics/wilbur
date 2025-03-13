import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


arguments = []

arguments.append(
    DeclareLaunchArgument(
        "world",
        default_value="rockyard.sdf",
        description="name of the world file",
    )
)


arguments.append(
    DeclareLaunchArgument(
        "world_pkg",
        default_value="rockyard_world",
        description="name of the package that has the world file",
    )
)


def launch_setup(context):

    # Initialize Arguments
    world = LaunchConfiguration("world").perform(context)
    world_pkg = LaunchConfiguration("world_pkg").perform(context)

    pkg_deploy = get_package_share_directory("wilbur_deploy")

    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    gz_launch_path = PathJoinSubstitution([pkg_ros_gz_sim, "launch", "gz_sim.launch.py"])

    world_file = str(os.path.join(get_package_share_directory(world_pkg), "worlds", world))
    if not world_file.endswith(".sdf"):
        world_file += ".sdf"

    if not os.path.isfile(world_file):
        print("********************************************")
        print("world file (", world_file, ") does not exist, using default empty world")
        print("********************************************")
        world_file = str(os.path.join(pkg_deploy, "worlds", "empty_world.sdf"))

    actions = []

    # TODO: option for gazebo headless
    # actions.append(SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_model_path))
    # wrong resource path - should be IGN_GAZEBO_RESOURCE_PATH for fortress and ignition
    # https://gazebosim.org/docs/fortress/ros_gz_project_template_guide/
    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                "gz_args": ["-r -v 4 " + world_file],  # -r to unpause the sim (required to load controls) -v verbose
                "on_exit_shutdown": "True",
            }.items(),
        )
    )

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
        output="screen",
    )
    nodes = []
    nodes.append(clock_bridge)

    return nodes + actions


def generate_launch_description():
    n = OpaqueFunction(function=launch_setup)
    ld = LaunchDescription(arguments)
    ld.add_action(n)
    return ld
