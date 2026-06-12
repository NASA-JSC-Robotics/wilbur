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
