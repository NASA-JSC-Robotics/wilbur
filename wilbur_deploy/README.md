# Wilbur Deploy

Contains required configuration and launch files to launch the Wilbur Robot in simulation and on hardware.

## Mock Hardware Simulation

Configured with multiple controller managers to simulate running across different machines.

```bash
ros2 launch wilbur_deploy ur_mock_sim.launch.py

ros2 launch wilbur_deploy w200_mock_sim.launch.py
```

This will bring up the mock hardware interfaces, etc.

## Gazebo (Ignition) Simulation

```bash
# This will bring up the UR and the base
ros2 launch wilbur_deploy simulate.launch.py
```

**NOTE**: You must set `IGN_GAZEBO_RESOURCE_PATH` to include `/opt/ros/${ROS_DISTRO}/share` for models to load.

**NOTE**: For OGRE issues friendly reminder to set `LIBGL_ALWAYS_SOFTWARE=1` before launching.

## MoveIt Config

There is a WIP moveit configuration but it needs to be cleaned up and properly connected for both sims.
