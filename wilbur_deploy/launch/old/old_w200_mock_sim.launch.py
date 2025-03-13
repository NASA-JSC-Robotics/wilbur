from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os


def generate_launch_description():

    declared_arguments = []

    warthog_mock_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("wilbur_deploy"), "launch", "control.launch.py")
        ),
        launch_arguments={
            "sim_ignition": "false",
            "use_fake_hardware": "true",
        }.items(),
    )

    return LaunchDescription(declared_arguments + [warthog_mock_launch])
