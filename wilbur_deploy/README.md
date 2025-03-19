# Wilbur Deploy

Contains required configuration and launch files to launch the Wilbur Robot in simulation and on hardware.
Supports launching either on a single controller pc, or splitting the w200 and UR + gripper across two machines.

## Mock Hardware Simulation

To launch the single PC mock hardware setup:

```bash
ros2 launch wilbur_deploy control_mock_hardware.launch.py
```

Or to launch the w200 and UR separately:

```bash
# Brings up the warthog only
ros2 launch wilbur_deploy control_mock_hardware.launch.py separate_controls_pcs:=true

# Brings up the UR10e only (under the namespace "/ur/")
ros2 launch wilbur_deploy control_mock_hardware.launch.py separate_controls_pcs:=true launch_ur:=true
```

This will bring up the mock hardware interfaces, etc.

## Gazebo (Ignition) Simulation

```bash
# This will bring up the UR and the base in Gazebo
ros2 launch wilbur_deploy sim_gz.launch.py
```

**NOTE**: You must set `IGN_GAZEBO_RESOURCE_PATH` to include `/opt/ros/${ROS_DISTRO}/share` for models to load.

**NOTE**: For OGRE issues friendly reminder to set `LIBGL_ALWAYS_SOFTWARE=1` before launching.

## MoveIt Config

There is a WIP moveit configuration but it needs to be cleaned up and properly connected for both sims.
By default it will work with both standalone configurations.

To run:

```bash
ros2 launch wilbur_moveit_config wilbur_moveit.launch.py
```

To use it it a split controller configuration, the trajectory execution management configuration must be namespaced.
In particular, prepend `/ur/` to the controller names in [moveit_controllers.yaml](../wilbur_moveit_config/config/moveit_controllers.yaml).

E.g.

```yaml
moveit_simple_controller_manager:
  controller_names:
    - /ur/joint_trajectory_controller

  /ur/joint_trajectory_controller:
  ...
```
