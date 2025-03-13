from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
import os


def generate_launch_description():

    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "tf_prefix",
            default_value='""',
            description="tf_prefix of the joint names, useful for \
        multi-robot setup. If changed, also joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Start robot with fake hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_ignition",
            default_value="false",
            description="Robot is starting using ignition",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "headless_mode",
            default_value="false",
            description="Enable headless mode for robot control",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "runtime_config_package",
            default_value="wilbur_deploy",
            description="Package with the controllers_file runtime settings in the config/ directory",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "controllers_file",
            default_value="ur_controllers.yaml",
            description="Select the controller configuration yaml file",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_sensor_commands",
            default_value="false",
            description="Enable fake command interfaces for sensors used for simple simulations. \
            Used only if 'use_fake_hardware' parameter is true.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "initial_joint_controller",
            default_value="joint_trajectory_controller",
            description="Initially loaded robot controller.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "activate_joint_controller",
            default_value="false",
            description="Activate loaded joint controller.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "enable_admittance",
            default_value="false",
            description="Allow the admittance controllers to spawn",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "rviz",
            default_value="false",
            description="start rviz?",
        )
    )
    declared_arguments.append(DeclareLaunchArgument("description_package", default_value="wilbur_description"))
    declared_arguments.append(DeclareLaunchArgument("description_file", default_value="wilbur.urdf.xacro"))
    declared_arguments.append(DeclareLaunchArgument("ur_namespace", default_value="/ur"))

    tf_prefix = LaunchConfiguration("tf_prefix")
    sim_ignition = LaunchConfiguration("sim_ignition")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    headless_mode = LaunchConfiguration("headless_mode")
    runtime_config_package = LaunchConfiguration("runtime_config_package")
    controllers_file = LaunchConfiguration("controllers_file")
    fake_sensor_commands = LaunchConfiguration("fake_sensor_commands")
    initial_joint_controller = LaunchConfiguration("initial_joint_controller")
    activate_joint_controller = LaunchConfiguration("activate_joint_controller")
    rviz = LaunchConfiguration("rviz")
    description_package = LaunchConfiguration("description_package")
    description_file = LaunchConfiguration("description_file")
    ur_namespace = LaunchConfiguration("ur_namespace")

    launches = []

    base_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("drt_ros2_ur_tools"), "launch", "drt_ur_control.launch.py")
        ),
        launch_arguments={
            "ur_type": "ur10e",
            "robot_ip": "192.168.1.102",
            "controller_spawner_timeout": "100",
            "description_package": description_package,
            "description_file": description_file,
            "runtime_config_package": runtime_config_package,
            "tf_prefix": tf_prefix,
            "controllers_file": controllers_file,
            "use_fake_hardware": use_fake_hardware,
            "headless_mode": headless_mode,
            "fake_sensor_commands": fake_sensor_commands,
            "initial_joint_controller": initial_joint_controller,
            "activate_joint_controller": activate_joint_controller,
            "launch_rviz": rviz,
            "use_controller_stopper": "false",
            "ur_namespace": ur_namespace,
            # We are not launching the UR's robot state publisher as it will have an incomplete description
            # of the system, since not all arguments from our xacro are parameterized.
            "launch_rsp": "false",
        }.items(),
        condition=UnlessCondition(sim_ignition),
    )
    launches.append(base_launch)

    nodes = []

    # Add a topic republisher for the joint states topic, since there is no support for remapping spawned
    # controller's topics in Humble.
    republisher_node = Node(
        package="topic_tools",
        executable="relay",
        name="ur_joint_states_relay",
        output="both",
        arguments=[
            PathJoinSubstitution([ur_namespace, "joint_states"]),
            "/joint_states",
        ],
    )
    nodes.append(republisher_node)

    return LaunchDescription(declared_arguments + launches + nodes)
