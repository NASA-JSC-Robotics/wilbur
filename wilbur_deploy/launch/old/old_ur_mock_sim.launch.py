from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
import os


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(DeclareLaunchArgument("description_package", default_value="wilbur_description"))
    declared_arguments.append(DeclareLaunchArgument("description_file", default_value="wilbur.urdf.xacro"))

    description_package = LaunchConfiguration("description_package")
    description_file = LaunchConfiguration("description_file")

    ur_mock_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("wilbur_deploy"), "launch", "ur_control.launch.py")
        ),
        launch_arguments={
            "use_fake_hardware": "true",
            "fake_sensor_commands": "true",
            "activate_joint_controller": "true",
            "description_package": description_package,
            "description_file": description_file,
        }.items(),
    )

    return LaunchDescription(declared_arguments + [ur_mock_launch])
