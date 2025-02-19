# Wilbur Deploy

Contains required configuration and launch files to launch the Wilbur Robot in simulation and on hardware.

## Mock Hardware Simulation

Configured with multiple controller managers to simulate running across different machines.

```bash
ros2 launch wilbur_deploy ur_mock_sim.launch.py

ros2 launch wilbur_deploy w200_mock_sim.launch.py
```

This will bring up the mock hardware interfaces, etc.

## Gazeboe (Ignition) Simulation

```bash
ros2 launch wilbur_deploy simulate.launch.py

ros2 launch wilbur_deploy moveit.launch.py use_sim_time:=true

ros2 run rviz2 rviz2 use_sim_time:=true -d install/wilbur_deploy/share/wilbur_deploy/rviz/config.rviz
```
