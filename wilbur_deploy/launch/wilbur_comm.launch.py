from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():

    pkg_wilbur_deploy = 'wilbur_deploy'
    warthog_deploy_config = PathJoinSubstitution([FindPackageShare(pkg_wilbur_deploy), 'config', 'warthog'])

    declared_arguments = [
        DeclareLaunchArgument(
            "ns",
            default_value="",
            description="Namespace for the hardware robot",
        ),
        DeclareLaunchArgument(
            "diagnostic_updater_params",
            default_value=PathJoinSubstitution([warthog_deploy_config, 'diagnostic_updater.yaml']),
            description="",
        ),
        DeclareLaunchArgument(
            "diagnostic_aggregator_params",
            default_value=PathJoinSubstitution([warthog_deploy_config, 'diagnostic_aggregator.yaml']),
            description="",
        ),
        DeclareLaunchArgument(
            "foxglove_bridge_parameters",
            default_value=PathJoinSubstitution([warthog_deploy_config, 'foxglove_bridge.yaml']),
            description="",
        ),
        DeclareLaunchArgument(
            "imu_filter",
            default_value=PathJoinSubstitution([warthog_deploy_config, 'imu_filter.yaml']),
            description="",
        ),
    ]

    ns = LaunchConfiguration('ns')
    default_ns = "warthog"
    diagnostic_updater_params = LaunchConfiguration('diagnostic_updater_params')
    diagnostic_aggregator_params = LaunchConfiguration('diagnostic_aggregator_params')
    # foxglove_bridge_parameters = LaunchConfiguration('foxglove_bridge_parameters')
    imu_filter = LaunchConfiguration('imu_filter')

    # Include Packages

    pkg_clearpath_common = FindPackageShare('clearpath_common')
    pkg_clearpath_diagnostics = FindPackageShare('clearpath_diagnostics')
    pkg_valence_bms_driver = FindPackageShare('valence_bms_driver')

    # Declare launch files
    launch_file_platform = PathJoinSubstitution([
        pkg_clearpath_common, 'launch', 'platform.launch.py'])
    launch_file_proton = PathJoinSubstitution([
        FindPackageShare(pkg_wilbur_deploy), 'launch', 'warthog', 'proton.launch.py'])
    launch_file_diagnostics = PathJoinSubstitution([
        pkg_clearpath_diagnostics, 'launch', 'diagnostics.launch.py'])
    # launch_file_foxglove_bridge = PathJoinSubstitution([
    #     pkg_clearpath_diagnostics, 'launch', 'foxglove_bridge.launch.py'])
    launch_file_bms = PathJoinSubstitution([
        pkg_valence_bms_driver, 'launch', 'bms.launch.py'])

    # Include launch files
    launch_platform = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_platform]),
        launch_arguments = {
            'namespace': default_ns,
            'setup_path': warthog_deploy_config,
            'use_sim_time': 'false',
            'enable_ekf': 'true'

        }.items()
    )

    launch_proton = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_proton]),
        launch_arguments = {
            'namespace': default_ns, 
            'platform': 'w200'
        }.items()
    )

    diagnostics_action = GroupAction(
        [
            # Aggregator
            Node(
                package='diagnostic_aggregator',
                executable='aggregator_node',
                name='diagnostic_aggregator',
                namespace=default_ns,
                output='screen',
                parameters=[diagnostic_aggregator_params],
                remappings=[
                    ('/diagnostics', 'diagnostics'),
                    ('/diagnostics_agg', 'diagnostics_agg'),
                    ('/diagnostics_toplevel_state', 'diagnostics_toplevel_state'),
                ],
            ),
            # Updater
            Node(
                package='clearpath_diagnostics',
                executable='clearpath_diagnostic_updater',
                name='clearpath_diagnostic_updater',
                namespace=default_ns,
                output='screen',
                parameters=[diagnostic_aggregator_params],
                remappings=[
                    ('/diagnostics', 'diagnostics'),
                    ('/diagnostics_agg', 'diagnostics_agg'),
                    ('/diagnostics_toplevel_state', 'diagnostics_toplevel_state'),
                ],
            ),
        ]
    )   

    # launch_foxglove_bridge = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([launch_file_foxglove_bridge]),
    #     launch_arguments = {
    #         'namespace': default_ns,
    #         'parameters': foxglove_bridge_parameters,
    #     }.items()
    # )

    launch_bms = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_bms]),
        launch_arguments = {
            'robot_namespace': default_ns,
            'namespace': os.path.join(default_ns, 'platform', 'bms'),
            'interface': 'can1',
            'bms_id': '0'
        }.items()
    )

    # Nodes
    node_battery_state_control = Node(
        name='battery_state_control',
        executable='battery_state_control',
        package='clearpath_hardware_interfaces',
        namespace=ns,
        output='screen',
        arguments = {
            '-s': warthog_deploy_config,
        }.items()
    )

    node_wireless_watcher = Node(
        name='wireless_watcher',
        executable='wireless_watcher',
        package='wireless_watcher',
        namespace=ns,
        output='screen',
        remappings = {
            '/diagnostics': 'diagnostics',
        }.items(),
        parameters = [
            {
                'hz': 1.0,
                'dev': '',
                'connected_topic': 'platform/wifi_connected',
                'connection_topic': 'platform/wifi_status',
            },
        ],
    )

    node_imu_filter_madgwick = Node(
        name='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        package='imu_filter_madgwick',
        namespace=ns,
        output='screen',
        remappings = [
                (
                    'imu/data_raw'
                    ,
                    'sensors/imu_0/data_raw'
                )
                ,
                (
                    'imu/mag'
                    ,
                    'sensors/imu_0/magnetic_field'
                )
                ,
                (
                    'imu/data'
                    ,
                    'sensors/imu_0/data'
                )
                ,
                (
                    '/tf'
                    ,
                    'tf'
                )
                ,
            ]
        ,
        parameters=
            [
                imu_filter
                ,
            ]
        ,
    )

    node_lighting_node = Node(
        name='lighting_node',
        executable='lighting_node',
        package='clearpath_hardware_interfaces',
        namespace=ns,
        output='screen',
        remappings=
            [
                (
                    '/diagnostics'
                    ,
                    'diagnostics'
                )
                ,
            ]
        ,
        parameters=
            [
                {
                    'platform': 'w200'
                    ,
                }
                ,
            ]
        ,
    )

    node_sevcon_traction_node = Node(
        name='sevcon_traction_node',
        executable='sevcon_traction_node',
        package='sevcon_traction',
        namespace=ns,
        output='screen',
        remappings=
            [
                (
                    '/diagnostics'
                    ,
                    'diagnostics'
                )
                ,
            ]
        ,
    )

    launches = [
        # launch_platform,
        launch_proton,
        # launch_foxglove_bridge,
        launch_bms,
    ]

    nodes = [
        diagnostics_action,
        node_battery_state_control,
        node_wireless_watcher,
        node_imu_filter_madgwick,
        node_lighting_node,
        node_sevcon_traction_node,
    ]

    return LaunchDescription(declared_arguments + launches + nodes)