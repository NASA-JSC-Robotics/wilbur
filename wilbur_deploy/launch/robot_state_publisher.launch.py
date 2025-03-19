from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_ignition",
            default_value="false",
            description="Start robot with simulated hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="true",
            description="Start robot with simulated hardware mirroring command to its states.",
        )
    )

    sim_ignition = LaunchConfiguration("sim_ignition")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")

    # The intention here is for this to be the one true robot state publisher for all of wilbur, so this
    # should have the complete robot description without any of the omissions from the other controllers.
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare("wilbur_description"), "urdf", "wilbur.urdf.xacro"]),
            " ",
            "sim_ignition:=",
            sim_ignition,
            " ",
            "use_fake_hardware:=",
            use_fake_hardware,
            " ",
        ]
    )
    robot_description = {"robot_description": ParameterValue(value=robot_description_content, value_type=str)}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    return LaunchDescription(declared_arguments + [robot_state_publisher_node])
