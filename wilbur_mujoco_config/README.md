# WilBUR Mujoco Simulation

This is a simulation of the JSC Robotics WilBUR robot using the Mujoco simulation tools and mujoco_ros2_control.  This simulation currently does not fully support the UR arm.

## Build/Install

Builds and installs with the wilBUR code.  No special actions required.

## Run

```
ros2 launch wilbur_mujoco_sim wilbur_mujoco_sim.launch.py  include_ur:=false
```
To drive with a joystick:
```
ros2 launch willbur_mujoco_deploy teleop.launch.py
```

To simply check connection:
```
ros2 topic pub /velocity_controller/cmd_vel geometry_msgs/msg/TwistStamped "{header: {stamp: now, frame_id: 'base_link'}, twist: {linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}}" --rate 10
```

[Notes on Simulation Choices](docs/simulation_notes.md)