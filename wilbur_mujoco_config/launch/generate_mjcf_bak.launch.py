import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


from launch import LaunchDescription
from launch.substitutions import (
    Command,
    FindExecutable,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit
from launch.actions import RegisterEventHandler


def generate_launch_description():

    wilbur_mujoco_package_name = "wilbur_mujoco_config"
    wilbur_mujoco_description_file = "wilbur_xacro.urdf"
    wilbur_mujoco_package_path = get_package_share_directory(wilbur_mujoco_package_name)

    mujoco_inputs = os.path.join(
        wilbur_mujoco_package_path, "description", "mujoco_inputs.xml"
    )

    # main robot description for Wilbur
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare(wilbur_mujoco_package_name),
                    "urdf",
                    wilbur_mujoco_description_file,
                ]
            ),
        ]
    )
    print(robot_description_content)

    make_mjcf_from_robot_description = Node(
        package="mujoco_ros2_simulation",
        executable="make_mjcf_from_robot_description.py",
        output="screen",
        arguments=[
            "-r",
            robot_description_content,
            "-m",
            mujoco_inputs,
            "-c",  # convert stl to obj
            "-f",
        ],
    )

    post_process_mjcf = Node(
        package="wilbur_mujoco_config",
        executable="post_process_mjcf.py",
        output="screen",
    )

    delay_post_process = RegisterEventHandler(
        OnProcessExit(
            target_action=make_mjcf_from_robot_description, on_exit=[post_process_mjcf]
        )
    )

#   return LaunchDescription([make_mjcf_from_robot_description, delay_post_process])
    return LaunchDescription([make_mjcf_from_robot_description])
